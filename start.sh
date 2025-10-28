#!/bin/bash
source venv/bin/activate
export FLASK_APP=app:create_app
flask run --debug
