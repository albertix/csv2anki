import click
import sys


def split_models(argv):
    models = []
    for i in argv:
        if i == '-M' or i == '--Model':
            model = []
            models.append(model)
        else:
            models[-1].append(i)

    models = [format_model(model) for model in models]
    return models


def format_model(argv):
    print(argv)
    csv = []
    tmpl = []
    css = None
    argv = iter(argv)
    i = next(argv, None)
    while i:
        print(i)
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
                print('usage: --tmpl tmpl ...')
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
    print(split_models(sys.argv[1:]))
