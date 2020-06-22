# from lazy_ticker import core  # used for testing paths
from fastapi import FastAPI, Response, status
from fastapi.responses import FileResponse
from lazy_ticker.database import LazyDB
from lazy_ticker.twitter_scraper import scrape_user_id
from lazy_ticker.schemas import InstrumentsList
from typing import Dict
from enum import Enum
import uuid

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


# TODO: In the future it should delete all name.json from data folder.
# or send a message to a clean up task which does the ^ job at the end
# of a pipeline cycle.
# IDEA: also removes all tweets with user_id
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


class TimePeriod(str, Enum):
    MONTHS = "months"
    WEEKS = "weeks"
    DAYS = "days"
    HOURS = "hours"

    # IDEA: May add the ability to query by amount using amount kwarg.

    def convert_to_period(self, amount: int = 1) -> Dict[str, int]:
        return {self.value: amount}


def generate_file_response(query: InstrumentsList, filename: str):
    random_id = uuid.uuid4().hex
    temp_file = f"/tmp/{random_id}.txt"  # UUID, caching withn x time
    with open(temp_file, mode="w") as write_file:
        query = ",".join([str(q) for q in query])
        write_file.write(query)
    filename = f"last_{filename}_watchlist"

    return FileResponse(temp_file, filename=filename)


@app.get("/watchlist/{time_period}/download")
async def download_watchlist(time_period: TimePeriod):
    period = time_period.convert_to_period()
    watchlist = LazyDB.get_watchlist_symbols_within_time_period(period)
    response_list = InstrumentsList(instruments=watchlist).create_list_tickers()

    return generate_file_response(response_list, time_period.value)


@app.get("/watchlist/{time_period}")
async def get_watchlist(time_period: TimePeriod):
    period = time_period.convert_to_period()
    watchlist = LazyDB.get_watchlist_symbols_within_time_period(period)

    return InstrumentsList(instruments=watchlist)


@app.get("/recent/tweet")
async def get_latest_tweet():
    return LazyDB.get_most_recently_tweeted_symbol()


@app.get("/recent/ticker")
async def get_latest_ticker():
    return LazyDB.get_most_recent_unique_ticker()
