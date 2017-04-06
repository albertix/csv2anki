# -*- coding: utf-8 -*-
# Copyright: Albertix <albertix@live.com>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import click
from csv2anki import Collection


@click.group()
def cli():
    pass


@cli.command()
@click.option('--src', '-s', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option('--dest', '-d', type=click.Path(exists=False), default="default.apkg")
def package(src, dest):
    col = Collection.from_dir(src)
    col.to_zip(dest)


@cli.command()
@click.option('--src', '-s', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.option('--dest', '-d', type=click.Path(exists=False), default="default")
def unpack(src, dest):
    col = Collection.from_zip(src)
    col.to_files(dest)

