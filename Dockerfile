# Adapted from https://gist.github.com/soof-golan/6ebb97a792ccd87816c0bda1e6e8b8c2
# This is minimal startup of django app, which uses SQL lite, and no background task like celery

FROM python:3.11 as python-base

# https://python-poetry.org/docs#ci-recommendations
ENV POETRY_VERSION=1.5.0
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VENV=/opt/poetry-venv
# Tell Poetry where to place its cache and virtual environment
ENV POETRY_CACHE_DIR=/opt/.cache

# Create stage for Poetry installation
FROM python-base as poetry-base

# Creating a virtual environment just for poetry and install it with pip
RUN python3 -m venv $POETRY_VENV \
	&& $POETRY_VENV/bin/pip install -U pip setuptools \
	&& $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Create a new stage from the base python image
FROM python-base as example-app

# Copy Poetry to app image
COPY --from=poetry-base ${POETRY_VENV} ${POETRY_VENV}

# Add Poetry to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

WORKDIR /app

# Copy Dependencies
COPY poetry.lock pyproject.toml ./

# [OPTIONAL] Validate the project is properly configured
RUN poetry check

# Install Dependencies
RUN poetry install --no-interaction --no-cache --without dev

# spacy needs a file to be downloaded
# RUN poetry run python -m spacy download en_core_web_sm
# playwright needs a browser
RUN poetry run playwright install

# Copy Application
COPY . /app

RUN apt-get -y update && apt-get -y upgrade && apt-get install -y --no-install-recommends ffmpeg id3v2 wget xvfb gnupg ca-certificates


ENV CHROMEDRIVER_DIR=/usr/bin


# Install Chrome 114 from a mirror (e.g. mirror.cs.uchicago.edu)
# Chrome & Chromedriver should match, if possible
ENV CHROME_VERSION=114.0.5735.90

RUN wget -q https://mirror.cs.uchicago.edu/google-chrome/pool/main/g/google-chrome-stable/google-chrome-stable_${CHROME_VERSION}-1_amd64.deb && \
    apt-get install -y ./google-chrome-stable_${CHROME_VERSION}-1_amd64.deb && \
    rm google-chrome-stable_${CHROME_VERSION}-1_amd64.deb


# chromedriver https://chromedriver.storage.googleapis.com/LATEST_RELEASE
ENV CHROMEDRIVER_VERSION=114.0.5735.90

# Step 2: Download and install
RUN wget -q -O /tmp/chromedriver.zip "https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip" || (echo "Failed to download Chromedriver version $CHROMEDRIVER_VERSION" && exit 1) && \
    unzip /tmp/chromedriver.zip -d ${CHROMEDRIVER_DIR} && \
    chmod +x ${CHROMEDRIVER_DIR}/chromedriver && \
    rm /tmp/chromedriver.zip


# Put Chromedriver into the PATH
ENV PATH=$CHROMEDRIVER_DIR:$PATH


# Expose the port that Django will run on
EXPOSE 3000

RUN ["chmod", "+x", "/app/docker-entrypoint.sh"]

ENTRYPOINT ["/app/docker-entrypoint.sh"]
