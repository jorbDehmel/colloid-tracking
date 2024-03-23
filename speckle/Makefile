# Run style and typing tests on the `speckle` package.
# Jordan Dehmel, 2024
# jedehmel@mavs.coloradomesa.edu
# jdehmel@outlook.com
# github.com/jorbDehmel/physicsScripts

.PHONY:	test
all:	type-check style-check test

.PHONY:	type-check
type-check:
	mypy --strict --allow-untyped-decorators --ignore-missing-imports .

.PHONY:	style-check
style-check:
	flake8 --exclude '__init__.py' .

.PHONY:	test
test:
	pytest --cov .
