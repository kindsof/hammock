all: pep8 pylint unittest

clean:
	find -name *.pyc -delete

pylint:
	../strato-pylint/pylint.sh ./

pep8:
	pep8 --max-line-length=145 ./

unittest:
	python -m unittest discover hammock -p "test_*.py" 
