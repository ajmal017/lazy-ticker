# from lazy_ticker import core  # used for testing paths
from fastapi import FastAPI, Request, Response, Path, status
from fastapi.responses import FileResponse
from lazy_ticker.database import LazyDB
from lazy_ticker.twitter_scraper import scrape_user_id
from lazy_ticker.schemas import InstrumentsList, TimePeriod

app = FastAPI()


@app.get("/user/")
async def get_all_users():
    query = LazyDB.get_all_users()
    if query:
        return {"message": query}
    else:
        return {"message": None}


def clean_username(username: str) -> str:
    return username.replace("@", "")


# TODO added cache for same request
@app.post("/user/{username}", status_code=201)
async def add_user(response: Response, username: str = Path(..., regex="^[a-zA-Z0-9\_\@]+$")):
    username = clean_username(username)
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
async def remove_user(username: str = Path(..., regex="^[a-zA-Z0-9\_\@]+$")):
    username = clean_username(username)
    if LazyDB.remove_user(name=username):
        return {"message": f"{username} removed"}
    else:
        return {"message": f"{username} doesn't exist."}


@app.get("/user/{username}")
async def get_user(username: str = Path(..., regex="^[a-zA-Z0-9\_\@]+$")):
    username = clean_username(username)
    query = LazyDB.get_user(name=username)
    if query:
        return {"message": query}
    else:
        return {"message": f"{username} doesn't exist."}


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
