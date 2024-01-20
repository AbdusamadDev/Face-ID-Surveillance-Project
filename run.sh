#!/bin/bash

source /home/ubuntu/project/BazaarSurveillance/venv/bin/activate
export PYTHONPATH=$PYTHONPATH:/home/ubuntu/project/BazaarSurveillance

python3 -m ai.tests
