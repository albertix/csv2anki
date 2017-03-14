from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
import collections
import csv
import hashlib
import itertools
import datetime
import os
import re
import string
from collections import OrderedDict
Base = declarative_base()


class Dumpable(object):
    __all__ = OrderedDict()

    def as_list(self, items: collections.Iterable = None):
        items = items if items else self.__all__.keys()
        return list((getattr(self, i) for i in items))

    def as_dict(self, items: collections.Iterable = None):
        items = items if items else self.__all__.keys()
        return dict(((k, getattr(self, k)) for k in items))

    def as_default(self):
        pass

    def from_list(self, values, items: collections.Iterable = None):
        items = items if items else self.__all__.keys()
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


class Conf(Dumpable):
    __all__ = ('activeDecks', 'addToCur', 'collapseTime', 'curDeck', 'curModel',
               'dueCounts', 'estTimes', 'newBury', 'newSpread', 'nextPos',
               'sortBackwards', 'sortType', 'timeLim')

    def __init__(self, deck: Deck, model: Model):
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


class Col(Base):
    __tablename__ = 'col'

    id = Column(Integer, primary_key=True)
    crt = Column(Integer, nullable=False)
    mod = Column(Integer, nullable=False)
    scm = Column(Integer, nullable=False)
    ver = Column(Integer, nullable=False)
    dty = Column(Integer, nullable=False)
    usn = Column(Integer, nullable=False)
    ls = Column(Integer, nullable=False)
    _conf = Column('conf', String, nullable=False)
    _models = Column('models', String, nullable=False)
    _decks = Column('decks', String, nullable=False)
    _dconf = Column('dconf', String, nullable=False)
    _tags = Column('tags', String, nullable=False)

    @hybrid_property
    def conf(self):
        pass

    @hybrid_property
    def tags(self):
        return json.loads(self._tags)

    @tags.setter
    def tags(self, tags):
        self._tags = json.dumps(tags)

e = create_engine("sqlite:///collection.anki2", echo=True)
# Base.metadata.create_all(e)

s = Session(e)
