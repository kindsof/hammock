all: pep8 pylint unittest packages rename

clean:
	find -name *.pyc -delete
	rm -rf dist hammock.egg-info

pylint:
	pylint -r n --rcfile=.pylintrc hammock tests

pep8:
	pep8 --max-line-length=145 hammock tests

unittest:
	python -m unittest discover tests -p "test_*.py"

install: requirement.txt setup.py hammock/*
	pip install -r requirement.txt
	python setup.py install

packages: rpm rename

rpm: clean setup.py hammock/*
	python setup.py bdist --formats=rpm
	python setup.py bdist_egg
	rm -rf build
	rm dist/*.src.rpm dist/*.tar.gz

rename:
	mv $(wildcard  dist/*.rpm) $(basename $(wildcard dist/*.rpm))-$(shell git rev-parse --short=7 HEAD).rpm

submit:
	solvent submitproduct rpm dist

approve:
	solvent approve --product rpm

prepareForCleanBuild:
	pip install -r requirement.txt
	pip install uwsgi

copy_code_to_node:
	sshpass -p 'rackattack' scp -r -o ServerAliveInterval=5 -o ServerAliveCountMax=1 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null hammock root@$(IP):/usr/lib/python2.7/site-packages/
