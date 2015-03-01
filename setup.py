from setuptools import setup

setup(name='pykurento',
      version='0.0.1',
      description='A python kurento client based on websocket-client',
      url='https://github.com/minervaproject/pykurento',
      download_url='https://github.com/minervaproject/pykurento/tarball/0.0.1',
      author='Gene Hallman, MinervaProject',
      author_email='gene@minervaproject.com',
      license='LGPL',
      packages=['pykurento'],
      install_requires=[
        'websocket-client>=0.21.0'
      ],
      zip_safe=False)
