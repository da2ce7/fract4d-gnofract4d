#!/usr/bin/env python

import unittest
import copy
import math

import gtk
import gobject
import hig

class Test(unittest.TestCase):
    def setUp(self):
        pass
                
    def tearDown(self):
        pass

    def wait(self):
        gtk.main()
        
    def quitloop(self,f,status):
        if status == 0:
            gtk.main_quit()

    def testCreate(self):
        d = hig.Alert(gtk.STOCK_DIALOG_INFO,"Hello!")
        self.assertNotEqual(d,None)

        self.runAndDismiss(d)

        d = hig.Alert(gtk.image_new_from_stock(
            gtk.STOCK_DIALOG_ERROR, gtk.ICON_SIZE_DIALOG),
                      "Oh no!",
                      "A terrible thing has happened")

        self.runAndDismiss(d)
        
    def testInformation(self):
        d = hig.InformationAlert(
            "Your zipper is undone",
            "This might be considered unsightly.")

        self.runAndDismiss(d)
        
    def testError(self):
        d = hig.ErrorAlert(
            "You don't want to do it like that",
            "Chaos will ensue.",
            None)

        self.runAndDismiss(d)
        
        d = hig.ErrorAlert(
            "Could not destroy universe",
            "Destructor ray malfunctioned.",
            None,
            "Try again")

        self.runAndDismiss(d)
        
    def testConfirm(self):
        d = hig.ConfirmationAlert(
            "Do you really want to hurt me?",
            "Do you really want to make me cry?")

        self.runAndDismiss(d)

        d = hig.ConfirmationAlert(
            "Convert sub-meson structure?",
            "The process is agonizingly painful and could result in permanent damage to the space-time continuum",
            None,
            "Convert",
            "Go Fishing")

        self.runAndDismiss(d)

    def runAndDismiss(self,d):
        def dismiss():
            d.response(gtk.RESPONSE_ACCEPT)
            return False

        # increase timeout to see what dialogs look like
        gtk.timeout_add(10,dismiss)
        
        r = d.run()
        d.destroy()
        
    def testPeriodText(self):
        self.assertEqual(hig._periodText(86400 * 3.5), "3 days")
        self.assertEqual(hig._periodText(3600 * 17.2), "17 hours")
        self.assertEqual(hig._periodText(60 * 17), "17 minutes")
        self.assertEqual(hig._periodText(23), "23 seconds")
        
    def testSaveConfirm(self):
        d = hig.SaveConfirmationAlert(
            "Wombat.doc")

        self.runAndDismiss(d)

        d = hig.SaveConfirmationAlert(
            "Wombat.doc",
            791)

        self.runAndDismiss(d)
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
