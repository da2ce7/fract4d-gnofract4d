%define ver     1.7 
%define RELEASE 1
%define prefix  /usr      

Summary: Fractal generator/browser
Name: gnofract4d
Version: %ver
Release: 1
Copyright: GPL
Group: Applications/Graphics
Source: ftp://gnofract4d.sourceforge.net/gnofract4d-%{PACKAGE_VERSION}.tar.gz
BuildRoot: /var/tmp/gnofract4d-%{PACKAGE_VERSION}-root
URL: http://gnofract4d.sourceforge.net/
Requires: gnome-libs >= 1.0.12  gcc-c++ >= 2.95
Docdir: %{prefix}/doc
Prefix: %prefix

%description
Gnofract4D is a Fractal generator/browser. It can generate some weird 
fractals which are hybrids between the Mandelbrot and Julia sets.

%prep
%setup 

%build
CFLAGS="$RPM_OPT_FLAGS" CXXFLAGS="$RPM_OPT_FLAGS" ./configure \
        --prefix=%{prefix}
make 
                                       

%install
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT

make prefix=$RPM_BUILD_ROOT%{prefix} install

# hack to get gnome-config-relative stuff into build dir. ugh.
mkdir -p $RPM_BUILD_ROOT/%{prefix}/share/maps/gnofract4d
mkdir -p $RPM_BUILD_ROOT/%{prefix}/share/pixmaps/gnofract4d
cp `gnome-config --datadir`/maps/gnofract4d/* $RPM_BUILD_ROOT/%{prefix}/share/maps/gnofract4d
cp `gnome-config --datadir`/pixmaps/gnofract4d/* $RPM_BUILD_ROOT/%{prefix}/share/pixmaps/gnofract4d

%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog NEWS README

%{prefix}/bin/gnofract4d
%{prefix}/share/gnome/apps/Graphics/gnofract4d.desktop
%{prefix}/share/gnome/help/gnofract4d/*/*
%{prefix}/share/maps/gnofract4d/*
%{prefix}/share/pixmaps/gnofract4d/*
%{prefix}/share/gnofract4d/*
