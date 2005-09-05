#!/usr/bin/env python

# Override the default build distutils command to do what I want

from distutils.command.build_ext import build_ext
from distutils.core import Command
import os

class my_build_ext (build_ext):
    user_options = build_ext.user_options
    def __init__(self, dict):
        build_ext.__init__(self,dict)

    def build_extensions(self):
        print self.compiler.__dict__

        # python2.2 doesn't honor these, so we have to sneak in
        cxx = os.environ["CXX"]
        cc = os.environ["CC"]

        self.compiler.preprocessor[0] = cc
        self.compiler.compiler_so[0] = cc
        self.compiler.compiler[0] = cc
        if hasattr(self.compiler, "compiler_cxx"):
            self.compiler.compiler_cxx[0] = cxx
        self.compiler.linker_so[0] = cxx
        
        if self.compiler.compiler[0].find("33") > -1:
            # gcc 3.3 can't cope with -mtune, ditch that
            self.compiler.compiler = [
                opt for opt in self.compiler.compiler \
                    if opt.find("-mtune") == -1 ]

        if self.compiler.compiler_so[0].find("33") > -1:
            # gcc 3.3 can't cope with -mtune, ditch that
            self.compiler.compiler_so = [
                opt for opt in self.compiler.compiler_so \
                    if opt.find("-mtune") == -1 ]
            print self.compiler.compiler_so

        print self.compiler.__dict__
        build_ext.build_extensions(self)

