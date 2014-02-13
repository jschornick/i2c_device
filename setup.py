import os
from setuptools import setup, find_packages

# Setup flags and parameters
pkg_name = 'i2c_device'  # top-level package name

# Cache readme contents for use as long_description
readme = open('readme.md').read()

# Call setup()
setup(
  name=pkg_name,
  version='0.1',
  description='I2C device configuration library for Python',
  long_description=readme,
  url='https://github.com/jschornick/i2c_device',
  author='Jeff Schornick',
  author_email='jeff@schornick.org',
  license='MIT',
  packages=find_packages(),
  include_package_data=True,
  package_data={
    pkg_name: [
      '*.yaml'
    ]
  },
  zip_safe=True,
  install_requires=[
    'smbus',
    'PyYAML'
  ],
  test_suite=(pkg_name + '.tests'),
  platforms='any',
  keywords='i2c device abstraction development utilities tools',
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Education',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2.7',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Utilities'
  ])
