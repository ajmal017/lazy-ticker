import typer
from typing import List

cli = typer.Typer()


@cli.command()
def add_symbol(symbol: str):
    typer.echo(f"Adding {symbol} to database.")


@cli.command()
def add_symbols(symbols: List[str]):
    typer.echo(f"Adding {symbols} to database.")


if __name__ == "__main__":
    cli()
