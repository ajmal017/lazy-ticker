# lazy-ticker

Playing around with some new libraries. Fastapi, tda-api, pydantic, typer.

```
nox -s testserver
nox -f chromedriver-noxfile.py -s download_chromedriver
nox -f chromedriver-noxfile.py -s remove_chromedriver
```

Required .env
```
TD_AMERITRADE_API_KEY="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA@AMER.OAUTHAP"
TD_AMERITRADE_REDIRECT_URI="https://localhost:8080"
TD_AMERITRADE_ACCOUNT_NUMBER="000000000"

DATABASE_IP=localhost
DATABASE_PORT=5432
DATABASE_USER=lazyuser
DATABASE_PASSWORD=lazysecret
```

Optional .env
```
CHROMEDRIVER_LOCATION
```
