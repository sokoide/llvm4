import grammar
import antlr4
import sys


def main():
    input = ''.join(sys.stdin.readlines())
    lexer = grammar.SoLangLexer(antlr4.InputStream(input))

    token_stream = antlr4.CommonTokenStream(lexer)
    parser = grammar.SoLangParser(token_stream)

    visitor = grammar.MyVisitor()

    # visit AST nodes
    visitor.visitCompilationUnit(parser.compilationUnit())


if __name__ == '__main__':
    main()
