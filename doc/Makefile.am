HTML_FILES=index.html \
	maths.html \
	types.html \
	mouse.html \
	toolbar.html \
	filemenu.html \
	preferences.html \
	about.html

XML_FILES = gnofract4d.xml
CSS = gnofract4d-doc.css
XSL_FILES = gnofract4d.xsl

GIFS = julia_perturbed.png julia_standard.png \
	mandelbrot_perturbed.png mandelbrot_standard.png \
	xw_plane.png hybrid.png

STYLESHEET_GIFS=gnofract4d/stylesheet-images/caution.gif

gnofract4d_helpdir = $(datadir)/gnome/help/gnofract4d/C

gnofract4d_help_DATA = $(XML_FILES) $(GIFS)

EXTRA_DIST = \
	$(XML_FILES) \
	$(XSL_FILES) \
	$(HTML_FILES) \
	$(CSS) \
	$(GIFS) \
	$(STYLESHEET_GIFS)

all:

$(HTML_FILES): $(XML_FILES) $(XSL_FILES) $(CSS)
	-xsltproc --param use.id.as.filename 1 \
	--stringparam html.stylesheet $(CSS) \
	$(XSL_FILES) $(XML_FILES)



