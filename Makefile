init:
	pip3 install -r requirements.txt
test:
	coverage run -m unittest test/*
	coverage html

.PHONY: init test
