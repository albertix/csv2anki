import collections
import os
import re


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
        with open(text_path, 'r') as f:
            txt = f.read()
    return txt


class Model(object):

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
        :param type:
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


class ModelDeck(object):
    def __init__(self, notes, model, deck):
        self.notes = notes
        self.model = model
        self.deck = deck

    @staticmethod
    def from_csv_file(csv_file, tmpls, css=None):
        csv_path = os.path.abspath(csv_path)


    def to_db(self, conn):
        pass


class Models(object):
    pass


class Collection(object):
    __all__ = ('id', 'crt', 'mod', 'scm', 'ver',
               'dty', 'usn', 'ls', 'conf', 'models',
               'decks', 'dconf', 'tags')

    def __init__(self):
        self.model_decks = []

    @staticmethod
    def from_files(model_files, media_files):
        '''
        :param model_files: [[csv_files, tmpl_files, css_file] ...]
                csv_files  ( model_name[deck_name].csv ...)
                tmpl_files ( tmpl_name.txt ...)
        :param media_files:
        :return:
        '''

        for csv_files, tmpl_files, css_file in model_files:
            css = text(css_file)
            tmpls = [Model.gen_tmpl(text(tmpl_file),
                                    basename(tmpl_file))
                     for tmpl_file in tmpl_files]
            csv_texts = [text(csv_file) for csv_file in csv_files]

