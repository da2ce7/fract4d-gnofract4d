#!/usr/bin/python

# Copyright (C) 2006  Branko Kokanovic
#
#   DlgAdvOpt.py: dialog for advanced interpolation options for director
#

from gi.repository import Gtk
from gi.repository import GObject
import os
import re
from threading import *


class DlgAdvOptions:

    def __init__(self,current_kf,animation,parent):
        self.dialog=Gtk.Dialog(
            transient_for=parent,
            title="Keyframe advanced options",
            modal=True,
            destroy_with_parent=True
        )
        self.dialog.add_buttons(Gtk.STOCK_OK, Gtk.ResponseType.OK,
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL)

        self.current_kf=current_kf
        self.animation=animation

        self.tbl_main=Gtk.Table(n_rows=6,n_columns=2,homogeneous=False)
        self.tbl_main.set_row_spacings(10)
        self.tbl_main.set_col_spacings(10)
        self.tbl_main.set_border_width(10)

        dirs=animation.get_directions(self.current_kf)

        self.lbl_xy=Gtk.Label(label="XY angles interpolation direction:")
        self.tbl_main.attach(self.lbl_xy,0,1,0,1)
        self.cmb_xy=Gtk.ComboBoxText() #Gtk.ComboBox()
        self.cmb_xy.append_text("Nearer")
        self.cmb_xy.append_text("Longer")
        self.cmb_xy.append_text("Clockwise")
        self.cmb_xy.append_text("Counterclockwise")
        self.cmb_xy.set_active(dirs[0])
        self.tbl_main.attach(self.cmb_xy,1,2,0,1)
        self.lbl_xz=Gtk.Label(label="XZ angles interpolation direction:")
        self.tbl_main.attach(self.lbl_xz,0,1,1,2)
        self.cmb_xz=Gtk.ComboBoxText() #Gtk.ComboBox()
        self.cmb_xz.append_text("Nearer")
        self.cmb_xz.append_text("Longer")
        self.cmb_xz.append_text("Clockwise")
        self.cmb_xz.append_text("Counterclockwise")
        self.cmb_xz.set_active(dirs[1])
        self.tbl_main.attach(self.cmb_xz,1,2,1,2)
        self.lbl_xw=Gtk.Label(label="XW angles interpolation direction:")
        self.tbl_main.attach(self.lbl_xw,0,1,2,3)
        self.cmb_xw=Gtk.ComboBoxText() #Gtk.ComboBox()
        self.cmb_xw.append_text("Nearer")
        self.cmb_xw.append_text("Longer")
        self.cmb_xw.append_text("Clockwise")
        self.cmb_xw.append_text("Counterclockwise")
        self.cmb_xw.set_active(dirs[2])
        self.tbl_main.attach(self.cmb_xw,1,2,2,3)
        self.lbl_yz=Gtk.Label(label="YZ angles interpolation direction:")
        self.tbl_main.attach(self.lbl_yz,0,1,3,4)
        self.cmb_yz=Gtk.ComboBoxText() #Gtk.ComboBox()
        self.cmb_yz.append_text("Nearer")
        self.cmb_yz.append_text("Longer")
        self.cmb_yz.append_text("Clockwise")
        self.cmb_yz.append_text("Counterclockwise")
        self.cmb_yz.set_active(dirs[3])
        self.tbl_main.attach(self.cmb_yz,1,2,3,4)
        self.lbl_yw=Gtk.Label(label="YW angles interpolation direction:")
        self.tbl_main.attach(self.lbl_yw,0,1,4,5)
        self.cmb_yw=Gtk.ComboBoxText() #Gtk.ComboBox()
        self.cmb_yw.append_text("Nearer")
        self.cmb_yw.append_text("Longer")
        self.cmb_yw.append_text("Clockwise")
        self.cmb_yw.append_text("Counterclockwise")
        self.cmb_yw.set_active(dirs[4])
        self.tbl_main.attach(self.cmb_yw,1,2,4,5)
        self.lbl_zw=Gtk.Label(label="ZW angles interpolation direction:")
        self.tbl_main.attach(self.lbl_zw,0,1,5,6)
        self.cmb_zw=Gtk.ComboBoxText() #Gtk.ComboBox()
        self.cmb_zw.append_text("Nearer")
        self.cmb_zw.append_text("Longer")
        self.cmb_zw.append_text("Clockwise")
        self.cmb_zw.append_text("Counterclockwise")
        self.cmb_zw.set_active(dirs[5])
        self.tbl_main.attach(self.cmb_zw,1,2,5,6)
        self.dialog.vbox.pack_start(self.tbl_main,True,True,0)
        #self.dialog.set_geometry_hints(None,min_aspect=3.5,max_aspect=3.5)

    def show(self):
        self.dialog.show_all()
        response = self.dialog.run()
        if response == Gtk.ResponseType.OK:
            dirs=(self.cmb_xy.get_active(),self.cmb_xz.get_active(),self.cmb_xw.get_active(),
                self.cmb_yz.get_active(),self.cmb_yw.get_active(),self.cmb_zw.get_active())
            self.animation.set_directions(self.current_kf,dirs)

        self.dialog.destroy()
        return
