# experiment with GTK input behavior

import gtk

import os


def onData(fd, condition):
    bytes = os.read(fd, 1)
    print "%c" % bytes[0]

def main():
    (readfd, writefd) = os.pipe()
    gtk.input_add(readfd, gtk.gdk.INPUT_READ, onData)
    os.write(writefd, "abcd")
    gtk.main()

main()
