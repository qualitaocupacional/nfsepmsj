import os
import re
from setuptools import find_packages, setup

from codecs import open

here = os.path.abspath(os.path.dirname(__file__))

install_requires = [
    'requests>=2.7.0',
    'lxml>=4.2.1',
    'zeep>=2.5.0',
    'signxml>=2.5.2',
    'pyOpenSSL>=17.5.0',
    'six>=1.11.0',
]


def read_file(*parts):
    with open(os.path.join(here, *parts), 'r', encoding='utf-8') as fp:
        return fp.read()

def find_version(*paths):
    version_file = read_file(*paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


setup(
    name='nfsepmsj',
    version=find_version('nfsepmsj', '__init__.py'),
    description='Biblioteca para acesso ao Webservices de NFSe da Prefeitura Municipal de Sao Jose - SC',
    long_description=read_file('README.rst'),
    url='https://github.com/qualitaocupacional/nfsepmsj',
    author='Qualita Seguranca e Saude Ocupacional',
    author_email='lab.ti@qualitaocupacional.com.br',
    license='Apache 2.0',
    packages=find_packages(exclude=['contrib', 'docs']),
    include_package_data=True,
    install_requires=install_requires,
    zip_safe=False,
    test_suite='nose.collector',
    tests_require=['nose'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)

# Run tests:
# python setup.py test
