## Process this file with automake to produce Makefile.in

SUBDIRS = m4  po macros src doc 

install-data-local:
	@$(NORMAL_INSTALL)
	if test -d $(srcdir)/pixmaps; then \
	  $(mkinstalldirs) $(DESTDIR)@PACKAGE_PIXMAPS_DIR@; \
	  for pixmap in $(srcdir)/pixmaps/*; do \
	    if test -f $$pixmap; then \
	      $(INSTALL_DATA) $$pixmap $(DESTDIR)@PACKAGE_PIXMAPS_DIR@; \
	    fi \
	  done \
	fi
	if test -d $(srcdir)/maps; then \
	  $(mkinstalldirs) $(DESTDIR)@PACKAGE_MAPS_DIR@; \
	  for map in $(srcdir)/maps/*; do \
	    if test -f $$map; then \
	      $(INSTALL_DATA) $$map $(DESTDIR)@PACKAGE_MAPS_DIR@; \
	    fi \
	  done \
	fi

dist-hook:
	if test -d pixmaps; then \
	  mkdir $(distdir)/pixmaps; \
	  for pixmap in pixmaps/*; do \
	    if test -f $$pixmap; then \
	      cp -p $$pixmap $(distdir)/pixmaps; \
	    fi \
	  done \
	fi
	if test -d maps; then \
	  mkdir $(distdir)/maps; \
	  for map in maps/*; do \
	    if test -f $$map; then \
	      cp -p $$map $(distdir)/maps; \
	    fi \
	  done \
	fi

EXTRA_DIST = config.rpath  \
	gnofract4d.desktop 

Graphicsdir= $(datadir)/gnome/apps/Graphics
Graphics_DATA=gnofract4d.desktop


ACLOCAL_AMFLAGS = -I m4
