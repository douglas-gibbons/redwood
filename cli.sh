#!/bin/bash -e

BASEDIR=$(dirname $0)
uv --directory $BASEDIR run cli.py
