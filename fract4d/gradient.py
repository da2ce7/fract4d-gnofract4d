#!/usr/bin/env python

import math
import re

#Class definition for Gradients

#gradientfile_re = re.compile(r'\s*(RGB|HSV)\s+(Linear|Sinusoidal|CurvedI|CurvedD)\s+(\d+\.?\d+)\s+(\d+)\s+(\d+)\s+(\d+\.?\d+)\s+(\d+)\s+(\d+)')

#These two are shtolen from libgimpcolor/gimpcolorspace.c
#No longer! they are NOW adapted from the algorithms at http://www.cs.rit.edu/~ncs/color/t_convert.html
def RGBtoHSV(rgb):
	hsv = [0,0,0]
	trgb = rgb[:]
	trgb.sort()
	
	min = trgb[0]
	max = trgb[2]

	delta = float(max - min)
	hsv[2] = max

	if delta == 0:
		# r = g = b = 0		# s = 0, v is undefined
		hsv[1] = 0
		hsv[0] = -1
	else:
		hsv[1]=delta / max
		
		if rgb[0] == max:
			hsv[0] = (rgb[1] - rgb[2]) / delta		# between yellow & magenta
		elif rgb[1] == max:
			hsv[0] = 2 + (rgb[2] - rgb[0] ) / delta	# between cyan & yellow
		else:
			hsv[0] = 4 + (rgb[0] - rgb[1] ) / delta	# between magenta & cyan

	hsv[0] *= 60				# degrees
	if hsv[0] < 0:
		hsv[0] += 360
		
	return hsv

def HSVtoRGB(hsvcol):
	hsv=hsvcol[:]
	rgb=[0,0,0]
	
	hsv[0]/=60
	
	if hsv[1] == 0:
		return [hsv[2],hsv[2],hsv[2]]
	
	i = int(hsv[0])
	f = hsv[0] - i							#Decimal bit of hue
	p = hsv[2] * (1 - hsv[1])
	q = hsv[2] * (1 - hsv[1] * f)
	t = hsv[2] * (1 - hsv[1] * (1 - f))
	
	if i == 0:
		rgb[0] = hsv[2]
		rgb[1] = t
		rgb[2] = p
	elif i == 1:
		rgb[0] = q
		rgb[1] = hsv[2]
		rgb[2] = p
	elif i == 2:
		rgb[0] = p
		rgb[1] = hsv[2]
		rgb[2] = t
	elif i == 3:
		rgb[0] = p
		rgb[1] = q
		rgb[2] = hsv[2]
	elif i == 4:
		rgb[0] = t
		rgb[1] = p
		rgb[2] = hsv[2]
	elif i == 5:
		rgb[0] = hsv[2]
		rgb[1] = p
		rgb[2] = q
	
	return rgb
		

class Handle:
	def __init__(self, pos, colour):
		self.pos = pos
		self.col = colour
	def setcol(self, newcol, info):
		self.col=newcol
		if newcol[0] > 255 or newcol[1] > 255 or newcol[2] > 255: print info
		
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
		
		#Key:	Colouring mode, Blending mode, [position [R|H, G|S, B|V], [same again, but for left handle]]
		#	Note that HSV colouring mode does NOT specify the colour in H, S and V, merely blends along the
		#	HSV axes.
		#Possibly add option for midpoint
		
		self.cur=1
		self.num=255
		self.detail=1.0/self.num
		self.alternate=0
		self.offset=0
		
		self.compute()
		
	def compute(self):
		clist=[]; i=0; alt=0
		while i < 1:
			ialt=i+alt
			if ialt > 1:
				ialt-=1.0
			ialt+=self.offset
			if ialt > 1:
				ialt-=1.0
			col=self.getColourAt(ialt)
			clist.append((i,
						 int(col[0]),
						 int(col[1]),
						 int(col[2]),
						 255))
			i += self.detail
			alt+=self.alternate
			if alt > 1:
				alt-=1.0
							
		self.clist = clist
			
	def getColourAt(self, pos):
		#Clever stuff is shtolen from gimp/app/core/gimpgradient.c
		seg = self.getSegAt(pos)
		if seg == None: return [0, 0, 0]
		
		cmode = seg.cmode
		bmode = seg.bmode
		
		s_lcol = seg.left.col[:]
		s_rcol = seg.right.col[:]
		if cmode == 'HSV':
			s_lcol = RGBtoHSV(s_lcol)
			s_rcol = RGBtoHSV(s_rcol)
			
		s_lpos = seg.left.pos
		s_rpos = seg.right.pos
		
		s_len = s_rpos-s_lpos
		if s_len == 0:
			s_len = 0.00001
		
		#Uncomment the following when we've implemented movable middle handles
		#s_mpos = (.5 - s_lpos) / s_len
		s_mpos = 0.5
		pos	= (pos- s_lpos) / s_len
		
		if bmode == 'Linear':
			factor = self.getLinearFactor(pos, s_mpos)
		elif bmode == 'Sinusoidal':
			factor = self.getSineFactor(pos, s_mpos)
		elif bmode == 'CurvedI':
			factor = self.getCurvedIFactor(pos, s_mpos)
		else:
			factor = self.getCurvedDFactor(pos, s_mpos)
		
		
		#Assume RGB mode, for the moment
		RH = s_lcol[0] + (s_rcol[0] - s_lcol[0]) * factor
		GS = s_lcol[1] + (s_rcol[1] - s_lcol[1]) * factor
		BV = s_lcol[2] + (s_rcol[2] - s_lcol[2]) * factor
		
		if cmode == 'RGB':
			return [RH, GS, BV]
		else:
			return HSVtoRGB([RH,GS,BV])
		
	#Returns the segment in which pos resides.
	def getSegAt(self, pos):
		bestseg = None
		for seg in self.segments:
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
		
	#def getCurvedFactor(self, pos, middle):
	#	return pos**( math.log(0.5) / math.log(middle) )
	def getSineFactor(self, pos, middle):
		pos = self.getLinearFactor(pos, middle)
		return (math.sin ((-math.pi / 2.0) + math.pi * pos) + 1.0) / 2.0
	def getCurvedIFactor(self, pos, middle):
		pos = self.getLinearFactor(pos, middle) - 1.0
		return math.sqrt (1.0 - pos * pos)
	def getCurvedDFactor(self, pos, middle):
		pos = self.getLinearFactor(pos, middle)
		return 1.0 - math.sqrt (1.0 - pos * pos)
		
	def add(self, x):
		seg = self.getSegAt(x)
		segindex = self.segments.index(seg)
		
		if segindex+1 < len(self.segments):
			segright = self.segments[segindex+1]
		else: segright = None
		
		s_len = (seg.right.pos-seg.left.pos)
		s_mid = seg.left.pos + s_len*0.5
		newcol= self.getColourAt(s_mid)
		
		seg.right.pos = s_mid
		seg.right.col = newcol
		if segright == None:
			self.segments.append(Segment(Handle(s_mid, newcol), Handle(1, self.segments[0].left.col), seg.cmode, seg.bmode))
		else:
			self.segments.insert(segindex+1,
								  Segment(Handle(s_mid, newcol), Handle(segright.left.pos, segright.left.col), seg.cmode, seg.bmode))
								  
		self.compute()
			
	def remove(self, h):
		if h == 0 or h == len(self.segments)*2:
			return
		
		seg, side = self.getSegFromHandle(h)
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
		
		self.compute()

	def move(self, handle, move):
		seg, side = self.getSegFromHandle(handle)
		segindex = self.segments.index(seg)
		
		if (segindex > 0 or side == 'right') and (segindex < len(self.segments)-1 or side == 'left'):
			if side == 'left':
				self.segments[segindex-1].right.pos+=move
				if self.segments[segindex-1].right.pos > 1:
					self.segments[segindex-1].right.pos = 1
				elif self.segments[segindex-1].right.pos < 0:
					self.segments[segindex-1].right.pos = 0
						
				seg.left.pos+=move
				if seg.left.pos > 1:
					seg.left.pos =1
				elif seg.left.pos < 0:
					seg.left.pos =0
					
				if seg.left.pos > seg.right.pos:
					seg.left.pos = seg.right.pos
					self.segments[segindex-1].right.pos=seg.right.pos
				elif self.segments[segindex-1].right.pos < self.segments[segindex-1].left.pos:
					self.segments[segindex-1].right.pos=self.segments[segindex-1].left.pos
					seg.left.pos=self.segments[segindex-1].left.pos
			else:
				self.segments[segindex+1].left.pos+=move
				if self.segments[segindex+1].left.pos > 1:
					self.segments[segindex+1].left.pos = 1
				elif self.segments[segindex+1].left.pos < 0:
					self.segments[segindex+1].left.pos = 0
					
				seg.right.pos+=move
				if seg.right.pos > 1:
					seg.right.pos =1
				elif seg.right.pos < 0:
					seg.right.pos =0
					
				if seg.left.pos > seg.right.pos:
					seg.right.pos=seg.left.pos
					self.segments[segindex+1].left.pos=seg.left.pos
				elif self.segments[segindex+1].right.pos < self.segments[segindex+1].left.pos:
					self.segments[segindex+1].left.pos=self.segments[segindex+1].right.pos
					seg.right.pos=self.segments[segindex+1].right.pos

	def getCList(self):
		return self.clist
	def getOffset(self):
		return self.offset
	def setOffset(self, newoffset):
		self.offset=newoffset
	def getAlt(self):
		return self.alternate
	def setAlt(self, newalt):
		self.alternate=newalt
