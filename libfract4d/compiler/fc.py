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

import fractparser
import fractlexer
import translate
import codegen

class Compiler:
    def __init__(self):
        self.parser = fractparser.parser
        self.lexer = fractlexer.lexer
        self.files = {}
        print "new compiler"
        
    def usage(self):
        print "fc -o [outfile] -f [formula] infile"
        sys.exit(1)

    def load_formula_file(self, filename):
        try:
            s = open(filename,"r").read() # read in a whole file
            self.lexer.lineno = 1
            result = self.parser.parse(s)
            formulas = {}
            for formula in result.children:
                formulas[formula.leaf] = formula

            self.files[filename] = (formulas,s)
        except Exception, err:
            print "Error parsing '%s' : %s" % (filename, err)
            raise
        
    def main(self):
        try:
            opts, args = getopt.getopt(sys.argv[1:], "o:f:",
                                       [ "output=", "formula=" ])
        except getopt.GetoptError:
            self.usage()

        for (arg,val) in opts:
            if arg=="-f" or arg=="--formula":
                self.formula = val
            elif arg=="-o" or arg=="--output":
                self.outputfile = val
            
        if len(args) < 1:
            self.usage()

        try:
            self.load_formula_file(args[0])
        except IOError, err:
            sys.exit(1)
            
        # find the function we want
        self.ast = None
        for formula in result.children:
            if formula.leaf == self.formula:
                self.ast = formula
                break

        if self.ast == None:
            print "Can't find formula %s in %s" % \
                  (self.formula, self.formulafile)
            sys.exit(1)

        self.ir = translate.T(self.ast)
        if self.ir.errors != []:
            print "Errors during translation"
            for e in self.ir.errors:
                print e
            sys.exit(1)

        try:
            cg = codegen.T(self.ir.symbols)
            cg.output_all(self.ir, {"z" : "", "pixel" : ""})
            c_code = cg.output_c(self.ir)
        except TranslationError, err:
            print "Error during code generation"
            print err
            sys.exit(1)

        try:
            cFileName = cg.writeToTempFile(c_code,".c")
            oFileName = self.outputfile
            #print c_code
            cmd = "gcc -Wall -fPIC -dPIC -O3 -shared %s -o %s -lm" % \
                  (cFileName, oFileName)
            (status,output) = commands.getstatusoutput(cmd)
        except Exception, err:
            print "Error invoking C compiler: %s" % err
            sys.exit(1)

        if status != 0:
            print "Errors reported by C compiler:"
            print output
            sys.exit(1)

        
        



def main():
    fc = Compiler()
    fc.main()

if __name__ =='__main__': main()
