<?xml version='1.0'?>
<xsl:stylesheet  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"  version="1.0">


<!-- Imports the DocBook HTML chunking stylesheets. --> 
<xsl:import href="/usr/share/sgml/docbook/xsl-stylesheets-1.68.1-1/html/docbook.xsl"/>
<xsl:template match="guimenuitem">
  <span class="guimenuitem"><xsl:call-template name="inline.charseq"/></span>
</xsl:template>

</xsl:stylesheet>
