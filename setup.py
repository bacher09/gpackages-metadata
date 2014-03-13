#!/usr/bin/env python
from setuptools import setup, find_packages
import sys


def lt27():
    v = sys.version_info
    return (v[0], v[1]) < (2, 7)


def lt33():
    v = sys.version_info
    return (v[0], v[1]) < (3, 3)

install_packages = ['six']
tests_require = [
    'nose>=1.0',
    'coverage'
]


if lt33():
    tests_require.append('mock')


if lt27():
    install_packages.append("lxml")
    tests_require.append('unittest2')


setup(
    name='packages_metadata',
    description='Read gentoo packages metadata',
    install_requires=install_packages,
    tests_require=tests_require,
    packages=find_packages(),
    test_suite="nose.collector",
    license="GPL-2",
    author='Slava Bacherikov',
    author_email='slava@bacherikov.org.ua',
    keywords=["gentoo", "portage"],
    version="0.1a"
)
