import luigi
from luigi import LocalTarget
import pydantic
from lazy_ticker.paths import PROJECT_ROOT
from lazy_ticker.database import LazyDB
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

        users = LazyDB.get_all_users()

        sleep(5)
        with open(output_path, mode="a") as write_file:
            for user in users:
                write_file.write(str(user.name))


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

        sleep(5)
        with open(output_path, mode="r") as read_file:
            print(read_file.read())
        output_path.unlink()


while True:
    for wait_time in range(5):
        sleep(1)
        print(".", end="", flush=True)
    luigi.build([CreateTextFile()], workers=1, local_scheduler=False)

    for wait_time in range(5):
        sleep(1)
        print(".", end="", flush=True)
    luigi.build([DeleteTextFile()], workers=1, local_scheduler=False)
