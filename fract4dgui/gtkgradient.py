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
		self.origmpos  = 0
		
		self.f = f
		self.grad=grad
		self.grad.compute()
		
		self.create_gradient_dialog()

	def show(parent,f,grad):
		dialog.T.reveal(GradientDialog,parent,f,grad)
		
	show = staticmethod(show)
	
	def create_gradient_dialog(self):
		hData = self.grad.getDataFromHandle(self.grad.cur)
		HSVCo = gradient.RGBtoHSV(hData[1])
	
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
		
		###COLOUR SELECTION###
		self.csel = gtk.ColorSelection()
		self.csel.set_has_palette(True)
		
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
		
		#self.vbox.pack_start(self.csel, 1, 0, 10)
		
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
	
	###CALLBACKS FOR RGB/HSV/etc SPINBUTTONS###
	def redchanged(self, widget):
		seg, index = self.grad.getSegFromHandle(self.grad.cur)
		seg[index][1][0] = widget.get_value_as_int()
		self.grad.compute()
		self.gradarea.queue_draw()
	
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
			s_lpos = (seg[2][0]+(1-self.grad.offset)) * self.grad.num
			s_rpos = (seg[3][0]+(1-self.grad.offset)) * self.grad.num
			
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
		x=event.x/self.grad.num
		x-=1-self.grad.offset
		if x < 0:
			x+=1
		
		seg = self.grad.getRawSegAt(x)
		relx = x - seg[2][0]
		
		if relx < (seg[3][0]-seg[2][0])/2:
			self.grad.cur=self.grad.segments.index(seg)*2
		else:
			self.grad.cur=self.grad.segments.index(seg)*2+1
		
		self.gradarea.queue_draw()
		
		self.mousedown = True
		self.origmpos  = event.x
		
		return False
	
	def gradarea_clicked(self, widget, event):
		self.mousedown = False
		self.grad.compute()
		self.gradarea.queue_draw()
		self.f.colorlist=self.grad.clist
		self.f.changed(False)
		
		return False
		
	def gradarea_mousemoved(self, widget, event):
		if self.mousedown:
			seg, index = self.grad.getSegFromHandle(self.grad.cur)
			segindex = self.grad.segments.index(seg)
			move = (event.x - self.origmpos)/self.grad.num
			#A humongous bowl of hackiness!
			#Basically, this is similar to the problem when drawing the handles: each
			#handle is comprised of two individuals. Therefore we most move either the
			#one that occupies one segment up or down. An exception will be raised if
			#the selected handle is either the last or the first, so then we move the
			#one on the other end.
			if index == 2:
				try:
					self.grad.segments[segindex-1][3][0]+=move
					if self.grad.segments[segindex-1][3][0] > 1:
						self.grad.segments[segindex-1][3][0]-=1
					elif self.grad.segments[segindex-1][3][0] < 0:
						self.grad.segments[segindex-1][3][0]+=1
				except IndexError:
					self.grad.segments[self.grad.segments.len()-1][3][0]+=move
					if self.grad.segments[self.grad.segments.len()-1][3][0] > 1:
						self.grad.segments[self.grad.segments.len()-1][3][0]-=1
					elif self.grad.segments[self.grad.segments.len()-1][3][0] < 0:
						self.grad.segments[self.grad.segments.len()-1][3][0]+=1
			else:
				try:
					self.grad.segments[segindex+1][2][0]+=move
					if self.grad.segments[segindex+1][2][0] > 1:
						self.grad.segments[segindex+1][2][0]-=1
					elif self.grad.segments[segindex+1][2][0] < 0:
						self.grad.segments[segindex+1][2][0]+=1
				except IndexError:
					self.grad.segments[0][2][0]+=move
					if self.grad.segments[0][2][0] > 1:
						self.grad.segments[0][2][0]-=1
					elif self.grad.segments[0][2][0] < 0:
						self.grad.segments[0][2][0]+=1
					
			seg[index][0]+=move
			if seg[index][0] > 1:
				seg[index][0] -=1
			elif seg[index][0] < 0:
				seg[index][0] +=1
			
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

