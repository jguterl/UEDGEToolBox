"""
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / 'README.md').read_text(encoding='utf-8')

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='UEDGEToolBox',
    version='0.1.0',
    description='Toolbox for UEDGE',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/jguterl/UEDGEToolBox',
    author='J. Guterl',  # Optional

    # This should be a valid email address corresponding to the author listed
    # above.
    author_email='guterlj@fusion.gat.com',  
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Any UEDGE users',
        'Topic :: Software Development :: Analysis and Run Tools for UEDGE',
        'License :: ???',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='sample, setuptools, development',  # Optional
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.5, <4',
    install_requires=['colorama,datetime,os, sys, math, string, re,numpy,easygui,scipy,mpldatacursor'],  # Optional
    #extras_require={  # Optional
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    #},

    #package_data={  # Optional
    #    'sample': ['package_data.dat'],
    #},
    #data_files=[('my_data', ['data/data_file'])],  # Optional

    #entry_points={  # Optional
    #    'console_scripts': [
    #        'sample=sample:main',
    #    ],
    #},

    project_urls={  
        'Bug Reports': 'https://github.com/jguterl/UEDGEToolBox/issues',
        'UEDGE': 'https://github.com/LLNL/UEDGE/',
        'Source': 'https://github.com/jguterl/UEDGEToolBox/',
    },
)
