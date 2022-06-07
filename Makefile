init:
	pip3 install -r requirements.txt
test:
	coverage run -m pytest
	coverage html

.PHONY: init test
