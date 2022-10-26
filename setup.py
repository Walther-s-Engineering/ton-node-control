#!/usr/bin/env python3

from distutils.core import setup
from setuptools import find_packages


author = dict(
    author='Alexander Walther | Walther\'s Engineering',
    author_email='asushofman@gmail.com',
)
project_info = dict(
    name='ton-node-control',
    version='0.0.1',
)
packages_and_modules = dict(
    packages=find_packages(
        where='ton_node_control',
        include=['ton_node_control*'],
        exclude=['*.tests']
    ),
)
classifiers = dict(
    classifiers=[
        'Development Status :: 1 - WIP',
        'Environment :: Console',
        'Environment :: Internet',
        'Programming Language :: Python',
        'Operating System :: Linux :: Ubuntu',
        'Topic :: Software Development :: Blockchain :: Finance',
    ],
)


if __name__ == '__main__':
    setup(
        **author,
        **classifiers,
        **project_info,
        **packages_and_modules,
    )
