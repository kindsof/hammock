all: build rename tox

TESTS ?= discover -b tests -p "test_*.py"

# TODO: remove this paragraph, python3.5 is not yet installed on the build machines...
TOXENV ?= py27
ENV := TOXENV=$(TOXENV)

.PHONY: tox
tox: .tox
	$(ENV) tox

.tox: dev-requirements.txt tox.ini setup.py
	$(ENV) tox --notest --recreate

clean:
	find -name *.py[co] -delete
	rm -rf build dist *.egg-info

flake8:
	flake8 hammock tests

pylint:
	pylint -r n --py3k hammock tests
	pylint -r n hammock tests

coverage:
	coverage erase
	coverage run -m unittest $(TESTS)
	coverage html

unittest:
	python -m unittest $(TESTS)

build: rpm rename

rpm:  setup.py hammock/*
	python setup.py bdist --formats=rpm
	rm dist/*.src.rpm dist/*.tar.gz

rename: dist/hammock-rest-0.0.1-1.noarch.rpm
	- rm -f $(basename $<)-*.rpm
	mv $< $(basename $<)-$(shell git rev-parse --short=7 HEAD).rpm

upload:
	python setup.py sdist upload

submit:
	solvent submitproduct rpm dist

approve:
	solvent approve --product rpm
	$(MAKE) upload

prepareForCleanBuild:
	sudo pip install tox

install:$ setup.py hammock/*
	python setup.py install

requirements: dev-requirements.txt
	pip install --upgrade pip -r -r dev-requirements.txt

test-gunicorn:
	gunicorn tests.app:application

test-uwsgi:
	.tox/py27/bin/python -m tests.app

test-cli:
	.tox/py27/bin/python -m tests.cli
