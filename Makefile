#
# Assuming: you have python poetry installed
# sudo apt install python3-poetry
#
# if poetry install takes too long
# export PYTHON_KEYRING_BACKEND=keyring.backends.fail.Keyring
#
# yt-dlp needs to be callable from path https://github.com/yt-dlp/yt-dlp/wiki/Installation
#
.PHONY: install installsysdeps
.PHONY: run
.PHONY: reformat
.PHONY: backfiles test test-min test-real

CP = cp
PROJECT_NAME = crawler-buddy
PORT=3000

# Assumptions:
#  - python poetry is in your path

install:
	poetry install
	#poetry run python -m spacy download en_core_web_sm
	poetry run playwright install

installsysdeps:
	apt -y install wget id3v2 chromium-chromedriver xvfb

server:
	rm -rf storage
	poetry run python script_server.py -k -m

# Assumptions:
#  - python black is in your path
# Black should use gitignore files to ignore refactoring
reformat:
	poetry run black src
	poetry run black utils
	poetry run black *.py

backfiles:
	find . -type f -name "*.bak" -exec rm -f {} +

test: test-min test-real

test-unit:
	poetry run python -u -m unittest discover -s tests/unit -v 2>&1 | tee test_output.txt

test-real:
	poetry run python -u -m unittest discover -s tests/real -v 2>&1 | tee test_output.txt
