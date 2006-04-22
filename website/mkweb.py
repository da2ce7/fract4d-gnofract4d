#!/usr/bin/env python
import os

import kid

module = kid.load_template("outline.kid",cache=1)

class Bag:
    def __init__(self,**kwds):
        self.__dict__.update(kwds)


announce = Bag(
    date="April 15th, 2006",
    text="Version 2.13 released, featuring render-to-disk.")

pages = [
    Bag(name="Home",
        file="index.html",
        comments=[ "It warms my heart to see such a fine open source fractal program. A really great job!",
                   "After my opinion it is the best open source fractal editor/browser available on the web..."],
        image="front.jpg",
        announce=announce),

    Bag(name="Features",
        file="features.html",
        image="cheby.jpg",
        comments=[
    "I'm always surprised how fast it runs...",
    "I'm still dribbling out of my slack-jawed mouth...",
    "What a great program..."]
        ),

    Bag(name="Screenshots",
        image="newton.jpg",
        file="screenshots.html",
        comments=[
    "Thanks for a really cool program...",
    "Thanks for producing the best piece of fractal software for Linux!",
    "Gnofract4D, c'est &#224; mon avis, le meilleur logiciel de fractales sous Linux." ]
    ),
    
    Bag(name="Galleries",
        image="front_buffalo.jpg",
        file="gallery.html",
        comments=[
        "Thanks for the great fractal program...",
        "I'm an enthusiastic user of your program gnofract4d. It's really great..."
        ]
        ),
    
    Bag(name="Download",
        file="download.html",
        image="buffalo002.jpg",
        comments=[
    "Well, this pretty much rocks...",
    "Thanks for creating Gnofract 4D, I've found it a real pleasure to use so far..."]
        ),

    Bag(name="FAQ",
        file="faq.html",
        image="faq.jpg"
        ),

    Bag(name="Links",
        file="links.html",
        image="jm.jpg",
        comments=[
    "Thanks for a cool site and amazing app/creations!",
    "Really a nice tool."        
    ]),
        
    ]

def process_all(pages):
    for page in pages:
        body_text = open(os.path.join("in", page.file)).read()
        out = open(page.file, "w")
        template = module.Template(
            body=body_text,
            pages=pages,
            page=page)
        try:
            print >>out, str(template)
        except Exception, exn:
            print "Error processing page %s" % page.file
            raise
            
        out.close()
        if hasattr(page,"children"):
            process_all(page.children)

process_all(pages)
