gnofract4d_helpdir = $(datadir)/gnome/help/gnofract4d/C

gnofract4d_help_DATA = \
	gnofract4d.html \
	topic.dat \
	docbook.css

SGML_FILES = gnofract4d.sgml

GIFS = julia_perturbed.png julia_standard.png \
	mandelbrot_perturbed.png mandelbrot_standard.png \
	xw_plane.png hybrid.png

STYLESHEET_GIFS=gnofract4d/stylesheet-images/caution.gif

EXTRA_DIST = \
	$(SGML_FILES) \
	topic.dat \
	$(GIFS) \
	$(STYLESHEET_GIFS)

all:

gnofract4d.html : gnofract4d/gnofract4d.html
	-cp gnofract4d/*.html .

gnofract4d/gnofract4d.html: $(SGML_FILES)
	-db2html -V %use-id-as-filename% $(SGML_FILES)

dist-hook:
	mkdir -p $(distdir)/gnofract4d
	mkdir -p $(distdir)/gnofract4d/stylesheet-images
	-cp gnofract4d/*.html $(distdir)/gnofract4d
	-cp gnofract4d.html $(distdir)
	-cp gnofract4d/stylesheet-images/*.gif $(distdir)/gnofract4d/stylesheet-images

install-data-local: gnofract4d.html
	$(mkinstalldirs) $(DESTDIR)$(gnofract4d_helpdir)/images
	$(mkinstalldirs) $(DESTDIR)$(gnofract4d_helpdir)/stylesheet-images
	-for file in $(srcdir)/gnofract4d/*.html $(srcdir)/*.png ; do \
		basefile=`basename $$file`; \
		echo $$basefile; \
		$(INSTALL_DATA) $(srcdir)/$$file $(DESTDIR)$(gnofract4d_helpdir)/$$basefile; \
	done
	-for file in $(srcdir)/gnofract4d/stylesheet-images/*.gif ; do \
		basefile=`basename $$file`; \
		echo $$basefile; \
		$(INSTALL_DATA) $(srcdir)/$$file $(DESTDIR)$(gnofract4d_helpdir)/stylesheet-images/$$basefile; \
	done

gnofract4d.ps: gnofract4d.sgml
	-db2ps $<

gnofract4d.rtf: gnofract4d.sgml
	-db2rtf $<

