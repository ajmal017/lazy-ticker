from fastapi import FastAPI, Request, Response, Path, status, Query
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from lazy_ticker.schemas import InstrumentSchema, InstrumentsList, TimePeriod
import pydantic
from typing import List

import uplink
import uuid

from mimesis.schema import Field, Schema
from mimesis.enums import Gender
from random import choice


class API(uplink.Consumer):
    @uplink.get("watchlist/{time_period}/")
    def get_watchlist(self, time_period: uplink.Path):
        pass

    @uplink.get("recent/tweet")
    def get_latest_tweet(self):
        pass

    @uplink.get("recent/ticker")
    def get_latest_ticker(self):
        pass

    @uplink.post("/user/{username}")
    def add_user(self, username: uplink.Path):
        pass

    @uplink.get("/user/")
    def get_all_users(self):
        pass


backend_api = API(base_url="http://backend:5001/")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request, time_period: TimePeriod = TimePeriod.MONTHS):
    return RedirectResponse(f"/watchlist/{time_period.value}")


@app.get("/watchlist/{time_period}")
async def index(request: Request, time_period: TimePeriod = TimePeriod.MONTHS):
    watchlist = backend_api.get_watchlist(time_period.value)
    watchlist_lenght = len(watchlist.json()["instruments"])
    recent_ticker = backend_api.get_latest_ticker()
    following = backend_api.get_all_users()

    instrument = InstrumentSchema(**recent_ticker.json())  # BUG: issue here when empty
    tradingview = instrument.get_tradingview_ticker(inverted=False)[0]

    return templates.TemplateResponse(
        "watchlist.html",
        {
            "request": request,
            "watchlist": watchlist.json(),
            "watchlist_lenght": watchlist_lenght,
            "time_periods": TimePeriod,
            "current_period": time_period,
            "instrument": instrument,
            "tradingview": tradingview,
            "following": following,
        },
    )


@app.get("/add_user")
async def add_user(username: str = Query(...)):
    backend_api.add_user(username=username).json()
    return RedirectResponse("/user_list")


@app.get("/user_list")
async def get_user_list(request: Request,):
    all_users = backend_api.get_all_users().json()["message"]
    users_amount = len(all_users)
    return templates.TemplateResponse(
        "users.html", {"request": request, "all_users": all_users, "users_amount": users_amount}
    )


def generate_file_response(query: InstrumentsList, filename: str, inverted: bool):
    random_id = uuid.uuid4().hex
    temp_file = f"/tmp/{random_id}.txt"
    with open(temp_file, mode="w") as write_file:
        query = ",".join([str(q) for q in query[:1000]])  # NOTE: Tradingview only allows 1000.
        write_file.write(query)
    if inverted:
        filename = f"last_{filename}_inverted_watchlist.txt"
    else:
        filename = f"last_{filename}_watchlist.txt"

    return FileResponse(temp_file, filename=filename)


@app.get("/watchlist/{time_period}/download")
async def download_watchlist(time_period: TimePeriod, inverted: bool = False):
    watchlist = backend_api.get_watchlist(time_period.value)
    instruments = watchlist.json()["instruments"]
    response_list = InstrumentsList(instruments=instruments).create_list_tickers(inverted=inverted)

    if response_list:
        return generate_file_response(response_list, time_period.value, inverted=inverted)
    else:
        return generate_file_response(["EMPTY"], time_period.value, inverted=inverted)


@app.get("/watchlist/{time_period}/json")
async def download_watchlist(time_period: TimePeriod, inverted: bool = False):
    watchlist = backend_api.get_watchlist(time_period.value)
    return watchlist.json()


@app.get("/{random}")
async def echo(random: str):

    locales = ["en", "cs", "da", "en-au", "en-ca", "et", "es", "it", "ja", "ko", "nl"]

    _ = Field(choice(locales))
    description = lambda: {
        "id": _("uuid"),
        "name": _("text.word"),
        "version": _("version", pre_release=True),
        "timestamp": _("timestamp", posix=False),
        "owner": {
            "email": _("person.email", domains=["google.com", "yahoo.com"], key=str.lower),
            "token": _("token_hex"),
            "creator": _("full_name", gender=Gender.FEMALE),
        },
        "filename": f"/{random}",
    }
    schema = Schema(schema=description)

    message = {"message": schema.create(iterations=1)}
    print(message)
    return message


def clean_username(username: str) -> str:
    return username.replace("@", "")
