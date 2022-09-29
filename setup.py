#!/usr/bin/env python

from setuptools import find_packages, setup

from wagtail_streamfield_migration_toolkit import __version__


long_description = """
This package aims to make it easier for developers using StreamField who need to write data
migrations when making changes involving blocks/block structure in the StreamField. We expose a
custom migration operation class (`MigrateStreamData`) for migrations, which recurses through
a streamfield to apply chosen sub-operations to all blocks matching a specific type. With it we also 
supply a set of sub-operations to perform the most common changes, while also allowing you to
write your own when needed.

For more details, see https://github.com/sandilsranasinghe/wagtail-streamfield-migration-toolkit
"""

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
        "Development Status :: 2 - Pre-Alpha",
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
        "Wagtail>=3.0,<4.1",
    ],
    extras_require={
        "testing": [
            "freezegun>=0.3.8",
            "wagtail-factories==3.1.0",
        ],
        "docs": ["pydoc-markdown==4.6.3"],
    },
    zip_safe=False,
)
