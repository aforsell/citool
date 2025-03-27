# Makefile for citool

PYTHON=python3
VENV=.venv
ACTIVATE=. $(VENV)/bin/activate

install:
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && pip install -U pip
	$(ACTIVATE) && pip install -r requirements.txt
	$(ACTIVATE) && pip install -r requirements-dev.txt

test:
	$(ACTIVATE) && pytest --cov=src --cov-report=term-missing

lint:
	$(ACTIVATE) && ruff check src tests

format:
	$(ACTIVATE) && ruff format src tests

run:
	$(ACTIVATE) && ./bin/citool --help

clean:
	rm -rf .pytest_cache .coverage htmlcov .mypy_cache

setup-test-project:
	./setup_test_project.sh

clean-test-project:
	rm -rf test_project

.PHONY: install test lint format run clean setup-test-project clean-test-project
