#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'gevent '
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='ilabs',
    version='1.2.1',
    description="python enteprise integration framework project. Powerfull class library based on EAI patterns and a modeling and simulation tool.",
    long_description=readme + '\n\n' + history,
    author="thanos vassilakis",
    author_email='thanosv@gmail.com',
    url='https://github.com/thanos/ilabs',
    packages=[
        'ilabs',
    ],
    package_dir={'ilabs':
                 'ilabs'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    zip_safe=False,
    keywords='ilabs',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
