%define ver     1.9 
%define RELEASE 1
%define prefix  /usr      

Summary: Fractal generator/browser
Name: gnofract4d
Version: %ver
Release: 1
Copyright: GPL
Group: X11/Applications/Graphics
Source:	http://dl.sf.net/gnofract4d/%{name}-%{version}.tar.gz
BuildRoot: %{tmpdir}/%{name}-%{PACKAGE_VERSION}-root-%(id -u -n)
URL: http://gnofract4d.sourceforge.net/
Requires: gnome-libs >= 1.4.0
Requires: gcc-c++ >= 2.95
Docdir: %{prefix}/doc
Prefix: %prefix

%description
Gnofract4D is a fractal browser. It can generate many different fractals, 
including some which are hybrids between the Mandelbrot and Julia sets.

%prep
%setup -q

%build
CFLAGS="$RPM_OPT_FLAGS" CXXFLAGS="$RPM_OPT_FLAGS" SKIP_DOC_INSTALL=1 ./configure \
        --prefix=%{prefix}
make 
                                       

%install
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != / ] && rm -rf $RPM_BUILD_ROOT

make prefix=$RPM_BUILD_ROOT%{prefix} install

rm -rf $RPM_BUILD_ROOT%{prefix}/var/scrollkeeper
rm -rf $RPM_BUILD_ROOT%{prefix}/bin/fract4d
rm -rf $RPM_BUILD_ROOT%{prefix}/share/locale/it/LC_MESSAGES/gnofract4d.mo

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
%{prefix}/share/maps/gnofract4d/*
