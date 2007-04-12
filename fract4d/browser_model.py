
import fc

FRACTAL = 0
INNER = 1
OUTER = 2
TRANSFORM = 3
GRADIENT = 4

# from the above constants to those inside compiler
func_mapping = [
    fc.FormulaTypes.FRACTAL,
    fc.FormulaTypes.COLORFUNC,
    fc.FormulaTypes.COLORFUNC,
    fc.FormulaTypes.TRANSFORM,
    fc.FormulaTypes.GRADIENT
    ]

def stricmp(a,b):
    return cmp(a.lower(),b.lower())

class TypeInfo:
    def __init__(self, parent, compiler, t, exclude=None):
        self.parent = parent
        self.formula_type = t
        self.exclude= exclude
        self.fname = None
        self.formula = None
        self.formulas = []
        self.files = compiler.find_files_of_type(t)
        self.files.sort(stricmp)
        
    def set_file(self,compiler,fname):
        if self.fname == fname:
            return
        ff = compiler.get_file(fname)
        self.formulas = ff.get_formula_names(self.exclude)
        self.formulas.sort(stricmp)
        self.fname = fname
        self.set_formula(compiler,None)
        self.file_changed()
        
    def set_formula(self,compiler,formula):
        if self.formula == formula:
            return
        self.formula = formula
        self.formula_changed()
        
    def file_changed(self):
        self.parent.file_changed()

    def formula_changed(self):
        self.parent.formula_changed()
        
class T:
    def __init__(self,compiler):
        self.compiler = compiler
        self.typeinfo = [
            TypeInfo(self, compiler, fc.FormulaTypes.FRACTAL),
            TypeInfo(self, compiler, fc.FormulaTypes.COLORFUNC, "OUTSIDE"),
            TypeInfo(self, compiler, fc.FormulaTypes.COLORFUNC, "INSIDE"),
            TypeInfo(self, compiler, fc.FormulaTypes.TRANSFORM),
            TypeInfo(self, compiler, fc.FormulaTypes.GRADIENT)
            ]
        self.current_type = -1
        self.set_type(FRACTAL)

    def set_type(self,t):
        if self.current_type == t:
            return
        self.current_type = t
        self.current = self.typeinfo[t]
        self.type_changed()

    def set_file(self,fname):
        self.current.set_file(self.compiler,fname)

    def set_formula(self,formula):
        self.current.set_formula(self.compiler,formula)
        
    def type_changed(self):
        pass

    def file_changed(self):
        pass

    def formula_changed(self):
        pass
    
    def get_type_info(self,t):
        return self.typeinfo[t]
