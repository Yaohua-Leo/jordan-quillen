.PHONY: test lint claims literature-index experiments

test:
	python -m pytest

lint:
	python -m ruff check .

claims:
	python scripts/check_claims.py

literature-index:
	python scripts/make_literature_index.py

experiments:
	python scripts/run_all_experiments.py
