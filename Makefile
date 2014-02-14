default: build

.PHONY: build test devinst install clean

build:
	python setup.py build

test:
	python setup.py test

devinst:
	python setup.py develop

install:
	python setup.py install

clean:
	rm -rf build *.egg *.egg-info
	find . -name "*.pyc" -print0 | xargs -0 rm -f

# vim: set noexpandtab:
