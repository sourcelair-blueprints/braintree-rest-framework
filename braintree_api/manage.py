#!/usr/bin/env python
import os
import subprocess
import sys

# HACK: Install dependencies if not already installed
PIP_LOG = 'pip.install.log'
if not os.path.exists(PIP_LOG):
    with open(PIP_LOG, 'wb') as LOG_FILE:
        subprocess.check_call(
            ['pip', 'install', '-r', '../requirements.txt'],
            stdout=LOG_FILE,
            stderr=LOG_FILE
        )

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "braintree_api.settings")

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
