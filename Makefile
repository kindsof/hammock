ifndef TOXENV
 TOXENV := py27
endif
ENV := TOXENV=$(TOXENV)

all: tox packages rename

.PHONY: tox
tox:
	$(ENV) tox

clean:
	find -name *.pyc -delete
	rm -rf dist *.egg-info htmlcov

flake8:
	$(ENV) tox -e flake8

pylint:
	$(ENV) tox -e pylint

unittest:
	$(ENV) tox -e unittest

install:$ requirements setup.py hammock/*
	python setup.py install

packages: rpm rename

rpm:  setup.py hammock/*
	python setup.py bdist --formats=rpm
	python setup.py bdist_egg
	rm -rf build
	rm dist/*.src.rpm dist/*.tar.gz

rename: dist/hammock-0.0.1-1.noarch.rpm
	- rm -f $(basename $<)-*.rpm
	mv $< $(basename $<)-$(shell git rev-parse --short=7 HEAD).rpm

submit:
	solvent submitproduct rpm dist

approve:
	solvent approve --product rpm

prepareForCleanBuild:
	sudo pip install tox

copy_code_to_node:
	sshpass -p 'rackattack' scp -r -o ServerAliveInterval=5 -o ServerAliveCountMax=1 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null hammock root@$(IP):/usr/lib/python2.7/site-packages/

requirements: requirements.txt dev-requirements.txt
	pip install --upgrade pip -r requirements.txt -r dev-requirements.txt

test_gunicorn:
	gunicorn tests.app:application

test_uwsgi:
	uwsgi --http :8000 --module tests.app --honour-stdin --need-app
