import luigi
from luigi import LocalTarget
import pydantic
from lazy_ticker.paths import PROJECT_ROOT
from pathlib import Path
from time import sleep


@pydantic.validate_arguments
def create_target(path: Path):
    return luigi.LocalTarget(str(path))


def create_path(local_target: LocalTarget):
    if not isinstance(local_target, LocalTarget):
        raise TypeError("Must be type a LocalTarget")
    return Path(local_target.path)


class CreateTextFile(luigi.Task):
    def output(self):
        target = PROJECT_ROOT / "testfile"
        return create_target(target)

    def run(self):
        output_path = create_path(self.output())
        from time import sleep

        sleep(15)
        output_path.touch()


class DeleteTextFile(luigi.Task):
    def complete(self):
        output_path = create_path(self.output())
        return output_path.exists() == False

    def output(self):
        target = PROJECT_ROOT / "testfile"
        return create_target(target)

    def run(self):
        output_path = create_path(self.output())
        from time import sleep

        sleep(15)
        output_path.unlink()


while True:
    for wait_time in range(15):
        sleep(1)
        print(".", end="", flush=True)
    luigi.build([CreateTextFile()], workers=1, local_scheduler=False)

    for wait_time in range(15):
        sleep(1)
        print(".", end="", flush=True)
    luigi.build([DeleteTextFile()], workers=1, local_scheduler=False)
