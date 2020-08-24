ANTLR4=java -jar /usr/local/lib/antlr-4.8-complete.jar

GRAMMAR_PY=build/grammar/SoLangLexer.py \
build/grammar/SoLang.interp \
build/grammar/SoLang.tokens \
build/grammar/SoLangLexer.interp \
build/grammar/SoLangLexer.tokens \
build/grammar/SoLangParser.py

all: $(GRAMMAR_PY) build/builtin.ll

run: all
	python main.py

clean:
	[ -d build ] && rm -rf build/*
	[ -d __pycache__ ] && rm -rf __pycache__

test: all
	echo "* running main.py"
	echo "write(-2.5+1.2*2);" | python main.py
	llvm-link build/out.ll build/builtin.ll -S -o build/linked.ll
	echo "* running linked.ll by lli (inetrpreter)"
	lli build/linked.ll
	echo "* running another test for 3*(3+5)/4 <LF> 1+2*3"
	echo "write(3*(3+5)/4);write(1);" | python main.py
	llvm-link build/out.ll build/builtin.ll -S -o build/linked.ll
	llc build/linked.ll -o build/linked.s
	clang build/linked.s -o build/linked
	echo "* running native linked"
	build/linked

# generation rules
$(GRAMMAR_PY): grammar/SoLang.g4
	[ -d build ] || mkdir build
	$(ANTLR4) grammar/SoLang.g4 -no-listener -visitor -o build

build/builtin.ll: builtin.c
	[ -d build ] || mkdir build
	clang -emit-llvm -S -O -o build/builtin.ll builtin.c

