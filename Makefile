all: pep8 pylint unittest packages

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

packages: setup.py hammock/*
	python setup.py bdist --formats=rpm
	rm -rf build
	rm dist/*.src.rpm dist/*.tar.gz

submit:
	sudo -E solvent submitproduct rpm dist

approve:
	sudo -E solvent approve --product rpm
