"""
Uses pyflakes to process files and look for pyflakes validation errors.


"""

import _ast
import atexit
import json
import os
import sys


from pyflakes.scripts import pyflakes
from pyflakes import checker


MEMORY = {}


def save_memory():
    if MEMORY:
        with open("memory.json", "w") as memfile:
            json.dump(MEMORY, memfile)

atexit.register(save_memory)


def load_memory():
    global MEMORY
    if os.path.exists("memory.json") and os.stat("memory.json").st_size > 0:
        with open("memory.json", "r") as memfile:
            MEMORY = json.load(memfile)



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


IGNORE, DELETE, REPLACE, CONTINUE = "i", "d", "r", "c"

def prompt():
    input = raw_input("action (ignore/delete/replace/continue): ")
    if input:
        action = input[-1]
        action = action.lower()
        if action in (IGNORE, DELETE, REPLACE, CONTINUE):
            return action
        else:
            return None
    else:
        return None


def updatePath(filename, warnings, warning_db):
    with open(filename, "r") as infile:
        contents = infile.readlines()
    with open("{}.clean".format(filename), "w") as outfile:
        print "updating file: {}".format(filename)
        for warning in warnings:
            print "{}".format(warning)
            print "source: {}".format(contents[warning.lineno - 1])

            message = str(warning).split(":")[-1]

            replacement = ""
            if message in warning_db:
                # get the action from memory
                action, replacement = warning_db[message]
            else:
                # prompt for the action...
                action = prompt()
                while not action:
                    action = prompt()

                if action == REPLACE:
                    replacement = raw_input("replacement: ")

                # and memorize the action:
                warning_db[message] = (action, replacement)

            # perform the action:
            if action == REPLACE:
                line = contents[warning.lineno - 1]
                indent = len(line) - len(line.lstrip())
                contents[warning.lineno - 1] = "{}{}\n".format(
                    " " * indent,
                    replacement
                )
            elif action == IGNORE:
                pass
            elif action == DELETE:
                contents[warning.lineno - 1] = "\n"
            elif action == CONTINUE:
                pass

        # write the modified file out:
        # TODO: overwrite original file
        for line in contents:
            outfile.write(line)

    print warning_db

    #TODO: when we're done debugging
    # check the original file for any further warnings
    #return checkPath(filename)
    return []


def main():
    """
    process a file, directory, or stdin with pyflakes

    Given a file:
     - check with pyflakes
     - run update path if there are warnings until that file is clean

    """
    load_memory()

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
                ws = checkPath(arg)
                while ws:
                    ws = updatePath(arg, ws, MEMORY)
    else:
        # if it's stdin all we can do is print out warnings:
        warnings.extend(check(sys.stdin.read(), '<stdin>'))
        for warning in warnings:
            print warning

    raise SystemExit(warnings > 0)

def g():
    x = 0
    return

def f():
    x = 0
    return


