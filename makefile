.PHONY : venv black flake9 mypy pylint lint pretty tests

VENV ?= .venv
PYTHON ?= python3.10
TESTS ?= tests
CODE ?= redantic
ALL = $(CODE) $(TESTS)
JOBS ?= 4

venv:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/python -m pip install --upgrade pip
	$(VENV)/bin/python -m pip install poetry
	$(VENV)/bin/poetry install

black:
	$(VENV)/bin/black --skip-string-normalization --check $(ALL)

flake8:
	$(VENV)/bin/flake8 --jobs $(JOBS) --statistics --show-source $(ALL)

mypy:
	$(VENV)/bin/mypy --install-types $(ALL)

lint: black flake8 mypy

pretty:
	$(VENV)/bin/isort $(ALL)
	$(VENV)/bin/black --skip-string-normalization $(ALL)

tests:
	$(VENV)/bin/pytest --cov=$(CODE) $(TESTS)
