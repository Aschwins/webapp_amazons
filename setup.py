import os

from setuptools import setup, find_packages

deploy_packages = [
    "flask"
]

setup(
    name='package-name',
    version="1.0.0",
    packages=find_packages(where='src'),
    package_dir={"": "src"},
    install_requires=deploy_packages,
    description='Amazons Flask App',
    entry_points={"console_scripts": ["amazons = amazons.cli:main"]},
    author='Aschwin Schilperoort',
    long_description_content_type='text/markdown',
)