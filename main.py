# from lazy_ticker import core  # used for testing paths
from fastapi import FastAPI, Response, status
from fastapi.responses import FileResponse
from lazy_ticker.database import LazyDB
from lazy_ticker.twitter_scraper import scrape_user_id
from lazy_ticker.schemas import InstrumentsList
from enum import Enum

app = FastAPI()


@app.get("/user/")
async def get_all_users():
    query = LazyDB.get_all_users()
    if query:
        return {"message": query}
    else:
        return {"message": None}


# TODO added cache for same request
@app.post("/user/{username}", status_code=201)
async def add_user(username: str, response: Response):
    # TODO: parse @ symbols. Maybe use regex
    user_id = scrape_user_id(username)
    if user_id:
        LazyDB.add_user(name=username, user_id=user_id)
        return {"message": f"{username} added"}
    else:
        response.status_code = 400
        return {"message": f"{username} is an invalid account name."}


@app.delete("/user/{username}")
async def remove_user(username: str):
    if LazyDB.remove_user(name=username):
        return {"message": f"{username} removed"}
    else:
        return {"message": f"{username} doesn't exist."}


@app.get("/user/{username}")
async def get_user(username: str):
    query = LazyDB.get_user(name=username)
    if query:
        return {"message": query}
    else:
        return {"message": f"{username} doesn't exist."}


class TimeFrame(str, Enum):
    MONTH = "MONTH"
    WEEK = "WEEK"
    DAY = "DAY"
    HOUR = "HOUR"


def generate_file_response(query: InstrumentsList, filename: str):
    temp_file = "/tmp/temp.txt"  # UUID, caching withn x time
    with open(temp_file, mode="w") as write_file:
        query = ",".join([str(q) for q in query])
        write_file.write(query)

    return FileResponse(temp_file, filename=filename)


@app.get("/watchlist/{timeframe}")
async def get_watchlist(timeframe: TimeFrame):
    if timeframe == TimeFrame.MONTH:
        watchlist = LazyDB.get_watchlist_symbols_within_last_month()
    elif timeframe == TimeFrame.WEEK:
        watchlist = LazyDB.get_watchlist_symbols_within_last_week()
    elif timeframe == TimeFrame.DAY:
        watchlist = LazyDB.get_watchlist_symbols_within_last_day()
    elif timeframe == TimeFrame.HOUR:
        watchlist = LazyDB.get_watchlist_symbols_within_last_hour()

    if watchlist:
        l = InstrumentsList(instruments=watchlist).create_list_tickers()
        return generate_file_response(l, f"{timeframe}.txt")
    else:
        return "X"
