from fastapi import FastAPI, Request, Response, Path, status
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from lazy_ticker.schemas import InstrumentSchema, InstrumentsList, TimePeriod

from uplink import Consumer, get, Path
import uuid


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
async def index(request: Request, time_period: TimePeriod = TimePeriod.MONTHS):
    return RedirectResponse(f"/watchlist/{time_period.value}")


@app.get("/watchlist/{time_period}")
async def index(request: Request, time_period: TimePeriod = TimePeriod.MONTHS):
    watchlist = backend_api.get_watchlist(time_period.value)
    recent_ticker = backend_api.get_latest_ticker()

    instrument = InstrumentSchema(**recent_ticker.json())
    tradingview = instrument.get_tradingview_ticker(include_inverted=False)[0]

    return templates.TemplateResponse(
        "watchlist.html",
        {
            "request": request,
            "watchlist": watchlist.json(),
            "time_periods": TimePeriod,
            "current_period": time_period,
            "instrument": instrument,
            "tradingview": tradingview,
        },
    )


def generate_file_response(query: InstrumentsList, filename: str):
    random_id = uuid.uuid4().hex
    temp_file = f"/tmp/{random_id}.txt"
    with open(temp_file, mode="w") as write_file:
        query = ",".join([str(q) for q in query])
        write_file.write(query)
    filename = f"last_{filename}_watchlist"

    return FileResponse(temp_file, filename=filename)


@app.get("/watchlist/{time_period}/download")
async def download_watchlist(time_period: TimePeriod):
    watchlist = backend_api.get_watchlist(time_period.value)
    instruments = watchlist.json()["instruments"]
    response_list = InstrumentsList(instruments=instruments).create_list_tickers()
    if response_list:
        return generate_file_response(response_list, time_period.value)
    else:
        return generate_file_response(["EMPTY"], time_period.value)


def clean_username(username: str) -> str:
    return username.replace("@", "")
