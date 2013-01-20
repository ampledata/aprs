all: install_requirements develop todo

develop:
	python setup.py develop

install_requirements:
	pip install -r requirements.txt --use-mirrors

install:
	python setup.py install

uninstall:
	pip uninstall -y aprs

todo:
	grep \#\ TODO Makefile

clean:
	rm -rf *.egg* build dist *.py[oc] */*.py[co] cover doctest_pypi.cfg \
	 	nosetests.xml pylint.log *.egg output.xml flake8.log tests.log \
		test-result.xml htmlcov fab.log

publish:
	python setup.py register sdist upload

nosetests:
	python setup.py nosetests

pep8:
	flake8

flake8:
	flake8 --exit-zero  --max-complexity 12 aprs/*.py tests/*.py *.py | \
		awk -F\: '{printf "%s:%s: [E]%s\n", $$1, $$2, $$3}' | tee flake8.log

clonedigger:
	clonedigger --cpd-output aprs tests

lint:
	pylint -f parseable -i y -r y aprs/*.py tests/*.py *.py | \
		tee pylint.log

test: install_requirements lint clonedigger flake8 nosetests
