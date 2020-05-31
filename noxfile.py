import nox


@nox.session(python=False)
def testserver(session):
    session.run("pipenv", "run", "uvicorn", "main:app", "--reload")

