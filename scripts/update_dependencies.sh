#!/bin/sh
echo "Hi, I'm going to update the dependencies of the project"
pre-commit autoupdate
wait
uv lock
wait
git add uv.lock && git add .pre-commit-config.yaml
git commit -m "update dependencies"
