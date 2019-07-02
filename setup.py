#!/usr/bin/env python

from setuptools import setup

setup(
    name='ctt',
    install_requires=['flask_sqlalchemy', 'flask-cors', 'gunicorn'],
    scripts=['createuser.py'],
    packages=['ctt'],
)
