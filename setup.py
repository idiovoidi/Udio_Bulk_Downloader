"""Setup configuration for Udio Library Downloader."""

from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='udio-downloader',
    version='0.1.0',
    description='Download and backup your Udio music library',
    author='Udio Downloader Contributors',
    packages=find_packages(),
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'udio-downloader=udio_downloader.cli:cli',
        ],
    },
    python_requires='>=3.10',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
)
