#!/usr/bin/env python

from setuptools import setup


setup(name='flakypy',
      version='1.0.0',
      description='',
      long_description=open("README.rst", "r").read(),
      author='Mike Steder',
      author_email='steder@gmail.com',
      url='http://github.com/steder/flakypy',
      modules=['flakypy.py',
                ],
      scripts=['bin/flakypy'],
     #test_suite="",
      install_requires=["pyflakes",
                        ],
      license="MIT",
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          ]
)
