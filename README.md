# lazy-ticker

playing around with fastapi

```
nox -s testserver
nox -f chromedriver-noxfile.py -s download_chromedriver
nox -f chromedriver-noxfile.py -s remove_chromedriver
```

Required env
```
TD_AMERITRADE_API_KEY="AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA@AMER.OAUTHAP"
TD_AMERITRADE_REDIRECT_URI="https://localhost:8080"
TD_AMERITRADE_ACCOUNT_NUMBER="000000000"
DATABASE_URI="postgresql://user:pass@localhost:5432/mydatabase"  
```

Optional env
```
CHROMEDRIVER_LOCATION
```
