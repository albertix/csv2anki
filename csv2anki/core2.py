import datetime
import json
from os.path import join as p_join


def tstamp():
    return int(datetime.datetime.now().timestamp())


def msstamp():
    return int(datetime.datetime.now().timestamp() * 1000)


timestamp = tstamp()
id_start = msstamp()
n_id_gen = itertools.count(id_start)
c_id_gen = itertools.count(id_start)
m_id_gen = itertools.count(id_start)


class Collection(object):
    def __init__(self, models, name='default', conf=None, decks=None, dconf=None, tags=None):
        def make_conf(curModel=None, curDeck=1, activeDecks=None):
            activeDecks = activeDecks if activeDecks else [curDeck]
            conf = {
                'activeDecks': activeDecks,
                'addToCur': True,
                'collapseTime': 1200,
                'curDeck': curDeck,
                'curModel': curModel if curModel else str(id_start),
                'dueCounts': True,
                'estTimes': True,
                'newBury': True,
                'newSpread': 0,
                'nextPos': 1,
                'sortBackwards': False,
                'sortType': 'noteFld',
                'timeLim': 0}
            return conf

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
            'conf': conf if conf else make_conf(),
            'models': models,
            'decks': decks if decks else make_decks(name=name),
            'dconf': dconf if dconf else make_dconf(),
            'tags': tags if tags else {},
        }

        self.col = col

    def __getattr__(self, item):
        return self.col.get(item, None)

    def __setattr__(self, key, value):
        self.col[key] = value

    def value(self):
        return self.col

    def to_list(self):
        return (
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
        )

class Model(object):
    def __init__(self, tags=None, css=None):
