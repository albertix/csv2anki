import collections


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

