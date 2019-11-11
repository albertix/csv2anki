# -*- coding: utf-8 -*-
# Copyright: Albertix <albertix@live.com>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import copy
import csv
import hashlib
import io
import json
import os
import re
import shutil
import string
import zipfile
import tempfile
# import logging
import datetime
import itertools
import platform
import sqlite3

import chardet.universaldetector

from csv2anki.db import create_db

debug = None


def basename(path):
    b_name = os.path.basename(os.path.abspath(path))
    s = ('.' + b_name).rindex('.')
    if s > 1:
        b_name = b_name[:s-1]
    elif s == 1:
        b_name = b_name[1:]
    else:
        b_name = b_name
    return b_name


def model_name_info(name):
    if platform.system() == 'Windows':
        name=name.replace('：：','::')
    model_name, _, other_name = re.findall('^(.*?)(\[(.*)\])?$', name)[0]
    return model_name, other_name


def detect(txt_b, step=1):
    detector = chardet.universaldetector.UniversalDetector()
    lines = txt_b.splitlines()
    for line in lines[::step]:
        detector.feed(line)
        if detector.result and detector.result['confidence'] >= 0.95:
            break
        elif detector.done:
            break
    detector.close()
    return detector.result['encoding']


def text(text_path, encoding=None):
    text_path = os.path.abspath(text_path)
    txt = ''
    if os.path.isfile(text_path):
        with open(text_path, 'rb') as f:
            txt_b = f.read()
        txt_io = None
        if not encoding:
            try:
                txt_io = io.TextIOWrapper(io.BufferedReader(io.BytesIO(txt_b)), encoding=detect(txt_b, step=2))
                txt = txt_io.read()
            except UnicodeDecodeError:
                txt_io = io.TextIOWrapper(io.BufferedReader(io.BytesIO(txt_b)), encoding=detect(txt_b))
                txt = txt_io.read()
            finally:
                txt_io.close()
        else:
            with io.TextIOWrapper(io.BufferedReader(io.BytesIO(txt_b)), encoding=encoding) as txt_io:
                txt = txt_io.read()

        if (txt + " ")[0] == '\ufeff':
            txt = txt[1:]
    return txt


class Comparable(object):
    __fields__ = []

    def __repr__(self):
        return json.dumps([getattr(self, field)
                           for field in type(self).__fields__])

    def __hash__(self):
        """
        !!!
        注意 在所有fields不再变化时，才能使用
        :return:
        """
        return hash(self.__repr__())

    def __eq__(self, other):
        return all([getattr(self, field) == getattr(other, field)
                    for field in type(self).__fields__]
                   ) if isinstance(other, type(self)) else False


class Model(Comparable):

    __fields__ = ['tmpls', 'flds', 'is_cloze', 'css', 'model_name']

    CSS = ".card {\n font-family: arial;\n font-size: 20px;\n text-align: center;\n" \
          " color: black;\n background-color: white;\n}\n\n.cloze {\n font-weight: bold;\n color: blue;\n}"

    LatexPre = "\\documentclass[12pt]{article}\n\\special{papersize=3in,5in}\n" \
               "\\usepackage[utf8]{inputenc}\n\\usepackage{amssymb,amsmath}\n\\pagestyle{empty}\n" \
               "\\setlength{\\parindent}{0in}\n\\begin{document}\n"

    @staticmethod
    def from_obj(model_obj):
        tmpls = Model.gen_tmpls_from_obj(model_obj["tmpls"])
        flds = Model.gen_flds_from_obj(model_obj["flds"])
        return Model(tmpls, flds,
                     is_cloze=(model_obj["type"] == 1),
                     css=model_obj["css"],
                     model_name=model_obj["name"])

    @staticmethod
    def gen_tmpl_from_obj(tmpl_obj):
        return tmpl_obj["name"], tmpl_obj['qfmt'], tmpl_obj['afmt']

    @staticmethod
    def gen_tmpls_from_obj(tmpls_obj):
        tmpls_obj = sorted(tmpls_obj, key=lambda x: x['ord'])
        return list(Model.gen_tmpl_from_obj(tmpl) for tmpl in tmpls_obj)

    @staticmethod
    def is_cloze(tmpl_text):
        return True if re.match('{{(type:)?cloze:[^}]+}}', tmpl_text) else False

    @staticmethod
    def clozed(tmpls):
        for i, tmpl in enumerate(tmpls):
            if Model.is_cloze(tmpl[1]) or Model.is_cloze(tmpl[2]):
                return [tmpl], True
        return tmpls, False

    @staticmethod
    def gen_tmpls(tmpl_paths):
        """
        :param tmpl_paths: model_name[tmpl_name].txt => tmpl_name
        :return: [[tmpl['name'], tmpl['qtmpl'], tmpl['atmpl']] ...]
        """

        def b_name(path):
            name = basename(path)
            model_name, tmpl_name = model_name_info(name)
            tmpl_name = tmpl_name if tmpl_name else name
            return tmpl_name

        tmpls = [Model.gen_tmpl(text(tmpl_path),
                                b_name(tmpl_path))
                 for tmpl_path in tmpl_paths]
        return list(tmpls)

    @staticmethod
    def gen_tmpl(tmpl_text, tmpl_name):
        """
        :param tmpl_text:
        :param tmpl_name: tmpl_name only, without tmpl_name'[model_name].txt'
        :return: tmpl['name'], tmpl['qtmpl'], tmpl['atmpl']
        """
        m = re.fullmatch(r'(.*)(\n[<]={10,}[>])\2\n(.*)',
                         tmpl_text, flags=re.DOTALL)
        if m:
            r = m.groups()
            if len(r) == 3:
                # tmpl['qtmpl'], tmpl['atmpl']
                return tmpl_name, r[0], r[2]
        else:
            return tmpl_name, tmpl_text, ""

    def __init__(self, tmpls, flds, is_cloze=False, css=None, model_name="default"):
        """
        
        :param tmpls: [(name, q_tmpl, a_tmpl), ...]
        :param flds: [fld ...]
        :param is_cloze: False as Default
        :param css: CSS
        :param model_name: default as Default
        """

        if not is_cloze:
            tmpls, is_cloze = Model.clozed(tmpls)
        self.tmpls = tmpls
        self.flds = flds
        self.is_cloze = is_cloze
        self.css = css if css else Model.CSS
        self.model_name = model_name
        self.mid = None

    @staticmethod
    def gen_flds_from_obj(flds_obj):
        flds_obj = sorted(flds_obj, key=lambda x: x['ord'])
        flds = [name["name"] if not name["rtl"] else name["name"]+':rtl'
                for name in flds_obj]
        return flds

    @staticmethod
    def make_obj_flds(flds):
        flds = list([{
                         "name": name if not name.endswith(':rtl') else name[:-4],
                         "media": [],
                         "sticky": False,
                         "rtl": False if not name.endswith(":rtl") else True,
                         "ord": i,
                         "font": "Arial",
                         "size": 20
                     } for i, name in enumerate(flds)])
        return flds

    @staticmethod
    def make_obj_req(tmpls):
        return list([[i, "any", [0]] for i in range(len(tmpls))])

    @staticmethod
    def make_txt_tmpls(model):
        """
        :param model: 
        :return: [[name, fmt] ...] name = tmpl_name[model_name].txt
        """
        tmpls = []
        for tmpl_name, qfmt, afmt in model.tmpls:
            name = "{model_name}[{tmpl_name}].txt".\
                format(model_name=model.model_name, tmpl_name=tmpl_name)
            fmt = """{qfmt}\n<====================>\n<====================>\n{afmt}"""\
                .format(qfmt=qfmt, afmt=afmt)
            tmpls.append([name, fmt])
        return tmpls

    def to_tmpls_css_txt(self):
        """
        :return: [[[name, fmt] ...], css] name = tmpl_name[model_name].txt
        """
        tmpls = Model.make_txt_tmpls(self)
        css = ["{}.css".format(self.model_name), self.css]
        return tmpls, css

    @staticmethod
    def make_obj_tmpls(tmpls):
        # tmpls= [tmpl['name'], tmpl['qtmpl'], tmpl['atmpl']] ...
        tmpls_obj = []
        for i, (tmpl_name, qfmt, afmt) in enumerate(tmpls):
            tmpl = {
                'afmt': afmt,
                'bafmt': "",
                'bqfmt': "",
                'did': None,
                'name': tmpl_name,
                'ord': i,
                'qfmt': qfmt
            }
            tmpls_obj.append(tmpl)
        return tmpls_obj

    def to_obj(self):
        model = {
            "id": self.mid,
            "vers": [],
            "tags": [],
            "did": None,
            "usn": -1,
            "sortf": 0,
            "latexPre": Model.LatexPre,
            "latexPost": "\\end{document}",
            "name": self.model_name,
            "flds": Model.make_obj_flds(self.flds),
            "tmpls": Model.make_obj_tmpls(self.tmpls),
            "mod": self.mid,
            "type": 0,
            "css": self.css,
        }
        if self.is_cloze:
            model['type'] = 1
        else:
            model['req'] = Model.make_obj_req(model['tmpls'])
        return model


class Deck(Comparable):
    __fields__ = ['deck_name']

    def __init__(self, deck_name):
        self.deck_name = deck_name
        self.did = None

    @staticmethod
    def from_obj(deck_obj):
        return Deck(deck_obj['name'])

    def to_obj(self):
        deck = {
            "name": self.deck_name,
            "extendRev": 50,
            "usn": 0,
            "collapsed": False,
            "newToday": [
                0,
                0
            ],
            "timeToday": [
                0,
                0
            ],
            "dyn": 0,
            "extendNew": 10,
            "conf": 1,
            "revToday": [
                0,
                0
            ],
            "lrnToday": [
                0,
                0
            ],
            "id": self.did,
            "mod": self.did // 1000 if self.did else 1,
            "desc": ""
        }
        return deck


class ModelDeck(object):
    __fields__ = ['notes', 'model', 'deck']

    def __init__(self, notes, model, deck, has_tag=False):
        self.notes = notes
        self.model = model
        self.deck = deck
        self.has_tag = has_tag

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.model == other.model\
                   and self.deck == other.model\
                   and self.notes == other.notes
        else:
            return False

    @staticmethod
    def from_db(conn, mid, did, col_models_decks_obj):
        model = Model.from_obj(col_models_decks_obj[0][str(mid)])
        deck = Deck.from_obj(col_models_decks_obj[1][str(did)])

        cursor = conn.cursor()
        note_objs = cursor.execute('SELECT DISTINCT notes.flds, notes.tags FROM cards, notes'
                                   ' WHERE cards.nid = notes.id '
                                   '        and notes.mid = ? '
                                   '        and cards.did = ?',
                                   (mid, did)).fetchall()

        notes = list(note_obj[0].split('\x1f') + [note_obj[1]]
                     for note_obj in note_objs)
        cursor.close()
        return ModelDeck(notes, model, deck, has_tag=True)

    def to_csv_text(self, name=True):
        txt = io.StringIO(newline=None)
        w = csv.writer(txt, dialect='excel-tab')
        if self.has_tag:
            w.writerow(self.model.flds + ['tags'])
        else:
            w.writerow(self.model.flds)
        w.writerows(self.notes)
        if name is True:
            return "{model_name}[{deck_name}].csv"\
                .format(model_name=self.model.model_name,
                        deck_name=self.deck.deck_name
                        ), txt.getvalue()
        elif isinstance(name, str):
            return name, txt.getvalue()
        else:
            return "default.csv", txt.getvalue()

    @staticmethod
    def from_csv_text(csv_text, tmpls, csv_name='', css=None):
        """
        :param csv_text: 
        :param tmpls: 
        :param csv_name: model_name[deck_name] without .csv
        :param css: 
        :return: 
        """
        model_name, deck_name = model_name_info(csv_name)
        model_name = model_name if model_name else 'default'
        deck_name = deck_name if deck_name else 'default'

        with io.StringIO(csv_text) as f:
            reader = csv.reader(f, dialect='excel-tab')
            flds = next(reader)

            has_tag = False
            len_flds = len(flds)
            if len_flds > 1 and flds[-1] == 'tags':
                flds = flds[:-1]
                has_tag = True

            model = Model(tmpls=tmpls, flds=flds, css=css, model_name=model_name)
            deck = Deck(deck_name)

            notes = list([note[:len_flds] for note in reader])

        return ModelDeck(notes, model, deck, has_tag=has_tag)

    @staticmethod
    def make_obj_note(note, tags, mid, nid_gen):

        def guid(nn_id):
            # 64 位
            chars = string.ascii_letters + string.digits + "!#"
            g = ""
            while nn_id > 0:
                g += chars[nn_id & 63]
                nn_id >>= 6
            return g

        n_id = next(nid_gen)
        n_guid = guid(n_id)
        n_mid = mid
        n_mod = n_id // 1000
        n_usn = -1
        n_tags = tags
        n_flds = '\x1f'.join(note)
        n_sfld = note[0]
        n_csum = int(hashlib.sha1(bytes(note[0], 'utf8')).hexdigest()[:8], 16)
        n_flags = 0
        n_data = ''
        return (n_id, n_guid, n_mid,
                n_mod, n_usn, n_tags,
                n_flds, n_sfld, n_csum,
                n_flags, n_data)

    @staticmethod
    def make_obj_note_cards(nid, ords, cid_gen, cid_start=0, did=1):
        cards = []
        for t_ord in ords:
            c_id = next(cid_gen)
            c_nid = nid
            c_did = did
            c_ord = t_ord
            c_mod = c_id // 1000
            c_usn = -1
            c_type = 0
            c_queue = 0
            c_due = nid - cid_start + 1
            c_ivl = 0
            c_factor = 0
            c_reps = 0
            c_lapses = 0
            c_left = 0
            c_odue = 0
            c_odid = 0
            c_flags = 0
            c_data = ''
            cards.append((c_id, c_nid, c_did, c_ord, c_mod,
                          c_usn, c_type, c_queue, c_due, c_ivl,
                          c_factor, c_reps, c_lapses, c_left, c_odue,
                          c_odid, c_flags, c_data))

        return cards

    @staticmethod
    def cloze_ords(note_flds):
        note_flds = note_flds.split('\x1f')
        ords = set()
        for fld in note_flds:
            for t_ord in re.findall('{{c(\d+)::.+?}}', fld):
                ords.add(int(t_ord) - 1)
        if not ords:
            ords = {0, }
        return ords

    def to_notes_cards_objs(self, nid_gen, cid_gen, cid_start):
        if self.has_tag:
            notes = [ModelDeck.make_obj_note(note[:-1], note[-1], self.model.mid, nid_gen)
                     for note in self.notes]
        else:
            notes = [ModelDeck.make_obj_note(note, '', self.model.mid, nid_gen)
                     for note in self.notes]
        if not self.model.is_cloze:
            ords = tuple(range(len(self.model.tmpls)))
            cards_list = [ModelDeck.make_obj_note_cards(nid=note[0], ords=ords,
                                                        cid_gen=cid_gen, cid_start=cid_start,
                                                        did=self.deck.did)
                          for note in notes]
        else:
            cards_list = [ModelDeck.make_obj_note_cards(nid=note[0],
                                                        # note[6]: flds
                                                        ords=ModelDeck.cloze_ords(note[6]),
                                                        cid_gen=cid_gen, cid_start=cid_start,
                                                        did=self.deck.did)
                          for note in notes]
        cards = itertools.chain(*cards_list)
        return tuple(notes), tuple(cards)


class Collection(object):
    __fields__ = ['id', 'crt', 'mod', 'scm', 'ver',
                  'dty', 'usn', 'ls', 'conf', 'models',
                  'decks', 'dconf', 'tags']

    def __init__(self, model_decks, media_files):
        self.model_decks = model_decks if model_decks else []
        self.media_files = media_files if media_files else []

    @staticmethod
    def make_obj_conf(mid, did=1):
        conf = {
            'activeDecks': [did],
            'addToCur': True,
            'collapseTime': 1200,
            'curDeck': did,
            'curModel': mid,
            'dueCounts': True,
            'estTimes': True,
            'newBury': True,
            'newSpread': 0,
            'nextPos': 1,
            'sortBackwards': False,
            'sortType': 'noteFld',
            'timeLim': 0}
        return conf

    @staticmethod
    def make_obj_dconf(dconf_id=1):
        return {'{}'.format(dconf_id): {
            'autoplay': True,
            'id': 1,
            'lapse': {
                'delays': [10],
                'leechAction': 0,
                'leechFails': 8,
                'minInt': 1,
                'mult': 0},
            'maxTaken': 60,
            'mod': 0,
            'name': 'Default',
            'new': {
                'bury': True,
                'delays': [1, 10],
                'initialFactor': 2500,
                'ints': [1, 4, 7],
                'order': 1,
                'perDay': 20,
                'separate': True},
            'replayq': True,
            'rev': {
                'bury': True,
                'ease4': 1.3,
                'fuzz': 0.05,
                'ivlFct': 1,
                'maxIvl': 36500,
                'minSpace': 1,
                'perDay': 100},
            'timer': 0,
            'usn': 0}}

    @staticmethod
    def make_media_file(file_path, dir_path, i):
        shutil.copy(file_path, os.path.join(dir_path, "{}".format(i)))

    def to_files(self, dir_path, encoding='utf8'):
        dir_path = os.path.abspath(dir_path)
        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)

        for model in self.models:
            tmpls, (css_name, css_text) = model.to_tmpls_css_txt()
            css_path = os.path.join(dir_path, css_name)
            with open(css_path, 'w', encoding=encoding) as f:
                f.write(css_text)
            for model_name, fmt in tmpls:
                tmpl_path = os.path.join(dir_path, model_name)
                with open(tmpl_path, 'w', encoding=encoding) as f:
                    f.write(fmt)

        for deck_model in self.model_decks:
            csv_name, csv_text = deck_model.to_csv_text()
            if platform.system() == 'Windows':
                csv_path=csv_path.replace('::', '：：')
            csv_path = os.path.join(dir_path, csv_name)
            with open(csv_path, 'w', encoding=encoding) as f:
                f.write(csv_text)

        media_dir = os.path.join(dir_path, 'media')
        if not os.path.isdir(media_dir):
            os.mkdir(media_dir)

        media_file = set()
        for f_type, file_path in self.media_files:
            if f_type == 'file':
                file_name = os.path.basename(file_path)
                if file_name not in media_file:
                    media_file.add(file_name)
                    shutil.copy(file_path, os.path.join(media_dir, file_name))
            elif f_type == 'anki':
                with zipfile.ZipFile(file_path) as anki_zip:
                    with anki_zip.open("media") as sub_media:
                        sub_media_obj = json.loads(sub_media.read())
                    for i, imedia in sub_media_obj.items():
                        if imedia not in media_file:
                            media_file.add(imedia)
                            with open(os.path.join(media_dir, imedia), 'wb') as f:
                                f.write(anki_zip.read(i))

    @staticmethod
    def from_dir(dir_path):
        dir_path = os.path.abspath(dir_path)
        media_path = os.path.join(dir_path, "media")
        media_files = []
        if os.path.isdir(media_path):
            media_files = [('file', os.path.join(media_path, file))
                           for file in os.listdir(media_path)]

        files = os.listdir(dir_path)

        csv_files = [file for file in files if file.endswith('.csv')]
        tmpl_files = [file for file in files if file.endswith('.txt')]
        css_files = [file for file in files if file.endswith('.css')]

        models = {}

        for csv_name in csv_files:
            short_name = basename(csv_name)
            model_name, other_info = model_name_info(short_name)
            model_name = model_name if model_name else short_name

            model_info = models.get(model_name)
            if model_info is None:
                model_info = {'csv': set(), 'tmpl': set(), 'css': None}
                models[model_name] = model_info

            model_info['csv'].add(os.path.join(dir_path, csv_name))

        un_linked = set()
        for tmpl_name in tmpl_files:
            short_name = basename(tmpl_name)
            model_name, other_info = model_name_info(short_name)
            model_name = model_name if other_info else "default"

            model_info = models.get(model_name)
            if model_info is None and model_name == "default":
                un_linked.add(os.path.join(dir_path, tmpl_name))
                continue

            model_info['tmpl'].add(os.path.join(dir_path, tmpl_name))

        for css_name in css_files:
            model_name = basename(css_name)

            model_info = models.get(model_name)
            if model_info is None or (not css_name):
                continue

            model_info['css'] = os.path.join(dir_path, css_name)

        # 仅有一个model的牌组，若不存在tmpl，将未链接model的tmpl与其链接。
        if len(models) == 1:
            m = next(iter(models.values()))
            if not m['tmpl']:
                m['tmpl'].update(un_linked)

        model_files = list([
                               list(model_files['csv']),
                               list(model_files['tmpl']),
                               model_files['css']
                           ] for model_files
                           in models.values()
                           if model_files['csv'] and model_files['tmpl'])

        return Collection.from_files(model_files, media_files)

    @staticmethod
    def from_files(model_files, media_files):
        """
        :param model_files: [[csv_files, tmpl_files, css_file], ...]
                               csv_files  ( model_name[deck_name].csv ...)
                               tmpl_files ( tmpl_name.txt ...)
        :param media_files: [[type, meida_file_path | anki.apkg], ...]
                               type: file | anki
        :return:
        """
        model_decks = []
        for csv_files, tmpl_files, css_file in model_files:
            css = text(css_file)
            tmpls = Model.gen_tmpls(tmpl_files)
            csv_name_texts = [(basename(csv_file), text(csv_file)) for csv_file in csv_files]

            model_decks.append([ModelDeck.from_csv_text(csv_text,
                                                        tmpls=tmpls,
                                                        csv_name=csv_name,
                                                        css=css)
                                for csv_name, csv_text
                                in csv_name_texts])

        model_decks = list(itertools.chain(*model_decks))

        return Collection(model_decks, media_files)

    @staticmethod
    def gen_model_decks_from_db(conn):
        cursor = conn.cursor()
        col_models_decks_obj = cursor.execute('select models, decks from col').fetchone()
        col_models_decks_obj = (json.loads(col_models_decks_obj[0]), json.loads(col_models_decks_obj[1]))
        mid_dids = cursor.execute('SELECT DISTINCT mid, did'
                                  ' FROM cards, notes'
                                  ' WHERE cards.nid = notes.id').fetchall()
        # debug.append([conn, col_models_decks_obj, mid_dids])
        model_decks = [ModelDeck.from_db(conn, mid, did, col_models_decks_obj)
                       for mid, did in mid_dids]
        cursor.close()
        return list(model_decks)

    @staticmethod
    def from_zip(path):
        path = os.path.abspath(path)
        with tempfile.NamedTemporaryFile(delete=False) as f:
            with zipfile.ZipFile(path) as anki_zip:
                with anki_zip.open('collection.anki2') as col_file:
                    f.write(col_file.read())
            with sqlite3.connect(f.name) as dbconn:
                model_decks = Collection.gen_model_decks_from_db(dbconn)
            dbconn.close()
        os.remove(f.name)
        return Collection(model_decks, [['anki', path]])

    @property
    def models(self):
        """
        !!! READ ONLY !!!
        :return:
        """
        models = []
        for model_deck in self.model_decks:
            if model_deck.model not in models:
                models.append(copy.deepcopy(model_deck.model))
        return models

    @property
    def decks(self):
        """
        !!! READ ONLY !!!
        :return:
        """
        decks = []
        for model_deck in self.model_decks:
            if model_deck.deck not in decks:
                decks.append(copy.deepcopy(model_deck.deck))
        return decks

    def info(self, id_start=None):
        models = []
        decks = []
        model_decks = [copy.copy(model_deck) for model_deck in self.model_decks]
        # unique models, decks
        for i, model_deck in enumerate(model_decks):
            if model_deck.model in models:
                model_deck.model = models[models.index(model_deck.model)]
            else:
                new_model = copy.copy(model_deck.model)
                models.append(new_model)
                model_deck.model = new_model

            if model_deck.deck in decks:
                model_deck.deck = decks[decks.index(model_deck.deck)]
            else:
                new_deck = copy.copy(model_deck.deck)
                decks.append(new_deck)
                model_deck.deck = new_deck

        # index models, decks
        id_start = id_start if id_start else int(datetime.datetime.now().timestamp() * 1000)
        mid_gen = itertools.count(id_start)
        did_gen = itertools.count(id_start)
        nid_gen = itertools.count(id_start)
        cid_gen = itertools.count(id_start)
        for m in models:
            m.mid = next(mid_gen)
        for d in decks:
            d.did = next(did_gen)

        decks[0].did = 1

        all_notes, all_cards = [], []
        for model_deck in model_decks:
            notes, cards = model_deck.to_notes_cards_objs(nid_gen, cid_gen, id_start)
            all_notes.append(notes)
            all_cards.append(cards)

        all_notes = tuple(itertools.chain(*all_notes))
        all_cards = tuple(itertools.chain(*all_cards))
        all_decks = {"{}".format(deck.did): deck.to_obj() for deck in decks}
        all_models = {"{}".format(model.mid): model.to_obj() for model in models}

        conf = Collection.make_obj_conf(models[0].mid)
        dconf = Collection.make_obj_dconf()
        tags = {}

        col = (1, id_start//1000, id_start, id_start, 11,
               0, 0, 0, json.dumps(conf), json.dumps(all_models),
               json.dumps(all_decks), json.dumps(dconf), json.dumps(tags))

        # self.debug = [decks, models, model_decks]
        return col, all_notes, all_cards

    def to_zip(self, z_file="default"):
        z_file = z_file if z_file.endswith('.apkg') else "{}.apkg".format(z_file)
        z_path = os.path.abspath(z_file)
        if os.path.isdir(z_path):
            z_path = os.path.join(z_path, 'default.apkg')

        with zipfile.ZipFile(z_path, 'w', zipfile.ZIP_DEFLATED) as zf:

            with tempfile.NamedTemporaryFile(delete=False) as f:
                # db_path = os.path.join(test_db_path, 'collection.anki2')
                db_path = f.name
                # gen db write to db_path
                col, notes, cards = self.info()
                create_db(col, notes, cards, db_path)

                zf.write(db_path, arcname='collection.anki2')

            media_file = set()
            media_dict = {}
            media_gen = itertools.count(0)
            for f_type, file_path in self.media_files:
                if f_type == 'file':
                    file_name = os.path.basename(file_path)
                    if file_name not in media_file:
                        i = next(media_gen)
                        media_file.add(file_name)
                        media_dict[str(i)] = file_name
                        zf.write(file_path, arcname=str(i))
                elif f_type == 'anki':
                    with zipfile.ZipFile(file_path) as anki_zip:
                        with anki_zip.open("media") as sub_media:
                            sub_media_obj = json.loads(sub_media.read())
                        for i, imedia in sub_media_obj.items():
                            if imedia not in media_file:
                                i = next(media_gen)
                                media_file.add(imedia)
                                media_dict[str(i)] = imedia
                                with anki_zip.open(i) as sub_media_file:
                                    zf.write(sub_media_file.read(), arcname=str(i))
            zf.writestr('media', json.dumps(media_dict))
            os.remove(f.name)
