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
            self.files[basefile] = FormulaFile(formulas,s)
        
        except Exception, err:
            #print "Error parsing '%s' : %s" % (filename, err)
            raise

    def generate_code(self,ir,outputfile):
        cg = codegen.T(ir.symbols)
        cg.output_all(ir, {"z" : "", "pixel" : ""})
        self.c_code = cg.output_c(ir)
        
        cFileName = cg.writeToTempFile(self.c_code,".c")
        #print c_code
        cmd = "gcc -Wall -fPIC -dPIC -O3 -shared %s -o %s -lm" % \
              (cFileName, outputfile)
        (status,output) = commands.getstatusoutput(cmd)
        if status != 0:
            raise fracttypes.TranslationError(
                "Error reported by C compiler:%s" % output)
        

    def get_formula(self, filename, formula):
        ff = self.files.get(os.path.basename(filename))
        if ff == None : return None
        f = ff.get_formula(formula)
        if f != None:
            f = translate.T(f)
        return f

def usage():
    print "FC : a compiler from Fractint .frm files to C code"
    print "fc.py -o [outfile] -f [formula] infile"
    sys.exit(1)

def generate(fc,formulafile, formula, outputfile):
    # find the function we want
    ir = fc.get_formula(formulafile,formula)
    if ir == None:
        print "Can't find formula %s in %s" % \
              (formula, formulafile)
        sys.exit(1)

    if ir.errors != []:
        print "Errors during translation"
        for e in ir.errors:
            print e
        sys.exit(1)

    try:
        fc.generate_code(ir, outputfile)
    except fracttypes.TranslationError, err:
        print err
        sys.exit(1)

def main():
    fc = Compiler()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "o:f:",
                                   [ "output=", "formula=" ])
    except getopt.GetoptError:
        usage()

    formula = None
    outputfile = None
    for (arg,val) in opts:
        if arg=="-f" or arg=="--formula":
            formula = val
        elif arg=="-o" or arg=="--output":
            outputfile = val
            
    if len(args) < 1 or not formula or not outputfile:
        usage()

    try:
        formulafile = args[0]
        fc.load_formula_file(args[0])
    except IOError, err:
        sys.exit(1)

    if formula == "*":
        for formula in fc.files[os.path.basename(formulafile)].formulas.keys():
            print "%s:%s" % (formulafile, formula)
            generate(fc,formulafile,formula,outputfile)
    else:
        generate(fc,formulafile,formula,outputfile)
    
if __name__ =='__main__': main()
