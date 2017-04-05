all: dist flake8 pylint unittest

# Default nose2 arguments, if test module was not specified
TEST ?= --config setup.cfg

clean:
	find -name *.py[co] -delete
	rm -rf build dist *.egg-info .cache

flake8:
	flake8 hammock tests

pylint:
	pylint -r n --py3k hammock tests
	pylint -r n hammock tests

unittest:
	coverage erase
	mkdir -p build
	nose2 $(TEST)
	coverage xml
	coverage html

dist: setup.py hammock/*
	python setup.py sdist

upload:
	python setup.py sdist upload -r http://strato-pypi.dc1:5002


install:$ setup.py hammock/*
	python setup.py install

requirements: dev-requirements.txt
	pip install --upgrade pip -r -r dev-requirements.txt

test-gunicorn:
	gunicorn tests.app:application

test-uwsgi:
	python -m tests.app

test-cli:
	python -m tests.cli

test-doc:
	python -m hammock.doc tests.resources1 --yaml

test-swagger:
	python -m hammock.swaggerize tests.resources1
