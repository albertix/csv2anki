import click

@click.group()
def hello():
    pass


@hello.command('h')
@click.argument('name')
@click.option('--count', '-c', default=1, help='number of greetings')
def h(name, count):
    for x in range(count):
        click.echo('Hello %s!' % name)

if __name__ == '__main__':
    hello()