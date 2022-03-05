import click

@click.group()
def cli():
    pass

@cli.command()
@click.option('--udid', type=str)
@click.argument('filename')
def config(filename, udid):
    """config by json file"""
    click.echo(f"do task {filename} on {udid}")

if __name__ == '__main__':
    cli()