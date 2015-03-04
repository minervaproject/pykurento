#!/bin/bash

gunicorn --name pykurento --worker-class tornado --workers 10 --timeout=300 --bind=127.0.0.1:${PORT-8080} examples.app
