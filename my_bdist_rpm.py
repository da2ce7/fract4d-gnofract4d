#!/usr/bin.env python

# Override the default bdist_rpm distutils command to do what I want

from distutils.command.bdist_rpm import bdist_rpm
from distutils.core import Command

class my_bdist_rpm (bdist_rpm):
    user_options = bdist_rpm.user_options
    def __init__(self, dict):
        bdist_rpm.__init__(self,dict)

    def insert_after(self,spec, find,add):
        for i in xrange(len(spec)):
            if spec[i].startswith(find):
                spec.insert(i,add)
                return
            
    def add_to_section(self,spec,sect,add):
        found = False
        for i in xrange(len(spec)):
            if spec[i].startswith(sect):
                found = True
            elif spec[i].startswith('%'):
                if found:
                    spec.insert(i,add)
                    return
        if found:
            # this is the last section
            spec.insert(i,add)
        else:
            raise IndexError("sect %s not found" % sect)
    
    def _make_spec_file(self):
        'override the default to specify AutoReqProv: no'
        
        spec = bdist_rpm._make_spec_file(self)

        # reduce the number of explicit pre-requisites
        self.insert_after(spec, 'Url','AutoReqProv: no')

        # install a .desktop file and register .fct files with ourselves
        self.insert_after(spec, '%define', '%define desktop_vendor ey')
        self.add_to_section(spec, '%install', '''
%{__install} -d -m0755 %{buildroot}/usr/share/applications/
desktop-file-install \
--vendor %{desktop_vendor}                 \
--dir %{buildroot}/usr/share/applications \
%{buildroot}%{_datadir}/gnofract4d/gnofract4d.desktop

%post
update-mime-database %{_datadir}/mime &> /dev/null || :
update-desktop-database &> /dev/null || :

%postun
update-mime-database %{_datadir}/mime &> /dev/null || :
update-desktop-database &> /dev/null || :

''')

        self.add_to_section(
            spec, '%files',
            '%{_datadir}/applications/%{desktop_vendor}-gnofract4d.desktop')
        
        print "SPEC>"
        print "\n".join(spec)
        print "EOF>"
        
        return spec
