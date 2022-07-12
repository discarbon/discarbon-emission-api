# disCarbon Emission API

An API to provide carbon emission estimates for flights, events and other activities.

## Development
### Running Natively

Assuming pyenv is used to manage virtual environments:
```
pyenv virtualenv 3.10 310-discarbon-emission-api
pyenv shell 310-discarbon-emission-api
pip install -r requirements.txt
uvicorn app.main:emission_api --reload
```

### Running in a Docker Container

```
docker build -t discarbon-emission-api .
docker run -it --init -p 8000:8000 -e PORT=8000 discarbon-emission-api
```

### Test in browser

Read the doc; http://127.0.0.1:8000/docs

Try an endpoint: http://127.0.0.1:8000/emissions/travel/planeByIATA/ZRH/ABZ/economy

### Linting and Autoformatting

The [`pre-commit` framework](https://pre-commit.com/index.html) has been configured for this repo with the following checks (hooks) for linting, import sorting and code auto-formatting:
- [`flake8`](https://flake8.pycqa.org) - linter,
- [`isort`](https://pycqa.github.io/isort/) - automatic import sorter,
- [`black`](https://black.readthedocs.io) - automatic code formatter.

Use of `pre-commit` is not a strict requirement, but is highly recommended as these checks are ran as part of Github actions. If `pre-commit` is enabled, these checks must pass before `git commit` runs successfully. Run the following to use `pre-commit`:
```shell
pip install -r requirements_dev.txt
pre-commit install
```
The hooks can be ran without running `git commit` via:
```shell
pre-commit run --all-files
```
The VS Code settings for these tools in `.vscode/settings.json` should help the pre-commit hooks pass.

### Testing

Run the tests locally:
```
pip install -r requirements_dev.txt
pip install -e .
pytest
```