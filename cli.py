import typer
from typing import List

from lazy_ticker.database import LazyDB
from lazy_ticker.ticker import get_instruments

cli = typer.Typer()


@cli.command()
def add(symbols: List[str]):
    valid_symbols = get_instruments(symbols)
    LazyDB.add_symbols(valid_symbols)
    for symbol in valid_symbols:
        typer.echo(f"Adding {symbol.symbol} to database.")


@cli.command()
def get(limit: int = 10):
    for symbol in LazyDB.get_most_recent(limit):
        typer.echo(f"{symbol.symbol}")


if __name__ == "__main__":
    cli()
