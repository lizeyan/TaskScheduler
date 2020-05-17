import codecs
import os.path
import pathlib

import pkg_resources
from setuptools import setup, find_packages


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith('__version__'):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]
    else:
        raise RuntimeError("Unable to find version string.")


def parse_requirements(path):
    with pathlib.Path(path).open() as requirements_txt:
        install_requires = [
            str(requirement)
            for requirement
            in pkg_resources.parse_requirements(requirements_txt)
        ]
    return install_requires


def read_readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='PyTaskScheduler',
    version=get_version('ts/__init__.py'),
    description="This package focus on build a task scheduler via Python. \
With TaskScheduler you can define a project with tasks which have some dependency on each other, and run this project.",
    author='Zeyan Li',
    author_email='li_zeyan@icloud.com',
    url='https://github.com/lizeyan/TaskScheduler',
    packages=find_packages(),
    project_urls={
        "Bug Tracker": "https://github.com/lizeyan/TaskScheduler/issues",
        "Source Code": "https://github.com/lizeyan/TaskScheduler",
        "Documentation": "https://ts.lizeyan.me",
    },
    install_requires=parse_requirements('requirements.txt'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    license='MIT',
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    python_requires='>=3.6',
    scripts=[
        'bin/ts'
    ]
)
