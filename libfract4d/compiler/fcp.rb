require 'rockit/rockit'
module Fc
  # Parser for Fractal
  # created by Rockit version 0.3.8 on Mon May 26 18:58:13 PDT 2003
  # Rockit is copyright (c) 2001 Robert Feldt, feldt@ce.chalmers.se
  # and licensed under GPL
  # but this parser is under LGPL
  tokens = [
    t1 = EofToken.new("EOF",/^(¤~~¤¤~^^~4702372928)/),
    t2 = Token.new("Comment",/^(;[^\r\n]*)/,:Skip),
    t3 = Token.new("Blank",/^((( )|(\t)|(\v))+)/,:Skip),
    t4 = Token.new("Identifier",/^([#@]?[A-Z]([A-Z]|\d)*)/i),
    t5 = Token.new("Float",/^((?=\d|\.\d)\d*(\.\d*)?([Ee]([+-]?\d+))?)/),
    t6 = Token.new("String",/^("[^\r\n]*")/),
    t7 = Token.new("Newline",/^((\r\n)|(\r)|(\n))/),
    t8 = Token.new("FormulaID",/^([-A-Z0-9_]+)/i),
    t9 = Token.new("Type",/^((bool)|(int)|(float)|(complex)|(color))/i),
    t10 = StringToken.new("StrToken126","{"),
    t11 = StringToken.new("StrToken128","}"),
    t12 = StringToken.new("StrToken41","("),
    t13 = StringToken.new("StrToken42",")"),
    t14 = StringToken.new("StrToken-834773728","init"),
    t15 = StringToken.new("StrToken59",":"),
    t16 = StringToken.new("StrToken-692607890","loop"),
    t17 = StringToken.new("StrToken401247375","bailout"),
    t18 = StringToken.new("StrToken-701478559","default"),
    t19 = StringToken.new("StrToken227196369","param"),
    t20 = StringToken.new("StrToken326923001","endparam"),
    t21 = StringToken.new("StrToken62","="),
    t22 = StringToken.new("StrToken45",","),
    t23 = StringToken.new("StrToken127","|"),
    t24 = StringToken.new("StrToken46","-"),
    t25 = StringToken.new("StrToken96","^"),
    t26 = StringToken.new("StrToken48","/"),
    t27 = StringToken.new("StrToken43","*"),
    t28 = StringToken.new("StrToken44","+"),
    t29 = StringToken.new("StrToken61","<"),
    t30 = StringToken.new("StrToken63",">"),
    t31 = StringToken.new("StrToken4126650","=="),
    t32 = StringToken.new("StrToken4059001","<="),
    t33 = StringToken.new("StrToken4194298",">="),
    t34 = StringToken.new("StrToken2232478","!=")
  ]
  productions = [
    p1 = Production.new("Formulas'".intern,[:Formulas],SyntaxTreeBuilder.new("Formulas'",["formulas"],[])),
    p2 = Production.new(:Formulas,[:Plus537590734],SyntaxTreeBuilder.new("Formulas",["formulas"],[])),
    p3 = Production.new(:Plus537590734,[:Plus537590734, :Formula],ArrayNodeBuilder.new([1],0,nil,nil,[],true)),
    p4 = Production.new(:Plus537590734,[:Formula],ArrayNodeBuilder.new([0],nil,nil,nil,[],true)),
    p5 = Production.new(:Formula,[:FormulaName, t10, t7, :FormulaBody, t11, :Mult537587814],SyntaxTreeBuilder.new("Formula",["name", "_", "_", "body", "_", "_"],[])),
    p6 = Production.new(:Formula,[:FormulaName, t10, t7, :FormulaBody, t11],ArrayNodeBuilder.new([],nil,SyntaxTreeBuilder.new("Formula",["name", "_", "_", "body", "_", "_"],[]),5,[],true)),
    p7 = Production.new(:Mult537587814,[:Mult537587814, t7],ArrayNodeBuilder.new([1],0,nil,nil,[],true)),
    p8 = Production.new(:Mult537587814,[t7],ArrayNodeBuilder.new([0],nil,nil,nil,[],true)),
    p9 = Production.new(:FormulaName,[t8],SyntaxTreeBuilder.new("FormID",["name"],[])),
    p10 = Production.new(:FormulaName,[t8, t12, t4, t13],SyntaxTreeBuilder.new("FormID",["name", "_", "id"],[])),
    p11 = Production.new(:FormulaBody,[:Plus537580034],SyntaxTreeBuilder.new("FormulaBody",["sections"],[])),
    p12 = Production.new(:Plus537580034,[:Plus537580034, :Section],ArrayNodeBuilder.new([1],0,nil,nil,[],true)),
    p13 = Production.new(:Plus537580034,[:Section],ArrayNodeBuilder.new([0],nil,nil,nil,[],true)),
    p14 = Production.new(:Section,[t14, t15, t7, :Statements],SyntaxTreeBuilder.new("Section",["name", "_", "_", "statements"],[])),
    p15 = Production.new(:Section,[t16, t15, t7, :Statements],SyntaxTreeBuilder.new("Section",["name", "_", "_", "statements"],[])),
    p16 = Production.new(:Section,[t17, t15, t7, :Exp, t7],SyntaxTreeBuilder.new("Section",["name", "_", "_", "statements"],[])),
    p17 = Production.new(:Section,[t18, t15, t7, :Defstatements],SyntaxTreeBuilder.new("Section",["name", "_", "_", "statements"],[])),
    p18 = Production.new(:Section,[t7],SyntaxTreeBuilder.new("Section",[],[])),
    p19 = Production.new(:Defstatements,[:Plus537565094],SyntaxTreeBuilder.new("Defstatements",["defstatements"],[])),
    p20 = Production.new(:Plus537565094,[:Plus537565094, :Defstatement],ArrayNodeBuilder.new([1],0,nil,nil,[],true)),
    p21 = Production.new(:Plus537565094,[:Defstatement],ArrayNodeBuilder.new([0],nil,nil,nil,[],true)),
    p22 = Production.new(:Defstatement,[:Setting],LiftingSyntaxTreeBuilder.new([],[])),
    p23 = Production.new(:Defstatement,[t19, t4, t7, :Settings],SyntaxTreeBuilder.new("Defstatement",["c1", "identifier", "newline", "settings"],[])),
    p24 = Production.new(:Defstatement,[t20, t7],SyntaxTreeBuilder.new("Param",["_", "id", "_", "settings", "_", "_"],[])),
    p25 = Production.new(:Settings,[:Plus537557334],SyntaxTreeBuilder.new("Settings",["settings"],[])),
    p26 = Production.new(:Plus537557334,[:Plus537557334, :Setting],ArrayNodeBuilder.new([1],0,nil,nil,[],true)),
    p27 = Production.new(:Plus537557334,[:Setting],ArrayNodeBuilder.new([0],nil,nil,nil,[],true)),
    p28 = Production.new(:Setting,[t4, t21, :Value, t7],SyntaxTreeBuilder.new("Setting",["id", "_", "value", "_"],[])),
    p29 = Production.new(:Value,[t6],LiftingSyntaxTreeBuilder.new([],[])),
    p30 = Production.new(:Value,[:Exp],LiftingSyntaxTreeBuilder.new([],[])),
    p31 = Production.new(:Statements,[:Plus537549584],SyntaxTreeBuilder.new("Statements",["statements"],[])),
    p32 = Production.new(:Plus537549584,[:Plus537549584, :Statement],ArrayNodeBuilder.new([1],0,nil,nil,[],true)),
    p33 = Production.new(:Plus537549584,[:Statement],ArrayNodeBuilder.new([0],nil,nil,nil,[],true)),
    p34 = Production.new(:Statement,[:Exp, t7],SyntaxTreeBuilder.new("Statement",["exp", "newline"],[])),
    p35 = Production.new(:Exp,[t5],SyntaxTreeBuilder.new("Constant",["num"],[])),
    p36 = Production.new(:Exp,[t4],SyntaxTreeBuilder.new("Variable",["var"],[])),
    p37 = Production.new(:Exp,[t4, t21, :Exp],SyntaxTreeBuilder.new("Assignment",["var", "_", "exp"],[])),
    p38 = Production.new(:Exp,[t9, t4, t21, :Exp],SyntaxTreeBuilder.new("TypedAssignment",["type", "var", "_", "exp"],[])),
    p39 = Production.new(:Exp,[t4, t12, :Exp, t13],SyntaxTreeBuilder.new("FunCall",["function", "_", "param", "_"],[])),
    p40 = Production.new(:Exp,[t12, :Exp, t13],LiftingSyntaxTreeBuilder.new(["_", "exp", "_"],[])),
    p41 = Production.new(:Exp,[t12, :Exp, t22, :Exp, t13],SyntaxTreeBuilder.new("Complex",["_", "left", "_", "right", "_"],[])),
    p42 = Production.new(:Exp,[t23, :Exp, t23],SyntaxTreeBuilder.new("Magnitude",["_", "exp", "_"],[])),
    p43 = Production.new(:Exp,[t24, :Exp],SyntaxTreeBuilder.new("UnaryMinus",["_", "exp"],[])),
    p44 = Production.new(:Exp,[:Exp, t25, :Exp],SyntaxTreeBuilder.new("Exponentiation",["left", "_", "right"],[])),
    p45 = Production.new(:Exp,[:Exp, t26, :Exp],SyntaxTreeBuilder.new("Div",["left", "_", "right"],[])),
    p46 = Production.new(:Exp,[:Exp, t27, :Exp],SyntaxTreeBuilder.new("Mul",["left", "_", "right"],[])),
    p47 = Production.new(:Exp,[:Exp, t28, :Exp],SyntaxTreeBuilder.new("Plus",["left", "_", "right"],[])),
    p48 = Production.new(:Exp,[:Exp, t24, :Exp],SyntaxTreeBuilder.new("Minus",["left", "_", "right"],[])),
    p49 = Production.new(:Exp,[:Exp, t29, :Exp],SyntaxTreeBuilder.new("Cond",["left", "op", "right"],[])),
    p50 = Production.new(:Exp,[:Exp, t30, :Exp],SyntaxTreeBuilder.new("Cond",["left", "op", "right"],[])),
    p51 = Production.new(:Exp,[:Exp, t31, :Exp],SyntaxTreeBuilder.new("Cond",["left", "op", "right"],[])),
    p52 = Production.new(:Exp,[:Exp, t32, :Exp],SyntaxTreeBuilder.new("Cond",["left", "op", "right"],[])),
    p53 = Production.new(:Exp,[:Exp, t33, :Exp],SyntaxTreeBuilder.new("Cond",["left", "op", "right"],[])),
    p54 = Production.new(:Exp,[:Exp, t34, :Exp],SyntaxTreeBuilder.new("Cond",["left", "op", "right"],[]))
  ]
  relations = [
    Relation.new(Production.new(:Exp,[:Exp, OrElement.new([
    t29 = StringToken.new("StrToken61","<"),
    t30 = StringToken.new("StrToken63",">"),
    t31 = StringToken.new("StrToken4126650","=="),
    t32 = StringToken.new("StrToken4059001","<="),
    t33 = StringToken.new("StrToken4194298",">="),
    t34 = StringToken.new("StrToken2232478","!=")
  ]), :Exp],SyntaxTreeBuilder.new("Cond",["left", "op", "right"],[])),:LEFT,Production.new(:Exp,[:Exp, OrElement.new([
    t29 = StringToken.new("StrToken61","<"),
    t30 = StringToken.new("StrToken63",">"),
    t31 = StringToken.new("StrToken4126650","=="),
    t32 = StringToken.new("StrToken4059001","<="),
    t33 = StringToken.new("StrToken4194298",">="),
    t34 = StringToken.new("StrToken2232478","!=")
  ]), :Exp],SyntaxTreeBuilder.new("Cond",["left", "op", "right"],[]))),
    Relation.new(p47,:LEFT,p47),
    Relation.new(p48,:LEFT,p48),
    Relation.new(p46,:LEFT,p46),
    Relation.new(p44,:RIGHT,p44),
    Relation.new(Production.new(:Exp,[:Exp, OrElement.new([
    t29 = StringToken.new("StrToken61","<"),
    t30 = StringToken.new("StrToken63",">"),
    t31 = StringToken.new("StrToken4126650","=="),
    t32 = StringToken.new("StrToken4059001","<="),
    t33 = StringToken.new("StrToken4194298",">="),
    t34 = StringToken.new("StrToken2232478","!=")
  ]), :Exp],SyntaxTreeBuilder.new("Cond",["left", "op", "right"],[])),:HIGHER,p37),
    Relation.new(Production.new(:Exp,[:Exp, OrElement.new([
    t29 = StringToken.new("StrToken61","<"),
    t30 = StringToken.new("StrToken63",">"),
    t31 = StringToken.new("StrToken4126650","=="),
    t32 = StringToken.new("StrToken4059001","<="),
    t33 = StringToken.new("StrToken4194298",">="),
    t34 = StringToken.new("StrToken2232478","!=")
  ]), :Exp],SyntaxTreeBuilder.new("Cond",["left", "op", "right"],[])),:HIGHER,p38),
    Relation.new(p39,:HIGHER,p43),
    Relation.new(p39,:HIGHER,p44),
    Relation.new(p39,:HIGHER,p45),
    Relation.new(p39,:HIGHER,p46),
    Relation.new(p39,:HIGHER,p47),
    Relation.new(p39,:HIGHER,p48),
    Relation.new(p39,:HIGHER,Production.new(:Exp,[:Exp, OrElement.new([
    t29 = StringToken.new("StrToken61","<"),
    t30 = StringToken.new("StrToken63",">"),
    t31 = StringToken.new("StrToken4126650","=="),
    t32 = StringToken.new("StrToken4059001","<="),
    t33 = StringToken.new("StrToken4194298",">="),
    t34 = StringToken.new("StrToken2232478","!=")
  ]), :Exp],SyntaxTreeBuilder.new("Cond",["left", "op", "right"],[]))),
    Relation.new(p39,:HIGHER,p37),
    Relation.new(p39,:HIGHER,p38),
    Relation.new(p45,:HIGHER,p47),
    Relation.new(p45,:HIGHER,p48),
    Relation.new(p45,:HIGHER,Production.new(:Exp,[:Exp, OrElement.new([
    t29 = StringToken.new("StrToken61","<"),
    t30 = StringToken.new("StrToken63",">"),
    t31 = StringToken.new("StrToken4126650","=="),
    t32 = StringToken.new("StrToken4059001","<="),
    t33 = StringToken.new("StrToken4194298",">="),
    t34 = StringToken.new("StrToken2232478","!=")
  ]), :Exp],SyntaxTreeBuilder.new("Cond",["left", "op", "right"],[]))),
    Relation.new(p45,:HIGHER,p37),
    Relation.new(p45,:HIGHER,p38),
    Relation.new(p43,:HIGHER,p44),
    Relation.new(p43,:HIGHER,p45),
    Relation.new(p43,:HIGHER,p46),
    Relation.new(p43,:HIGHER,p47),
    Relation.new(p43,:HIGHER,p48),
    Relation.new(p43,:HIGHER,Production.new(:Exp,[:Exp, OrElement.new([
    t29 = StringToken.new("StrToken61","<"),
    t30 = StringToken.new("StrToken63",">"),
    t31 = StringToken.new("StrToken4126650","=="),
    t32 = StringToken.new("StrToken4059001","<="),
    t33 = StringToken.new("StrToken4194298",">="),
    t34 = StringToken.new("StrToken2232478","!=")
  ]), :Exp],SyntaxTreeBuilder.new("Cond",["left", "op", "right"],[]))),
    Relation.new(p43,:HIGHER,p37),
    Relation.new(p43,:HIGHER,p38),
    Relation.new(p44,:HIGHER,p45),
    Relation.new(p44,:HIGHER,p46),
    Relation.new(p44,:HIGHER,p47),
    Relation.new(p44,:HIGHER,p48),
    Relation.new(p44,:HIGHER,Production.new(:Exp,[:Exp, OrElement.new([
    t29 = StringToken.new("StrToken61","<"),
    t30 = StringToken.new("StrToken63",">"),
    t31 = StringToken.new("StrToken4126650","=="),
    t32 = StringToken.new("StrToken4059001","<="),
    t33 = StringToken.new("StrToken4194298",">="),
    t34 = StringToken.new("StrToken2232478","!=")
  ]), :Exp],SyntaxTreeBuilder.new("Cond",["left", "op", "right"],[]))),
    Relation.new(p44,:HIGHER,p37),
    Relation.new(p44,:HIGHER,p38),
    Relation.new(p47,:HIGHER,Production.new(:Exp,[:Exp, OrElement.new([
    t29 = StringToken.new("StrToken61","<"),
    t30 = StringToken.new("StrToken63",">"),
    t31 = StringToken.new("StrToken4126650","=="),
    t32 = StringToken.new("StrToken4059001","<="),
    t33 = StringToken.new("StrToken4194298",">="),
    t34 = StringToken.new("StrToken2232478","!=")
  ]), :Exp],SyntaxTreeBuilder.new("Cond",["left", "op", "right"],[]))),
    Relation.new(p47,:HIGHER,p37),
    Relation.new(p47,:HIGHER,p38),
    Relation.new(p48,:HIGHER,Production.new(:Exp,[:Exp, OrElement.new([
    t29 = StringToken.new("StrToken61","<"),
    t30 = StringToken.new("StrToken63",">"),
    t31 = StringToken.new("StrToken4126650","=="),
    t32 = StringToken.new("StrToken4059001","<="),
    t33 = StringToken.new("StrToken4194298",">="),
    t34 = StringToken.new("StrToken2232478","!=")
  ]), :Exp],SyntaxTreeBuilder.new("Cond",["left", "op", "right"],[]))),
    Relation.new(p48,:HIGHER,p37),
    Relation.new(p48,:HIGHER,p38),
    Relation.new(p46,:HIGHER,p47),
    Relation.new(p46,:HIGHER,p48),
    Relation.new(p46,:HIGHER,Production.new(:Exp,[:Exp, OrElement.new([
    t29 = StringToken.new("StrToken61","<"),
    t30 = StringToken.new("StrToken63",">"),
    t31 = StringToken.new("StrToken4126650","=="),
    t32 = StringToken.new("StrToken4059001","<="),
    t33 = StringToken.new("StrToken4194298",">="),
    t34 = StringToken.new("StrToken2232478","!=")
  ]), :Exp],SyntaxTreeBuilder.new("Cond",["left", "op", "right"],[]))),
    Relation.new(p46,:HIGHER,p37),
    Relation.new(p46,:HIGHER,p38),
    Relation.new(p37,:EQUAL,p38),
    Relation.new(p45,:EQUAL,p46),
    Relation.new(p38,:EQUAL,p37),
    Relation.new(p47,:EQUAL,p48),
    Relation.new(p48,:EQUAL,p47),
    Relation.new(p46,:EQUAL,p45)
  ]
  priorities = ProductionPriorities.new(relations)
  action_table = [[5, 128], [25, 2048, 32, 512], [5, 128, 4, 1], [2, 1], [33, 512], [12, 17179869177], [37, 8], [8, 17179869177], [41, 64], [45, 4096], [49, 32768, 53, 8192, 57, 65536, 69, 64, 73, 131072], [36, 512], [81, 16384], [85, 16384], [89, 16384], [49, 32768, 53, 8192, 57, 65536, 69, 64, 73, 131072, 40, 1024], [48, 17179868536], [68, 17179868536], [97, 16384], [101, 1024], [105, 64], [109, 64], [113, 64], [44, 17179868536], [117, 64], [121, 64, 20, 17179869177], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [185, 8, 197, 524288, 201, 262144], [28, 17179869177], [205, 64, 16, 17179869177], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304, 120, 17179868536], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [217, 2048, 221, 1048576, 140, 17177776192], [136, 17177776192], [56, 17179868536], [225, 8], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [128, 17179868536], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 273, 64, 277, 1073741824], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [52, 17179868536], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 285, 64, 277, 1073741824], [80, 17179868536], [64, 17179868536], [289, 1048576], [185, 8, 197, 524288, 201, 262144, 72, 17179868536], [84, 17179868536], [297, 64], [301, 8], [24, 17179869177], [124, 17179868536], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 305, 4096, 309, 2097152, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 277, 1073741824], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [321, 1048576], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 277, 1073741824, 168, 17177776192], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [132, 17179868536], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 277, 1073741824, 369, 4194304], [60, 17179868536], [133, 2048, 373, 32, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [76, 17179868536], [92, 17179868536], [385, 64], [156, 17177776192], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 393, 4096, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 277, 1073741824], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 277, 1073741824, 144, 17177776192], [133, 2048, 137, 8, 141, 16, 149, 256, 153, 8388608, 165, 4194304], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 277, 1073741824, 196, 17177776192], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 277, 1073741824, 212, 17177776192], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 277, 1073741824, 204, 17177776192], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 277, 1073741824, 184, 17177776192], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 277, 1073741824, 172, 17177776192], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 277, 1073741824, 180, 17177776192], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 277, 1073741824, 192, 17177776192], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 277, 1073741824, 188, 17177776192], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 277, 1073741824, 176, 17177776192], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 277, 1073741824, 208, 17177776192], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 277, 1073741824, 200, 17177776192], [164, 17177776192], [112, 64], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 277, 1073741824, 116, 64], [401, 64], [185, 8], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 417, 4096, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 277, 1073741824], [152, 17177776192], [233, 536870912, 237, 8589934592, 241, 2147483648, 245, 134217728, 249, 16777216, 253, 67108864, 257, 268435456, 261, 8388608, 265, 33554432, 269, 4294967296, 277, 1073741824, 148, 17177776192], [108, 17179868536], [88, 17179868536], [104, 17179868536], [185, 8, 96, 17179868536], [160, 17177776192], [100, 17179868536]]
  goto_hash = {60 => {19 => 83}, 38 => {19 => 57}, 27 => {16 => 42, 17 => 32, 18 => 39, 19 => 40}, 77 => {19 => 97}, 66 => {19 => 89}, 55 => {19 => 79}, 33 => {19 => 53}, 0 => {5 => 4, 1 => 3, 2 => 2, 3 => 5}, 72 => {19 => 94, 15 => 95}, 61 => {19 => 84}, 28 => {19 => 43}, 67 => {19 => 90}, 62 => {19 => 85}, 29 => {11 => 44, 14 => 48, 9 => 45, 10 => 47}, 2 => {5 => 4, 3 => 7}, 96 => {12 => 101, 13 => 103, 14 => 102}, 63 => {19 => 86}, 41 => {19 => 70}, 80 => {19 => 99}, 69 => {19 => 91}, 58 => {19 => 81}, 47 => {11 => 73, 14 => 48}, 25 => {4 => 31}, 64 => {19 => 87}, 103 => {14 => 105}, 59 => {19 => 82}, 26 => {16 => 36, 17 => 32, 18 => 39, 19 => 40}, 15 => {8 => 23}, 65 => {19 => 88}, 54 => {19 => 78}, 32 => {18 => 52, 19 => 40}, 10 => {6 => 19, 7 => 15, 8 => 16}}
  @@parse_table537586004 = ParseTable.new(productions,tokens,priorities,action_table,goto_hash,2,[
    :REDUCE,
    :SHIFT,
    :ACCEPT
  ])
  def Fc.parser
    GeneralizedLrParser.new(@@parse_table537586004)
  end
end
