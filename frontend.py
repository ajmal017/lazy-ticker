# from lazy_ticker import core  # used for testing paths
from fastapi import FastAPI, Request, Response, Path, status
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from lazy_ticker.schemas import InstrumentSchema, TimePeriod

from uplink import Consumer, get, Path


class API(Consumer):
    @get("watchlist/{time_period}/")
    def get_watchlist(self, time_period: Path):
        pass

    @get("recent/tweet")
    def get_latest_tweet(self):
        pass

    @get("recent/ticker")
    def get_latest_ticker(self):
        pass


backend_api = API(base_url="http://backend:5001/")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request, timeperiod: TimePeriod = TimePeriod.MONTHS):
    return RedirectResponse(f"/watchlist/{timeperiod.value}")

    # watchlist = backend_api.get_watchlist(timeperiod.value)
    # recent_ticker = backend_api.get_latest_ticker()
    #
    # instrument = InstrumentSchema(**recent_ticker.json())
    # tradingview = instrument.get_tradingview_ticker(include_inverted=False)[0]
    #
    # return templates.TemplateResponse(
    #     "index.html",
    #     {
    #         "request": request,
    #         "watchlist": watchlist.json(),
    #         "time_periods": TimePeriod,
    #         "current_period": timeperiod,
    #         "recent_instrument": instrument,
    #         "tradingview": tradingview,
    #     },
    # )


@app.get("/watchlist/{timeperiod}")
async def index(request: Request, timeperiod: TimePeriod = TimePeriod.MONTHS):
    watchlist = backend_api.get_watchlist(timeperiod.value)
    recent_ticker = backend_api.get_latest_ticker()

    instrument = InstrumentSchema(**recent_ticker.json())
    tradingview = instrument.get_tradingview_ticker(include_inverted=False)[0]

    return templates.TemplateResponse(
        "watchlist.html",
        {
            "request": request,
            "watchlist": watchlist.json(),
            "time_periods": TimePeriod,
            "current_period": timeperiod,
            "instrument": instrument,
            "tradingview": tradingview,
        },
    )


# @app.post("/")


def clean_username(username: str) -> str:
    return username.replace("@", "")
