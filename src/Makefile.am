## Process this file with automake to produce Makefile.in

INCLUDES = \
	-I$(top_srcdir)/intl \
	$(GNOME_INCLUDEDIR)

bin_PROGRAMS = gnofract4d

gnofract4d_SOURCES = \
	main.c \
	support.c support.h \
	interface.c interface.h \
	callbacks.c callbacks.h \
	calc.cpp calc.h \
	test-fonction.cpp test-fonction.h \
	vectors.h fract.h \
	model.c model.h \
	gf4d_angle.c gf4d_angle.h \
	gf4d_fractal.c gf4d_fractal.h \
	gundo.c gundo.h \
	gundo_ui.c gundo_ui.h

gnofract4d_LDADD = $(GNOME_LIBDIR) $(GNOMEUI_LIBS) $(INTLLIBS)

