#!/usr/bin/env python

# create a DocBook XML document documenting the standard library

from xml.sax.saxutils import escape, quoteattr

import symbol
import fracttypes

def strOfType(t):
    return fracttypes.strOfType(t).capitalize()

class SymbolPrinter:
    def __init__(self):
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
        print '<sect3 id=%s>' % quoteattr(key)
        print '<title>%s %s</title>' % (escape(key), type)
        
    def output_function(self,val):
        print '<para><informaltable>'
        print '<tgroup cols="2">'
        print '''<thead><row>
                    <entry>Input Type</entry>
                    <entry>Output Type</entry>
                 </row></thead>'''
        print '<tbody>'
        for func in val:
             print '<row>'
             print '<entry>'
             print ", ".join(map(strOfType,func.args))
             print '</entry>'
             print '<entry>%s</entry>' % strOfType(func.ret)
             print '</row>'
        print '</tbody>'
        print '</tgroup>'
        print '</informaltable>'
        print '</para>'

    def output_refentry_footer(self):
        print '</sect3>'

    def output_refentry_body(self,val):
        print '<para>'
        text = val.__doc__ or "No documentation yet."
        print escape(text)
        print '</para>'
        
    def output_symbol(self,key,val,type):
        self.output_refentry_header(key,val,type)
        
        if isinstance(val,symbol.OverloadList):
            self.output_function(val)            
        else:
            print '<para>Type: %s</para>' % strOfType(val.type)
        self.output_refentry_body(val)
        self.output_refentry_footer()

    def output_all(self):
        self.output_table(self.funcs,"Functions", "function")
        self.output_table(self.vars, "Symbols", "(symbol)")
        self.output_table(self.operators, "Operators", "operator")
        
    def output_table(self,table,name,type):
        print '<sect2 id="%s">' % name
        print '<title>%s</title>' % name
        keys = table.keys()
        keys.sort()
        for k in keys:
            self.output_symbol(k,table[k],type)
        print '</sect2>'
        
def main():
    d = symbol.T()
    printer = SymbolPrinter()

    for k in d.default_dict.keys():
        printer.add_symbol(d.demangle(k),d[k])

    printer.output_all()
    
if __name__ == '__main__':
    main()

