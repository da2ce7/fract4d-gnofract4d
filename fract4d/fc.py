#!/usr/bin/env python

# A compiler from UltraFractal or Fractint formula files to C code

# The UltraFractal manual is the best current description of the file
# format. You can download it from http://www.ultrafractal.com/uf3-manual.zip

# The implementation is based on the outline in "Modern Compiler
# Implementation in ML: basic techniques" (Appel 1997, Cambridge)

# Overall structure:
# fractlexer.py and fractparser.py are the lexer and parser, respectively.
# They use the PLY package to do lexing and SLR parsing, and produce as
# output an abstract syntax tree (defined in the Absyn module).

# The Translate module type-checks the code, maintains the symbol
# table (symbol.py) and converts it into an intermediate form (ir.py)

# Canon performs several simplifying passes on the IR to make it easier
# to deal with, then codegen converts it into a linear sequence of
# simple C instructions

# Finally we invoke the C compiler to convert to a native code shared library

import getopt
import sys
import commands
import os.path
import stat
import random
import md5
import re

import fractparser
import fractlexer
import translate
import codegen
import fracttypes
import absyn
import preprocessor

class FormulaFile:
    def __init__(self, formulas, contents,mtime,filename):
        self.formulas = formulas
        self.contents = contents
        self.mtime = mtime
        self.filename = filename
        self.file_backed = True
        
    def override_buffer(self,buffer,formulas):
        'file has been changed in memory'
        self.contents = buffer
        self.formulas = formulas
        self.file_backed= False
        
    def out_of_date(self):
        return self.file_backed and \
               os.stat(self.filename)[stat.ST_MTIME] > self.mtime
    
    def get_formula(self,formula):
        return self.formulas.get(formula)
    
    def get_formula_names(self, skip_type=None):
        '''return all the coloring funcs except those marked as only suitable
        for the OTHER kind (inside vs outside)'''
        names = []
        for name in self.formulas.keys():
            sym = self.formulas[name].symmetry
            if sym == None  or sym == "BOTH" or sym != skip_type:
                names.append(name)

        return names
    
class Compiler:
    isFRM = re.compile(r'(\.frm\Z)|(.ufm\Z)', re.IGNORECASE)
    isCFRM = re.compile(r'(\.cfrm\Z)|(.ucl\Z)', re.IGNORECASE)
    def __init__(self):
        self.parser = fractparser.parser
        self.lexer = fractlexer.lexer
        self.files = {}
        self.c_code = ""
        self.file_path = []
        self.cache_dir = os.path.expanduser("~/.gnofract4d-cache/")
        self.init_cache()
        self.compiler_name = "gcc"
        self.flags = "-fPIC -DPIC -g -O3 -shared"
        self.libs = "-lm"
        self.tree_cache = {}
        self.leave_dirty = False
        
    def formula_files(self):
        return [ (x,y) for (x,y) in self.files.items() 
                 if Compiler.isFRM.search(x)]

    def find_files(self):
        files = {}
        for dir in self.file_path:
            if not os.path.isdir(dir):
                continue
            for file in os.listdir(dir):
                if os.path.isfile(os.path.join(dir,file)):
                    files[file] = 1
        return files.keys()

    def find_formula_files(self):
        return [file for file in self.find_files()
                if Compiler.isFRM.search(file)]
                
    def get_text(self,fname):
        file = self.files.get(fname)
        if not file:
            self.load_formula_file(fname)
        
        return self.files[fname].contents

    def find_colorfunc_files(self):
        return [file for file in self.find_files()
                if Compiler.isCFRM.search(file)]
        
    def colorfunc_files(self):
        return [ (x,y) for (x,y) in self.files.items() 
                 if Compiler.isCFRM.search(x)]
        
    def init_cache(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def last_chance(self,filename):
        '''does nothing here, but can be overridden by GUI to prompt user.'''
        raise IOError("Can't find formula file %s in formula search path" % \
                      filename)

    def compile_one(self,formula):
        self.compile(formula)

        t = translate.T(absyn.Formula("",[],-1))
        cg = self.compile(t)
        t.merge(formula,"")
        outputfile = os.path.abspath(self.generate_code(t, cg))        
        return outputfile
        
    def compile_all(self,formula,cf0,cf1):        
        self.compile(formula)
        self.compile(cf0)
        self.compile(cf1)

        # create temp empty formula and merge everything into that
        t = translate.T(absyn.Formula("",[],-1))
        cg = self.compile(t)
        t.merge(formula,"")
        t.merge(cf0,"cf0_")        
        t.merge(cf1,"cf1_")

        #print t.symbols.keys()
        #print cg.symbols.keys()
        
        outputfile = os.path.abspath(self.generate_code(t, cg))
        
        return outputfile
    
    def find_file(self,filename):
        if os.path.exists(filename):
            dir = os.path.dirname(filename)
            if self.file_path.count(dir) == 0:
                # add directory to search path
                self.file_path.append(dir)            
            return filename
        for path in self.file_path:
            f = os.path.join(path,filename)
            if os.path.exists(f):
                return f

        return self.last_chance(filename)        

    def parse_file(self,s):
        self.lexer.lineno = 1
        result = None
        try:
            pp = preprocessor.T(s)
            result = self.parser.parse(pp.out())
        except preprocessor.Error, err:
            # create an Error formula listing the problem
            result = self.parser.parse('error {\n}\n')

            result.children[0].children[0] = absyn.PreprocessorError(str(err), -1)
            #print result.pretty()
            
        formulas = {}
        for formula in result.children:
            formulas[formula.leaf] = formula
        return formulas
    
    def load_formula_file(self, filename):
        try:
            filename = self.find_file(filename)
            s = open(filename,"r").read() # read in a whole file
            formulas = self.parse_file(s)

            basefile = os.path.basename(filename)
            mtime = os.stat(filename)[stat.ST_MTIME]
            ff = FormulaFile(formulas,s,mtime,filename)
            self.files[basefile] = ff 

            return ff
        except Exception, err:
            #print "Error parsing '%s' : %s" % (filename, err)
            raise

    def out_of_date(self,filename):
        basefile = os.path.basename(filename)
        ff = self.files.get(basefile)
        if not ff:            
            self.load_formula_file(filename)
            ff = self.files.get(basefile)
        return ff.out_of_date()
    
    def get_file(self,filename):
        basefile = os.path.basename(filename)
        ff = self.files.get(basefile)
        if not ff:
            self.load_formula_file(filename)
            ff = self.files.get(basefile)
        elif ff.out_of_date():
            self.load_formula_file(filename)
            ff = self.files.get(basefile)            
        return ff
    
    def compile(self,ir):
        cg = codegen.T(ir.symbols)
        cg.output_all(ir)
        return cg

    def makefilename(self,name,ext):
        return os.path.join(self.cache_dir, "fract4d_%s%s" % (name, ext))

    def hashcode(self,c_code):
        hash = md5.new(c_code)
        hash.update(self.compiler_name)
        hash.update(self.flags)
        hash.update(self.libs)
        return hash.hexdigest()
        
    def generate_code(self,ir, cg, outputfile=None,cfile=None):
        cg.output_decls(ir)
        self.c_code = cg.output_c(ir)

        hash = self.hashcode(self.c_code)
        
        if outputfile == None:
            outputfile = self.makefilename(hash,".so")
            if os.path.exists(outputfile):
                # skip compilation - we already have this code
                return outputfile
        
        if cfile == None:
            cfile = self.makefilename(hash,".c")
            
        open(cfile,"w").write(self.c_code)

        # -march=i686 for 10% speed gain
        cmd = "%s %s %s -o %s %s" % \
              (self.compiler_name, cfile, self.flags, outputfile, self.libs)
        #print "cmd: %s" % cmd

        (status,output) = commands.getstatusoutput(cmd)
        if status != 0:
            raise fracttypes.TranslationError(
                "Error reported by C compiler:%s" % output)

        return outputfile

    def get_parsetree(self,filename,formname):
        ff = self.get_file(filename)
        if ff == None : return None
        return ff.get_formula(formname)
        
    def get_formula(self, filename, formname):
        #print "get formula"
        f = self.get_parsetree(filename,formname)

        if f != None:
            f = translate.T(f)
        return f
        
    def get_colorfunc(self,filename, formula, name):
        ff = self.get_file(filename)
        if ff == None : return None
        f = ff.get_formula(formula)

        if f != None:
            f = translate.ColorFunc(f,name)

        return f

    def clear_cache(self):
        for f in os.listdir(self.cache_dir):
            os.remove(os.path.join(self.cache_dir,f))

    def __del__(self):
        if not self.leave_dirty:
            self.clear_cache()
        
def usage():
    print "FC : a compiler from Fractint .frm files to C code"
    print "fc.py -o [outfile] -f [formula] infile"
    sys.exit(1)

def generate(fc,formulafile, formula, outputfile, cfile):
    # find the function we want
    ir = fc.get_formula(formulafile,formula)
    if ir == None:
        raise Exception("Can't find formula %s in %s" % \
              (formula, formulafile))

    if ir.errors != []:
        print "Errors during translation"
        for e in ir.errors:
            print e
        raise Exception("Errors during translation")

    cg = fc.compile(ir)
    fc.generate_code(ir, cg, outputfile,cfile)

def main(args):
    fc = Compiler()
    fc.leave_dirty = True
    for arg in args:
        ff = fc.load_formula_file(arg)
        for name in ff.get_formula_names():
            print name
            form = fc.get_formula(arg,name)
            cg = fc.compile(form)
            
if __name__ == '__main__':
    main(sys.argv[1:])

