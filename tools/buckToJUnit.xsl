<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:func="ca.umontreal.ca.cenr.quinoa" xmlns:xs="http://www.w3.org/2001/XMLSchema"
  exclude-result-prefixes="func" version="2.0">
  <xsl:output method="xml" omit-xml-declaration="no" indent="yes" encoding="UTF-8"/>
  <xsl:strip-space elements="*"/>

  <xsl:template match="/tests">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="test">
    <xsl:variable name="filename" select="concat('TEST-', @name, '.xml')"/>
    <xsl:result-document href="{$filename}" method="xml">
      <xsl:variable name="testCount" select="count(testresult)"/>
      <xsl:variable name="nonEmptyStacks" select="count(testresult[stacktrace != ''])"/>
      <xsl:variable name="failures"
        select="count(testresult[contains(stacktrace, 'java.lang.AssertionError')])"/>
      <xsl:variable name="errors" select="$nonEmptyStacks - $failures"/>
      <testsuite failures="{$failures}" time="{func:toMS(@time)}" errors="{$errors}" skipped="0"
        tests="{$testCount}" name="{@name}">
        <xsl:apply-templates/>
      </testsuite>
    </xsl:result-document>
  </xsl:template>

  <xsl:template match="testresult">
    <testcase time="{func:toMS(@time)}" classname="{../@name}" name="{@name}">
      <xsl:apply-templates/>
    </testcase>
  </xsl:template>

  <xsl:template match="message"/>

  <xsl:template match="stacktrace[. != '']">
    <failure message="{../message}" type="{substring-before(., ':')}">
      <xsl:value-of select="."/>
    </failure>
  </xsl:template>

  <xsl:function name="func:toMS">
    <xsl:param name="sec" as="xs:decimal"/>
    <xsl:value-of select="$sec div 1000"/>
  </xsl:function>
</xsl:stylesheet>
