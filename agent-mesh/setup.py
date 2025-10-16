# Copyright (c) 2020-2021 Vishal Anand
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

import setuptools
import os

VERSION = os.environ.get('VERSION') or '1.0.1'


def get_long_desc():
    with open("README.md", "r") as fh:
        long_description = fh.read()
    return long_description


setuptools.setup(
    name="agent_mesh",
    version=VERSION,
    author="AKASH S E",
    author_email="akash181gowda@gmail.com",
    description="",
    long_description=get_long_desc(),
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    install_requires=[
        'networkx>=3.0',
        'graphene>=3.0',
        'psycopg2-binary>=2.9.0'
    ],
    license='',
    python_requires='>=3.6',
    include_package_data=True,
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        "Operating System :: OS Independent",
    ],
)
