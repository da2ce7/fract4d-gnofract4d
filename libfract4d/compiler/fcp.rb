require 'rockit/rockit'
module Fc
  # Parser for Fractal
  # created by Rockit version 0.3.8 on Mon May 26 07:44:39 PDT 2003
  # Rockit is copyright (c) 2001 Robert Feldt, feldt@ce.chalmers.se
  # and licensed under GPL
  # but this parser is under LGPL
  tokens = [
    t1 = EofToken.new("EOF",/^(¤~~¤¤~^^~1992010820)/),
    t2 = Token.new("Blank",/^((( )|(\t)|(\v))+)/,:Skip),
    t3 = Token.new("Identifier",/^([A-Z]([A-Z]|\d)*)/),
    t4 = Token.new("Number",/^(\d+)/),
    t5 = Token.new("String",/^("[^\r\n]*")/),
    t6 = Token.new("Newline",/^((\r\n)|(\r)|(\n))/),
    t7 = StringToken.new("StrToken4938446","IF"),
    t8 = StringToken.new("StrToken-348808290","THEN"),
    t9 = StringToken.new("StrToken444258599","ENDIF"),
    t10 = StringToken.new("StrToken601721745","FOR"),
    t11 = StringToken.new("StrToken3923703",":="),
    t12 = StringToken.new("StrToken5682594","TO"),
    t13 = StringToken.new("StrToken-773780254","NEXT"),
    t14 = StringToken.new("StrToken162884623","READ"),
    t15 = StringToken.new("StrToken-948472525","PRINT"),
    t16 = StringToken.new("StrToken984331673","PRINTLN"),
    t17 = StringToken.new("StrToken41","("),
    t18 = StringToken.new("StrToken42",")"),
    t19 = StringToken.new("StrToken764846604","ELSE"),
    t20 = StringToken.new("StrToken61","<"),
    t21 = StringToken.new("StrToken63",">"),
    t22 = StringToken.new("StrToken62","="),
    t23 = StringToken.new("StrToken44","+"),
    t24 = StringToken.new("StrToken46","-"),
    t25 = StringToken.new("StrToken43","*"),
    t26 = StringToken.new("StrToken48","/"),
    t27 = StringToken.new("StrToken661359470","MOD")
  ]
  productions = [
    p1 = Production.new("Statements'".intern,[:Statements],SyntaxTreeBuilder.new("Statements'",["statements"],[])),
    p2 = Production.new(:Statements,[:Plus537628504],SyntaxTreeBuilder.new("Statements",["statements"],[])),
    p3 = Production.new(:Plus537628504,[:Plus537628504, :Statement],ArrayNodeBuilder.new([1],0,nil,nil,[],true)),
    p4 = Production.new(:Plus537628504,[:Statement],ArrayNodeBuilder.new([0],nil,nil,nil,[],true)),
    p5 = Production.new(:Statement,[t7, :Condition, t8, t6, :Statements, t19, t6, :Statements, t9, t6],GroupingSyntaxTreeBuilder.new(5,7,SyntaxTreeBuilder.new("If",["_", "condition", "_", "_", "statements", "optelse", "_", "_"],[]))),
    p6 = Production.new(:Statement,[t7, :Condition, t8, t6, :Statements, t9, t6],SyntaxTreeBuilder.new("If",["_", "condition", "_", "_", "statements", "optelse", "_", "_"],[5])),
    p7 = Production.new(:Statement,[t10, t3, t11, :Expr, t12, :Expr, t6, :Statements, t13, t6],SyntaxTreeBuilder.new("For",["_", "ident", "_", "from", "_", "to", "_", "statements", "_", "_"],[])),
    p8 = Production.new(:Statement,[t14, t3, t6],SyntaxTreeBuilder.new("Read",["_", "ident", "_"],[])),
    p9 = Production.new(:Statement,[t15, :Expr, t6],SyntaxTreeBuilder.new("Print",["_", "message", "_"],[])),
    p10 = Production.new(:Statement,[t15, t5, t6],SyntaxTreeBuilder.new("Print",["_", "message", "_"],[])),
    p11 = Production.new(:Statement,[t16, t6],SyntaxTreeBuilder.new("PrintLn",[],[])),
    p12 = Production.new(:Statement,[t3, t11, :Expr, t6],SyntaxTreeBuilder.new("Assignment",["ident", "_", "expression", "_"],[])),
    p13 = Production.new(:Condition,[:Expr, t20, :Expr],SyntaxTreeBuilder.new("Condition",["left", "op", "right"],[])),
    p14 = Production.new(:Condition,[:Expr, t21, :Expr],SyntaxTreeBuilder.new("Condition",["left", "op", "right"],[])),
    p15 = Production.new(:Condition,[:Expr, t22, :Expr],SyntaxTreeBuilder.new("Condition",["left", "op", "right"],[])),
    p16 = Production.new(:Expr,[t4],LiftingSyntaxTreeBuilder.new([],[])),
    p17 = Production.new(:Expr,[t3],LiftingSyntaxTreeBuilder.new([],[])),
    p18 = Production.new(:Expr,[t17, :Expr, t18],LiftingSyntaxTreeBuilder.new(["_", "expr", "_"],[])),
    p19 = Production.new(:Expr,[:Expr, t23, :Expr],SyntaxTreeBuilder.new("BinExpr",["left", "op", "right"],[])),
    p20 = Production.new(:Expr,[:Expr, t24, :Expr],SyntaxTreeBuilder.new("BinExpr",["left", "op", "right"],[])),
    p21 = Production.new(:Expr,[:Expr, t25, :Expr],SyntaxTreeBuilder.new("BinExpr",["left", "op", "right"],[])),
    p22 = Production.new(:Expr,[:Expr, t26, :Expr],SyntaxTreeBuilder.new("BinExpr",["left", "op", "right"],[])),
    p23 = Production.new(:Expr,[:Expr, t27, :Expr],SyntaxTreeBuilder.new("BinExpr",["left", "op", "right"],[]))
  ]
  relations = [
  
  ]
  priorities = ProductionPriorities.new(relations)
  action_table = [[5, 32768, 9, 512, 13, 16384, 21, 8192, 29, 64, 33, 4], [41, 32], [45, 4], [49, 65536, 53, 16, 61, 8, 65, 4], [2, 1], [69, 4], [12, 134217725], [49, 65536, 61, 8, 65, 4], [81, 1024], [5, 32768, 9, 512, 13, 16384, 21, 8192, 29, 64, 33, 4, 4, 266497], [40, 134217725], [89, 1024], [49, 65536, 61, 8, 65, 4], [97, 32], [101, 67108864, 105, 4194304, 109, 16777216, 113, 32, 117, 33554432, 121, 8388608], [60, 133826720], [64, 133826720], [125, 32], [101, 67108864, 129, 1048576, 133, 2097152, 105, 4194304, 109, 16777216, 117, 33554432, 121, 8388608, 137, 524288], [141, 128], [49, 65536, 61, 8, 65, 4], [8, 134217725], [49, 65536, 61, 8, 65, 4], [101, 67108864, 105, 4194304, 109, 16777216, 153, 131072, 117, 33554432, 121, 8388608], [36, 134217725], [49, 65536, 61, 8, 65, 4], [49, 65536, 61, 8, 65, 4], [49, 65536, 61, 8, 65, 4], [32, 134217725], [49, 65536, 61, 8, 65, 4], [49, 65536, 61, 8, 65, 4], [28, 134217725], [49, 65536, 61, 8, 65, 4], [49, 65536, 61, 8, 65, 4], [49, 65536, 61, 8, 65, 4], [189, 32], [101, 67108864, 105, 4194304, 109, 16777216, 193, 32, 117, 33554432, 121, 8388608], [101, 67108864, 105, 4194304, 109, 16777216, 197, 2048, 117, 33554432, 121, 8388608], [68, 133826720], [101, 67108864, 105, 4194304, 109, 16777216, 117, 33554432, 121, 8388608, 88, 133826592], [101, 67108864, 105, 4194304, 109, 16777216, 117, 33554432, 121, 8388608, 72, 133826592], [101, 67108864, 105, 4194304, 109, 16777216, 117, 33554432, 121, 8388608, 80, 133826592], [101, 67108864, 105, 4194304, 109, 16777216, 117, 33554432, 121, 8388608, 84, 133826592], [101, 67108864, 105, 4194304, 109, 16777216, 117, 33554432, 121, 8388608, 76, 133826592], [101, 67108864, 105, 4194304, 109, 16777216, 117, 33554432, 121, 8388608, 52, 128], [101, 67108864, 105, 4194304, 109, 16777216, 117, 33554432, 121, 8388608, 56, 128], [101, 67108864, 105, 4194304, 109, 16777216, 117, 33554432, 121, 8388608, 48, 128], [5, 32768, 9, 512, 13, 16384, 21, 8192, 29, 64, 33, 4], [44, 134217725], [49, 65536, 61, 8, 65, 4], [209, 256, 213, 262144], [101, 67108864, 105, 4194304, 109, 16777216, 217, 32, 117, 33554432, 121, 8388608], [221, 32], [225, 32], [5, 32768, 9, 512, 13, 16384, 21, 8192, 29, 64, 33, 4], [20, 134217725], [5, 32768, 9, 512, 13, 16384, 21, 8192, 29, 64, 33, 4], [237, 4096], [241, 256], [245, 32], [249, 32], [24, 134217725], [16, 134217725]]
  goto_hash = {49 => {5 => 51}, 27 => {5 => 41}, 33 => {5 => 45}, 22 => {5 => 37}, 0 => {1 => 4, 2 => 9, 3 => 6}, 56 => {1 => 58, 2 => 9, 3 => 6}, 34 => {5 => 46}, 12 => {5 => 23}, 29 => {5 => 42}, 7 => {5 => 18, 4 => 19}, 30 => {5 => 43}, 47 => {1 => 50, 2 => 9, 3 => 6}, 25 => {5 => 39}, 3 => {5 => 14}, 20 => {5 => 36}, 9 => {3 => 21}, 26 => {5 => 40}, 54 => {1 => 57, 2 => 9, 3 => 6}, 32 => {5 => 44}}
  @@parse_table537425404 = ParseTable.new(productions,tokens,priorities,action_table,goto_hash,2,[
    :REDUCE,
    :SHIFT,
    :ACCEPT
  ])
  def Fc.parser
    GeneralizedLrParser.new(@@parse_table537425404)
  end
end
