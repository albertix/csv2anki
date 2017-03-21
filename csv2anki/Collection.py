import copy
import csv
import io
import json
import os
import re
import zipfile
import tempfile
import logging


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
    def is_cloze(tmpl_text):
        return True if re.match('{{cloze:[^}]+}}', tmpl_text) else False

    @staticmethod
    def clozed(tmpls):
        for i, tmpl in enumerate(tmpls):
            if Model.is_cloze(tmpl[0]) and Model.is_cloze(tmpl[1]):
                return [tmpl], True
        return tmpls, False

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

    def __init__(self, tmpls, flds, is_cloze=None, css=None, model_name="default"):
        '''
        :param tmpls: [(qtmpl, atmpl), ...]
        :param flds:
        :param is_cloze:
        :param css:
        :param model_name:
        '''

        if is_cloze is None:
            tmpls, is_cloze = Model.clozed(tmpls)
        self.tmpls = tmpls
        self.flds = flds
        self.is_cloze = is_cloze
        self.css = css if css else Model.CSS
        self.model_name = model_name

    def to_json(self):
        pass


class Deck(Comparable):
    __fields__ = ['deck_name']

    def __init__(self, deck_name):
        self.deck_name = deck_name


class ModelDeck(object):
    __fields__ = ['notes', 'model', 'deck']

    def __init__(self, notes, model, deck):
        self.notes = notes
        self.model = model
        self.deck = deck

    @staticmethod
    def from_csv_text(csv_text, tmpls, csv_name='', css=None):
        model_name, _, deck_name = re.findall('^(.*?)(\[(.*)\])?$', csv_name)[0]
        model_name = model_name if model_name else 'default'
        deck_name = deck_name if deck_name else 'default'

        with io.StringIO(csv_text) as f:
            reader = csv.reader(f, dialect='excel-tab')
            flds = next(reader)

            model = Model(tmpls=tmpls, flds=flds, css=css, model_name=model_name)
            deck = Deck(deck_name)

            notes = list([note for note in reader])

        return ModelDeck(notes, model, deck)

    def to_db(self, conn):
        pass


class Models(object):
    pass


class Collection(object):
    __all__ = ('id', 'crt', 'mod', 'scm', 'ver',
               'dty', 'usn', 'ls', 'conf', 'models',
               'decks', 'dconf', 'tags')

    def __init__(self, model_decks, media_files):
        self.model_decks = model_decks if model_decks else []
        self.media_files = media_files

    @staticmethod
    def from_files(model_files, media_files):
        '''
        :param model_files: [[csv_files, tmpl_files, css_file] ...]
                csv_files  ( model_name[deck_name].csv ...)
                tmpl_files ( tmpl_name.txt ...)
        :param media_files:
        :return:
        '''
        model_decks = []
        for csv_files, tmpl_files, css_file in model_files:
            css = text(css_file)
            tmpls = [Model.gen_tmpl(text(tmpl_file),
                                    basename(tmpl_file))
                     for tmpl_file in tmpl_files]
            csv_name_texts = [(basename(csv_file), text(csv_file)) for csv_file in csv_files]

            model_decks = [ModelDeck.from_csv_text(csv_text,
                                                   tmpls=tmpls,
                                                   csv_name=csv_name,
                                                   css=css)
                           for csv_name, csv_text
                           in csv_name_texts]

        return Collection(model_decks, media_files)

    def info(self):
        models = []
        decks = []
        model_decks = [copy.copy(model_deck) for model_deck in self.model_decks]
        # unique models, decks
        for i, model_deck in enumerate(model_decks):
            if model_deck.model in models:
                model_deck.model = models[models.index(model_deck.model)]
            else:
                models.append(model_deck.model)

            if model_deck.deck in decks:
                model_deck.deck = decks[decks.index(model_deck.deck)]
            else:
                decks.append(model_deck.deck)

        return model_decks

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

            with tempfile.TemporaryDirectory() as tmp_dir_name:
                db_path = os.path.join(tmp_dir_name, 'collection.anki2')

                # gen db write to db_path

                zf.write(db_path, arcname='collection.anki2')
