PYTHON ?= python3
NODE ?= node

.PHONY: check check-publication check-course check-assets check-python check-js serve rebuild

check: check-publication check-python check-js

check-course: check-assets check

check-publication:
	$(PYTHON) tools/check_publication.py

check-assets:
	$(PYTHON) app/tools/build.py --check

check-python:
	PYTHONDONTWRITEBYTECODE=1 $(PYTHON) -m unittest discover -s app/tests -v

check-js:
	$(NODE) --test app/tests/test_study_store.js app/tests/test_session_store.js

serve:
	$(PYTHON) app/server.py

rebuild:
	$(PYTHON) app/tools/build.py
