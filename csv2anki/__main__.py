import click
import tempfile
import os
import csv2anki


@click.group()
def cli():
    pass


@cli.command("upkg")
@click.argument('apkg_path', nargs=1)
@click.option('-e', '--unpack_dir', help='解压位置', default='.')
def cli_unpack(apkg_path, unpack_dir):
    """解压缩 apkg 文件"""
    csv2anki.unpack(apkg_path, unpack_dir)


@cli.command("pkg")
@click.argument('taget_path')
@click.argument('src_path')
@click.option('-t', '-temp_dir', help='缓存文件夹', default=None)
@click.option('-m', '-media_dir', help='媒体文件夹', default='.')
@click.option('-n', '-deck_name', help='牌组名称，若目标位置包含[name].apkg，牌组名为[name]', default='default')
def cli_package(taget_path, src_path, temp_dir, media_dir, deck_name):
    """打包 apkg 文件"""
    taget_name = os.path.basename(os.path.abspath(taget_path))
    if deck_name == 'default' and len(taget_name) > 5 and taget_name.endswith('.apkg'):
        deck_name = taget_name[:-5]
    if temp_dir and os.path.isdir(temp_dir):
        csv2anki.package(taget_path, src_path, temp_dir, media_dir, deck_name)
    else:
        with tempfile.TemporaryDirectory() as tmpdirname:
            csv2anki.package(taget_path, src_path, tmpdirname, media_dir, deck_name)


@cli.command("spkg")
@click.argument('taget_path')
@click.argument('cvs_path')
@click.option('-t', '-tmpl_paths', help='模板文件', multiple=True)
@click.option('-c', '-css_path', help='CSS文件', default=None)
@click.option('-m', '-media_dir', help='媒体文件夹，包括图片，音频等', default=None)
@click.option('-n', '-deck_name', help='牌组名称，若目标位置包含[name].apkg，牌组名为[name]', default='default')
def cli_simple_package(taget_path, cvs_path, tmpl_paths, css_path, media_dir, deck_name):
    taget_name = os.path.basename(os.path.abspath(taget_path))
    if deck_name == 'default' and len(taget_name) > 5 and taget_name.endswith('.apkg'):
        deck_name = taget_name[:-5]

    with tempfile.TemporaryDirectory() as tmpdirname:
        model = csv2anki.make_model_from_dir(csv_path=cvs_path, tmpl_paths=tmpl_paths,
                                             css_path=css_path, name='default', temp_dir=tmpdirname)
        models = dict({model[0]: model[1]})
        col = csv2anki.make_col(models, name=deck_name)
        csv2anki.package(taget_path, "", tmpdirname,media_dir=media_dir,deck_name=deck_name, col=col)


if __name__ == '__main__':
    cli()
