import os, re
from setuptools import setup, find_packages


version = '0.0.1'

excludes_dependencies = [
    'nose',
    'rednose',
    'ipython'
]


# monkey patch os for vagrant hardlinks
del os.link

# drop caches
os.system("find . -type f -name '*.pyc' -delete")

# prepare requires
requires = []
with open('requirements.txt') as file:
    p = r'^({}).*'.format('|'.join(excludes_dependencies))
    for lib in file.read().splitlines():
        if not re.search(p, lib):
            requires.append(lib)

# prepare config
config = dict(

    # author
    author = 'Dmitry Belyakov',
    author_email='dmitrybelyakov@gmail.com',

    # project meta
    name = 'shiftmemory',
    version=version,
    url = 'https://github.com/projectshift/shift-memory',
    download_url='https://github.com/projectshift/shift-memory/tarball/'+version,
    description='Python3 cache library',
    keywords=['python3', 'cache', 'redis', 'memcached'],

    # license
    license = 'MIT',

    # packages
    packages = find_packages(exclude=['tests']),

    # dependencies
    install_requires = requires

)

# finally run the setup
setup(**config)