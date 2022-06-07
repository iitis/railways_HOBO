init:
	pip3 install -r requirements.txt
test:
	coverage run -m unittest tests/*
	coverage html

.PHONY: init test
