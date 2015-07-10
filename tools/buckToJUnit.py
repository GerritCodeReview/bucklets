#!/usr/bin/python
# Copyright (C) 2015 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from optparse import OptionParser
from os import path, chdir
from os.path import abspath
from shutil import rmtree
from subprocess import check_call, CalledProcessError
from tempfile import mkdtemp

TOOLS = path.abspath(path.dirname(__file__))

opts = OptionParser()
opts.add_option('-t', help='test results to convert')
opts.add_option('-o', help='output directory')
args, _ = opts.parse_args()
tempDir = mkdtemp()
try:
  try:
    check_call(['curl', '--proxy-anyauth', '-sfo', path.join(tempDir, 'saxon.jar'),
                'http://central.maven.org/maven2/net/sf/saxon/Saxon-HE/9.6.0-6/Saxon-HE-9.6.0-6.jar'])
  except OSError as err:
    print('could not invoke curl: %s\nis curl installed?' % err)
    exit(1)
  except CalledProcessError as err:
    print('error using curl: %s' % err)
    exit(1)

  buckReport = abspath(args.t)
  buckToJUnitXsl = abspath(path.join(TOOLS, 'buckToJUnit.xsl'))

  chdir(args.o)
  try:
    check_call(['java', '-jar', path.join(tempDir, 'saxon.jar'), '-s:' + buckReport, '-xsl:' + buckToJUnitXsl])
  except CalledProcessError as err:
    exit(1)
finally:
  rmtree(tempDir)
