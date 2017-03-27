import copy
import csv
import hashlib
import io
import json
import os
import re
import string
import zipfile
import tempfile
import logging
import datetime
import itertools
from .db import create_db

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


def text(text_path):
    text_path = os.path.abspath(text_path)
    txt = ''
    if os.path.isfile(text_path):
        with open(text_path, 'r', encoding='utf8') as f:
            txt = f.read()
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
        return tmpl_obj["name"], tmpl_obj['qfmt'], tmpl_obj['qfmt']

    @staticmethod
    def gen_tmpls_from_obj(tmpls_obj):
        tmpls_obj = sorted(tmpls_obj, key=lambda x: x['ord'])
        return list(Model.gen_tmpls_from_obj(tmpl) for tmpl in tmpls_obj)

    @staticmethod
    def is_cloze(tmpl_text):
        return True if re.match('{{cloze:[^}]+}}', tmpl_text) else False

    @staticmethod
    def clozed(tmpls):
        for i, tmpl in enumerate(tmpls):
            if Model.is_cloze(tmpl[1]) and Model.is_cloze(tmpl[2]):
                return [tmpl], True
        return tmpls, False

    @staticmethod
    def gen_tmpls(tmpl_paths):
        tmpls = [Model.gen_tmpl(text(tmpl_path),
                                basename(tmpl_path))
                 for tmpl_path in tmpl_paths]
        return list(tmpls)

    @staticmethod
    def gen_tmpl(tmpl_text, tmpl_name):
        """
        :param tmpl_text:
        :param tmpl_name:
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

    def __init__(self, tmpls, flds, is_cloze=None, css=None, model_name="default", has_tags=False):
        """
        :param tmpls: [(name, q_tmpl, a_tmpl), ...]
        :param flds: [fld ...]
        :param is_cloze: False as Default
        :param css: CSS
        :param model_name: default as Default
        :param has_tags: True as Default
        """

        if is_cloze is None:
            tmpls, is_cloze = Model.clozed(tmpls)
        self.tmpls = tmpls
        self.flds = flds
        self.is_cloze = is_cloze
        self.css = css if css else Model.CSS
        self.model_name = model_name
        self.has_tags = has_tags
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
        return tmpls

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
            "mod": self.did // 1000,
            "desc": ""
        }
        return deck


class ModelDeck(object):
    __fields__ = ['notes', 'model', 'deck']

    def __init__(self, notes, model, deck):
        self.notes = notes
        self.model = model
        self.deck = deck

    @staticmethod
    def from_db(conn, mid, did, col_models_decks_obj):
        model = Model.from_obj(col_models_decks_obj[0][str(mid)])
        deck = Deck.from_obj(col_models_decks_obj[1][str(did)])

        with conn.cursor() as cursor:
            note_objs = cursor.execute('SELECT notes.flds, notes.tags FROM cards, notes'
                                       ' WHERE cards.nid = notes.id '
                                       '        and notes.mid = ? '
                                       '        and cards.did = ?',
                                       (mid, did)).fetchall()

            notes = list(note_obj[0].split('\x1f') + [note_objs[1]]
                         for note_obj in note_objs)

        return ModelDeck(notes, model, deck)

    @staticmethod
    def from_csv_text(csv_text, tmpls, csv_name='', css=None):
        model_name, _, deck_name = re.findall('^(.*?)(\[(.*)\])?$', csv_name)[0]
        model_name = model_name if model_name else 'default'
        deck_name = deck_name if deck_name else 'default'

        with io.StringIO(csv_text) as f:
            reader = csv.reader(f, dialect='excel-tab')
            flds = next(reader)

            has_tags = False
            if len(flds) > 1 and flds[-1] == 'tags':
                flds = flds[:-1]
                has_tags = True

            model = Model(tmpls=tmpls, flds=flds, css=css, model_name=model_name, has_tags=has_tags)
            deck = Deck(deck_name)

            notes = list([note for note in reader])

        return ModelDeck(notes, model, deck)

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
    def cloze_ords(flds):
        flds = flds.split('\x1f')
        ords = set()
        for fld in flds:
            for t_ord in re.findall('{{c(\d+)::.+?}}', fld):
                ords.add(int(t_ord) - 1)
        if not ords:
            ords = {0, }
        return ords

    def to_notes_cards_objs(self, nid_gen, cid_gen, cid_start):
        if self.model.has_tags:
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
    __all__ = tuple(('id', 'crt', 'mod', 'scm', 'ver',
                     'dty', 'usn', 'ls', 'conf', 'models',
                     'decks', 'dconf', 'tags'))

    def __init__(self, model_decks, media_files, temp_dir=None):
        self.model_decks = model_decks if model_decks else []
        self.media_files = media_files if media_files else []
        self.temp_dir = temp_dir

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
    def from_files(model_files, media_files):
        """
        :param model_files: [[csv_files, tmpl_files, css_file] ...]
                csv_files  ( model_name[deck_name].csv ...)
                tmpl_files ( tmpl_name.txt ...)
        :param media_files:
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
        mid_dids = cursor.execute('SELECT DISTINCT mid, did'
                                  ' FROM cards, notes'
                                  ' WHERE cards.nid = notes.id').fetchall()
        model_decks = [ModelDeck.from_db(conn, mid, did, col_models_decks_obj)
                       for mid, did in mid_dids]
        return list(model_decks)

    @staticmethod
    def from_zip(path):
        path = os.path.abspath(path)

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

    def to_zip(self, z_file):

        z_file = z_file if z_file.endswith('.apkg') else "{}.apkg".format(z_file)
        z_path = os.path.abspath(z_file)
        if os.path.isdir(z_path):
            z_path = os.path.join(z_path, 'default.apkg')

        media = {}
        with zipfile.ZipFile(z_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for i, media_file in enumerate(self.media_files):
                zf.write(media_file, arcname=i)
                media[str(i)] = os.path.basename(media_file)
            zf.writestr('media', json.dumps(media))

            with tempfile.NamedTemporaryFile(delete=False) as f:
                # db_path = os.path.join(test_db_path, 'collection.anki2')
                db_path = f.name
                print(db_path)
                # gen db write to db_path
                col, notes, cards = self.info()
                create_db(col, notes, cards, db_path)

                zf.write(db_path, arcname='collection.anki2')

            os.remove(f.name)
