import os
from csv2anki.collection import Collection
import click
import sys

import itertools

import collections


def split_argv(argv):
    args = []
    for i in argv:
        if i in ['-S', '--Save', '--save']:
            arg = ['save']
            args.append(arg)
        elif i in ['-E', '--Extract', '--extract']:
            arg = ['extract']
            args.append(arg)
        elif i in ['--media']:
            arg = ['media']
            args.append(arg)
        elif i in ['-M', '--Model', '--model']:
            arg = ['model']
            args.append(arg)
        elif i in ['-A', '--Anki', '--anki']:
            arg = ['anki']
            args.append(arg)
        else:
            args[-1].append(i)

    model_decks = [format_model(arg[1:]) for arg in args if arg[0] == 'model']
    ankis = [arg[1:] for arg in args if arg[0] == 'anki']
    taget = next(iter(arg[1] for arg in args if arg[0] == 'save'), None)
    extract = next(iter(arg[1] for arg in args if arg[0] == 'extract'), None)
    media = [arg[1:] for arg in args if arg[0] == 'media']
    media = list(itertools.chain(*media))

    def walk_list(l):
        paths = []
        for il in l:
            if not il:
                paths.append(None)
            elif isinstance(il, (list, tuple)):
                paths.append(walk_list(il))
            else:
                m_path = os.path.abspath(il)
                if os.path.isfile(m_path):
                    paths.append(m_path)
                elif os.path.isdir(m_path):
                    for item in os.listdir(m_path):
                        item = os.path.join(m_path, item)
                        if os.path.isfile(item):
                            paths.append(item)
        return paths

    model_decks = walk_list(model_decks)
    ankis = walk_list(ankis)

    media_path = walk_list(media)

    return model_decks, ankis, taget, extract, media_path


def format_model(argv):
    csv = []
    tmpl = []
    css = None
    argv = iter(argv)
    i = next(argv, None)
    while i:
        if i == '--csv' or i == '-c':
            ni = next(argv, None)
            if ni is None or ni[0] == '-':
                print('usage: --csv csv ...')
                raise SystemError()
            while ni and not ni[0] == '-':
                csv.append(ni)
                ni = next(argv, None)
            i = ni
        elif i == '--tmpl' or i == '-t':
            ni = next(argv, None)
            if ni is None or ni[0] == '-':
                print('usage: --tmpl tmpl ...')
                raise SystemError()
            while ni and not ni[0] == '-':
                tmpl.append(ni)
                ni = next(argv, None)
            i = ni
        elif i == '--css' or i == '-s':
            ni = next(argv, None)
            if ni is None or ni[0] == '-':
                print('usage: --css css ...')
                raise SystemError()
            css = ni
            i = next(argv, None)
        else:
            print('only support --tmpl --csv --css')
            raise SystemError()

    if not csv or not tmpl:
        print('No tmpls or csv!')
        raise SystemError()
    return csv, tmpl, css


if __name__ == '__main__':
    m_model_decks, m_ankis, m_taget, m_extract, m_media_path = split_argv(sys.argv[1:])
    col = Collection.from_files(m_model_decks, m_media_path)
    col.to_zip(m_taget)

    # if m_extract:
    #     col.to_files(m_extract)


