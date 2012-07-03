"""
Uses pyflakes to process files and look for pyflakes validation errors.


"""

import _ast
import os
import sys


from pyflakes.scripts import pyflakes
from pyflakes import checker


def check(codeString, filename):
    try:
        tree = compile(codeString, filename, "exec", _ast.PyCF_ONLY_AST)
    except SyntaxError as value:
        msg = value.args[0]
        (lineno, offset, text) = value.lineno, value.offset, value.text

        if text is None:
            print >>sys.stderr, "%s: problem decoding source"%(filename,)
        else:
            line = text.splintlines()[-1]
            if offset is not None:
                offset = offset - (len(text) - len(line))
            print >>sys.stderr, "%s:%d: %s"%(filename, lineno, msg)
            print >>sys.stderr, line

            if offset is not None:
                print >>sys.stderr, " " * offset, "^"
        raise
    else:
        w = checker.Checker(tree, filename)
        w.messages.sort(key=lambda msg: msg.lineno)
        return w.messages


def checkPath(filename):
    try:
        return check(file(filename, "U").read() + "\n", filename)
    except IOError, msg:
        print >>sys.stderr, "%s: %s"%(filename, msg.args[1])
        return []


def main():
    warnings = []
    args = sys.argv[1:]

    if args:
        for arg in args:
            if os.path.isdir(arg):
                for dirpath, dirnames, filenames in os.walk(arg):
                    for filename in filenames:
                        if filename.endswith('.py'):
                            ws = checkPath(os.path.join(dirpath, filename))
                            warnings.extend(ws)
            else:
                warnings.extend(checkPath(arg))
    else:
        warnings.extend(check(sys.stdin.read(), '<stdin>'))

    for warning in warnings:
        print warning

    raise SystemExit(warnings > 0)


def f():
    x = 0
    return


