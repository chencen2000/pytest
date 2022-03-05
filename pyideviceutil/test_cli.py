import click

@click.group()
def cli():
    pass

@cli.command()
@click.option('-u','--udid', type=str)
@click.argument('filename')
def cmd1(filename):
    """Command on cli1"""
    click.echo(f"cmd1. {filename}")

if __name__ == '__main__':
    cli()