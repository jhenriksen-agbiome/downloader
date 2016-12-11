import os
import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand

short_description = "NCBI sequence download microservice"
long_description = short_description

install_requires = [
    'aiodns',
    'aiofiles',
    'aiohttp',
    'aiohttp-route-decorator',
    'cchardet',
    'envparse',
]


tests_require = [
    'pytest',
    'coverage',
    'pytest-cov',
    'pytest-asyncio',
    'pytest-aiohttp',
]


def read_version():
    for line in open(os.path.join('downloader', 'version.py'), 'r'):
        if line.startswith('__version__'):
            return line.split('=')[-1].strip().strip("'")


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name='antismash-downloader',
    version=read_version(),
    author='Kai Blin',
    author_email='kblin@biosustain.dtu.dk',
    description=short_description,
    long_description=long_description,
    install_requires=install_requires,
    tests_require=tests_require,
    cmdclass={'test': PyTest},
    packages=['downloader'],
    url='https://github.com/antismash/downloader/',
    license='Apache Software License',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    extras_require={
        'testing': tests_require,
    },
)
