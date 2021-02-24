#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup


def get_long_description():
    with open('README.md', encoding='utf8') as f:
        return f.read()


def get_packages(package):
    return [
        dirpath
        for dirpath, dirnames, filenames in os.walk(package)
        if os.path.exists(os.path.join(dirpath, '__init__.py'))
    ]


setup(
    name='star_resty',
    python_requires='>=3.7',
    install_requires=[
        'ujson',
        'typing_extensions',
        'marshmallow>=3.0.0rc8,<4',
        'starlette<1',
        'apispec<4',
    ],
    version='0.0.14',
    url='https://github.com/slv0/start_resty',
    license='BSD',
    description='The web framework',
    long_description=get_long_description(),
    long_description_content_type='text/markdown',
    author='Slava Cheremushkin',
    author_email='slv0.chr@gmail.com',
    packages=get_packages('star_resty'),
    package_data={'star_resty': ['py.typed']},
    data_files=[('', ['LICENSE'])],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 3.7',
    ],
    zip_safe=False,
)
