## Process this file with automake to produce Makefile.in

INCLUDES = \
	-I$(top_srcdir)/intl \
	$(GNOME_INCLUDEDIR)

bin_PROGRAMS = gnofract4d 
# itertest

gnofract4d_SOURCES = \
	main.cpp \
	interface.cpp interface.h \
	angles.h angles.cpp \
	properties.h properties.cpp \
	menus.h menus.cpp \
	toolbars.h toolbars.cpp \
	drawingareas.h drawingareas.cpp \
	callbacks.cpp callbacks.h \
	fract.cpp fract.h fract_public.h fract_callbacks.h calc.h \
	pointFunc.cpp pointFunc.h pointFunc_public.h state.h \
	vectors.h \
	model.cpp model.h \
	gf4d_angle.cpp gf4d_angle.h \
	gf4d_fractal.cpp gf4d_fractal.h \
	gf4d_fourway.cpp gf4d_fourway.h \
	gf4d_movie.cpp gf4d_movie.h \
	gf4d_utils.cpp gf4d_utils.h \
	preview.cpp preview.h \
	gundo.cpp gundo.h \
	gundo_ui.cpp gundo_ui.h \
	image.cpp image.h \
	colorizer.cpp colorizer.h colorizer_public.h \
	colorFunc.h colorFunc.cpp \
	iterFunc.h iterFunc.cpp \
	bailFunc.h bailFunc.cpp \
	fractFunc.h fractFunc.cpp fractThreadFunc.cpp \
	cmapbrowser.h cmapbrowser.cpp \
	movie_editor.h movie_editor.cpp \
	io.h io.cpp \
	threadpool.h \
	tls.h tls.cpp \
	compiler.h compiler.cpp \
	preferences.h preferences.cpp

EXTRA_DIST=compiler_template.cpp

Codedir = $(datadir)/gnofract4d
Code_DATA= compiler_template.cpp \
	pointFunc.h \
	state.h

#itertest_SOURCES = \
#	io.h io.cpp \
#	colorizer.cpp colorizer.h colorizer_public.h \
#	colorFunc.h colorFunc.cpp \
#	iter_harness.cpp \
#	compiler_output.cpp

#itertest_LDADD = $(GNOME_LIBDIR) $(GTK_LIBS) \
#	$(GNOMEUI_LIBS) $(INTLLIBS) $(PTHREAD_LIB)

gnofract4d_LDADD = $(GNOME_LIBDIR) $(GTK_LIBS) \
	$(GNOMEUI_LIBS) $(INTLLIBS) $(PTHREAD_LIB)

CXXFLAGS = -g -O3 -ffast-math -Wall -D_REENTRANT -DCXX="\"$(CXX)\"" 
