from pathlib import Path

SOURCE_PATH = Path(__file__).parent.absolute()
PROJECT_ROOT = SOURCE_PATH.parent
LOCAL_CHROMEDRIVER_LOCATION = PROJECT_ROOT / "chromedriver"
DATA_DIRECTORY = PROJECT_ROOT / "data"
