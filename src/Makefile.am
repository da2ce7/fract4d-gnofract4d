## Process this file with automake to produce Makefile.in

INCLUDES = \
	-I$(top_srcdir)/libfract4d \
        -DGNOMELOCALEDIR=\""$(prefix)/$(DATADIRNAME)/locale"\"

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
	preview.cpp preview.h \
	gundo.cpp gundo.h \
	gundo_ui.cpp gundo_ui.h \
	cmapbrowser.h cmapbrowser.cpp \
	tls.h tls.cpp \
	preferences.h preferences.cpp \
	image.cpp image.h \
	marshallers.c

DEAD_FILES = movie_editor.h movie_editor.cpp 

marshallers.h: marshallers.list
	( @GLIB_GENMARSHAL@ --prefix=gf4d_marshal marshallers.list --header > marshal.tmp && mv marshal.tmp marshallers.h ) || ( rm -f marshal.tmp && exit 1 )

marshallers.c: marshallers.list
	( @GLIB_GENMARSHAL@ --prefix=gf4d_marshal marshallers.list --body > \
	marshal.tmp && mv marshal.tmp marshallers.c ) \
	|| ( rm -f marshal.tmp && exit 1 )

$(gnofract4d_OBJECTS): marshallers.h marshallers.c

gnofract4d_LDADD = ../libfract4d/libfract4d.la $(GNOFRACT4D_CFLAGS) \
	$(GNOFRACT4D_LIBS)

CXXFLAGS = -g -O3 -ffast-math -Wall -D_REENTRANT -DCXX="\"$(CXX)\"" \
	-DPREFIX=\""$(prefix)"\" \
	-DSYSCONFDIR=\""$(sysconfdir)"\" \
	-DDATADIR=\""$(datadir)"\" \
	-DLIBDIR=\""$(libdir)"\" \
	$(GNOFRACT4D_CFLAGS) -DGTK_DISABLE_DEPRECATED -DGNOME_DISABLE_DEPRECATED

CFLAGS = $(CXXFLAGS)
