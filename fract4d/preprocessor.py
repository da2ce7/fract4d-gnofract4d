import re

ifdef_re = re.compile(r'\s*\$ifdef\s+([a-z][a-z0-9_]*)', re.IGNORECASE)
endif_re = re.compile(r'\s*\$endif', re.IGNORECASE)

class Error(Exception):
    def __init__(self,msg):
        Exception.__init__(self,msg)
        pass
    
class T:
    def __init__(self, s):
        lines = s.splitlines(True)
        ifdef_stack = []
        out_lines = []
        i = 1
        for line in lines:
            if ifdef_re.match(line):
                ifdef_stack.append(i)
            elif endif_re.match(line):
                if ifdef_stack == []:
                    raise Error("%d: $ENDIF without $IFDEF" % i)
                ifdef_stack.pop()
            else:
                if ifdef_stack == []:
                    out_lines.append(line)

            i += 1
            
        if ifdef_stack != []:
            raise Error("%d: $IFDEF without $ENDIF" % ifdef_stack[-1])
        
        self._out = "".join(out_lines)
        
    def out(self):
        return self._out
    
