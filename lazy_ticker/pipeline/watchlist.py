from datetime import datetime, timedelta
from time import time
from lazy_ticker.database import LazyDB, Hours
from lazy_ticker.paths import WATCHLIST_PATH
from pathlib import Path
import shutil

import luigi


class CreateWatchlistsFolder(luigi.Task):
    def output(self):
        target = str(WATCHLIST_PATH)
        return luigi.LocalTarget(target)

    def run(self):
        directory = Path(self.output().path)
        directory.mkdir(exist_ok=True)


class CreateDateFolder(luigi.Task):
    date = luigi.DateParameter()

    def requires(self):
        return CreateWatchlistsFolder()

    def output(self):
        folder_name = f"{self.date.year}_{self.date.month}_{self.date.day}"
        target = str(Path(self.input().path) / folder_name)
        return luigi.LocalTarget(target)

    def run(self):
        directory = Path(self.output().path)
        directory.mkdir(exist_ok=True)


class CreateWatchlist(luigi.Task):
    date = luigi.DateParameter()
    since = luigi.EnumParameter(enum=Hours)
    inverted = luigi.BoolParameter()

    def requires(self):
        return CreateWatchlistsFolder()

    def output(self):
        if self.inverted:
            target = f"last_{self.since.name}_hour_watchlist_plus_inverted.txt"
        else:
            target = f"last_{self.since.name}_hour_watchlist.txt"

        path = Path(self.input().path) / target
        return luigi.LocalTarget(str(path))

    def run(self):
        symbols = LazyDB.get_symbols_since(self.since)
        watch_list = []
        for symbol in symbols:
            watch_list += symbol.get_trading_view_string(include_inverted=self.inverted)

        with open(self.output().path, mode="w") as file:
            file.write(",".join(watch_list))


class CleanUpWatchList(luigi.Task):
    date = luigi.DateParameter(default=datetime.utcnow())
    created_by = luigi.IntParameter(default=time() - 1 * 60)

    def requires(self):
        return CreateWatchlistsFolder()

    def run(self):
        path = Path(self.input().path)
        paths = list(path.glob("**/*"))
        for p in paths:
            created = p.stat().st_ctime
            if created < self.created_by:
                print(self.created_by)
                if p.is_file():
                    p.unlink()

    def complete(self):
        path = Path(self.input().path)
        paths = list(path.glob("**/*"))
        for p in paths:
            created = p.stat().st_ctime
            if created < self.created_by:
                return False
        else:
            return True


class WatchlistTaskWrapper(luigi.WrapperTask):
    date = luigi.DateParameter(default=datetime.utcnow())

    def requires(self):
        inverted = [CreateWatchlist(date=self.date, since=hour, inverted=True) for hour in Hours]
        normal = [CreateWatchlist(date=self.date, since=hour, inverted=False) for hour in Hours]
        tasks = normal + inverted
        for task in tasks:
            yield task


WATCHLIST_PIPELINE = [CleanUpWatchList(), WatchlistTaskWrapper()]

if __name__ == "__main__":
    luigi.build([CleanUpWatchList()], workers=1, local_scheduler=False)
    luigi.build([WatchlistTaskWrapper()], workers=10, local_scheduler=False)
