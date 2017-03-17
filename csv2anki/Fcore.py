
class Collection(object):

    def __init__(self, models):
        '''
        :param models:
        '''

        self.tags = {}

    @property
    def conf(self):
        pass

    @property
    def dconf(self):
        pass

    @staticmethod
    def from_jsons(models_json, decks_json):
        models = [
            (
                model['id'],
                [
                    fld['name'] if not fld['rtl'] else fld['name'] + ':rtl'
                    for fld in sorted(model['flds'], key=lambda fld: fld['ord'])],
                [
                    (tmpl['name'], tmpl['afmt'], tmpl['qfmt'])
                    for tmpl in model['tmpls']],
                model['css'])
            for model
            in (json.loads(models_json)).values()]

        decks = [
            (
                deck['id'],
                deck['name'])
            for deck in (json.loads(decks_json)).values()]

class Model(object):
    CSS = ''

    def __init__(self, flds, tmpls, css=None, mid=None):
        self.flds = flds
        self.tmpls = tmpls
        self.css = css if css else Model.CSS
        self.id = mid

    def gen_flds(self):
        pass

class Deck(object):
    def __init__(self, models):
        pass


class Models(object):
    '''
    models = [
        [id, flds, [[card_name1, [atmpl, qtmpl] ...], css]
        ...
    ]
    '''

    CSS = ""

    def __init__(self, flds, tmpls, css=None):
        self.flds = flds
        self.tmpls = tmpls
        self.css = css if css else Models.CSS

    @staticmethod
    def from_json(models_json):
        models = [
            {
                'mid': model['id'],
                'flds': [
                    fld['name'] if not fld['rtl'] else fld['name'] + ':rtl'
                    for fld in sorted(model['flds'], key=lambda fld: fld['ord'])],
                'tmpls': [
                    (tmpl['name'], tmpl['afmt'], tmpl['qfmt'])
                    for tmpl in model['tmpls']],
                'css': model['css']}
            for model
            in (json.loads(models_json)).values()]

        models = [Model(**args) for args in models]
        return models

    @staticmethod
    def to_json(models):
        pass

    @staticmethod
    def from_csv(csv, deck_name):



        return flds, notes, type, deck_name

class NotesDeck(object):
    def __init__(self, model, notes, deck_name):
        self.model = model
        self.notes = notes
        self.deck_name = deck_name