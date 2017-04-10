# -*- coding: utf-8 -*-
# Copyright: Albertix <albertix@live.com>
# License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html

import click
from csv2anki import Collection


class SpecialEpilog(click.Command):
    # http://stackoverflow.com/a/42489610/6704299
    def format_epilog(self, ctx, formatter):
        if self.epilog:
            formatter.write_paragraph()
            for line in self.epilog.split('\n'):
                formatter.write_text(line)

package_help_string = """
Files:
    SRC_DIR Must have:
        model_name[deck_name].csv  (1+)
        model_name[card_name].txt  (1+)
    Or:
        model_name.csv (1) without [deck_name]
        card_name.txt (1+) without model_name[]
    OPTION:
        model_name.css
        
    
    csv:  model_name[deck_name].csv
        fld1\tfld2\t...\ttags
        xxx1\txxx2\t...\ttag1 tag2
        ...
    
    Template:  model_name[card_name].txt
        # In dividing line, len('=') => 10
        Front                   |# Front Template
        {{fld1}}<br>
        <==============>        |# Dividing line
        <==============>        |# Dividing line
        {{FrontSide}}           |# Back Template
        <hr id=answer>
        {{fld2}}

    Styling:  model_name.css
        # Default
        .card {
          font-family: arial;
          font-size: 20px;
          text-align: center;
          color: black;
          background-color: white;
        }
        .cloze {
          font-weight: bold;
          color: blue;
        }
    """


@click.group()
def cli():
    pass


@cli.command(cls=SpecialEpilog, epilog=package_help_string)
@click.argument('src', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('dest', type=click.Path(exists=False), default="default.apkg")
def package(src, dest):
    """
    package src_dir dest.apkg
    """
    col = Collection.from_dir(src)
    col.to_zip(dest)


@cli.command()
@click.argument('src', type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument('dest', type=click.Path(exists=False), default="default")
def unpack(src, dest):
    """
    unpack src.apkg to dest_dir
    """
    col = Collection.from_zip(src)
    col.to_files(dest)
