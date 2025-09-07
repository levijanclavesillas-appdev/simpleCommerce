#!/bin/bash
cd /root/simpStore/e-commerce

# Reset local changes and pull latest
git reset --hard HEAD
git pull

# Activate virtual environment
source /root/simpStore/e-commerce/venv/bin/activate

# Start Django dev server
exec python3 manage.py runserver 0.0.0.0:8000
