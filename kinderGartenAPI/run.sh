#!/bin/bash

cd "$(dirname "$0")"

# Get the server address from .env or use default
DEV_SERVER_ADDRESS=$(grep ^DEV_SERVER_ADDRESS .env | cut -d '=' -f2)
if [ -z "$DEV_SERVER_ADDRESS" ]; then
    DEV_SERVER_ADDRESS="192.168.0.37:8000"
fi

# Run Django server with that address
/Users/mac/Documents/kinderGarten-BE/venv/bin/python manage.py runserver $DEV_SERVER_ADDRESS
