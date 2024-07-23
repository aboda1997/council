# This script replaces the values in .env with those in the environment directory depending on the argument given
# For example: To run with 'stage' environment variables, call 'setenv.py stage'
import os
import sys
from pathlib import Path

if not (len(sys.argv) > 1):
    raise Exception("Missing Environment Type Argument")

BASE_DIR = Path(__file__).resolve().parent.parent.parent
BACKEND_ENV = os.path.join(BASE_DIR, 'backend', '.env')
SELECTED_ENV = os.path.join(BASE_DIR, 'environments', sys.argv[1], '.env.backend')

with open(SELECTED_ENV, 'r') as SELECTED_ENV, open(BACKEND_ENV, 'w') as BACKEND_ENV:
    for line in SELECTED_ENV:
        BACKEND_ENV.write(line)

print('Backend environment has been set to', sys.argv[1])
