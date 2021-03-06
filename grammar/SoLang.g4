// Please generate visitor by
// 
// Mac/Linux: alias antlr4=java -jar /path/to/antlr-4.8-complete.jar $*) Win: antlr4.bat contains
// 'java -jar c:\tools\antlr-4.8-complete.jar %*' Then run, antlr4 SoLang.g4 -no-listener -visitor
// -o generated

grammar SoLang;

options {
	language = Python3;
}

compilationUnit: function+;

function: 'int' Ident '(' paramdefs? ')' block;

block: '{' stmt+ '}';

stmt:
	expr ';'					# exprStmt
	| 'int' Ident ';'			# variableDefinitionStmt
	| Ident '=' expr ';'		# asgnStmt
	| if_stmt					# ifStmt
	| 'write' '(' expr ')' ';'	# writeStmt
	| 'return' expr ';'			# returnStmt;

if_stmt: 'if' '(' cond ')' block else_block?;

else_block: elseif_block* 'else' block;

elseif_block: 'else' 'if' block;

cond:
	expr '==' expr
	| expr '!=' expr
	| expr '<=' expr
	| expr '<' expr
	| expr '>=' expr
	| expr '>' expr
	| expr;

expr: ('+' | '-') expr		# unaryExpr
	| expr ('*' | '/') expr	# mulDivExpr
	| expr ('+' | '-') expr	# addSubExpr
	| '(' expr ')'			# parExpr
	| Number				# numberExpr
	| Ident '(' params? ')'	# functionCallExpr
	| Ident					# identExpr;

paramdefs: paramdef | paramdefs ',' paramdef;

paramdef: 'int' Ident;

params: param | params ',' param;

param: expr;

Ident: [a-zA-Z][a-zA-Z0-9_]*;
/* Number: [0-9]+ '.'? [0-9]* ; */
Number: [0-9]+;

Newline: ( '\r' '\n'? | '\n') -> skip;

Whitespace: [ \t]+ -> skip;

BlockComment: '/*' .*? '*/' -> skip;

LineComment: '//' ~[\r\n]* -> skip;
