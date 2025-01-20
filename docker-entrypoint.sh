#!/bin/bash

echo "Starting web server"
poetry run python script_server.py --port ${CRAWLER_BUDDY_PORT}
