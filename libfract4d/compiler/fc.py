#!/usr/bin/env python

# A compiler from UltraFractal or Fractint formula files to C code

# The UltraFractal manual is the canonical description of the file
# format. You can download it from http://www.ultrafractal.com/uf3-manual.zip

# The implementation is based on the outline in "Modern Compiler
# Implementation in ML: basic techniques" (Appel 1997, Cambridge)

# Overall structure:
# fractlexer.py and fractparser.py are the lexer and parser, respectively
# They use the PLY package to do lexing and SLR parsing, and produce as
# output an abstract syntax tree (defined in the Absyn module).

# The Translate module type-checks the code, maintains the symbol
# table (symbol.py) and converts it into an intermediate form (ir.py)

import getopt
import sys
import commands
import os.path
import random

import fractparser
import fractlexer
import translate
import codegen
import fracttypes

class FormulaFile:
    def __init__(self, formulas, contents):
        self.formulas = formulas
        self.contents = contents
    def get_formula(self,formula):
        return self.formulas.get(formula)

class Fractal:
    def __init__(self, compiler):
        self.formula = None
        self.cfuncs = [None,None]
        self.compiler = compiler
        self.outputfile = None

    def __del__(self):
        if self.outputfile:
            os.remove(self.outputfile)
        
    def set_formula(self,formulafile,func):
        self.formula = self.compiler.get_formula(formulafile,func)
        if self.formula == None:
            raise ValueError("no such formula: %s:%s" % (formulafile, func))
        
    def set_inner(self,funcfile,func):
        self.cfuncs[0] = self.compiler.get_colorfunc(funcfile,func,"cf0")
        if self.cfuncs[0] == None:
            raise ValueError("no such colorfunc: %s:%s" % (funcfile, func))

    def set_outer(self,funcfile,func):
        self.cfuncs[1] = self.compiler.get_colorfunc(funcfile,func,"cf1")
        if self.cfuncs[1] == None:
            raise ValueError("no such colorfunc: %s:%s" % (funcfile, func))

    def compile(self):
        if self.formula == None:
            raise ValueError("no formula")
        cg = self.compiler.compile(self.formula)
        self.compiler.compile(self.cfuncs[0])
        self.compiler.compile(self.cfuncs[1])

        self.formula.merge(self.cfuncs[0],"cf0")
        self.formula.merge(self.cfuncs[1],"cf1")        
        self.outputfile = self.compiler.generate_code(self.formula, cg)
        return self.outputfile
                                    
class Compiler:
    def __init__(self):
        self.parser = fractparser.parser
        self.lexer = fractlexer.lexer
        self.files = {}
        self.c_code = ""
        
    def load_formula_file(self, filename):
        try:
            s = open(filename,"r").read() # read in a whole file
            self.lexer.lineno = 1
            result = self.parser.parse(s)
            formulas = {}
            for formula in result.children:
                formulas[formula.leaf] = formula

            basefile = os.path.basename(filename)
            ff = FormulaFile(formulas,s)
            self.files[basefile] = ff 

            return ff
        except Exception, err:
            #print "Error parsing '%s' : %s" % (filename, err)
            raise

    def compile(self,ir):
        cg = codegen.T(ir.symbols)
        cg.output_all(ir)
        return cg

    def makefilename(self):
        # FIXME
        return "fract%d.so" % random.randrange(0,sys.maxint)
    
    def generate_code(self,ir, cg, outputfile=None,cfile=None):
        cg.output_decls(ir)
        self.c_code = cg.output_c(ir)
        
        cFileName = cg.writeToTempFile(self.c_code,".c")
        if cfile != None:
            open(cfile,"w").write(self.c_code)
        #print c_code

        if outputfile == None:
            outputfile = self.makefilename()
            
        cmd = "gcc -Wall -fPIC -DPIC -g -O3 -shared %s -o %s -lm" % \
              (cFileName, outputfile)
        (status,output) = commands.getstatusoutput(cmd)
        if status != 0:
            raise fracttypes.TranslationError(
                "Error reported by C compiler:%s" % output)

        return outputfile

    def get_formula(self, filename, formula):
        ff = self.files.get(os.path.basename(filename))
        if ff == None : return None
        f = ff.get_formula(formula)

        cf = None
        if f != None:
            f = translate.T(f)
        return f

    def get_colorfunc(self,filename, formula, name):
        ff = self.files.get(os.path.basename(filename))
        if ff == None : return None
        f = ff.get_formula(formula)

        if f != None:
            f = translate.ColorFunc(f,name)
        return f
        
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

def main():
    fc = Compiler()
    try:
        opts, args = getopt.getopt(
            sys.argv[1:], "o:f:c:C:S",
            [ "output=", "formula=", "colorfunc=", "colorfile=" ])
        
    except getopt.GetoptError:
        usage()

    formula = None
    outputfile = None
    colorfunc = None
    colorfile = None
    cfile = None
    for (arg,val) in opts:
        if arg=="-f" or arg=="--formula":
            formula = val
        elif arg=="-o" or arg=="--output":
            outputfile = val
        elif arg=="-c" or arg=="--colorfunc":
            colorfunc = val
        elif arg=="-C" or arg=="--colorile":
            colorfile = val
        elif arg=="-S":
            cfile = "out.c"
            
    if len(args) < 1 or not formula or not outputfile:
        usage()

    try:
        formulafile = args[0]
        fc.load_formula_file(args[0])
        if colorfile != None:
            fc.load_formula_file(colorfile)
    except IOError, err:
        print err
        sys.exit(1)

    if formula == "*":
        for formula in fc.files[os.path.basename(formulafile)].formulas.keys():
            print "%s:%s" % (formulafile, formula)
            try:
                generate(fc,formulafile,formula,outputfile,cfile)
            except Exception, err:
                print err
    else:
        generate(fc,formulafile,formula,outputfile,cfile)
            
if __name__ =='__main__': main()
