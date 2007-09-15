# This is called by the main gnofract4d script

import fractal,fc,fract4dc,image, fracttypes, fractconfig

class T:
    def __init__(self):
        self.compiler = fc.Compiler()
        self.update_compiler_prefs(fractconfig.instance)
        self.f = fractal.T(self.compiler)
        
    def update_compiler_prefs(self, prefs):
        self.compiler.compiler_name = prefs.get("compiler","name")
        self.compiler.flags = prefs.get("compiler","options")
        for path in prefs.get_list("formula_path"):
            self.compiler.add_func_path(path)
        
    def run(self,options):
        for path in options.extra_paths:            
            self.compiler.add_func_path(path)
        
        width = options.width or fractconfig.instance.getint("display","width")
        height = options.height or fractconfig.instance.getint("display","height")
        im = image.T(width,height)

        if len(options.args) > 0:
            self.load(options.args[0])

        self.f.apply_options(options)
        self.f.antialias = fractconfig.instance.getint("display","antialias")
        self.draw(im)

        if options.save_filename:
            im.save(options.save_filename)

    def draw(self,im):
        self.f.compile()
        self.f.draw(im)
        
    def load(self,filename):
        self.f.loadFctFile(open(filename))
