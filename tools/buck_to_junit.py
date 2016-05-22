#!/usr/bin/env python
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

import xml.etree.ElementTree as ET
from optparse import OptionParser
from os import path, chdir
from os.path import abspath, expanduser
from shutil import rmtree
from subprocess import check_call, CalledProcessError
from tempfile import mkdtemp

opts = OptionParser()
opts.add_option('-t', help='test report to convert')
opts.add_option('-o', help='output directory')
args, _ = opts.parse_args()

GROUP_ID = 'net.sf.saxon'
ARTIFACT = 'Saxon-HE'
VERSION = '9.6.0-6'
PACKAGING = 'jar'
jar = '/'.join([GROUP_ID.replace('.', '/'), ARTIFACT, VERSION, ARTIFACT + '-' +
                VERSION + '.' + PACKAGING])

def get_local_repo():
  m2_path = path.join(expanduser("~"), '.m2')
  default_local_repo = path.join(m2_path, 'repository')
  if path.exists(default_local_repo):
    return default_local_repo

  mvn_settings = path.join(m2_path, 'settings.xml')
  if path.exists(mvn_settings):
    tree = ET.parse(mvn_settings)
    return tree.getroot().find('localRepository').text

def download_and_install_to_local_repo():
  temp_dir = mkdtemp()
  temp_saxon_jar = path.join(temp_dir, 'saxon.jar')
  url = 'http://central.maven.org/maven2/' + jar
  try:
    check_call(['curl', '--proxy-anyauth', '-sfo', temp_saxon_jar, url])
  except OSError as err:
    print('could not invoke curl: %s\nis curl installed?' % err)
    exit(1)
  except CalledProcessError as err:
    print('error using curl: %s' % err)
    exit(1)

  try:
    check_call(['mvn', 'install:install-file', '-Dfile=' + temp_saxon_jar,
                '-DgroupId=' + GROUP_ID, '-DartifactId=' + ARTIFACT,
                '-Dversion=' + VERSION, '-Dpackaging=' + PACKAGING])
  except (OSError, CalledProcessError) as err:
    print('error installing jar to local maven repository: %s' % err)
    exit(1)
  finally:
    rmtree(temp_dir, ignore_errors=True)

def main():
  local_repo = get_local_repo()
  saxon_jar = path.join(local_repo, jar)
  if not path.exists(saxon_jar):
    download_and_install_to_local_repo()

  buck_report = abspath(args.t)
  buck_to_junit_xsl = abspath(
    path.join(path.abspath(path.dirname(__file__)), 'buckToJUnit.xsl'))

  chdir(args.o)
  try:
    check_call(['java', '-jar', saxon_jar, '-s:' + buck_report,
                '-xsl:' + buck_to_junit_xsl])
  except CalledProcessError as err:
    print('error converting to junit: %s' % err)
    exit(1)

if __name__ == '__main__':
  main()
