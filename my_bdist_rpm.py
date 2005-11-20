#!/usr/bin.env python

# Override the default bdist_rpm distutils command to do what I want

import re
import glob
import os
import sys

from distutils.command.bdist_rpm import bdist_rpm
from distutils.core import Command

topdir_re = re.compile(r'.*topdir (.*)')

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

    def spawn(self,cmd):
        '''HACK: On FC4 rpmbuild creates 2 RPMS, the normal one and a
        debuginfo one. This horrifies the Python 2.3 bdist_rpm,
        which only expects 1 RPM. This works around that by deleting
        the extraneous debuginfo RPM. Overriding this method rather than
        run() because there's less code. '''
        bdist_rpm.spawn(self,cmd)
        if sys.version[:3] == "2.3" and cmd[0] == "rpmbuild":
            for arg in cmd:
                m = topdir_re.match(arg)
                if m:
                    dir = m.group(1)                    
                    debuginfo_glob = os.path.join(
                        dir,"RPMS", "*", "*debuginfo*")
                    rpms = glob.glob(debuginfo_glob)
                    for rpm in rpms:
                        os.remove(rpm)

        
    def _make_spec_file(self):
        '''HACK: override the default PRIVATE function to specify:
           AutoReqProv: no
           add some commands to install desktop files & mime types
           '''
        
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
