#!/bin/bash
source venv/bin/activate
export FLASK_APP=app
export FLASK_DEBUG=1
flask run --app=create_app
