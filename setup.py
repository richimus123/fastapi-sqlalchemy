#!/usr/bin/env python

import os

from distutils.core import setup

REL_DIR = os.path.dirname(__file__)


def parse_requirements_file() -> list:
    """Parse the requirements file."""
    req_file = os.path.join(REL_DIR, 'requirements.txt')
    with open(req_file, 'rt') as f:
        required = f.read().splitlines()
    return required


setup(
      name='fastapi-sqlalchemy',
      version='0.0.1',
      description='Generate fastapi endpoints based upon SQL Alchemy tables.',
      author='Rich Stacey',
      url='https://github.com/richimus123/fastapi-sqlalchemy',
      packages=['fastapi_sqlalchemy'],
      install_requires=parse_requirements_file()
)
