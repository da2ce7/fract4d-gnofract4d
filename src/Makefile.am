## Process this file with automake to produce Makefile.in

INCLUDES = \
	-I$(top_srcdir)/intl \
	$(GNOME_INCLUDEDIR)

bin_PROGRAMS = gnofract4d

gnofract4d_SOURCES = \
	main.cpp \
	support.cpp support.h \
	interface.cpp interface.h \
	callbacks.cpp callbacks.h \
	fract.cpp fract.h fract_public.h calc.h \
	test-fonction.cpp test-fonction.h \
	vectors.h \
	model.cpp model.h \
	gf4d_angle.cpp gf4d_angle.h \
	gf4d_fractal.cpp gf4d_fractal.h \
	gundo.cpp gundo.h \
	gundo_ui.cpp gundo_ui.h \
	image.cpp image.h \
	colorizer.cpp colorizer.h colorizer_public.h \
	iterFunc.h iterFunc.cpp \
	bailFunc.h bailFunc.cpp

gnofract4d_LDADD = $(GNOME_LIBDIR) $(GTK_LIBS) $(GNOMEUI_LIBS) $(INTLLIBS) $(PTHREAD_LIB)

