
import re
import httplib

target_base = "http://formulas.ultrafractal.com/cgi-bin/"

href_re = re.compile(r'<a href="(/cgi-bin/formuladb.*?)"', re.IGNORECASE)

def parse(file):
    links = []
    for line in file:
        m = href_re.search(line)
        if m:
            links.append(m.group(1))

    return links

def fetchzip(name):
    url = target_base + name
    
