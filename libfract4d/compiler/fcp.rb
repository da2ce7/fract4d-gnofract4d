require 'rockit/rockit'
module Fc
  # Parser for Fractal
  # created by Rockit version 0.3.8 on Mon May 26 09:45:25 PDT 2003
  # Rockit is copyright (c) 2001 Robert Feldt, feldt@ce.chalmers.se
  # and licensed under GPL
  # but this parser is under LGPL
  tokens = [
    t1 = EofToken.new("EOF",/^(¤~~¤¤~^^~8525025127)/),
    t2 = Token.new("Comment",/^(;[^\r\n]*)/,:Skip),
    t3 = Token.new("Blank",/^((( )|(\t)|(\v))+)/,:Skip),
    t4 = Token.new("Identifier",/^([A-Z]([A-Z]|\d)*)/),
    t5 = Token.new("Number",/^(\d+)/),
    t6 = Token.new("String",/^("[^\r\n]*")/),
    t7 = Token.new("Newline",/^((\r\n)|(\r)|(\n))/),
    t8 = Token.new("FormulaID",/^([^\(\) \t\v{}]+)/),
    t9 = StringToken.new("StrToken126","{"),
    t10 = StringToken.new("StrToken128","}"),
    t11 = StringToken.new("StrToken41","("),
    t12 = StringToken.new("StrToken42",")"),
    t13 = StringToken.new("StrToken-834773728","init"),
    t14 = StringToken.new("StrToken59",":"),
    t15 = StringToken.new("StrToken-692607890","loop"),
    t16 = StringToken.new("StrToken401247375","bailout"),
    t17 = StringToken.new("StrToken-701478559","default"),
    t18 = StringToken.new("StrToken227196369","param"),
    t19 = StringToken.new("StrToken326923001","endparam"),
    t20 = StringToken.new("StrToken62","="),
    t21 = StringToken.new("StrToken127","|"),
    t22 = StringToken.new("StrToken61","<"),
    t23 = StringToken.new("StrToken63",">"),
    t24 = StringToken.new("StrToken4059001","<="),
    t25 = StringToken.new("StrToken4194298",">="),
    t26 = StringToken.new("StrToken2232478","!="),
    t27 = StringToken.new("StrToken44","+"),
    t28 = StringToken.new("StrToken46","-"),
    t29 = StringToken.new("StrToken43","*"),
    t30 = StringToken.new("StrToken48","/"),
    t31 = StringToken.new("StrToken38","%")
  ]
  productions = [
    p1 = Production.new("Formulas'".intern,[:Formulas],SyntaxTreeBuilder.new("Formulas'",["formulas"],[])),
    p2 = Production.new(:Formulas,[:Plus537776074],SyntaxTreeBuilder.new("Formulas",["formulas"],[])),
    p3 = Production.new(:Plus537776074,[:Plus537776074, :Formula],ArrayNodeBuilder.new([1],0,nil,nil,[],true)),
    p4 = Production.new(:Plus537776074,[:Formula],ArrayNodeBuilder.new([0],nil,nil,nil,[],true)),
    p5 = Production.new(:Formula,[:FormulaName, t9, t7, :FormulaBody, t10],SyntaxTreeBuilder.new("Formula",["name", "_", "_", "body", "_"],[])),
    p6 = Production.new(:Formula,[t7],SyntaxTreeBuilder.new("Formula",["c1"],[])),
    p7 = Production.new(:FormulaName,[t8],SyntaxTreeBuilder.new("FormID",["name"],[])),
    p8 = Production.new(:FormulaName,[t8, t11, t4, t12],SyntaxTreeBuilder.new("FormID",["name", "_", "id"],[])),
    p9 = Production.new(:FormulaBody,[:Plus537763174],SyntaxTreeBuilder.new("FormulaBody",["sections"],[])),
    p10 = Production.new(:Plus537763174,[:Plus537763174, :Section],ArrayNodeBuilder.new([1],0,nil,nil,[],true)),
    p11 = Production.new(:Plus537763174,[:Section],ArrayNodeBuilder.new([0],nil,nil,nil,[],true)),
    p12 = Production.new(:Section,[t13, t14, t7, :Statements],SyntaxTreeBuilder.new("Section",["name", "_", "_", "statements"],[])),
    p13 = Production.new(:Section,[t15, t14, t7, :Statements],SyntaxTreeBuilder.new("Section",["name", "_", "_", "statements"],[])),
    p14 = Production.new(:Section,[t16, t14, t7, :CondExp],SyntaxTreeBuilder.new("Section",["name", "_", "_", "exp"],[])),
    p15 = Production.new(:Section,[t17, t14, t7, :Defstatements],SyntaxTreeBuilder.new("Section",["name", "_", "_", "statements"],[])),
    p16 = Production.new(:Defstatements,[:Plus537747804],SyntaxTreeBuilder.new("Defstatements",["defstatements"],[])),
    p17 = Production.new(:Plus537747804,[:Plus537747804, :Defstatement],ArrayNodeBuilder.new([1],0,nil,nil,[],true)),
    p18 = Production.new(:Plus537747804,[:Defstatement],ArrayNodeBuilder.new([0],nil,nil,nil,[],true)),
    p19 = Production.new(:Defstatement,[:Setting],LiftingSyntaxTreeBuilder.new([],[])),
    p20 = Production.new(:Defstatement,[t18, t4, t7, :Settings],SyntaxTreeBuilder.new("Defstatement",["c1", "identifier", "newline", "settings"],[])),
    p21 = Production.new(:Defstatement,[t19, t7],SyntaxTreeBuilder.new("Param",["_", "id", "_", "settings", "_", "_"],[])),
    p22 = Production.new(:Settings,[:Plus537739504],SyntaxTreeBuilder.new("Settings",["settings"],[])),
    p23 = Production.new(:Plus537739504,[:Plus537739504, :Setting],ArrayNodeBuilder.new([1],0,nil,nil,[],true)),
    p24 = Production.new(:Plus537739504,[:Setting],ArrayNodeBuilder.new([0],nil,nil,nil,[],true)),
    p25 = Production.new(:Setting,[t4, t20, :Value, t7],SyntaxTreeBuilder.new("Setting",["id", "_", "value", "_"],[])),
    p26 = Production.new(:Value,[t6],LiftingSyntaxTreeBuilder.new([],[])),
    p27 = Production.new(:Value,[:Exp],LiftingSyntaxTreeBuilder.new([],[])),
    p28 = Production.new(:Statements,[:Plus537730444],SyntaxTreeBuilder.new("Statements",["statements"],[])),
    p29 = Production.new(:Plus537730444,[:Plus537730444, :Statement],ArrayNodeBuilder.new([1],0,nil,nil,[],true)),
    p30 = Production.new(:Plus537730444,[:Statement],ArrayNodeBuilder.new([0],nil,nil,nil,[],true)),
    p31 = Production.new(:Statement,[t4, t20, :Exp, t7],SyntaxTreeBuilder.new("Assignment",["id", "_", "exp", "_"],[])),
    p32 = Production.new(:CondExp,[:Exp, t22, :Exp],SyntaxTreeBuilder.new("Condition",["left", "op", "right"],[])),
    p33 = Production.new(:CondExp,[:Exp, t23, :Exp],SyntaxTreeBuilder.new("Condition",["left", "op", "right"],[])),
    p34 = Production.new(:CondExp,[:Exp, t20, :Exp],SyntaxTreeBuilder.new("Condition",["left", "op", "right"],[])),
    p35 = Production.new(:CondExp,[:Exp, t24, :Exp],SyntaxTreeBuilder.new("Condition",["left", "op", "right"],[])),
    p36 = Production.new(:CondExp,[:Exp, t25, :Exp],SyntaxTreeBuilder.new("Condition",["left", "op", "right"],[])),
    p37 = Production.new(:CondExp,[:Exp, t26, :Exp],SyntaxTreeBuilder.new("Condition",["left", "op", "right"],[])),
    p38 = Production.new(:Exp,[t5],LiftingSyntaxTreeBuilder.new([],[])),
    p39 = Production.new(:Exp,[t4],LiftingSyntaxTreeBuilder.new([],[])),
    p40 = Production.new(:Exp,[t11, :Exp, t12],LiftingSyntaxTreeBuilder.new(["_", "expr", "_"],[])),
    p41 = Production.new(:Exp,[t21, :Exp, t21],SyntaxTreeBuilder.new("UnExp",["op", "exp", "_"],[])),
    p42 = Production.new(:Exp,[:Exp, t27, :Exp],SyntaxTreeBuilder.new("BinExp",["left", "op", "right"],[])),
    p43 = Production.new(:Exp,[:Exp, t28, :Exp],SyntaxTreeBuilder.new("BinExp",["left", "op", "right"],[])),
    p44 = Production.new(:Exp,[:Exp, t29, :Exp],SyntaxTreeBuilder.new("BinExp",["left", "op", "right"],[])),
    p45 = Production.new(:Exp,[:Exp, t30, :Exp],SyntaxTreeBuilder.new("BinExp",["left", "op", "right"],[])),
    p46 = Production.new(:Exp,[:Exp, t31, :Exp],SyntaxTreeBuilder.new("BinExp",["left", "op", "right"],[]))
  ]
  relations = [
  
  ]
  priorities = ProductionPriorities.new(relations)
  action_table = [[5, 128, 25, 64], [29, 1024, 24, 256], [5, 128, 25, 64, 4, 1], [2, 1], [37, 256], [12, 2147483641], [20, 2147483641], [41, 8], [8, 2147483641], [45, 64], [49, 2048], [53, 16384, 57, 4096, 61, 32768, 73, 65536], [28, 256], [81, 8192], [85, 8192], [89, 8192], [53, 16384, 57, 4096, 61, 32768, 73, 65536, 32, 512], [40, 2147483256], [97, 8192], [101, 512], [105, 64], [109, 64], [113, 64], [36, 2147483256], [117, 64], [16, 2147483641], [133, 8], [133, 8], [141, 1024, 153, 16, 157, 1048576, 161, 8], [181, 262144, 185, 8, 189, 131072], [133, 8, 108, 2147483256], [48, 2147483256], [116, 2147483256], [197, 524288], [44, 2147483256], [141, 1024, 153, 16, 157, 1048576, 161, 8], [52, 2147483256], [205, 4194304, 209, 524288, 213, 67108864, 217, 33554432, 221, 8388608, 225, 268435456, 229, 1073741824, 233, 536870912, 237, 134217728, 241, 2097152, 245, 16777216], [148, 2147483256], [141, 1024, 153, 16, 157, 1048576, 161, 8], [152, 2147483256], [68, 2147483256], [56, 2147483256], [181, 262144, 185, 8, 189, 131072, 60, 2147483256], [72, 2147483256], [257, 64], [261, 524288], [265, 8], [112, 2147483256], [141, 1024, 153, 16, 157, 1048576, 161, 8], [213, 67108864, 225, 268435456, 273, 2048, 229, 1073741824, 233, 536870912, 237, 134217728], [141, 1024, 153, 16, 157, 1048576, 161, 8], [141, 1024, 153, 16, 157, 1048576, 161, 8], [141, 1024, 153, 16, 157, 1048576, 161, 8], [141, 1024, 153, 16, 157, 1048576, 161, 8], [141, 1024, 153, 16, 157, 1048576, 161, 8], [141, 1024, 153, 16, 157, 1048576, 161, 8], [141, 1024, 153, 16, 157, 1048576, 161, 8], [141, 1024, 153, 16, 157, 1048576, 161, 8], [141, 1024, 153, 16, 157, 1048576, 161, 8], [141, 1024, 153, 16, 157, 1048576, 161, 8], [141, 1024, 153, 16, 157, 1048576, 161, 8], [213, 67108864, 225, 268435456, 229, 1073741824, 233, 536870912, 237, 134217728, 321, 1048576], [64, 2147483256], [80, 2147483256], [141, 1024, 325, 32, 153, 16, 157, 1048576, 161, 8], [337, 64], [213, 67108864, 225, 268435456, 229, 1073741824, 233, 536870912, 237, 134217728, 341, 64], [156, 2147483256], [213, 67108864, 225, 268435456, 229, 1073741824, 233, 536870912, 237, 134217728, 128, 2147483256], [213, 67108864, 225, 268435456, 229, 1073741824, 233, 536870912, 237, 134217728, 132, 2147483256], [213, 67108864, 225, 268435456, 229, 1073741824, 233, 536870912, 237, 134217728, 164, 2146961472], [213, 67108864, 225, 268435456, 229, 1073741824, 233, 536870912, 237, 134217728, 144, 2147483256], [213, 67108864, 225, 268435456, 229, 1073741824, 233, 536870912, 237, 134217728, 136, 2147483256], [213, 67108864, 225, 268435456, 229, 1073741824, 233, 536870912, 237, 134217728, 172, 2146961472], [213, 67108864, 225, 268435456, 229, 1073741824, 233, 536870912, 237, 134217728, 180, 2146961472], [213, 67108864, 225, 268435456, 229, 1073741824, 233, 536870912, 237, 134217728, 176, 2146961472], [213, 67108864, 225, 268435456, 229, 1073741824, 233, 536870912, 237, 134217728, 168, 2146961472], [213, 67108864, 225, 268435456, 229, 1073741824, 233, 536870912, 237, 134217728, 124, 2147483256], [213, 67108864, 225, 268435456, 229, 1073741824, 233, 536870912, 237, 134217728, 140, 2147483256], [160, 2147483256], [100, 64], [213, 67108864, 225, 268435456, 229, 1073741824, 233, 536870912, 237, 134217728, 104, 64], [345, 64], [185, 8], [120, 2147483256], [96, 2147483256], [76, 2147483256], [92, 2147483256], [185, 8, 84, 2147483256], [88, 2147483256]]
  goto_hash = {60 => {19 => 78}, 49 => {19 => 67}, 27 => {16 => 30, 17 => 32, 15 => 34}, 16 => {7 => 23}, 55 => {19 => 73}, 11 => {5 => 19, 6 => 16, 7 => 17}, 0 => {1 => 3, 2 => 2, 3 => 5, 4 => 4}, 61 => {19 => 79}, 39 => {19 => 62}, 28 => {18 => 36, 19 => 37}, 89 => {13 => 90}, 56 => {19 => 74}, 84 => {11 => 87, 12 => 89, 13 => 88}, 51 => {19 => 69}, 29 => {13 => 44, 8 => 42, 9 => 43, 10 => 41}, 57 => {19 => 75}, 35 => {19 => 50}, 2 => {3 => 8, 4 => 4}, 52 => {19 => 70}, 30 => {17 => 48}, 58 => {19 => 76}, 53 => {19 => 71}, 59 => {19 => 77}, 26 => {16 => 30, 17 => 32, 15 => 31}, 65 => {19 => 82, 14 => 83}, 54 => {19 => 72}, 43 => {13 => 44, 10 => 63}}
  @@parse_table537758424 = ParseTable.new(productions,tokens,priorities,action_table,goto_hash,2,[
    :REDUCE,
    :SHIFT,
    :ACCEPT
  ])
  def Fc.parser
    GeneralizedLrParser.new(@@parse_table537758424)
  end
end
