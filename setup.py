#!/usr/bin/env python

from os import path

from setuptools import find_packages, setup

from wagtail_streamfield_migration_toolkit import __version__


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="wagtail-streamfield-migration-toolkit",
    version=__version__,
    description="A set of reusable utilities to allow Wagtail implementors to easily generate data migrations for changes to StreamField block structure.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Sandil Ranasinghe",
    author_email="sandilsranasinghe@gmail.com",
    url="",
    packages=find_packages(),
    include_package_data=True,
    license="BSD",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Wagtail",
        "Framework :: Wagtail :: 3",
        "Framework :: Wagtail :: 4",
    ],
    install_requires=[
        "Django>=3.2,<4.1",
        "Wagtail>=4.0rc1",
    ],
    extras_require={
        "testing": [
            "dj-database-url==0.5.0",
            "freezegun>=0.3.8",
            "wagtail-factories==3.1.0",
        ],
    },
    zip_safe=False,
)
