from lazy_ticker.paths import DATA_DIRECTORY
import shutil
import requests
import pendulum

URL = "http://localhost/user"

# IDEA: restor users from old data flag
# NOTE: Restore users from last states.

if DATA_DIRECTORY.exists():
    users = list(set(path.stem for path in DATA_DIRECTORY.glob("**/*.json")))
    for user in users:
        resp = requests.post(f"{URL}/{user}")
        print(resp)


# NOTE: Useful for cleanup. cleanup folders older than 24 hours utc time.
# date_paths = list(DATA_DIRECTORY.glob("*"))
date_paths = list(set(path.stem for path in DATA_DIRECTORY.glob("*")))

for path in date_paths:

    dir_dt = pendulum.from_format(path, "YYYY_MM_DD", tz="UTC")
    older_than_yesterday = dir_dt < pendulum.yesterday(tz="UTC")

    if older_than_yesterday:
        # shutil.rmtree(path)
        print(path, "is too old cleaning up")
