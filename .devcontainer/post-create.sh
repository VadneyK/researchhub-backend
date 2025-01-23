#!/usr/bin/env bash
set -e

# Install dependencies using Poetry only
cd src
poetry install
poetry shell

# Install Brownie dependencies
brownie pm install OpenZeppelin/openzeppelin-contracts@4.9.0

# Apply database migrations
python manage.py makemigrations
python manage.py migrate
# Copy static content
python manage.py collectstatic --no-input
cd -

echo "Post create script complete."
