PYVERS=2.4

all:
	# nothing for now

clean: $(PYVERS:%=clean-python%)
	rm -rf dist
	rm -rf build
	rm -rf src/*.egg-info

clean-python%:
	python$* setup.py clean

.PHONY: dist
dist: clean $(PYVERS:%=build-python%-egg)
	python setup.py sdist

build-python%-egg:
	python$* setup.py bdist_egg
