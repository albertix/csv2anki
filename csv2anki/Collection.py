from .Base import Dumpable


class Collection(Dumpable):
    __all__ = ('id', 'crt', 'mod', 'scm', 'ver',
               'dty', 'usn', 'ls', 'conf', 'models',
               'decks', 'dconf', 'tags')

    def as_default(self):
        col = self.as_list()
        # models
        pass
