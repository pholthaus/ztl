#!/usr/bin/env python

from distutils.core import setup

setup(name='ztl',
      version='0.1',
      description='A thin library relying on zmq to dispatch tasks',
      author='Patrick Holthaus',
      author_email='patrick.holthaus@googlemail.com',
      url='https://gitlab.com/robothouse/rh-user/ztl/',
      package_dir={'':'src'},
      packages=['ztl', 'ztl.core', 'ztl.example', 'ztl.script'],
     )
