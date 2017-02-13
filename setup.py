"""An open-source NLP visualiser for the modern web.
Port of https://github.com/nineinchnick/displacy.

See:
https://github.com/explosion/displacy
https://demos.explosion.ai/displacy
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='displacy',
    version='1.0.0',
    description='NLP visualiser',
    long_description=long_description,
    url='https://github.com/nineinchnick/displacy',
    author='Jan Waś',
    author_email='janek.jan@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Visualization',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='css natural-language-processing nlp spacy svg visualization',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    # py_modules=["displacy"],
    install_requires=['spacy'],
    entry_points={
        'console_scripts': [
            'displacy=displacy:main',
        ],
    },
)
