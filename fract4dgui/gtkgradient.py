import gtk
import dialog
import utils

from fract4d import gradient

def show_gradients(parent,f,grad):
	GradientDialog.show(parent,f,grad)
	
class GradientDialog(dialog.T):
	def __init__(self,main_window,f,grad):
		global userPrefs
		dialog.T.__init__(
			self,
			_("Gradients"),
			main_window,
			gtk.DIALOG_DESTROY_WITH_PARENT,
			(gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE))
		
		self.set_size_request(300, 400)
		
		self.mousedown = False
		self.origmpos = self.startmpos = 0
		
		self.f = f
		self.grad=grad
		self.grad.dialog = self
		self.grad.compute()
		
		self.create_gradient_dialog()

	def show(parent,f,grad):
		dialog.T.reveal(GradientDialog,parent,f,grad)
		
	show = staticmethod(show)
	
	def create_gradient_dialog(self):
		hData = self.grad.getDataFromHandle(self.grad.cur)
		HSVCo = gradient.RGBtoHSV(hData.col)
	
		###GRADIENT PREVIEW###
		self.gradarea=gtk.DrawingArea()
		self.gradarea.set_size_request(self.grad.num+8, 64)
		self.gradarea.connect('realize', self.gradarea_realized)
		self.gradarea.connect('expose_event', self.gradarea_expose)

		self.gradarea.add_events(
            gtk.gdk.BUTTON_RELEASE_MASK |
            gtk.gdk.BUTTON_PRESS_MASK |
            gtk.gdk.POINTER_MOTION_MASK)
        
		self.gradarea.connect('button-press-event', self.gradarea_mousedown)
		self.gradarea.connect('button-release-event', self.gradarea_clicked)
		self.gradarea.connect('motion-notify-event', self.gradarea_mousemoved)
		gradareaBox = gtk.HBox(False, 0)
		
		###CONTEXT MENU###
		menu_items = ( 
			( "/_Insert",	"<control>I",	self.grad.add,		0		 ),
			( "/_Delete",	"<control>D",	self.grad.remove,	0, 	None )
			)
		
		accel_group = gtk.AccelGroup()
		self.item_factory= gtk.ItemFactory(gtk.Menu, "<gradients>", accel_group)
		self.item_factory.create_items(menu_items)
		self.add_accel_group(accel_group)
		self.menu=self.item_factory.get_widget("<gradients>")
		
		###COLOR SELECTION###
		if gtk.pygtk_version[0] >= 2 and gtk.pygtk_version[1] >= 4:
			lblCsel = gtk.Label("Color:")
			self.csel = gtk.ColorButton(gtk.gdk.Color(hData.col[0]*255,hData.col[1]*255,hData.col[2]*255))
			self.csel.connect('color-set', self.colorchanged)
			self.colorbutton = True
		else:
			self.csel = gtk.Button("Color...")
			self.csel.connect('clicked', self.cbutton_clicked)
			self.csel_dialog = gtk.ColorSelectionDialog("Select a Color")
			self.csel_dialog.colorsel.set_current_color(
					gtk.gdk.color_parse("#%4x%4x%4x" % \
										(hData.col[0]*255,
										 hData.col[1]*255,
										 hData.col[2]*255)))
			self.csel_dialog.ok_button.connect('clicked', self.cdialog_response)
			self.colorbutton = False
		synccolsB = gtk.Button("Sync Colors")
		synccolsB.connect('clicked', self.sync_colors)
			
		CSelBox = gtk.HBox(False, 0)
		
		###OFFSET CONTROL###
		lblOffset = gtk.Label(_("Offset:"))
		lblOffsetBox = gtk.HBox(False, 0)
		
		offset=gtk.HScale(gtk.Adjustment(self.grad.getOffset(), 0, 1, 0.001, 0.01, 0.0))
		offset.set_digits(3)
		offset.connect('value-changed', self.offset_changed)
		
		
		###WIDGET PACKING###
		self.vbox.set_homogeneous(0)
		gradareaBox.pack_start(self.gradarea, 1, 0, 10)
		self.vbox.pack_start(gradareaBox, 0, 0, 10)
		
		if self.colorbutton: CSelBox.pack_start(lblCsel, 1, 0, 40)
		CSelBox.pack_start(self.csel, 1, 0, 10)
		CSelBox.pack_start(synccolsB, 1, 0, 10)
		self.vbox.pack_start(CSelBox, 1, 0, 10)
		
		lblOffsetBox.pack_start(lblOffset, 0, 0, 5)
		self.vbox.pack_start(lblOffsetBox, 0, 0, 5)
		self.vbox.pack_start(offset, 0, 0, 10)
		
	def offset_changed(self, widget):
		if self.grad.getOffset() != widget.get_value():
			self.grad.setOffset(1-widget.get_value())
			self.grad.compute()
			self.gradarea.queue_draw()
			self.f.colorlist=self.grad.clist
			self.f.changed(False)
	
	def colorchanged(self, widget):
		color = widget.get_color()
		self.update_color(color)
		
	def update_color(self, color):
		seg, index = self.grad.getSegFromHandle(self.grad.cur)
		seg[index][1] = [color.red/255, color.green/255, color.blue/255]
		self.grad.compute()
		self.gradarea.queue_draw()
		self.f.colorlist=self.grad.clist
		self.f.changed(False)
			
	#The backwards-compatible button was clicked
	def cbutton_clicked(self, widget):
		self.csel_dialog.show()
		
	def cdialog_response(self, widget):
		color = self.csel_dialog.colorsel.get_current_color()
		self.update_color(color)
		
		self.csel_dialog.hide()
		
		return False
		
	###Each handle is comprised of two handles, whose colors can be set independently.
	###This function finds the other handle and sets it to the current handle's color.
	def sync_colors(self, widget):
		if self.grad.cur % 2 == 0: #The handle is the first in its segment
			if self.grad.cur > 0:
				self.grad.segments[self.grad.cur/2-1].right.col = self.grad.getDataFromHandle(self.grad.cur).col
			else:
				self.grad.segments[-1].right.col = self.grad.getDataFromHandle(self.grad.cur).col
		else:
			if self.grad.cur < len(self.grad.segments):
				self.grad.segments[self.grad.cur/2+1].left.col = self.grad.getDataFromHandle(self.grad.cur).col
			else:
				self.grad.segments[0].left.col = self.grad.getDataFromHandle(self.grad.cur).col
				
		self.grad.compute()
		self.gradarea.queue_draw()
		self.f.colorlist=self.grad.clist
		self.f.changed(False)
	
	###INIT FOR GRADIENT PREVIEW###
	def gradarea_realized(self, widget):
		self.gradcol= widget.get_colormap().alloc_color(
            "#FFFFFFFFFFFF", True, True)
		self.gradgc = widget.window.new_gc(	foreground=self.gradcol,
											background=self.gradcol,
											fill=gtk.gdk.SOLID)
								
		widget.window.draw_rectangle(widget.style.white_gc,
								True,
								0, 0,
								widget.allocation.width,
								widget.allocation.height)
		return True
		
	def gradarea_expose(self, widget, event):
		#Assume some other process has compute()ed the gradient
		
		##Draw the gradient itself##
		for col in self.grad.clist:
			self.gradcol = widget.get_colormap().alloc_color(col[1]*256,col[2]*256,col[3]*256, True, True)
			self.gradgc.set_foreground(self.gradcol)
			widget.window.draw_line(self.gradgc,
									col[0]*self.grad.num+4, 0,
									col[0]*self.grad.num+4, 56)
		
		
		##Draw some handles##						
		for seg in self.grad.segments:
			s_lpos = (seg.left.pos+(1-self.grad.offset)) * self.grad.num
			s_rpos = (seg.right.pos+(1-self.grad.offset)) * self.grad.num
			
			if s_lpos > self.grad.num:
				s_lpos -= self.grad.num
			elif s_lpos < 0:
				s_lpos += self.grad.num
			if s_rpos > self.grad.num:
				s_rpos -= self.grad.num
			elif s_rpos < 0:
				s_rpos += self.grad.num
			
			s_lpos += 4
			s_rpos += 4
			
			wgc=widget.style.white_gc
			bgc=widget.style.black_gc
			
			index=self.grad.segments.index(seg)
			
			#A vast ugliness that should draw the selected handle with a white centre.
			#The problem is that each handle is really two handles - the second handle
			#of the left-hand segment and the first of the right.
			#The first two branches deal with handles in the middle, whilst the second
			#two deal with those at the edges. The other is a case for where neither
			#of the handles in a segment should be highlighted.			
			if self.grad.cur/2.0 == index or (self.grad.cur+1)/2.0 == index:
				self.draw_handle(widget.window, int(s_lpos), wgc, bgc)
				self.draw_handle(widget.window, int(s_rpos), bgc, bgc)
			elif (self.grad.cur-1)/2.0 == index:
				self.draw_handle(widget.window, int(s_lpos), bgc, bgc)
				self.draw_handle(widget.window, int(s_rpos), wgc, bgc)
			elif (self.grad.cur-1)/2.0 == len(self.grad.segments)-1.0 and index == 0:
				self.draw_handle(widget.window, int(s_lpos), wgc, bgc)
				self.draw_handle(widget.window, int(s_rpos), bgc, bgc)
			elif self.grad.cur == 0 and index == len(self.grad.segments)/2.0:
				self.draw_handle(widget.window, int(s_lpos), bgc, bgc)
				self.draw_handle(widget.window, int(s_rpos), wgc, bgc)
			else:
				self.draw_handle(widget.window, int(s_lpos), bgc, bgc)
				self.draw_handle(widget.window, int(s_rpos), bgc, bgc)
			
		return False
	
	def gradarea_mousedown(self, widget, event):
		if self.mousedown == False:
			x=event.x/self.grad.num
			x-=1-self.grad.offset
			if x < 0:
				x+=1
		
			seg = self.grad.getSegAt(x)
			relx = x - seg.left.pos
		
			if relx < (seg.right.pos-seg.left.pos)/2:
				self.grad.cur=self.grad.segments.index(seg)*2
			else:
				self.grad.cur=self.grad.segments.index(seg)*2+1
			self.gradarea.queue_draw()
		
		if event.button == 1:
			self.mousedown = True
			self.origmpos = self.startmpos = event.x
		elif event.button == 3:
			self.grad.mousepos = event.x #We can't pass this as callback data, because things're screwed. If this isn't true, please tell!
			#self.item_factory.popup(int(event.x), int(event.y), event.button)
			self.menu.popup(None, None, None, event.button, event.time)
		
		return False
	
	def gradarea_clicked(self, widget, event):
		self.mousedown = False
		if self.startmpos != event.x:
			self.grad.compute()
			self.gradarea.queue_draw()
			self.f.colorlist=self.grad.clist
			self.f.changed(False)
		
		return False
		
	def gradarea_mousemoved(self, widget, event):
		if self.mousedown:
			seg, side = self.grad.getSegFromHandle(self.grad.cur)
			segindex = self.grad.segments.index(seg)
			move = (event.x - self.origmpos)/self.grad.num
			#A humongous bowl of hackiness!
			#Basically, this is similar to the problem when drawing the handles: each
			#handle is comprised of two individuals. Therefore we most move either the
			#one that occupies one segment up or down. An exception will be raised if
			#the selected handle is either the last or the first, so then we move the
			#one on the other end.
			if (segindex > 0 or side == 'right') and (segindex < len(self.grad.segments)-1 or side == 'left'):
				if side == 'left':
					self.grad.segments[segindex-1].right.pos+=move
					if self.grad.segments[segindex-1].right.pos > 1:
						self.grad.segments[segindex-1].right.pos = 1
					elif self.grad.segments[segindex-1].right.pos < 0:
						self.grad.segments[segindex-1].right.pos = 0
						
					seg.left.pos+=move
					if seg.left.pos > 1:
						seg.left.pos =1
					elif seg.left.pos < 0:
						seg.left.pos =0
						
					if seg.left.pos > seg.right.pos:
						seg.left.pos = seg.right.pos
						self.grad.segments[segindex-1].right.pos=seg.right.pos
					elif self.grad.segments[segindex-1].right.pos < self.grad.segments[segindex-1].left.pos:
						self.grad.segments[segindex-1].right.pos=self.grad.segments[segindex-1].left.pos
						seg.left.pos=self.grad.segments[segindex-1].left.pos
				else:
					self.grad.segments[segindex+1].left.pos+=move
					if self.grad.segments[segindex+1].left.pos > 1:
						self.grad.segments[segindex+1].left.pos = 1
					elif self.grad.segments[segindex+1].left.pos < 0:
						self.grad.segments[segindex+1].left.pos = 0
						
					seg.right.pos+=move
					if seg.right.pos > 1:
						seg.right.pos =1
					elif seg.right.pos < 0:
						seg.right.pos =0
						
					if seg.left.pos > seg.right.pos:
						seg.right.pos=seg.left.pos
						self.grad.segments[segindex+1].left.pos=seg.left.pos
					elif self.grad.segments[segindex+1].right.pos < self.grad.segments[segindex+1].left.pos:
						self.grad.segments[segindex+1].left.pos=self.grad.segments[segindex+1].right.pos
						seg.right.pos=self.grad.segments[segindex+1].right.pos
			
			self.origmpos = event.x
			self.grad.compute()
			self.gradarea.queue_draw()
	
	def draw_handle(self, drawable, pos, fill, outline):
		for y in range(8):
			drawable.draw_line(fill, pos-y/2, y+56, pos+y/2, y+56)
		
		lpos = pos + 3.5
		rpos = pos - 3.5
		
		drawable.draw_line(outline, pos, 56, lpos, 63);
		drawable.draw_line(outline, pos, 56, rpos, 63);
		drawable.draw_line(outline, lpos, 63, rpos, 63);

