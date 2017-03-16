
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
                [
                    fld['name'] if not fld['rtl'] else fld['name'] + ':rtl'
                    for fld in sorted(model['flds'], key=lambda fld: fld['ord'])],
                [
                    (tmpl['name'], tmpl['afmt'], tmpl['qfmt'])
                    for tmpl in model['tmpls']],
                model['css'])
            for model
            in (json.loads(models_json)).values()]

        decks = 

class Model(object):

    CSS = ""

    def __init__(self, flds, tmpls, css=None):
        self.flds = flds
        self.tmpls = tmpls
        self.css = css if css else Models.CSS


class NotesDeck(object):
    def __init__(self, model, notes, deck_name):
        self.model = model
        self.notes = notes
        self.deck_name = deck_name