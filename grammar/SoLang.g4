// Please generate visitor by
//
// Mac/Linux: alias antlr4=java -jar /path/to/antlr-4.8-complete.jar $*)
// Win: antlr4.bat contains 'java -jar c:\tools\antlr-4.8-complete.jar %*'
// Then run,
// antlr4 SoLang.g4 -no-listener -visitor -o generated

grammar SoLang;

options {
	language = Python3;
}



compilationUnit:	function+ ;

function: 'int' Ident '(' expr* ')' block ;

block:   '{' stmt+ '}' ;

stmt:	expr ';'					#exprStmt
	|	Ident '=' expr  ';'			#identStmt
	| 	'write' '(' expr ')' ';' 	#writeStmt
	|	'return' expr ';'			#returnStmt
	;

expr:	('+'|'-') expr			#unaryExpr
	|	expr ('*'|'/') expr 	#mulDivExpr
    |   expr ('+'|'-') expr 	#addSubExpr
    |   '(' expr ')' 			#parExpr
	|	Number  				#numberExpr
	| 	Ident '(' ')'			#functionCallExpr
	| 	Ident					#identExpr
	;

Ident: [a-zA-Z][a-zA-Z0-9_]+ ;
/* Number: [0-9]+ '.'? [0-9]* ; */
Number: [0-9]+ ;

Newline: ( '\r' '\n'?
	| '\n'
	) -> skip
	;

Whitespace: [ \t]+ -> skip;

BlockComment
    :   '/*' .*? '*/'
        -> skip
    ;

LineComment
    :   '//' ~[\r\n]*
        -> skip
    ;
