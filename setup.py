import os
import re
import sys

from setuptools.command.test import test
from setuptools import setup, find_packages

BASE_PATH = os.path.dirname(__file__)
VERSION_FILE = os.path.join('psclient', 'version.py')


def read(file):
    """

    :param file:
    :return:
    """
    with open(os.path.join(BASE_PATH, file)) as f:
        return f.read()


def grep(file, name):
    """

    :param file:
    :param name:
    :return:
    """
    pattern = r"{attr}\W*=\W*'([^']+)'".format(attr=name)
    value, = re.findall(pattern, read(file))
    return value


def readme(file):
    """

    :param file:
    :return:
    """
    try:
        return read(file)
    except OSError as exc:
        print(str(exc), file=sys.stderr)


class PyTest(test):
    def finalize_options(self):
        """

        """
        test.finalize_options(self)

    def run_tests(self):
        """

        """
        # noinspection PyUnresolvedReferences
        import pytest
        sys.exit(pytest.main(['tests']))


setup(
    name='pscli',
    url=grep(VERSION_FILE, '__url__'),
    license=grep(VERSION_FILE, '__license__'),
    version=grep(VERSION_FILE, '__version__'),
    author=grep(VERSION_FILE, '__author_name__'),
    author_email=grep(VERSION_FILE, '__author_email__'),
    description='Unofficial Cisco Parstream Client with improved cli',
    long_description=readme('README.rst'),
    platforms='any',
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'psclient = psclient.cli:cli',
        ],
    },
    install_requires=[
        'tabulate >= 0.8',
        'pygments >= 2.6',
        'prompt_toolkit >= 3.0',
    ],
    tests_require=[
        'pytest',
        'pytest-cov'
    ],
    cmdclass={'test': PyTest},
    test_suite='tests',
    classifiers=[]
)
