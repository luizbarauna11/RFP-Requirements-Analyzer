.PHONY: install lint type test check run analyze analyze-offline docker

install:
	pip install -e ".[dev,pdf,docx]"

lint:
	ruff check src tests

type:
	mypy src

test:
	pytest -q

check: lint type test

run:
	uvicorn rfp_analyzer.api.main:app --reload --port 8080

analyze:
	rfp-analyzer analyze tests/fixtures/rfp_ficticia_field_services.txt --out output/

analyze-offline:
	rfp-analyzer analyze tests/fixtures/rfp_ficticia_field_services.txt --out output/ --offline

docker:
	docker build -t rfp-analyzer:local .
