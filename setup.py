#!/usr/bin/env python

from distutils.core import setup

setup(name='ztl',
      version='0.0.5',
      description='A thin library relying on zmq to dispatch tasks',
      author='Patrick Holthaus',
      author_email='patrick.holthaus@googlemail.com',
      url='https://gitlab.com/robothouse/rh-user/ztl/',
      package_dir={'':'src'},
      packages=['ztl', 'ztl.core', 'ztl.example', 'ztl.script'],
      scripts=['src/ztl/example/simple_client.py',
            'src/ztl/example/simple_server.py',
            'src/ztl/example/task_client.py',
            'src/ztl/example/task_server.py',
            'src/ztl/script/run_script.py'
      ],
      entry_points={
            'console_scripts': [
                  'ztl_simple_client=ztl.example.simple_client:main_cli',
                  'ztl_simple_server=ztl.example.simple_server:main_cli',
                  'ztl_task_server=ztl.example.task_server:main_cli',
                  'ztl_task_client=ztl.example.task_client:main_cli',
                  'ztl_run_script=ztl.script.run_script:main_cli'
            ]
      }
)
