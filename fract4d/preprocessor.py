import re

ifdef_re = re.compile(r'\s*\$ifdef(\s+(?P<var>[a-z][a-z0-9_]*))?',
                      re.IGNORECASE)
endif_re = re.compile(r'\s*\$endif', re.IGNORECASE)

define_re = re.compile(r'\s*\$define(\s+(?P<var>[a-z][a-z0-9_]*))?',
                       re.IGNORECASE)

class Error(Exception):
    def __init__(self,msg):
        Exception.__init__(self,msg)
        pass

class StackEntry:
    def __init__(self, line_num, isTrue):
        self.line_num = line_num
        self.isTrue = isTrue
class T:

    def currently_true(self):
        return self.ifdef_stack == [] or self.ifdef_stack[-1].isTrue

    def get_var(self, m, i, type):
        var = m.group("var")
        if not var:
            raise Error("%d: %s without variable" % (i, type))
        return var
    
    def __init__(self, s):
        self.vars = {}
        lines = s.splitlines(True)
        self.ifdef_stack = []
        out_lines = []
        i = 1
        for line in lines:
            m = ifdef_re.match(line)
            if m:
                var = self.get_var(m,i, "$IFDEF")
                isTrue = False
                if self.vars.has_key(var):
                    isTrue = self.currently_true()
                        
                self.ifdef_stack.append(StackEntry(i, isTrue))
            elif endif_re.match(line):
                if self.ifdef_stack == []:
                    raise Error("%d: $ENDIF without $IFDEF" % i)
                self.ifdef_stack.pop()
            else:
                m = define_re.match(line)
                if m:
                    # a $define
                    var = self.get_var(m,i, "$DEFINE")
                    self.vars[var] = 1
                else:
                    # just a line
                    if self.currently_true():
                        out_lines.append(line)

            i += 1
            
        if self.ifdef_stack != []:
            raise Error("%d: $IFDEF without $ENDIF" % \
                        self.ifdef_stack[-1].line_num)
        
        self._out = "".join(out_lines)
        
    def out(self):
        return self._out
    
