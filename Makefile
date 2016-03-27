all: build tox

# For unittests,
# If no specific test was given to run, run unitests in discover mode.
TEST ?= discover -b tests -p test_*.py

# TODO: remove this paragraph, python3.5 is not yet installed on the build machines...
TOXENV ?= py27
ENV := TOXENV=$(TOXENV)

tox: .tox
	$(ENV) tox

.tox: dev-requirements.txt requirements.txt tox.ini setup.py
	$(ENV) tox --notest --recreate || rm -rf .tox

clean:
	find hammock tests examples -name *.py[co] -delete
	rm -rf dist build *.egg-info .coverage

flake8:
	flake8 --max-line-length=145 hammock tests

pylint:
	pylint -r n --py3k hammock tests
	pylint -r n hammock tests

coverage:
	coverage erase
	coverage run -m unittest $(TEST)
	coverage html

unittest:
	python -m unittest $(TEST)

.PHONY: build
build:
	python setup.py sdist

install:
	python setup.py install

submit:
	#submit...

approve:
	python setup.py s_dist upload

test-gunicorn:
	gunicorn tests.app:application

test-uwsgi:
	.tox/py27/bin/python -m tests.app

test-cli:
	.tox/py27/bin/python -m tests.cli

prepareForCleanBuild:
	sudo pip install tox
