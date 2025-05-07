#!/bin/bash

ROOT_DIR=$1

cd $ROOT_DIR

black .

black --check .

pytest -rs -v --cov

