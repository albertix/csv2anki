import datetime
import json
import itertools
import hashlib
import string
import random
import os
import csv
import re
import collections
import tempfile


class Dumpable(object):
    __all__ = []

    def as_list(self, items:collections.Iterable=None):
        items = items if items else self.__all__
        return list((getattr(self, i) for i in items))

    def as_dict(self, items:collections.Iterable=None):
        items = items if items else self.__all__
        return dict(((k, getattr(self, k)) for k in items))

    def as_default(self):
        pass

    def from_list(self, values, items:collections.Iterable=None):
        items = items if items else self.__all__
        for i, k in enumerate(items):
            setattr(self, k, values[i])
    
    def from_dict(self, values, items:collections.Iterable=None):
        items = set(items) & self.__all__.keys() if items else self.__all__
        for k in items & values.keys():
            setattr(self, k, values[k])
            
    def from_default(self, values):
        pass


def tstamp():
    return int(datetime.datetime.now().timestamp())


def msstamp():
    return int(datetime.datetime.now().timestamp() * 1000)


timestamp = tstamp()
id_start = msstamp()
n_id_gen = itertools.count(id_start)
c_id_gen = itertools.count(id_start)
m_id_gen = itertools.count(id_start)


def read_text(path):
    with open(path, encoding='utf8') as f:
        text = f.read()
    return text


def main_name(path):
    bname = os.path.basename(os.path.abspath(path))
    s =('.' + bname).rindex('.')
    if s > 1:
        bname = bname[:s-1]
    elif s == 1:
        bname = bname[1:]
    else:
        bname = bname
    return bname


class Collection(object):

    def make_conf(cur_model=None, cur_deck=1, active_decks=None):
        active_decks = active_decks if active_decks else [cur_deck]
        conf = {
            'activeDecks': active_decks,
            'addToCur': True,
            'collapseTime': 1200,
            'curDeck': cur_deck,
            'curModel': cur_model if cur_model else str(id_start),
            'dueCounts': True,
            'estTimes': True,
            'newBury': True,
            'newSpread': 0,
            'nextPos': 1,
            'sortBackwards': False,
            'sortType': 'noteFld',
            'timeLim': 0}
        return conf

    def make_dconf(deck_id=1):
        return {'{}'.format(deck_id): {
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

    def make_decks(deck_id=1, name=None, mod=None):
        decks = {
            "{}".format(deck_id): {
                "name": name if name else "default",
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
                "id": 1,
                "mod": mod if mod else timestamp,
                "desc": ""
            }
        }
        return decks

    def make_col(models, decks=None, conf=None, tags=None, dconf=None, crt=None, name='default'):
        crt = crt if crt else timestamp
        col = {
            'id': 1,
            'crt': crt,
            'mod': crt * 1000,
            'scm': crt * 1000,
            'ver': 11,  # 第11版
            'dty': 0,
            'usn': 0,
            'ls': 0,
            'conf': conf if conf else Collection.make_conf(cur_model=next(iter(models.keys()))),
            'models': models,
            'decks': decks if decks else Collection.make_decks(name=name),
            'dconf': dconf if dconf else Collection.make_dconf(),
            'tags': tags if tags else {},
        }
        return col

    def __init__(self, models=None, decks=None, conf=None, tags=None, dconf=None, crt=None, name='default', raw_models=None):
        if raw_models:
            self.models = raw_models
        else:
            self.models = list([Model(m['tmpls'],) for m in models.values()])
        self.col = Collection.make_col(models, decks=decks, conf=conf, tags=tags, dconf=dconf, crt=crt, name=name)

    def to_tuple(self):
        return tuple((
            self.col['id'],
            self.col['crt'],
            self.col['mod'],
            self.col['scm'],
            self.col['ver'],
            self.col['dty'],
            self.col['usn'],
            self.col['ls'],
            json.dumps(self.col['conf']),
            json.dumps(self.col['models']),
            json.dumps(self.col['decks']),
            json.dumps(self.col['dconf']),
            json.dumps(self.col['tags']),
        ))

    def from_db(dbconn):
        cursor = dbconn.cursor()

        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0].lower()] = row[idx]
            return d

        cursor.row_factory = dict_factory
        col = cursor.execute('SELECT * FROM col').fetchone()
        cursor.close()
        models = json.loads(col['models'])
        decks = json.loads(col['decks'])
        conf = json.loads(col['conf'])
        tags = json.loads(col['tags'])
        dconf = json.loads(col['dconf'])
        c = Collection(models, decks=decks, conf=conf,
                       tags=tags, dconf=dconf, crt=col['crt'])
        return c


class Model(object):

    CSS = ".card {\n font-family: arial;\n font-size: 20px;\n text-align: center;\n" \
          " color: black;\n background-color: white;\n}\n\n.cloze {\n font-weight: bold;\n color: blue;\n}"

    LatexPre = "\\documentclass[12pt]{article}\n\\special{papersize=3in,5in}\n" \
               "\\usepackage[utf8]{inputenc}\n\\usepackage{amssymb,amsmath}\n\\pagestyle{empty}\n" \
               "\\setlength{\\parindent}{0in}\n\\begin{document}\n"

    def __init__(self, tmpls, flds, notes, mid=None, css=None, name=None, note_with_tags=True):
        mid = mid if mid else next(m_id_gen)
        css = css if css else Model.CSS

        def check_cloze(tmpl_text):
            return True if re.match('{{cloze:[^}]+}}', tmpl_text) else False

        def make_req(tmpls):
            return list([[i, "any", [0]] for i in range(len(tmpls))])

        model = {
            "id": mid,
            "vers": [],
            "tags": [],
            "did": 1,
            "usn": -1,
            "sortf": 0,
            "latexPre": Model.LatexPre,
            "latexPost": "\\end{document}",

            "name": name if name else str(mid),
            "flds": flds,
            "tmpls": tmpls,
            "mod": mid * 1000,
            "type": 0,
            "css": css,
        }

        # type check
        cloze_flag = False
        tmpl = None
        for tmpl in tmpls:
            if check_cloze(tmpl['afmt']) or check_cloze(tmpl['qfmt']):
                cloze_flag = True
                break
        if cloze_flag:
            model['type'] = 1
            model['tmpls'] = [tmpl]
            model['tmpls'][0]['ord'] = 0
        else:
            model['req'] = make_req(model['tmpls'])
        # type check end

        self.model = model
        self.is_cloze = cloze_flag
        self.note_with_tags = note_with_tags
        self.notes = notes
        self.notes_list = Model.notes_list(self.model, self.notes, self.note_with_tags)
        self.cards_list = Model.cards_list(self.model, self.notes_list)

    def rebuild(self):
        self.notes_list = Model.notes_list(self.model, self.notes, self.note_with_tags)
        self.cards_list = Model.cards_list(self.model, self.notes_list)

    def gen_note(mid, note_flds, tags=""):

        def guid():
            # 64 位
            chars = string.ascii_letters + string.digits + "!#"
            g = ""
            x = random.randint(1, 2 ** 60)
            while x > 0:
                g += chars[x & 63]
                x = x >> 6
            return g

        n_id = next(n_id_gen)
        n_guid = guid()
        n_mid = mid
        n_mod = n_id // 1000
        n_usn = -1
        n_tags = tags
        n_flds = '\x1f'.join(note_flds)
        n_sfld = note_flds[0]
        n_csum = int(hashlib.sha1(bytes(note_flds[0], 'utf8')).hexdigest()[:8], 16)
        n_flags = 0
        n_data = ''
        return (n_id, n_guid, n_mid,
                n_mod, n_usn, n_tags,
                n_flds, n_sfld, n_csum,
                n_flags, n_data)

    def notes_list(model:dict, notes, note_with_tags):
        if note_with_tags:
            notes = (Model.gen_note(model['id'], note, tags)
                     for *note, tags in notes)
        else:
            notes = (Model.gen_note(model['id'], note) for note in notes)
        return list(notes)

    def cards_list(model: dict, notes: collections.Iterable):

        def cloze_ords(note):
            flds = note[6].split('\x1f')
            ords = set()
            for fld in flds:
                for t_ord in re.findall('{{c(\d+)::.+?}}', fld):
                    ords.add(int(t_ord) - 1)
            if not ords:
                ords = {0, }
            return ords

        def gen_note_cards(nid, ords:collections.Iterable, did=1):
            cards = []
            for t_ord in ords:
                c_id = next(c_id_gen)
                c_nid = nid
                c_did = did
                c_ord = t_ord
                c_mod = c_id // 1000
                c_usn = -1
                c_type = 0
                c_queue = 0
                c_due = nid - id_start + 1
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

        if model['type'] == 1:
            cards_list = [gen_note_cards(note[0], cloze_ords(note), did=model['did'])
                          for note in notes]
        else:
            ords = set(map(lambda x: x['ord'], model['tmpls']))
            cards_list = [gen_note_cards(note[0], ords, did=model['did'])
                          for note in notes]
        cards = itertools.chain(*cards_list)
        return list(cards)

    def gen_tmpls(tmpl_paths:collections.Iterable, did=1):
        tmpl_dict = dict((main_name(tmpl_path),
                       read_text(
                           os.path.abspath(tmpl_path)))
                      for tmpl_path in tmpl_paths)
        tmpls = []
        for i, (name, text) in enumerate(tmpl_dict.items()):
            tmpl = {
                'afmt': "",
                'bafmt': "",
                'bqfmt': "",
                'did': did,
                'name': "{}".format(name),
                'ord': i,
                'qfmt': ""
            }
            m = re.fullmatch(r'(.*)(\n[<]={10,}[>])\2\n(.*)',
                             text, flags=re.DOTALL)
            if m:
                r = m.groups()
                if len(r) == 3:
                    tmpl["qfmt"] = r[0]
                    tmpl["afmt"] = r[2]
            tmpls.append(tmpl)
        if tmpls:
            tmpls[0]['did'] = None
        return tmpls

    def gen_flds(flds_list: collections.Iterable):
        flds = list([{
                         "name": name,
                         "media": [],
                         "sticky": False,
                         "rtl": False if not name.endswith(":rtl") else True,
                         "ord": i,
                         "font": "Arial",
                         "size": 20
                     } for i, name in enumerate(flds_list)])
        return flds

    def from_csv(tmpls, csv_path, mid=None, css=None, name=None, note_with_tags=True):

        csv_path = os.path.abspath(csv_path)
        name = name if name else main_name(csv_path)
        with open(csv_path, 'r', encoding='utf8') as csv_file:
            reader = csv.reader(csv_file, dialect='excel-tab')
            header = next(reader)

            notes = list([note for note in reader])

            if note_with_tags and len(header) > 1 and header[-1] == 'tags':
                header = header[:-1]
            else:
                note_with_tags = False

            flds = Model.gen_flds(header)

            model = Model(tmpls, flds, notes, mid=mid, css=css, name=name, note_with_tags=note_with_tags)

        return model


class Package(object):

    def __init__(self,deck_name, models, media, tempdir):
        self.media = media
        self.models = dict((str(m.model['id']), m.model) for m in modeles)

        self.notes_list = list(itertools.chain(*(m.notes_list for m in models)))
        self.cards_list = list(itertools.chain(*(m.cards_list for m in models)))

        self.col = Collection(self.models, name=deck_name)
        self.tempdir = tempdir

    def save(self, name='default.apkg'):
        pass


