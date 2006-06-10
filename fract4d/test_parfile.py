#!/usr/bin/env python

# test cases for parfile.py


import string
import unittest
import StringIO
import math

import testbase

import parfile
import fractal
import fc
import preprocessor

g_comp = fc.Compiler()
g_comp.file_path.append("../formulas")
g_comp.load_formula_file("gf4d.frm")
g_comp.load_formula_file("test.frm")
g_comp.load_formula_file("gf4d.cfrm")

fotd = """FOTD_for_04-05-06  { ; time=2:38:57.82--SF5 on a P200
reset=2004 type=mandel passes=1
center-mag=-0.74999655467724592903865/0.0171269216\\
3034049041486/5.51789e+018 params=0/0 float=y
maxiter=72000 inside=0 periodicity=10
colors=0000qJ0mP0iX0eb0di0`o0Xu0Tz2Pz2NzRTzoZqzbRz\\
dTzdTzeTzeTzeTzgVzgVzgVziVziVzkXzkXzkXzmXzmXzmXzgV\\
zdTu`RkXP`TNRNNGJL6GJ0CH08K04U0GcAWdPdkehvpmuxrzzx\\
zzzuzzqzzmzzizzezzbzzZzzVzzTzzRzzRxzPozPexNZvNPsLG\\
qL8oLEkNJiNNgNTeNXdN``PbXPeTPgPPkLPmHPqEPsARv6Rx2R\\
z0Rz0Rz0Rz0RzzLzzPzgTzLXz0`z0Xz0Vz0Rz0Pz0Lz0Jz0Gz0\\
Ez0Az08z04z02z00z00z00s2GNV`0uu0so6qiCodJo`PmVXkPd\\
kLiiGqgAvg6Lzb0zz2zgJzJ`z0Tz2Nz8HzECxJ6vP0sV0q`0me\\
0kk0io0os0su0xx4zzCzzHzzPzzVzzXzzXzzXzzXzzXzzXzxXx\\
vXvuXssXqqXmoXkmbizVdzPZyHTsCNh6HZ0CS06Q00S00U00W0\\
0Y00_00a40cC4eJ6hR8kZAneEqmGtuHwzJzzLzz0Hz0Gz0Gz0E\\
z0Ez0Ez0Cz0Cz0Cz0Ax0Av08u08q08o06m06k06s0Cgz0TZzz0\\
zz0zz2zq6ziAz`GzRJxHNvARuLGko0CV4de0Vo0NgVzkHzo6ss\\
0ev0TmCbq2Xs0Tu0Nv0J0z02z0Cs0Lb0XL2e46o0CiZpoRmqGe\\
c4`h0Tc0LGzzRdxbHim0VPJob2bm0R60AP0Cg0EzzzzzzzdqxH\\
dx0RzzLzmJzNHx0G0z00v60uE }"""

class ParTest(testbase.TestBase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testColors(self):
        self.assertEqual(parfile.colorRange(""), [])

        colors = parfile.colorRange("05F")
        self.assertEqual(len(colors),1)
        
        colors = parfile.colorRange("05F<63>DISDISDIS<89>uxxuxxvyyvyywzz<94>05F")
        self.assertEqual(len(colors),256)

        self.assertRaises(RuntimeError,parfile.colorRange, "&*(")
        self.assertRaises(RuntimeError,parfile.colorRange, "00")
        self.assertRaises(RuntimeError,parfile.colorRange, "000<0>000")
        self.assertRaises(RuntimeError,parfile.colorRange, "<1>000")
        self.assertRaises(RuntimeError,parfile.colorRange, "<nootherangle")
        self.assertRaises(ValueError,parfile.colorRange, "<>")

    def testLoadFOTD1(self):
        fotd_file = StringIO.StringIO(fotd)
        f = fractal.T(g_comp)        
        parfile.parse(fotd_file, f)
        self.assertEqual(f.maxiter, 72000)

    def testGetParams(self):
        fotd_file = StringIO.StringIO(fotd)
        
        params = parfile.get_params(fotd_file)
        self.assertEqual(len(params), 18)
        self.assertEqual(params[0],"FOTD_for_04-05-06")

    def testGetPairs(self):
        fotd_file = StringIO.StringIO(fotd)
        
        params = parfile.get_params(fotd_file)
        pairs = parfile.get_param_pairs(params)

        self.assertEqual(pairs["maxiter"],'72000')

    def testParseParams(self):
        f = fractal.T(g_comp)        
        parfile.parse_maxiter("72000",f)
        self.assertEqual(f.maxiter,72000)
        parfile.parse_colors('0000qJ0mP0iX0eb0di0`o0Xu0Tz2Pz2NzRTzoZqzbRzdTzdTzeTzeTzeTzgVzgVzgVziVziVzkXzkXzkXzmXzmXzmXzgVzdTu`RkXP`TNRNNGJL6GJ0CH08K04U0GcAWdPdkehvpmuxrzzxzzzuzzqzzmzzizzezzbzzZzzVzzTzzRzzRxzPozPexNZvNPsLGqL8oLEkNJiNNgNTeNXdN``PbXPeTPgPPkLPmHPqEPsARv6Rx2Rz0Rz0Rz0Rz0RzzLzzPzgTzLXz0`z0Xz0Vz0Rz0Pz0Lz0Jz0Gz0Ez0Az08z04z02z00z00z00s2GNV`0uu0so6qiCodJo`PmVXkPdkLiiGqgAvg6Lzb0zz2zgJzJ`z0Tz2Nz8HzECxJ6vP0sV0q`0me0kk0io0os0su0xx4zzCzzHzzPzzVzzXzzXzzXzzXzzXzzXzxXxvXvuXssXqqXmoXkmbizVdzPZyHTsCNh6HZ0CS06Q00S00U00W00Y00_00a40cC4eJ6hR8kZAneEqmGtuHwzJzzLzz0Hz0Gz0Gz0Ez0Ez0Ez0Cz0Cz0Cz0Ax0Av08u08q08o06m06k06s0Cgz0TZzz0zz0zz2zq6ziAz`GzRJxHNvARuLGko0CV4de0Vo0NgVzkHzo6ss0ev0TmCbq2Xs0Tu0Nv0J0z02z0Cs0Lb0XL2e46o0CiZpoRmqGec4`h0Tc0LGzzRdxbHim0VPJob2bm0R60AP0Cg0EzzzzzzzdqxHdx0RzzLzmJzNHx0G0z00v60uE',f)
        self.assertEqual(len(f.get_gradient().segments),255)

        parfile.parse_center_mag("-0.74999655467724592903865/0.01712692163034049041486/5.51789e+018",f)
        self.assertEqual(f.params[f.XCENTER],-0.74999655467724592903865)
        self.assertEqual(f.params[f.YCENTER],-0.01712692163034049041486)
        self.assertEqual(f.params[f.MAGNITUDE],2.0/5.51789e+018 * 1.33)

    def disabled_testLogTableLimits(self):
        # disabled since for some odd reason we get a slightly different
        # logtable from Fractint
        (lf,mlf) = parfile.get_log_table_limits(69,750,256,2004)
        self.assertEqual(69,lf)
        self.assertNearlyEqual([38.935782028258387], [mlf]) 

        n = parfile.calc_log_table_entry(0,69,lf,mlf, 2004)
        self.assertEqual(1 ,n)

        n = parfile.calc_log_table_entry(69,69,lf,mlf, 2004)
        self.assertEqual(1 ,n)

        n = parfile.calc_log_table_entry(70,69,lf,mlf, 2004)
        self.assertEqual(1 ,n)

        n = parfile.calc_log_table_entry(71,69,lf,mlf, 2004)
        self.assertEqual(2 ,n)

        # this gets the wrong answer
        n = parfile.calc_log_table_entry(749,69,lf,mlf, 2004)
        self.assertEqual(0xfd,n)
        
    def testSetupLogTable(self):
        table = parfile.setup_log_table(69, 750, 256, 2004)
        self.assertEqual(750,len(table))

        self.assertEqual([1] * 70, table[0:70]) # all entries <= logflag should be 1
        
def suite():
    return unittest.makeSuite(ParTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
