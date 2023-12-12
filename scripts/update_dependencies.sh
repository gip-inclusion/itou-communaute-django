#!/bin/sh
echo "Hi, I'm going to update the dependencies of the project"
pre-commit autoupdate
wait
poetry lock
wait
poetry export -f requirements.txt --output ./requirements/base.txt
wait
poetry export -f requirements.txt --output ./requirements/dev.txt --with dev
wait
git add requirements/dev.txt && git add requirements/base.txt && git add poetry.lock && git add .pre-commit-config.yaml
git commit -m "update dependencies"
