#!/usr/bin/python
# -*- coding: UTF-8 -*-

# Copyright (C) 2006  Branko Kokanovic
#
#   DlgAdvOpt.py: dialog for advanced options
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#                                                                             
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#                                                                             
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

import gtk
import gobject
import os
import re
from threading import *

from fract4d.directorbean import *

class DlgAdvOptions:
	
	def __init__(self,current_kf,dir_bean):
		self.dialog=gtk.Dialog("Keyframe advanced options...",None,
					gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
					(gtk.STOCK_OK,gtk.RESPONSE_OK,gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL))

		self.current_kf=current_kf
		self.dir_bean=dir_bean
		
		self.tbl_main=gtk.Table(6,2,False)
		self.tbl_main.set_row_spacings(10)
		self.tbl_main.set_col_spacings(10)
		self.tbl_main.set_border_width(10)
		
		dirs=dir_bean.get_directions(self.current_kf)
		
		self.lbl_xy=gtk.Label("XY angles interpolation direction:")
		self.tbl_main.attach(self.lbl_xy,0,1,0,1)
		self.cmb_xy=gtk.combo_box_new_text() #gtk.ComboBox()
		self.cmb_xy.append_text("Nearer")
		self.cmb_xy.append_text("Longer")
		self.cmb_xy.append_text("Clockwise")
		self.cmb_xy.append_text("Counterclockwise")
		self.cmb_xy.set_active(dirs[0])
		self.tbl_main.attach(self.cmb_xy,1,2,0,1)
		self.lbl_xz=gtk.Label("XZ angles interpolation direction:")
		self.tbl_main.attach(self.lbl_xz,0,1,1,2)
		self.cmb_xz=gtk.combo_box_new_text() #gtk.ComboBox()
		self.cmb_xz.append_text("Nearer")
		self.cmb_xz.append_text("Longer")
		self.cmb_xz.append_text("Clockwise")
		self.cmb_xz.append_text("Counterclockwise")
		self.cmb_xz.set_active(dirs[1])
		self.tbl_main.attach(self.cmb_xz,1,2,1,2)
		self.lbl_xw=gtk.Label("XW angles interpolation direction:")
		self.tbl_main.attach(self.lbl_xw,0,1,2,3)
		self.cmb_xw=gtk.combo_box_new_text() #gtk.ComboBox()
		self.cmb_xw.append_text("Nearer")
		self.cmb_xw.append_text("Longer")
		self.cmb_xw.append_text("Clockwise")
		self.cmb_xw.append_text("Counterclockwise")
		self.cmb_xw.set_active(dirs[2])
		self.tbl_main.attach(self.cmb_xw,1,2,2,3)
		self.lbl_yz=gtk.Label("YZ angles interpolation direction:")
		self.tbl_main.attach(self.lbl_yz,0,1,3,4)
		self.cmb_yz=gtk.combo_box_new_text() #gtk.ComboBox()
		self.cmb_yz.append_text("Nearer")
		self.cmb_yz.append_text("Longer")
		self.cmb_yz.append_text("Clockwise")
		self.cmb_yz.append_text("Counterclockwise")
		self.cmb_yz.set_active(dirs[3])
		self.tbl_main.attach(self.cmb_yz,1,2,3,4)
		self.lbl_yw=gtk.Label("YW angles interpolation direction:")
		self.tbl_main.attach(self.lbl_yw,0,1,4,5)
		self.cmb_yw=gtk.combo_box_new_text() #gtk.ComboBox()
		self.cmb_yw.append_text("Nearer")
		self.cmb_yw.append_text("Longer")
		self.cmb_yw.append_text("Clockwise")
		self.cmb_yw.append_text("Counterclockwise")
		self.cmb_yw.set_active(dirs[4])
		self.tbl_main.attach(self.cmb_yw,1,2,4,5)
		self.lbl_zw=gtk.Label("ZW angles interpolation direction:")
		self.tbl_main.attach(self.lbl_zw,0,1,5,6)
		self.cmb_zw=gtk.combo_box_new_text() #gtk.ComboBox()
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
		if response == gtk.RESPONSE_OK:
			dirs=(self.cmb_xy.get_active(),self.cmb_xz.get_active(),self.cmb_xw.get_active(),
				self.cmb_yz.get_active(),self.cmb_yw.get_active(),self.cmb_zw.get_active())
			self.dir_bean.set_directions(self.current_kf,dirs)
			
		self.dialog.destroy()
		return
