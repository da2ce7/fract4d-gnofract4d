
lib_LTLIBRARIES= libfract4d.la

AM_CXXFLAGS = -O3 -ffast-math -Wall -D_REENTRANT 

libfract4d_la_SOURCES=\
	fract4d.h \
	compiler.h \
	compiler.cpp \
	fract.cpp fract.h fract_public.h fract_callbacks.h calc.h \
	pointFunc.cpp pointFunc.h pointFunc_public.h state.h \
	vectors.h \
	image_public.h \
	colorizer.cpp colorizer.h colorizer_public.h \
	colorFunc.h colorFunc.cpp \
	colorTransferFunc.h colorTransferFunc.cpp \
	iterFunc.h iterFunc.cpp \
	bailFunc.h bailFunc.cpp \
	fractFunc.h fractFunc.cpp fractThreadFunc.cpp \
	io.h io.cpp \
	threadpool.h \
	fractWorker.h MTFractWorker.cpp

EXTRA_DIST=compiler_template.cpp

Codedir = $(datadir)/gnofract4d
Code_DATA= compiler_template.cpp \
	pointFunc.h \
	state.h
