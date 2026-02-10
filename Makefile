install:
	python3 -m pip install -r requirements.txt

install-dev:
	python3 -m pip install -r requirements-dev.txt

lint:
	python3 -m flake8 .
	python3 -m djlint . --check

format:
	python3 -m black .
	python3 -m isort .
	python3 -m djlint . --reformat
