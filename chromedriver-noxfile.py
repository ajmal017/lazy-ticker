import nox
from urllib.request import urlopen
import urllib.error
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

VERSION_URL = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
DOWNLOAD_URL = "https://chromedriver.storage.googleapis.com/{}/chromedriver_linux64.zip"

CHROMEDRIVER_LOCATION = PROJECT_ROOT / "chromedriver"
CHROMEDRIVER_DOWNLOAD_LOCATION = PROJECT_ROOT / "chromedriver_linux64.zip"
PLATFORM = "linux"


def get_chrome_version():
    with subprocess.Popen(["google-chrome", "--version"], stdout=subprocess.PIPE) as proc:
        version = proc.stdout.read().decode("utf-8").replace("Google Chrome", "").strip()
        return version


def get_chromedriver_latest_version():
    response = urlopen(VERSION_URL).read().decode()
    return response


def check_chrome_and_chromedriver_major_versions_match(chrome_version, chromedriver_version):
    if chrome_version.split(".")[0] != chromedriver_version.split(".")[0]:
        print("Chrome appears to be out of date. {chrome_version} != {chromedriver_version}")
        return False
    else:
        return True


@nox.session(python=False)
def download_chromedriver(session):

    if not CHROMEDRIVER_LOCATION.exists():
        print(CHROMEDRIVER_LOCATION, "doesnt exist")
        chrome_version = get_chrome_version()
        chromedriver_latest_version = get_chromedriver_latest_version()

        assert check_chrome_and_chromedriver_major_versions_match(
            chrome_version, chromedriver_latest_version
        )
        print(chromedriver_latest_version)
        download_url = DOWNLOAD_URL.format(chromedriver_latest_version)

        session.run("wget", "--verbose", "--no-clobber", download_url, external=True)
        session.run("unzip", str(CHROMEDRIVER_DOWNLOAD_LOCATION), external=True)
        assert session.run(f"{CHROMEDRIVER_LOCATION}", "--version")


@nox.session(python=False)
def remove_chromedriver(session):
    if CHROMEDRIVER_LOCATION.exists():
        print(CHROMEDRIVER_LOCATION, "exist")
        session.run("rm", str(CHROMEDRIVER_DOWNLOAD_LOCATION), external=True)
        session.run("rm", str(CHROMEDRIVER_LOCATION), external=True)
