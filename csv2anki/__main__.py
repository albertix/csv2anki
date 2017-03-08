import click
import tempfile
import os
from . import unpack, package


@click.group()
def cli():
    pass


@cli.command("upkg")
@click.argument('apkg_path', nargs=1)
@click.option('-e', '--unpack_dir', help='解压位置', default='.')
def cli_unpack(apkg_path, unpack_dir):
    """解压缩 apkg 文件"""
    unpack(apkg_path, unpack_dir)


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
    if os.path.isdir(temp_dir):
        package(taget_path, src_path, temp_dir, media_dir, deck_name)
    else:
        with tempfile.TemporaryDirectory() as tmpdirname:
            package(taget_path, src_path, tmpdirname, media_dir, deck_name)


if __name__ == '__main__':
    cli()
