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

from __future__ import print_function
from hashlib import sha1
from os import path, makedirs
from shutil import rmtree
from tempfile import mkdtemp
from subprocess import call, check_call, CalledProcessError
from zipfile import ZipFile

TOOLS = path.abspath(path.dirname(__file__))
ROOT = path.abspath(__file__)
for _ in range(0, 3):
  ROOT = path.dirname(ROOT)

PLUGIN_NAME = path.basename(path.normpath(ROOT))
tempDir = mkdtemp()
try:
  try:
    check_call(['buck', 'build', '//:' + PLUGIN_NAME])
  except CalledProcessError as err:
    exit(1)

  classes = path.join(tempDir, 'classes')
  with ZipFile(path.join(ROOT, 'buck-out/gen/' + PLUGIN_NAME + '.jar'), "r") as z:
    z.extractall(classes)

  testReport = path.join(tempDir, 'testReport.xml')
  call(['buck', 'test', '--code-coverage', '--xml', testReport])

  junitTestReportDir = path.join(tempDir, 'junitTestReport')
  makedirs(junitTestReportDir)
  try:
    check_call([path.join(TOOLS, 'buckToJUnit.py'), '-t', testReport, '-o', junitTestReportDir])
  except CalledProcessError as err:
    exit(1)

  sonarProjectProperties =  path.join(tempDir, 'sonar-project.properties')
  with open(sonarProjectProperties, 'w') as fd:
    print("""\
sonar.projectKey=%s
sonar.projectName=testSonarWithBuck
sonar.projectVersion=1.0

sonar.language=java
sonar.sources=src/main/java
sonar.tests=src/test/java
sonar.sourceEncoding=UTF-8
sonar.java.binaries=%s

sonar.junit.reportsPath=%s
sonar.core.codeCoveragePlugin=jacoco
sonar.jacoco.reportPath=%s\
""" % (str(hash(PLUGIN_NAME)) + "_" + PLUGIN_NAME,
       classes,
       junitTestReportDir,
       ROOT + '/buck-out/gen/jacoco/jacoco.exec'), file=fd)

  try:
    check_call(['sonar-runner', '-Dproject.settings=' + sonarProjectProperties,])
  except CalledProcessError as err:
    exit(1)
finally:
  #rmtree(path.join(ROOT, '.sonar'))
  rmtree(tempDir)
