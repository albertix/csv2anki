import collections
import csv
import hashlib
import itertools
import datetime
import os
import re
import string


def t_stamp():
    return int(datetime.datetime.now().timestamp())


def ms_stamp():
    return int(datetime.datetime.now().timestamp() * 1000)


timestamp = t_stamp()
id_start = ms_stamp()
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


class Dumpable(object):
    __all__ = []

    def as_list(self, items: collections.Iterable = None):
        items = items if items else self.__all__
        return list((getattr(self, i) for i in items))

    def as_dict(self, items: collections.Iterable = None):
        items = items if items else self.__all__
        return dict(((k, getattr(self, k)) for k in items))

    def as_default(self):
        pass

    def from_list(self, values, items: collections.Iterable = None):
        items = items if items else self.__all__
        for i, k in enumerate(items):
            setattr(self, k, values[i])

    def from_dict(self, values, items: collections.Iterable = None):
        items = set(items) & self.__all__.keys() if items else self.__all__
        for k in items & values.keys():
            setattr(self, k, values[k])

    def from_default(self, values):
        pass


class Deck(Dumpable):
    __all__ = ("name", "extendRev", "usn", "collapsed", "newToday",
               "timeToday", "dyn", "extendNew", "conf", "revToday",
               "lrnToday", "id", "mod", "desc")
    
    def __init__(self, did, name, mod):
        self.name = name if name else 'default'
        self.extendRev = 50
        self.usn = 0
        self.collapsed = False
        self.newToday = [
            0,
            0
        ]
        self.timeToday = [
            0,
            0
        ]
        self.dyn = 0
        self.extendNew = 10
        # self.conf = did  # refer to self.id
        self.revToday = [
            0,
            0
        ]
        self.lrnToday = [
            0,
            0
        ]
        self.id = did
        self.mod = mod
        self.desc = ""

    @property
    def conf(self):
        return self.id


class Dconf(Dumpable):
    __all__ = ('autoplay', 'id', 'lapse', 'maxTaken', 'mod',
               'name', 'new', 'replayq', 'rev', 'timer',
               'usn')

    def __init__(self, deck: Deck):
        self._deck = deck

        self.autoplay = True
        # self.id = 1  # refer to self._deck.id
        self.lapse = {
            'delays': [10],
            'leechAction': 0,
            'leechFails': 8,
            'minInt': 1,
            'mult': 0}
        self.maxTaken = 60
        self.mod = 0
        self.name = 'Default'
        self.new = {
            'bury': True,
            'delays': [1, 10],
            'initialFactor': 2500,
            'ints': [1, 4, 7],
            'order': 1,
            'perDay': 20,
            'separate': True}
        self.replayq = True
        self.rev = {
                'bury': True,
                'ease4': 1.3,
                'fuzz': 0.05,
                'ivlFct': 1,
                'maxIvl': 36500,
                'minSpace': 1,
                'perDay': 100}
        self.timer = 0
        self.usn = 0

        @property
        def id(self):
            return self._deck.id


class Model(Dumpable):

    @property
    def __all__(self):
        if self.type == 1:
            return ('id', 'vers', 'tags', 'did', 'usn',
                    'sortf', 'latexPre', 'latexPost', 'name', 'flds',
                    'tmpls', 'mod', 'type', 'css')
        else:
            return ('id', 'vers', 'tags', 'did', 'usn',
                    'sortf', 'latexPre', 'latexPost', 'name', 'flds',
                    'tmpls', 'mod', 'type', 'css', 'req')

    CSS = ".card {\n font-family: arial;\n font-size: 20px;\n text-align: center;\n" \
          " color: black;\n background-color: white;\n}\n\n.cloze {\n font-weight: bold;\n color: blue;\n}"

    LatexPre = "\\documentclass[12pt]{article}\n\\special{papersize=3in,5in}\n" \
               "\\usepackage[utf8]{inputenc}\n\\usepackage{amssymb,amsmath}\n\\pagestyle{empty}\n" \
               "\\setlength{\\parindent}{0in}\n\\begin{document}\n"

    def __init__(self, tmpls, flds, notes, mid=None, css=None, name=None, note_with_tags=True):
        mid = mid if mid else next(m_id_gen)
        css = css if css else Model.CSS

        self._notes = notes
        self._note_with_tags = note_with_tags

        self.id = mid
        self.vers = []
        self.tags = []
        self.did = 1
        self.usn = -1
        self.sortf = 0
        self.latexPre = Model.LatexPre
        self.latexPost = "\\end{document}"
        self.name = name if name else str(mid)
        self.flds = flds
        self.tmpls = tmpls
        # self.mod = mid * 1000   # refer self.id = mid
        self.type = 0
        # self.req     # relate to self.type  req if type = 0 else None
        self.css = css

        def check_cloze(tmpl_text):
            return True if re.match('{{cloze:[^}]+}}', tmpl_text) else False

        def make_req(tmpls):
            return list([[i, "any", [0]] for i in range(len(tmpls))])

        # type check
        cloze_flag = False
        tmpl = None
        for tmpl in tmpls:
            if check_cloze(tmpl['afmt']) or check_cloze(tmpl['qfmt']):
                cloze_flag = True
                break
        if cloze_flag:
            self.type = 1
            self.tmpls = [tmpl]
            self.tmpls[0]['ord'] = 0
        else:
            self.req = make_req(self.tmpls)
        # type check end

    @property
    def mod(self):
        return self.id * 1000

    @staticmethod
    def gen_templates(template_paths: collections.Iterable):
        tmpl_dict = {main_name(tmpl_path): read_text(os.path.abspath(tmpl_path))
                     for tmpl_path in template_paths}
        tmpls = []
        for i, (name, text) in enumerate(tmpl_dict.items()):
            tmpl = {
                'afmt': "",
                'bafmt': "",
                'bqfmt': "",
                'did': None,
                'name': "{}".format(name),
                'ord': 1,
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

    @staticmethod
    def gen_header(header: collections.Iterable):
        flds = list([{
                         "name": name if not name.endswith(":rtl") else name[:-4],
                         "media": [],
                         "sticky": False,
                         "rtl": False if not name.endswith(":rtl") else True,
                         "ord": i,
                         "font": "Arial",
                         "size": 20
                     } for i, name in enumerate(header)])
        return flds

    @staticmethod
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

            flds = Model.gen_header(header)
            model = Model(tmpls, flds, notes, mid=mid, css=css, name=name, note_with_tags=note_with_tags)
        return model

    def to_csv(self):
        header = list(map(lambda x: x['name'] if not x['rtl'] else x['name']+':rtl',
                          sorted(self.flds,
                                 key=lambda x: x['ord'])))
        if self._note_with_tags:
            header.append('tags')

        csv_notes = [header] + [note[:len(header)] for note in self._notes]

        return list(csv_notes)

    def save(self, csv_path, template_path=None, css_path=None):
        csv_path = os.path.abspath(csv_path)
        if os.path.isdir(csv_path):
            base_path = csv_path
            csv_path = os.path.join(base_path, 'cards.csv')
        else:
            base_path = os.path.dirname(csv_path)

        with open(csv_path, 'w', encoding='utf8') as f:
            w = csv.writer(f, dialect='excel-tab')
            w.writerows(self.to_csv())

        template_path = template_path if template_path and os.path.isdir(template_path) else base_path
        template_path = os.path.abspath(template_path)
        for tmpl in self.tmpls:
            with open(os.path.join(template_path, '{}.txt'.format(tmpl['name'])), 'w', encoding='utf8') as f:
                f.write(tmpl['qfmt'])
                f.write('\n<====================>\n')
                f.write('<====================>\n')
                f.write(tmpl['afmt'])

        if not css_path:
            css_path = os.path.join(base_path, 'cards.css')
        elif os.path.isdir(css_path):
            css_path = os.path.join(os.path.abspath(css_path), 'cards.css')
        else:
            css_path = os.path.abspath(css_path)

        with open(css_path, 'w', encoding='utf8') as f:
            f.write(self.css)

    @staticmethod
    def gen_note(mid, note_flds, tags=""):
        def guid(x):
            # 64 位
            chars = string.ascii_letters + string.digits + "!#"
            g = ""
            while x > 0:
                g += chars[x & 63]
                x = x >> 6
            return g

        n_id = next(n_id_gen)
        n_guid = guid(n_id)
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

    @property
    def notes_cards(self):

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

        if self._note_with_tags:
            notes = (Model.gen_note(self.id, note, tags)
                     for *note, tags in self._notes)
        else:
            notes = (Model.gen_note(self.id, note) for note in self._notes)
        notes = list(notes)

        if self.type == 1:
            cards_list = [gen_note_cards(note[0], cloze_ords(note), did=self.did)
                          for note in notes]
        else:
            ords = set(map(lambda x: x['ord'], self.tmpls))
            cards_list = [gen_note_cards(note[0], ords, did=self.did)
                          for note in notes]
        cards = list(itertools.chain(*cards_list))
        return notes, cards


class Conf(Dumpable):
    __all__ = ('activeDecks', 'addToCur', 'collapseTime', 'curDeck', 'curModel',
               'dueCounts', 'estTimes', 'newBury', 'newSpread', 'nextPos',
               'sortBackwards', 'sortType', 'timeLim')
    
    def __init__(self, deck:Deck, model:Model):
        self._deck = deck
        self._model = model
        # self.activeDecks = [cur_deck]  # refer to self._deck.id
        self.addToCur = True
        self.collapseTime = 1200
        # self.curDeck = cur_deck  # refer to self._deck.id
        # self.curModel = cur_model  # refer to self._model.id
        self.dueCounts = True
        self.estTimes = True
        self.newBury = True
        self.newSpread = 0
        self.nextPos = 1
        self.sortBackwards = False
        self.sortType = 'noteFld'
        self.timeLim = 0

    @property
    def activeDecks(self):
        return [self._deck.id]

    @property
    def curDeck(self):
        return self._deck.id

    @property
    def curModel(self):
        return self._model.id


class Collection(Dumpable):
    __all__ = ('id', 'crt', 'mod', 'scm', 'ver',
               'dty', 'usn', 'ls', 'conf', 'models',
               'decks', 'dconf', 'tags')



