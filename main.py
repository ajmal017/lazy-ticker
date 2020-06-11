from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import FileResponse
from lazy_ticker.database import LazyDB
from lazy_ticker.ticker import get_instruments
from typing import List
from lazy_ticker.schema import Hours
from lazy_ticker.paths import WATCHLIST_PATH
from lazy_ticker.pipeline import WATCHLIST_PIPELINE
import luigi

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "TESTING!!!"}


@app.get("/symbols/")
async def get_symbols(limit: int = 10):
    return LazyDB.get_most_recent(limit)


@app.get("/symbols/all")
async def get_all_symbols():
    return LazyDB.get_symbols()


@app.post("/symbols/")
async def add_symbols(symbols: List[str]):
    valid_symbols = get_instruments(symbols)
    LazyDB.add_symbols(valid_symbols)
    return valid_symbols


@app.post("/watchlist/download/{since}")
async def download_all_symbols(since: Hours, filename: str, inverted: bool = True):

    for task in WATCHLIST_PIPELINE:
        luigi.build([task], workers=10, local_scheduler=False)

    if inverted:
        target = f"last_{since.name}_hour_watchlist_plus_inverted.txt"
    else:
        target = f"last_{since.name}_hour_watchlist.txt"

    path = WATCHLIST_PATH / target
    return FileResponse(path, filename=filename)
