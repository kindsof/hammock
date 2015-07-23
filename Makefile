all: pep8 pylint unittest

clean:
	find -name *.pyc -delete

pylint:
	pylint -r n --rcfile=.pylintrc hammock tests

pep8:
	pep8 --max-line-length=145 hammock tests

unittest:
	python -m unittest discover tests -p "test_*.py"

install: requirement.txt setup.py hammock/*
	pip install -r requirement.txt
	python setup.py install
