gnofract4d_helpdir = $(datadir)/gnome/help/gnofract4d/C

gnofract4d_help_DATA = \
	gnofract4d.html \
	topic.dat 

SGML_FILES = gnofract4d.sgml

EXTRA_DIST = \
	$(SGML_FILES) \
	topic.dat 

all:

gnofract4d.html : gnofract4d/gnofract4d.html
	-cp gnofract4d/*.html .

gnofract4d/gnofract4d.html: $(SGML_FILES)
	-db2html gnofract4d.sgml

dist-hook:
	mkdir $(distdir)/gnofract4d
	-cp gnofract4d/*.html gnofract4d/*.css $(distdir)/gnofract4d
	-cp gnofract4d.html $(distdir)

install-data-local: gnofract4d.html
	$(mkinstalldirs) $(gnofract4d_helpdir)/images
	-for file in $(srcdir)/gnofract4d/*.html $(srcdir)/gnofract4d/*.css $(srcdir)/*.gif ; do \
		basefile=`basename $$file`; \
		echo $$basefile; \
		$(INSTALL_DATA) $(srcdir)/$$file $(gnofract4d_helpdir)/$$basefile; \
	done

gnofract4d.ps: gnofract4d.sgml
	-db2ps $<

gnofract4d.rtf: gnofract4d.sgml
	-db2rtf $<

