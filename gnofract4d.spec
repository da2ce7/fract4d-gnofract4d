%define ver     1.8 
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
Requires: gnome-libs >= 1.4.0  gcc-c++ >= 2.95
Docdir: %{prefix}/doc
Prefix: %prefix

%description
Gnofract4D is a fractal browser. It can generate many different fractals, 
including some which are hybrids between the Mandelbrot and Julia sets.

%prep
%setup 

%build
CFLAGS="$RPM_OPT_FLAGS" CXXFLAGS="$RPM_OPT_FLAGS" ./configure \
        --prefix=%{prefix}
make 
                                       

%install
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT

make prefix=$RPM_BUILD_ROOT%{prefix} install

%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
if which scrollkeeper-update>/dev/null 2>&1; then scrollkeeper-update; fi

%postun
/sbin/ldconfig
if which scrollkeeper-update>/dev/null 2>&1; then scrollkeeper-update; fi


%files
%defattr(-,root,root)
%doc AUTHORS COPYING ChangeLog NEWS README

%{prefix}/bin/gnofract4d
%{prefix}/lib/libfract4d.*
%{prefix}/share/gnome/apps/Graphics/gnofract4d.desktop
%doc %{prefix}/share/gnome/help/gnofract4d/*
%{prefix}/share/omf/gnofract4d/*
%{prefix}/share/gnofract4d/*
%{prefix}/share/pixmaps/gnofract4d/*
