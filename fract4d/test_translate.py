#!/usr/bin/env python

# test harness for translate module

import string
import unittest
import types

import testbase

import translate
import fractparser
import fractlexer
import fracttypes
import ir
import stdlib

class TranslateTest(testbase.TestBase):
    def setUp(self):
        self.parser = fractparser.parser

    def tearDown(self):
        pass

    def translate(self,s,dump=None):
        fractlexer.lexer.lineno = 1
        pt = self.parser.parse(s)
        return translate.T(pt.children[0], dump)

    def translatecf(self,s,dump=None):
        fractlexer.lexer.lineno = 1
        pt = self.parser.parse(s)
        return translate.ColorFunc(pt.children[0], "cf0", dump)

    def testCF(self):
        t1 = self.translatecf('''c1 {
                            final:
                            #index = #numiter / 256.0
                            }''')

        t2 = self.translatecf('c1 {\n#index = #numiter / 256.0\n}')
        
        self.assertNoErrors(t1)
        self.assertNoErrors(t2)
        self.assertEquivalentTranslations(t1,t2)

        t3 = self.translatecf('''
        c2 {
        init:
        float d = |z|
        loop:
        d = d + |z|
        final:
        #index = log(d+1.0)
        }''')
        self.assertNoErrors(t3)
        
    def testFractintSections(self):
        t1 = self.translate("t1 {\na=1,a=2:\nb=2\nc=3}")
        t2 = self.translate('''
             t2 {
                 init: 
                 a=1
                 a=2
                 loop:
                 b=2
                 bailout:
                 c=3
                 }''')
        
        self.assertEquivalentTranslations(t1,t2)
        self.assertNoErrors(t1)
        self.assertNoErrors(t2)

        t3 = self.translate('''
             t3 {
                 a=1:b=2,c=3
                 init:
                 a=1,a=2
                 loop:
                 b=2
                 bailout:
                 c=3
                 }''')
        self.assertEquivalentTranslations(t1,t3)
        self.assertEqual(len(t3.warnings),8,t3.warnings)

        t4 = self.translate('t_c3{\n:init: a = 1 + 3 * 7\n}')
        self.assertNoErrors(t4)

    def testImplicitConversionToComplex(self):
        t_icc = self.translate('''t11 {
        init: x = exp(1.0,0.0)
        }''')
        t_icc2 = self.translate('''t11 {
        init: x = exp((1.0,0.0))
        }''')
        self.assertNoErrors(t_icc)
        self.assertNoErrors(t_icc2)
        self.assertEquivalentTranslations(t_icc,t_icc2)
        
    def testBailout(self):
        # empty bailout
        t = self.translate('''t_bail_1 {
        bailout:
        }''')

        self.assertWarning(t, "No bailout expression found" )
        self.assertNoErrors(t)

        # uncastable bailout
        t = self.translate('''t_bail_2 {
        bailout:
        if 1 > 2
        endif
        }''')

        self.assertError(t, "invalid type none")
        
    def testAssign(self):
        # correct declarations
        t9 = self.translate('''t9 {
        init:
        int i
        float f
        complex c
        loop:
        i = 1
        f = 1.0
        }''')
        self.assertNoProbs(t9)

        # basic warnings and errors
        t10 = self.translate('''t10 {
        init: int i, float f, complex c
        loop:
        f = 1 ; upcast - warning
        i = 1.0 ; downcast - error
        }''')
        self.assertWarning(t10,"conversion from int to float on line 4")
        self.assertError(t10, "invalid type float for 1.0 on line 5, expecting int")

    def testBadTypeForParam(self):
        t = self.translate('''t_badparam {
        default:
        param foo
            default = "fish"
        endparam
        }''')
        self.assertError(t, "4: Cannot convert string (fish) to complex")

    def testParamTypeConversion(self):
        t = self.translate('''t_badparam {
        default:
        param foo
            default = (1.0,2.0)
        endparam
        }''')

        self.assertNoErrors(t)
        foo = t.symbols["@foo"]
        self.assertEqual(foo.default.value[0].value,1.0)
        self.assertEqual(foo.default.value[1].value,2.0)

    def disable_testMixedImplicitAndNamedParams(self):
        t = self.translate('''t_mix {
        init:
        x = @p1 + @myparam1 + @myparam2
        default:
        param myparam2
        default = (1.0,2.0)
        endparam
        }''')

        print t.symbols.parameters(True)
        print t.symbols.default_params()
        
    def testDefaultSection(self):
        t = self.translate('''t_d1 {
        default:
        maxiter = 100
        xyangle = 4.9
        center = (8.1,-2.0)
        title = "Hello World"
        param foo
            caption = "Angle"
            default = 10.0
        endparam
        param with_Turnaround8
            caption = "Turnaround 8?"
            default = true
            hint = ""
        endparam
        float param f1
        endparam
        }''')
        self.assertNoErrors(t)
        self.assertEqual(t.defaults["maxiter"].value,100)
        self.assertEqual(t.defaults["xyangle"].value,4.9)
        self.assertEqual(t.defaults["center"].value[0].value,8.1)
        self.assertEqual(t.defaults["center"].value[1].value,-2.0)
        self.assertEqual(t.defaults["title"].value,"Hello World")

        k = t.symbols.parameters().keys()
        k.sort()
        exp_k = ["t__a_f1", "t__a_foo","t__a_with_turnaround8"]
        exp_k.sort()
        self.assertEqual(k,exp_k)        

        foo = t.symbols["@foo"]
        self.assertEqual(foo.caption.value, "Angle")
        self.assertEqual(foo.default.value[0].value, 10.0)
        self.assertEqual(foo.default.value[1].value, 0.0)

        t8 = t.symbols["@with_turnaround8"]
        self.assertEqual(t8.hint.value,"")

        f1 = t.symbols["@f1"]
        self.assertEqual(f1.type,fracttypes.Float)

        params = t.symbols.parameters(True)
        op = t.symbols.order_of_params()
        self.assertEqual(op["t__a_f1"],0)
        self.assertEqual(op["t__a_foo"],1)
        self.assertEqual(op["t__a_with_turnaround8"],3)
        self.assertEqual(op["__SIZE__"],5)

        defparams = t.symbols.default_params()
        self.assertEqual(defparams,[0.0,10.0,0.0,1.0,0.0])
        
    def testEnum(self):
        t = self.translate('''t_enum {
        default:
        param calculate
        caption = "Calculate"
        enum    = "Sum" "Abs" "Diff"
        default = 1
        endparam
        init:
        if @calculate == 1
        x = 1
        else
        x = 7
        endif
        }''')

        self.assertNoErrors(t)

        calculate = t.symbols["@calculate"]
        e = calculate.enum
        self.assertEqual(e.value, ["Sum", "Abs", "Diff"])
        self.assertEqual(calculate.type,fracttypes.Int)
        
    def testStringErrors(self):
        t = self.translate('''t_se {
        init:
        x = 1 + "hello"
        }''')
        self.assertError(t, "Invalid argument types ['int', 'string'] for + on line 3")
        
    def testParams(self):
        t12 = self.translate('''t_params {
        init: complex x = @p1 + p2 + @my_param
        complex y = @fn1((1,0)) + fn2((2,0)) + @my_func((1,0))
        }''')
        self.assertNoErrors(t12)
        k = t12.symbols.parameters().keys()
        k.sort()
        exp_k = ["t__a_p1", "t__a_p2", "t__a_my_param",
                 "t__a_fn1", "t__a_fn2", "t__a_my_func"]
        exp_k.sort()
        self.assertEqual(k,exp_k)

        var_k = ["t__a_p1", "t__a_p2", "t__a_my_param"]
        var_k.sort()
        var_k.append("__SIZE__")
        
        op = t12.symbols.order_of_params()
        for (key,ord) in op.items():
            self.assertEqual(op[key],var_k.index(key)*2)


    def testFuncParam(self):
        t =self.translate('''test_func {
        loop:
        z = @myfunc(z) + #pixel
        bailout:
        |z| < @bailout
        default:
        float param bailout
	    default = 4.0
        endparam
        func myfunc
	    default = sqr()
            caption = "hello there"
        endfunc
        func myotherfunc
            default = sqr
            hint = "not used"
        endfunc
        }
        ''')
        self.assertNoErrors(t)

        self.assertEqual(t.symbols["@myfunc"][0].genFunc,stdlib.sqr_c_c)
        self.assertEqual(t.symbols["@myotherfunc"][0].genFunc,stdlib.sqr_c_c)
        
    def testBadFunc(self):
        t = self.translate('t_badfunc {\nx= badfunc(0):\n}')
        self.assertError(t,"Unknown function badfunc on line 2")
        
        
    def testIDs(self):
        t11 = self.translate('''t11 {
        init: int a = 1, int b = 2
        loop: a = b
        }''')
        self.assertNoProbs(t11)

        t12 = self.translate('t12 {\ninit: a = b}')
        self.assertWarning(t12, "Uninitialized variable b referenced on line 2")

    def testBinops(self):
        # simple ops with no coercions
        t13 = self.translate('''t13 {
        loop:
        complex a, complex b, complex c
        int ia, int ib, int ic
        a = b + c
        ia = ib + ic
        }''')
        
        #print t13.sections["loop"].pretty()
        self.assertNoProbs(t13)
        result = t13.sections["loop"]
        self.failUnless(isinstance(result.children[-1],ir.Move))
        # some coercions
        t = self.translate('''t_binop_2 {
        loop:
        complex a, complex b, complex c
        int ia, int ib, int ic
        float fa, float fb, float fc
        a = fa + ia
        fb = ib / ic
        }''')
        self.assertNoErrors(t)
        (plus,div) = t.sections["loop"].children[-2:]

        self.assertEqual(div.children[1].datatype, fracttypes.Float)
        self.assertEqual(div.children[1].children[0].children[0].datatype,
                         fracttypes.Int)

        self.assertFuncOnList(lambda x,y : x.__class__.__name__ == y,
                              [x for x in plus],
                              ["Move","Var","Cast","Binop","Var","Cast","Var"])


    def testIf(self):
        t = self.translate('''t_if_1 {
        loop:
        if a > b
        a = 2
        else
        a = 3
        endif
        }''')

        self.assertNoErrors(t)
        ifseq = t.sections["loop"].children[0]

        self.failUnless(ifseq.children[0].op == ">" and \
                        ifseq.children[0].trueDest == "label0" and \
                        ifseq.children[0].falseDest == "label1")

        self.failUnless(ifseq.children[1].children[0].name == "label0" and \
                        ifseq.children[1].children[-1].dest == "label2" and \
                        ifseq.children[2].children[0].name == "label1" and \
                        ifseq.children[3].name == "label2")

        t = self.translate('''t_if_2 {
        loop:
        if a
        a = 2
        endif
        }''')

        self.assertNoErrors(t)
        ifseq = t.sections["loop"].children[0]
        self.failUnless(ifseq.children[0].op == "!=")
        
        self.failUnless(ifseq.children[1].children[0].name == "label0" and \
                        ifseq.children[1].children[-1].dest == "label2" and \
                        ifseq.children[2].children[0].name == "label1" and \
                        ifseq.children[3].name == "label2")

        self.failUnless(len(ifseq.children[2].children)==1)

        expectedLabs = ['CJ:label0,label1', 'L:label0', 'J:label2', 'L:label1', 'CJ:label3,label4', 'L:label3', 'J:label5', 'L:label4', 'L:label5', 'L:label2']

        t = self.translate('''t_if_3 {
        loop:
        if a == 1
           a = 2
        elseif a == 2
           a = 3
        else
           a = 4
        endif
        }''')

        self.assertNoErrors(t)
        self.assertJumpsMatchLabs(t.sections["loop"])
        self.assertJumpsAndLabs(t, expectedLabs)

        t = self.translate('''t_if_4 {
        loop:
        if a == 1
        else
           if a == 2
              a = 4
           endif
        endif
        }''')

        self.assertNoErrors(t)
        self.assertJumpsMatchLabs(t.sections["loop"])
        self.assertJumpsAndLabs(t, expectedLabs)

    def testBooleans(self):
        t = self.translate('''t_bool_0 {
        init:
        a == 1 && b == 2
        }''')
        self.assertNoErrors(t)
        self.assertJumpsMatchLabs(t.sections["init"])

        t = self.translate('''t_bool_1 {
        init:
        a == 1 || b == 2
        }''')
        self.assertNoErrors(t)
        self.assertJumpsMatchLabs(t.sections["init"])
        
        t = self.translate('''t_bool_2 {
        init:
        if a == 1 && b == 2
           a = 2
        endif
        }''')
        self.assertNoErrors(t)
        self.assertJumpsMatchLabs(t.sections["init"])

        t = self.translate('''t_bool_3 {
        init:
        if a == 1 || b == 2
           a = 2
        endif
        }''')
        self.assertNoErrors(t)
        self.assertJumpsMatchLabs(t.sections["init"])

        t = self.translate('''t_bool_4 {
        init:
        bool a, bool b
        c = (real(a||b),imag(a&&b))
        float f = |a&&b|
        }''')
        self.assertNoErrors(t)
        
    def testMandel(self):
        t = self.translate('''t_mandel_1 {
        loop:
        z = z * z + c
        bailout:
        |z| < 4.0
        }''')

        self.assertNoErrors(t)

        t = self.translate('''t_mandel_2 {
        : z = z * z + c, |z| < 4.0
        }''')

        self.assertNoErrors(t)

    def testDecls(self):
        t1 = self.translate("t4 {\nglobal:int a\ncomplex b\nbool c = true\n}")
        self.assertNoProbs(t1)
        self.assertVar(t1, "a", fracttypes.Int)
        self.assertVar(t1, "b", fracttypes.Complex)
        t1 = self.translate('''
        t5 {
        init:
        float a = true,complex c = 1.0
        complex x = 2
        }''')
        self.assertNoErrors(t1)
        self.assertVar(t1, "a", fracttypes.Float)
        self.assertVar(t1, "c", fracttypes.Complex)
        self.assertVar(t1, "x", fracttypes.Complex)
        self.assertWarning(t1, "conversion from bool to float on line 4")
        self.assertWarning(t1, "conversion from float to complex on line 4")
        self.assertWarning(t1, "conversion from int to complex on line 5")

    def testMultiDecls(self):
        t1 = self.translate("t6 {\ninit:int a = int b = 2}")
        self.assertVar(t1, "a", fracttypes.Int)
        self.assertVar(t1, "b", fracttypes.Int)
        self.assertNoErrors(t1)
        
    def testBadDecls(self):
        t1 = self.translate("t7 {\nglobal:int z\n}")
        self.assertError(t1,"symbol 'z' is predefined")
        t1 = self.translate("t8 {\nglobal:int a\nfloat A\n}")
        self.assertError(t1,"'A' was already defined on line 2")

    def testMultiAssign(self):
        t = self.translate("t_ma {\ninit:z = c = 1.0\n}")
        self.assertNoErrors(t)

    def testAssignToFunc(self):
        t = self.translate("t_a2f {\ninit:real(z) = 2.0, imag(z)=1.5\n}")
        self.assertNoErrors(t)

    def testBjax(self):
        t = self.translate('''Bjax {;
  z=c=2/pixel:
   z =(1/((z^(real(p1)))*(c^(real(p2))))*c) + c
  }
''')
        self.assertNoErrors(t)
        self.assertWarning(t,"No bailout condition specified")

    def testComplexBool(self):
        t = self.translate('''t_cb{
            float x=real(z), float y=imag(z)
            bool chrH1 = x<-0.16646 || x>-0.13646; 
            }''')
        
        self.assertNoErrors(t)
    

def suite():
    return unittest.makeSuite(TranslateTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

