#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="XROR",
    version="0.0.1",
    description="Extended Reality Open Replay (XROR)",
    author="Vivek Nair",
    author_email="vivek@nair.me",
    url="https://github.com/metaguard/xror",
    install_requires=["fpzip", "pymongo"],
    packages=find_packages(),
)