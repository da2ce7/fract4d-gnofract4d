INCLUDES = \
	-I$(top_srcdir)/intl \
	-I$(top_srcdir)/libfract4d \
	$(GNOME_INCLUDEDIR)

bin_PROGRAMS = fract4d 
# itertest

fract4d_SOURCES = \
	main.cpp \
	image.cpp image.h

fract4d_LDADD = ../libfract4d/libfract4d.la $(GNOME_LIBDIR) $(GTK_LIBS) \
	$(GNOMEUI_LIBS) $(INTLLIBS) $(PTHREAD_LIB)

CXXFLAGS = -g -O3 -ffast-math -Wall -D_REENTRANT -DCXX="\"$(CXX)\"" 
