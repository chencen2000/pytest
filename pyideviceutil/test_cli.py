import click

@click.command()
@click.option('--udid', type=str)
@click.argument('filename')
def config(filename, udid):
    """Command on cli1"""
    click.echo(f"config: {filename} {udid}")

if __name__ == '__main__':
    config()