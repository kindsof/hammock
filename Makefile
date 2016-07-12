all: dist tox

# Default nose2 arguments, if test module was not specified
TEST ?= --config setup.cfg

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

unittest:
	coverage erase
	mkdir -p build
	nose2 $(TEST)
	coverage xml
	coverage html

dist: setup.py hammock/*
	python setup.py bdist --formats=rpm
	rm dist/*.src.rpm dist/*.tar.gz

upload:
	python setup.py sdist upload -r http://strato-pypi.dc1:5001

submit:
	solvent submitproduct rpm dist

approve:
	@if ! (git diff --exit-code --quiet && git diff --exit-code --cached --quiet); \
	then \
		echo "Please commit any local changes prior to approving"; \
		false; \
	fi
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

test-doc:
	.tox/py27/bin/python -m hammock.doc tests.resources1 --yaml
