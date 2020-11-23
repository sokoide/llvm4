#!/usr/bin/env python3
import grammar
import antlr4
import sys
import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='SoLang compiler')
    parser.add_argument('-O', dest='optimize', action='store_true',
                        default=False,
                        help='Optimize genrated IR')
    return parser.parse_args()


def tokenize(source: str) -> antlr4.CommonTokenStream:
    lexer = grammar.SoLangLexer(antlr4.InputStream(source))
    return antlr4.CommonTokenStream(lexer)


def visit(
        args: argparse.Namespace,
        token_stream: antlr4.CommonTokenStream) -> None:
    parser = grammar.SoLangParser(token_stream)
    visitor = grammar.MyVisitor(args)

    # visit AST nodes
    visitor.visitCompilationUnit(parser.compilationUnit())


def main():
    args = parse_args()
    source = ''.join(sys.stdin.readlines())
    token_stream = tokenize(source)
    visit(args, token_stream)


if __name__ == '__main__':
    main()
