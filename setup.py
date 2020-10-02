#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    """Retrieves the version from getpaid_przelewy24/__init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("getpaid_przelewy24", "__init__.py")


if sys.argv[-1] == 'publish':
    try:
        import wheel
        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

setup(
    name='django-getpaid-przelewy24',
    version=version,
    description="""django-getpaid processor for Przelewy24""",
    long_description=readme + '\n\n' + history,
    author='Konrad Lyda',
    author_email='konrad.lyda@gmail.com',
    url='https://github.com/k-lyda/django-getpaid-przelewy24',
    packages=[
        'getpaid_przelewy24',
    ],
    include_package_data=True,
    install_requires=["django-getpaid>=2.0"],
    license="MIT",
    zip_safe=False,
    keywords='django-getpaid-przelewy24',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
