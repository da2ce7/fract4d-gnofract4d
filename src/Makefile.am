## Process this file with automake to produce Makefile.in

INCLUDES = \
	-I$(top_srcdir)/intl \
	-I$(top_srcdir)/libfract4d \
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
	model.cpp model.h \
	gf4d_angle.cpp gf4d_angle.h \
	gf4d_fractal.cpp gf4d_fractal.h \
	gf4d_fourway.cpp gf4d_fourway.h \
	gf4d_movie.cpp gf4d_movie.h \
	gf4d_utils.cpp gf4d_utils.h \
	preview.cpp preview.h \
	gundo.cpp gundo.h \
	gundo_ui.cpp gundo_ui.h \
	cmapbrowser.h cmapbrowser.cpp \
	movie_editor.h movie_editor.cpp \
	tls.h tls.cpp \
	preferences.h preferences.cpp


gnofract4d_LDADD = ../libfract4d/libfract4d.la $(GNOME_LIBDIR) $(GTK_LIBS) \
	$(GNOMEUI_LIBS) $(INTLLIBS) $(PTHREAD_LIB)

CXXFLAGS = -g -O3 -ffast-math -Wall -D_REENTRANT -DCXX="\"$(CXX)\"" 
