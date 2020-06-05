import typer

cli = typer.Typer()


@cli.command()
def add_symbol(symbol: str):
    typer.echo(f"Adding {symbol} to database.")


if __name__ == "__main__":
    cli()
