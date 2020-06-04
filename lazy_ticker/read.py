import pandas
from decouple import config
from time import sleep

DATABASE_URI = config("DATABASE_URI")

while True:

    table = pandas.read_sql_table("chartdata", DATABASE_URI)

    columns = ["CHART_TIME", "OPEN_PRICE", "HIGH_PRICE", "LOW_PRICE", "CLOSE_PRICE"]
    es = table[table["key"] == "/NQ"][columns]

    es = es.set_index("CHART_TIME")
    rsamp = es.resample("1H").agg(
        {"OPEN_PRICE": "first", "HIGH_PRICE": "max", "LOW_PRICE": "min", "CLOSE_PRICE": "last"}
    )
    print(rsamp)
    sleep(5)
