# This is called by the main gnofract4d script

import shutil, os
import fractal,fc,fract4dc,image, fracttypes, fractconfig

class T:
    def __init__(self):
        self.compiler = fc.Compiler()
        self.update_compiler_prefs(fractconfig.instance)
        self.f = fractal.T(self.compiler)
        
    def update_compiler_prefs(self, prefs):
        self.compiler.update_from_prefs(prefs)
        
    def run(self,options):
        for path in options.extra_paths:            
            self.compiler.add_func_path(path)
        
        if options.flags != None:
            self.compiler.set_flags(options.flags)

        width = options.width or fractconfig.instance.getint("display","width")
        height = options.height or fractconfig.instance.getint("display","height")        
        threads = options.threads or fractconfig.instance.getint(
            "general","threads")

        im = image.T(width,height)

        if len(options.args) > 0:
            self.load(options.args[0])

        self.f.apply_options(options)
        self.f.antialias = options.antialias or \
            fractconfig.instance.getint("display","antialias")

        self.draw(im,options, threads)

        if options.save_filename:
            im.save(options.save_filename)

    def draw(self, im, options, nthreads):
        if options.usebuilt == None:
            outfile = self.f.compile()
        else:
            self.f.set_output_file(options.usebuilt)

        if options.buildonly == None:
            self.f.draw(im,nthreads)
        else:
            outdirname = os.path.dirname(options.buildonly)
            if len(outdirname) > 0:
                os.makedirs(outdirname)
                
            shutil.copy(outfile, options.buildonly)
            (base, ext) = os.path.splitext(outfile)
            cfile = base + ".c"
            shutil.copy(cfile, options.buildonly + ".c")
        
    def load(self,filename):
        self.f.loadFctFile(open(filename))
