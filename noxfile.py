import nox


# @nox.session(python=False)
# def testserver(session):
#     session.run("pipenv", "run", "uvicorn", "main:app", "--reload", "--port", "5000")


@nox.session(python=False)
def run_without_webtest(session):
    # session.run("pytest", "-v", "-m", "not webtest")
    session.run("pytest", "-v")
