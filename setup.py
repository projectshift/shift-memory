import os
from setuptools import setup


version = '0.0.1'

# monkey patch os for vagrant hardlinks
del os.link

# drop caches
os.system("find . -type f -name '*.pyc' -delete")

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
    packages = ['shiftmemory', 'shiftmemory.adapter'],

    # dependencies
    install_requires = ['redis>=2.10.3']

)

# finally run the setup
setup(**config)