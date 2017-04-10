import subprocess
import click


@click.group()
def cli():
    pass


@cli.command()
def clean():
    subprocess.call(['rm', '-r', 'dist', 'build', 'csv2anki.egg-info'])


@cli.command()
def build():
    subprocess.call(['python', 'setup.py', 'sdist', 'bdist_wheel'])


@cli.command()
def upload():
    print(' '.join(['twine', 'upload', 'dist/*']))
    # subprocess.call(['twine', 'upload', 'dist/*'])


if __name__ == '__main__':
    cli()
