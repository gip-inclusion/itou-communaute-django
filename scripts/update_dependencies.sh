#!/bin/sh
echo "Hi, I'm going to update the dependencies and extract last PRS for the changelog"
python ./scripts/changelog.py
wait
poetry lock
wait
poetry run poe export && poetry run poe export_dev
wait
git add requirements/dev.txt && git add requirements/base.txt && git add poetry.lock
git commit -m "update dependencies"
