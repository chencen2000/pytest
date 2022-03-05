import click

@click.group()
def cli():
    pass

@cli.command()
def list_devices():
    """list Apple devices"""
    click.echo(f"list Apple devices")

if __name__ == '__main__':
    cli()