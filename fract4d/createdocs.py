#!/usr/bin/env python

# create a DocBook XML document documenting the standard library

from xml.sax.saxutils import escape, quoteattr

import symbol
import fracttypes
import sys

def strOfType(t):
    return fracttypes.strOfType(t).capitalize()

class SymbolPrinter:
    def __init__(self,f):
        self.f = f
        self.funcs = {}
        self.operators = {}
        self.vars = {}

    def add_symbol(self,key,val):
        if isinstance(val,fracttypes.Var):
            self.vars[key] = val
        elif isinstance(val,symbol.OverloadList):
            if val.is_operator():
                self.operators[key] = val
            else:
                self.funcs[key] = val

    def output_refentry_header(self,key,val,type):
        print >>self.f, '<sect3 id=%s>' % quoteattr(key)
        print >>self.f, '<title>%s %s</title>' % (escape(key), type)
        
    def output_function(self,val):
        print >>self.f, '<para><informaltable>'
        print >>self.f, '<tgroup cols="2">'
        print >>self.f,  '''<thead><row>
                    <entry>Input Type</entry>
                    <entry>Output Type</entry>
                 </row></thead>'''
        print >>self.f,  '<tbody>'
        for func in val:
             print >>self.f,  '<row>'
             print >>self.f,  '<entry>'
             print >>self.f,  ", ".join(map(strOfType,func.args))
             print >>self.f,  '</entry>'
             print >>self.f,  '<entry>%s</entry>' % strOfType(func.ret)
             print >>self.f,  '</row>'
        print >>self.f,  '</tbody>'
        print >>self.f,  '</tgroup>'
        print >>self.f,  '</informaltable>'
        print >>self.f,  '</para>'

    def output_refentry_footer(self):
        print >>self.f,  '</sect3>'

    def output_refentry_body(self,val):
        print >>self.f,  '<para>'
        text = val.__doc__ or "No documentation yet."
        print >>self.f,  escape(text)
        print >>self.f,  '</para>'
        
    def output_symbol(self,key,val,type):
        self.output_refentry_header(key,val,type)
        
        if isinstance(val,symbol.OverloadList):
            self.output_function(val)            
        else:
            print >>self.f,  '<para>Type: %s</para>' % strOfType(val.type)
        self.output_refentry_body(val)
        self.output_refentry_footer()

    def output_all(self):
        self.output_table(self.funcs,"Functions", "function")
        self.output_table(self.vars, "Symbols", "(symbol)")
        self.output_table(self.operators, "Operators", "operator")
        
    def output_table(self,table,name,type):
        print >>self.f,  '<sect2 id="%s">' % name
        print >>self.f,  '<title>%s</title>' % name
        keys = table.keys()
        keys.sort()
        for k in keys:
            self.output_symbol(k,table[k],type)
        print >>self.f,  '</sect2>'
        
def main(outfile):
    out = open(outfile,"w")
    d = symbol.T()
    printer = SymbolPrinter(out)

    for k in d.default_dict.keys():
        printer.add_symbol(d.demangle(k),d[k])

    printer.output_all()
    
if __name__ == '__main__':
    main()
    
