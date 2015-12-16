all: tox build

tox:
	# tox is a tool for running tests in virtualenvs, see tox.ini for more details
	tox

flake8: generate-client-code

	flake8 phoenix tests build/phoenix-client/phoenix_client

pylint: generate-client-code

	pylint -r n --py3k phoenix tests build/phoenix-client/phoenix_client
	pylint -r n phoenix tests build/phoenix-client/phoenix_client

coverage: unittest

	# Create a coverage report and validate the given threshold
	coverage report --fail-under=100 -m

unittest:

	# Run phoenix unit-tests using coverage
	coverage erase
	coverage run --omit="*__init__*" --include="phoenix/*" -m unittest discover tests -p "test_*.py"
	coverage html

install: install-phoenix install-client

install-phoenix:

	# Install phoenix package
	pip install --upgrade ./

install-client: generate-client-code

	# Install phoenix-client package
	pip install --upgrade build/phoenix-client

test-uwsgi:

	python -m phoenix

submit:

	solvent submitproduct rpm dist

approve:

	solvent approve --product rpm

build: build-phoenix build-client

build-phoenix: setup.py phoenix/*

	# Generate the phoenix RPM then cleanup
	python setup.py bdist_rpm
	rm -rf dist/*.src.rpm dist/*.egg

build-client: build/phoenix-client/dist/phoenix-client-0.0.1.rpm

	# Copy client's distribution files to the dist directory
	cp build/phoenix-client/dist/phoenix-client-0.0.1.tar.gz dist/phoenix-client-0.0.1.tar.gz
	cp build/phoenix-client/dist/phoenix-client-0.0.1-1.noarch.rpm dist/phoenix-client-0.0.1-1.noarch.rpm

build/phoenix-client/dist/phoenix-client-0.0.1.rpm: generate-client-code

	# Generate the phoenix-client RPM using setup.py then cleanup
	(cd build/phoenix-client; python setup.py bdist_rpm)
	rm -rf build/phoenix-client/dist/*.src.rpm build/phoenix-client/dist/*.egg build/phoenix-client/build

generate-client-code: build/phoenix-client/phoenix_client/client.py

	# Create client's __init__.py and setup.py files
	touch build/phoenix-client/__init__.py
	touch build/phoenix-client/phoenix_client/__init__.py
	cp client_setup.py build/phoenix-client/setup.py

build/phoenix-client/phoenix_client/client.py:

	# Generate the client.py code and dump it into target
	mkdir -p build/phoenix-client/phoenix_client/
	python -m hammock.client MyClient phoenix.resources > $@

clean:

	# Clean all generated files
	find -name *.pyc -delete
	rm -rf build dist htmlcov *.egg-info *.egg *.rpm .tox .coverage

requirements: requirements.txt dev-requirements.txt
	pip install --upgrade pip -r dev-requirements.txt -r requirements.txt

prepareForCleanBuild:

	# One time installations needed for the build process
	sudo yum install python3 python3-devel  # the virtualenv needs to have a python executable to copy
	sudo pip install tox

