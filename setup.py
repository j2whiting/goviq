from setuptools import setup, find_packages

# Project metadata
NAME = "goviq"
VERSION = '0.1.0'
DESCRIPTION = 'Your package description'
AUTHOR = 'Your Name'
EMAIL = 'your.email@example.com'
URL = 'https://github.com/your_username/your_package'
LICENSE = 'MIT'

# Read the long description from README file
with open('README.md', 'r', encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

# List of required packages
REQUIRES = [
    'aiohttp==3.8.5',
    'beautifulsoup4==4.12.2',
    'regex',
    'requests==2.31.0',
    'tqdm',
]

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,
    license=LICENSE,
    packages=find_packages(exclude=['tests', 'docs']),
    install_requires=REQUIRES,
    python_requires='>=3.6',
)