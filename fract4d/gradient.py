#!/usr/bin/env python

#Class definition for Gradients

#These two are shtolen from libgimpcolor/gimpcolorspace.c
def RGBtoHSV(rgb):
	hsv=[0,0,0]
	
	trgb = rgb
	trgb.sort
	max = trgb[0]
	min = trgb[2]
	delta = max - min

	hsv[2]=max
	if delta > 0.00001:
		hsv[1]=delta/max
		if rgb[0] == max:
			hsv[0] = (rgb[1] - rgb[2]) / delta
			if hsv[0] < 0.0:
				hsv[0] += 6.0
			elif rgb[1] == max:
				hsv[0] = 2.0 + (rgb[2] - rgb[0]) / delta
			elif rgb[2] == max:
				hsv[0] = 4.0 + (rgb[0] - rgb[1]) / delta

		hsv[0] /= 6.0
	else:
		hsv[0] = 0.0
		hsv[1] = 0.0
		
	hsv[0]*=255
	hsv[1]*=255
	
	return hsv

def HSVtoRGB(hsv):
	rgb=[0,0,0]
	hsv=[hsv[0]/255,hsv[1]/255,hsv[2]/255]
	if hsv[1] == 0.0:
		rgb=[hsv[2],hsv[2],hsv[2]]
	else:
		hue = hsv[0]

		if hue == 1.0:
			hue = 0.0

		hue *= 6.0

		i = int(hue)
		f = hue - i
		w = hsv[2] * (1.0 - hsv[1])
		q = hsv[2] * (1.0 - (hsv[1] * f))
		t = hsv[2] * (1.0 - (hsv[1] * (1.0 - f)))
		
		#I'll be buggered if I know why this works
		if i == 0:
			rgb[0] = hsv[2]
			rgb[1] = t
			rgb[2] = w
		elif i == 1:
			rgb[0] = q
			rgb[1] = hsv[2]
			rgb[2] = w
		elif i == 2:
			rgb[0] = w
			rgb[1] = hsv[2]
			rgb[2] = t
		elif i == 3:
			rgb[0] = w
			rgb[1] = q
			rgb[2] = hsv[2]
		elif i == 4:
			rgb[0] = t
			rgb[1] = w
			rgb[2] = hsv[2]
		elif i == 5:
			rgb[0] = hsv[2]
			rgb[1] = w
			rgb[2] = q
			
	rgb=[rgb[0]*255,rgb[1]*255,rgb[2]*255]
			
	return rgb

class Handle:
	def __init__(self, pos, color):
		self.pos = pos
		self.col = color
		
class Segment:
    def __init__(self, lh, rh, color_mode='RGB', blend_mode='Linear'):
		self.cmode = color_mode
		self.bmode = blend_mode
		self.left = lh
		self.right = rh
					
class Gradient:
	def __init__(self):
		self.segments=[Segment(Handle(0, [255, 255, 0]), Handle(.5, [255, 0, 0])),
						Segment(Handle(.5, [255, 0, 0]),  Handle(.55, [0, 0, 255])),
						Segment(Handle(.55,[0, 0, 255]),  Handle(.7,  [0, 128, 0])),
						Segment(Handle(.7, [0, 128, 0]),  Handle(1, [255, 255, 0]))]
		
		#Key:	Coloring mode, Blending mode, [position [R|H, G|S, B|V], [same again, but for left handle]]
		#	Note that HSV coloring mode does NOT specify the color in H, S and V, merely blends along the
		#	HSV axes.
		#Possibly add option for midpoint
		
		self.cur=1
		self.num=255
		self.detail=1.0/self.num
		self.alternating=0
		self.offset=0
		self.dialog=None
		
	def compute(self):
		clist=[]; i=0; alt=0
		while i < 1:
			ialt=i+alt
			if ialt > 1:
				ialt-=1.0
			ialt+=self.offset
			if ialt > 1:
				ialt-=1.0
			col=self.getColorAt(ialt)
			clist.append((i,
						 int(col[0]),
						 int(col[1]),
						 int(col[2]),
						 255))
			i += self.detail
			alt+=self.alternating
			if alt > 1:
				alt-=1.0
							
		self.clist = clist
			
	def getColorAt(self, pos):
		#Clever stuff is shtolen from gimp/app/core/gimpgradient.c
		seg = self.getSegAt(pos)
		if seg == None: return [0, 0, 0]

		#if seg == 0:
		#	s_lpos = 0
		#	s_lcol = self.first
		#else:
		#	s_lpos = self.handles[seg-1][2][0]
		#	s_lcol = self.handles[seg-1][2][1]
		
		cmode = seg.cmode
		bmode = seg.bmode
		
		s_lcol = seg.left.col
		s_rcol = seg.right.col
		if cmode == 'HSV':
			s_lcol = RGBtoHSV(s_lcol)
			s_rcol = RGBtoHSV(s_rcol)
			
		s_lpos = seg.left.pos
		s_rpos = seg.right.pos
		
		#if pos > s_rpos:
		#	if s_rpos >= s_lpos:
		#		s_rpos+=1
		#	else:
		#		s_rpos-=1
		#if pos < s_lpos:
		#	if s_rpos >= s_lpos:
		#		s_lpos-=1
		#	else:
		#		s_lpos+=1
			#s_rpos-=s_lpos
			#pos   -=s_lpos
			#s_lpos =0
			#if s_rpos <= 0:
			#	s_rpos+=1
			#if pos <= 0:
			#	pos+=1
			
			
		#print s_rpos, s_lpos
		
		s_len = s_rpos-s_lpos
		if s_len == 0:
			s_len = 0.00001
		
		#Uncomment the following when we've implemented movable middle handles
		#s_mpos = (.5 - s_lpos) / s_len
		s_mpos = 0.5
		pos    = (pos- s_lpos) / s_len
		
		if bmode == 'Linear':
			factor = self.getLinearFactor(pos, s_mpos)
		else:
			factor = self.getCurvedFactor(pos, s_mpos)
		
		#print factor
		
		#Assume RGB mode, for the moment
		RH = s_lcol[0] + (s_rcol[0] - s_lcol[0]) * factor
		GS = s_lcol[1] + (s_rcol[1] - s_lcol[1]) * factor
		BV = s_lcol[2] + (s_rcol[2] - s_lcol[2]) * factor
		
		#print factor, s_lcol, s_rcol
		
		if cmode == 'RGB':
			return [RH, GS, BV]
		else:
			return HSVtoRGB([RH,GS,BV])
		
	#Another monstrosity brought about by the fact that we need to do weird stuff when
	#A segment crosses the border... This probably houses a couple of bugs I haven't found, yet...
	def getSegAt(self, pos):
		bestseg = None
		for seg in self.segments:
			#print seg.right.pos, bestpos, pos
			if pos <= seg.right.pos and pos >=seg.left.pos:
				bestseg = seg
		
		if bestseg != None:
			return bestseg
		else:	
			return None
		
	
	def getSegFromHandle(self, handle):
		seg = handle/2
		if handle/2.0 == seg:
			return self.segments[seg], 'left'
		else:
			return self.segments[seg], 'right'
	
	def getDataFromHandle(self, handle):
		seg = handle/2
		if handle/2.0 == seg:
			return self.segments[seg].left
		else:
			return self.segments[seg].right
	
	def getLinearFactor(self, pos, middle):
		if pos <= middle:
			return 0.5 * pos / middle
		else:
			pos -= middle;
			middle = 1.0 - middle
			return 0.5 + 0.5 * pos / middle
		
	def getCurvedFactor(self, pos, middle):
		return pos**( log(0.5) / log(middle) )
	
		
	def add(self, action, widget):
		x = self.mousepos/self.num
		
		seg = self.getSegAt(x)
		segindex = self.segments.index(seg)
		
		if segindex+1 < len(self.segments):
			segright = self.segments[segindex+1]
		else: segright = None
		
		s_len = (seg.right.pos-seg.left.pos)
		s_mid = seg.left.pos + s_len*0.5
		newcol= self.getColorAt(s_mid)
		
		seg.right.pos = s_mid
		seg.right.col = newcol
		if segright == None:
			self.segments.append(Segment(Handle(s_mid, newcol), Handle(1, self.segments[0].left.col), seg.cmode, seg.bmode))
		else:
			self.segments.insert(segindex+1,
								  Segment(Handle(s_mid, newcol), Handle(segright.left.pos, segright.left.col), seg.cmode, seg.bmode))
								  
		self.compute()
		if self.dialog != None:
			self.dialog.gradarea.queue_draw()
			
	def remove(self, action, widget):
		if self.cur == 0 or self.cur == len(self.segments):
			return
		
		seg, side = self.getSegFromHandle(self.cur)
		segindex = self.segments.index(seg)
		
		if side == 'left':
			segright = self.segments[segindex-1]
			segright.right.pos = seg.right.pos
			segright.right.col = seg.right.col
			self.segments.remove(seg)
		else:
			segleft = self.segments[segindex+1]
			segleft.left.pos = seg.left.pos
			segleft.left.col = seg.left.col
			self.segments.remove(seg)
		
		self.cur = 0
		
		self.compute()
		if self.dialog != None:
			self.dialog.gradarea.queue_draw()

	def getCList(self):
		return self.clist
	def getOffset(self):
		return self.offset
		
	def setOffset(self, newoffset):
		self.offset=newoffset
