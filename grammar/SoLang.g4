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

prog:   stmt+ ;

stmt:	expr ';'					#exprStmt
	|	ID '=' expr  ';'			#idStmt
	| 	'write' '(' expr ')' ';' 	#writeStmt
	;

expr:	('+'|'-') expr			#unaryExpr
	|	expr ('*'|'/') expr 	#mulDivExpr
    |   expr ('+'|'-') expr 	#addSubExpr
    |   '(' expr ')' 			#parExpr
	|	NUMBER  				#numberExpr
	| 	ID						#idExpr
	;


ID: [a-zA-Z][a-zA-Z0-9_]+ ;
NUMBER: [0-9]+ '.'? [0-9]* ;

NEWLINE: ( '\r' '\n'?
	| '\n'
	) -> skip
	;

WS: [ \t]+ -> skip;
