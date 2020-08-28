r"""
Julia pexpect-based Interface

EXAMPLES::

    TODO

AUTHORS:

- William Stein (2014-10-26)
"""

##########################################################################
#
#       Copyright (C) 2014 William Stein <wstein@gmail.com>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#
#                  http://www.gnu.org/licenses/
#
##########################################################################

import os
import pexpect
import random
import string

from uuid import uuid4

from sage.interfaces.expect import (Expect, ExpectElement, ExpectFunction,
                                    FunctionElement, gc_disabled)
from sage.structure.element import RingElement


def uuid():
    return str(uuid4())


PROMPT_LENGTH = 6


class Julia(Expect):
    def __init__(self,
                 maxread=100000,
                 script_subdirectory=None,
                 logfile=None,
                 server=None,
                 server_tmpdir=None):
        """
        EXAMPLES::

            sage: julia == loads(dumps(julia))
            True
        """
        self._prompt = 'julia> '
        Expect.__init__(self,
                        name='julia',
                        prompt=self._prompt,
                        command="sage-native-execute julia -q",
                        maxread=maxread,
                        server=server,
                        server_tmpdir=server_tmpdir,
                        script_subdirectory=script_subdirectory,
                        restart_on_ctrlc=False,
                        verbose_start=False,
                        logfile=logfile,

                        # If an input is longer than this number of
                        # characters, then try to switch to outputting
                        # to a file.
                        eval_using_file_cutoff=1024)  # TODO: don't need (?)

        self.__seq = 0
        self.__in_seq = 1

    def _start(self):
        """
        """
        pexpect_env = dict(os.environ)
        #pexpect_env['TERM'] = 'vt100'
        # we *use* the codes. DUH.  I should have thought of this 10
        # years ago...

        self._expect = pexpect.spawn(self._Expect__command, logfile=self._Expect__logfile, env=pexpect_env)
        self._expect.delaybeforesend = 0  # not a good idea for a CAS.
        self._expect.expect("julia> ")

    def eval2(self, code, **ignored):
        """
        EXAMPLES::
        """

        START = "\x1b[?2004l\x1b[0m"
        END = "\r\n\r\n\x1b[0G\x1b[0K\x1b[0G\x1b[0Kjulia> "
        if not self._expect:
            self._start()
        from sage.all import walltime
        t = walltime()
        with gc_disabled():
            s = self._expect
            u = uuid()
            line = code + '\n\n\n\n\n__ans__=ans;'
            line += 'println("%s");ans=__ans__;\n' % u
            s.send(line)
            s.expect(u)
            result = s.before
            self._last_result = result
            s.expect(u)
            self._last_result += s.before
            s.expect(u)
            self._last_result += s.before
            i = result.rfind(START)
            if i == -1:
                return result
            result = result[len(START) + i:]
            i = result.find(END)
            if i == -1:
                return result
            result = result[:i]
            if result.startswith("ERROR:"):
                julia_error = result.replace("in anonymous at no file", '')
                raise RuntimeError(julia_error)
            return result

    def _an_element_impl(self):
        """
        EXAMPLES::

            sage: julia._an_element_impl()
            0
        """
        return self(0)

    def _strip_prompt(self, t):
        return t

    def strip_answer(self, s):
        r"""
        Returns the string s with Julia's answer prompt removed.

        EXAMPLES::

        """
        return s

    def set(self, var, value):
        """
        Set the variable var to the given value.

        EXAMPLES::

            sage: julia.set('x', '2')
            sage: julia.get('x')
            '2'

        TEST:

        It must also be possible to eval the variable by name::

            sage: julia.eval('x')
            '2'
        """
        cmd = '%s=%s;' % (var, value)
        out = self.eval(cmd)
        if '***' in out:   # TODO
            raise TypeError("Error executing code in Sage\nCODE:\n\t%s\nSAGE ERROR:\n\t%s" % (cmd, out))

    def get(self, var):
        """
        EXAMPLES::

            sage: julia.set('x', '2')
            sage: julia.get('x')
            '2'
        """
        out = self.eval(var)
        return out

    def _repr_(self):
        """
        EXAMPLES::

            sage: julia
            Julia Interpreter
        """
        return 'Julia Interpreter'

    def __reduce__(self):
        """
        EXAMPLES::

            sage: julia.__reduce__()

        """
        return reduce_load_Julia, tuple([])

    def _function_class(self):
        """
        EXAMPLES::

            sage: julia._function_class()
            <class 'sage.interfaces.julia.JuliaFunction'>
         """
        return JuliaFunction

    def _quit_string(self):
        """
        EXAMPLES::

            sage: julia._quit_string()
            'exit()'

            sage: l = Julia()
            sage: l._start()
            sage: l.quit()
            sage: l.is_running()
            False
        """
        return 'exit()'

    def _read_in_file_command(self, filename):
        """
        EXAMPLES::

            sage: julia._read_in_file_command(tmp_filename()) # TODO
        """

    def trait_names(self):
        """
        EXAMPLES::

            sage: julia.trait_names()
            Traceback (most recent call last):
            ...
            NotImplementedError
        """
        raise NotImplementedError

    def kill(self, var):
        """
        EXAMPLES::

            sage: julia.kill('x')
            Traceback (most recent call last):
            ...
            NotImplementedError
        """
        raise NotImplementedError

    def console(self):
        """
        Spawn a new Julia command-line session.

        EXAMPLES::

            sage: julia.console() #not tested
            ...
        """
        julia_console()

    def julia_version(self):
        """
        Return the version of Julia being used.

        EXAMPLES::

            sage: julia.version()
            12
        """
        return julia_version()

    def _object_class(self):
        """
        EXAMPLES::

            sage: julia._object_class()
            <class 'sage.interfaces.julia.JuliaElement'>
        """
        return JuliaElement

    def _function_class(self):
        """
        EXAMPLES::

            sage: julia._function_class()
            <class 'sage.interfaces.julia.JuliaFunction'>
        """
        return JuliaFunction

    def _function_element_class(self):
        """
        EXAMPLES::

            sage: julia._function_element_class()
            <class 'sage.interfaces.julia.JuliaFunctionElement'>
        """
        return JuliaFunctionElement

    def _true_symbol(self):
        """
        EXAMPLES::

            sage: julia._true_symbol()
            'true'
        """
        return 'true'

    def _false_symbol(self):
        """
        EXAMPLES::

            sage: julia._false_symbol()
            'false'
        """
        return 'false'

    def _equality_symbol(self):
        """
        """
        return "=="

    def help(self, command):
        """
        EXAMPLES::

        """
        if '"' in command:
            raise ValueError('quote in command name')
        return self.eval('help("%s")' % command)

    def function_call(self, function, args=None, kwds=None):
        """
        EXAMPLES::

            sage: julia.function_call('sin', ['2'])
            0.9092974
            sage: julia.sin(2)
            0.9092974
        """
        args, kwds = self._convert_args_kwds(args, kwds)
        self._check_valid_function_name(function)
        function = function.replace("BANG","!")
        return self.new("%s(%s)" % (function,
                                    ",".join([s.name() for s in args])))


class JuliaElement(ExpectElement):
    def __cmp__(self, other):
        """
        EXAMPLES::

            sage: one = julia(1); two = julia(2)
            sage: one == one
            True
            sage: one != two
            True
            sage: one < two
            True
            sage: two > one
            True
            sage: one < 1
            False
            sage: two == 2
            True
        """
        P = self._check_valid()
        if not hasattr(other, 'parent') or P is not other.parent():
            other = P(other)

        if P.eval('%s == %s' % (self.name(), other.name())) == P._true_symbol():
            return 0
        elif P.eval('%s < %s' % (self.name(), other.name())) == P._true_symbol():
            return -1
        else:
            return 1

    def bool(self):
        """
        EXAMPLES::

            sage: julia(2).bool()
            True
            sage: julia(0).bool()
            False
            sage: bool(julia(2))
            True
        """
        P = self._check_valid()
        return P.eval("Bool(%s)" % self.name()) == P._true_symbol()

    def _add_(self, right):
        """
        EXAMPLES::

            sage: a = julia(1); b = julia(2)
            sage: a + b
            3
        """
        P = self._check_valid()
        return P.new('%s + %s' % (self._name, right._name))

    def _sub_(self, right):
        """
        EXAMPLES::

            sage: a = julia(1); b = julia(2)
            sage: a - b
            -1
        """
        P = self._check_valid()
        return P.new('%s - %s' % (self._name, right._name))

    def _mul_(self, right):
        """
        EXAMPLES::

            sage: a = julia(1); b = julia(2)
            sage: a * b
            2
        """
        P = self._check_valid()
        return P.new('%s * %s' % (self._name, right._name))

    def _div_(self, right):
        """
        EXAMPLES::

            sage: a = julia(1); b = julia(2)
            sage: a / b
            1/2
        """
        P = self._check_valid()
        return P.new('%s / %s' % (self._name, right._name))

    def __pow__(self, n):
        """
        EXAMPLES::

            sage: a = julia(3)
            sage: a^3
            27
        """
        P = self._check_valid()
        right = P(n)
        return P.new('%s ^ %s' % (self._name, right._name))


class JuliaFunctionElement(FunctionElement):
    def _sage_doc_(self):
        """
        EXAMPLES::

            sage: two = julia(2)
            sage: two.sin._sage_doc_()
            Traceback (most recent call last):
            ...
            NotImplementedError
        """
        M = self._obj.parent()
        return M.help(self._name)


class JuliaFunction(ExpectFunction):
    def _sage_doc_(self):
        """
        EXAMPLES::

            sage: julia.sin._sage_doc_()
            Traceback (most recent call last):
            ...
            NotImplementedError
        """
        M = self._parent
        return M.help(self._name)


def is_JuliaElement(x):
    """
    EXAMPLES::

        sage: from sage.interfaces.julia import is_JuliaElement
        sage: is_JuliaElement(julia(2))
        True
        sage: is_JuliaElement(2)
        False
    """
    return isinstance(x, JuliaElement)

# An instance
julia = Julia()

def julia_version():
    """
    Return the version of Julia installed.

    EXAMPLES::

        sage: julia_version()    # random; optional - julia
        v"1.5.0"
    """
    return str(julia.versioninfo())



def reduce_load_Julia():
    """
    EXAMPLES::

        sage: from sage.interfaces.julia import reduce_load_Julia
        sage: reduce_load_Julia()
        Julia Interpreter
    """
    return julia


def julia_console():
    """
    Spawn a new Julia command-line session.

    EXAMPLES::

        sage: julia.console() #not tested
        ...
    """
    os.system('julia')
