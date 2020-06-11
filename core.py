from lazy_ticker.pipeline import CleanUpWatchList, WatchlistTaskWrapper
import luigi

luigi.build([CleanUpWatchList()], workers=1, local_scheduler=False)
luigi.build([WatchlistTaskWrapper()], workers=10, local_scheduler=False)
