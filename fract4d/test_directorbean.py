#!/usr/bin/env python

# test director bean class implementation

import unittest
import sys

#from fracttypes import *
sys.path.append("..")
import directorbean

class Test(unittest.TestCase):
	def setUp(self):
		self.db = directorbean.DirectorBean()

	def tearDown(self):
		pass

	def testDefault(self):
		self.assertEqual(self.db.get_base_keyframe(),"")
		self.assertEqual(self.db.get_avi_file(),"")
		self.assertEqual(self.db.get_base_stop(),1)
		self.assertEqual(self.db.get_width(),640)
		self.assertEqual(self.db.get_height(),480)
		self.assertEqual(self.db.get_framerate(),25)
		self.assertEqual(self.db.get_redblue(),True)
		self.assertEqual(self.db.keyframes_count(),0)

	def testChangeOptions(self):
		filename="/testing/test.fct"
		dirname="/testing"
		number=300
		#base keyframe
		self.db.set_base_keyframe(filename)
		self.assertEqual(self.db.get_base_keyframe(),filename)
		#avi file
		self.db.set_avi_file(filename)
		self.assertEqual(self.db.get_avi_file(),filename)
		#base stop
		self.db.set_base_stop(number)
		self.assertEqual(self.db.get_base_stop(),number)
		#width
		self.db.set_width(number)
		self.assertEqual(self.db.get_width(),number)
		#height
		self.db.set_height(number)
		self.assertEqual(self.db.get_height(),number)
		#framerate
		number=28
		self.db.set_framerate(number)
		self.assertEqual(self.db.get_framerate(),number)
		#redblue
		self.db.set_redblue(False)
		self.assertEqual(self.db.get_redblue(),False)
		#test for count still 0
		self.assertEqual(self.db.keyframes_count(),0)

	def testKeyframes(self):
		filename="/testing/test.fct"
		duration=10
		stop=5
		int_type=directorbean.INT_LOG
		#test adding
		self.db.add_keyframe(filename,duration,stop,int_type)
		self.assertEqual(self.db.keyframes_count(),1)
		self.assertEqual(self.db.get_keyframe_filename(0),filename)
		self.assertEqual(self.db.get_keyframe_duration(0),duration)
		self.assertEqual(self.db.get_keyframe_stop(0),stop)
		self.assertEqual(self.db.get_keyframe_int(0),int_type)
		self.assertEqual(len(self.db.get_directions(0)),6)
		#test changing one by one
		filename2="/testing/test2.fct"
		duration2=20
		stop2=10
		int_type2=directorbean.INT_INVLOG

		self.db.set_keyframe_duration(0,duration2)
		self.assertEqual(self.db.get_keyframe_duration(0),duration2)
		self.db.set_keyframe_stop(0,stop2)
		self.assertEqual(self.db.get_keyframe_stop(0),stop2)
		self.db.set_keyframe_int(0,int_type2)
		self.assertEqual(self.db.get_keyframe_int(0),int_type2)
		#test changing whole
		self.db.change_keyframe(0,duration,stop,int_type)
		self.assertEqual(self.db.get_keyframe_duration(0),duration)
		self.assertEqual(self.db.get_keyframe_stop(0),stop)
		self.assertEqual(self.db.get_keyframe_int(0),int_type)
		#test adding new
		self.db.add_keyframe(filename2,duration2,stop2,int_type2)
		self.assertEqual(self.db.keyframes_count(),2)
		#test deleting
		self.db.remove_keyframe(1)
		self.assertEqual(self.db.keyframes_count(),1)
		self.db.remove_keyframe(0)
		self.assertEqual(self.db.keyframes_count(),0)

	def testLoading(self):
		result=self.db.load_animation("../testdata/animation.fcta")
		#base stuff
		self.assertEqual(self.db.get_base_keyframe(),"base_name")
		self.assertEqual(self.db.get_base_stop(),30)
		#keyframes
		self.assertEqual(self.db.keyframes_count(),2)
		self.assertEqual(self.db.get_keyframe_filename(0),"kf1")
		self.assertEqual(self.db.get_keyframe_duration(0),10)
		self.assertEqual(self.db.get_keyframe_stop(0),10)
		self.assertEqual(self.db.get_keyframe_int(0),0)
		self.assertEqual(self.db.get_keyframe_filename(1),"kf2")
		self.assertEqual(self.db.get_keyframe_duration(1),20)
		self.assertEqual(self.db.get_keyframe_stop(1),20)
		self.assertEqual(self.db.get_keyframe_int(1),1)
		#output stuff
		self.assertEqual(self.db.get_avi_file(),u"output.avi")
		self.assertEqual(self.db.get_framerate(),28)
		self.assertEqual(self.db.get_width(),320)
		self.assertEqual(self.db.get_height(),240)
		self.assertEqual(self.db.get_redblue(),False)

def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

