from setuptools import setup

setup(name='pykurento',
      version='0.0.1',
      description='A python kurento client based on websocket-client',
      url='http://github.com/minervaproject/pykurento',
      author='MinervaProject',
      author_email='dev@minervaproject.com',
      license='LGPL',
      packages=['pykurento'],
      install_requires=[
        'websocket-client>=0.21.0'
      ],
      zip_safe=False)
