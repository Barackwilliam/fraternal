#!/usr/bin/env bash
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input

# Compile translations (.po -> .mo). Non-fatal: the repo already ships
# compiled .mo files, so a failure here must not break the deploy.
python manage.py compile_po || echo "WARNING: compile_po skipped — using committed .mo files"

python manage.py migrate
