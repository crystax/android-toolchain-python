#!/usr/bin/env python
#
# Copyright (C) 2015 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Builds Python for the NDK."""
from __future__ import print_function

import argparse
import inspect
import os
import subprocess
import sys


def android_path(path=''):
    top = os.getenv('ANDROID_BUILD_TOP', '')
    return os.path.realpath(os.path.join(top, path))


def get_default_package_dir():
    return android_path('out/ndk')


def get_default_host():
    if sys.platform in ('linux', 'linux2'):
        return 'linux'
    elif sys.platform == 'darwin':
        return 'darwin'
    else:
        raise RuntimeError('Unsupported host: {}'.format(sys.platform))


class ArgParser(argparse.ArgumentParser):
    def __init__(self):
        super(ArgParser, self).__init__(
            description=inspect.getdoc(sys.modules[__name__]),
            formatter_class=argparse.RawDescriptionHelpFormatter)

        self.add_argument(
            '--host', choices=('darwin', 'linux', 'windows', 'windows64'),
            default=get_default_host(),
            help='Build binaries for given OS (e.g. linux).')
        self.add_argument(
            '--package-dir', help='Directory to place the packaged GCC.',
            default=get_default_package_dir())


def main():
    args = ArgParser().parse_args()

    if 'ANDROID_BUILD_TOP' not in os.environ:
        top = os.path.join(os.path.dirname(__file__), '../..')
        os.environ['ANDROID_BUILD_TOP'] = os.path.realpath(top)

    os.chdir(android_path('toolchain/python'))

    toolchain_path = android_path('toolchain')
    ndk_path = android_path('ndk')

    ndk_build_tools_path = android_path('ndk/build/tools')
    build_env = dict(os.environ)
    build_env['NDK_BUILDTOOLS_PATH'] = ndk_build_tools_path
    build_env['ANDROID_NDK_ROOT'] = ndk_path

    toolchain_dir_arg = '--toolchain-src-dir={}'.format(toolchain_path)
    package_dir_arg = '--package-dir={}'.format(args.package_dir)

    build_cmd = [
        'bash', 'build-python.sh', toolchain_dir_arg, package_dir_arg,
        '--verbose',
    ]

    if args.host in ('windows', 'windows64'):
        build_cmd.append('--mingw')

    if args.host != 'windows':
        build_cmd.append('--try-64')

    subprocess.check_call(build_cmd, env=build_env)

if __name__ == '__main__':
    main()
