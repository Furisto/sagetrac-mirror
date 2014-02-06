"""
RPC handling that is common to both Server and Client
"""


from sage.rpc.core.transport import TransportError


TYPE_INIT_CONNECTION = 'init_connection'
TYPE_INIT_REPLY = 'init_reply'
TYPE_REMOTE_LOG = 'rpc_logger'
TYPE_RPC_METHOD_CALL = 'rpc_method_call'


class RemoteProcedureException(TransportError):
    pass



class ProxyCaller(object):
    
    def __init__(self, rpc_caller, rpc_table, prefix=''):
        """
        EXAMPLES::

            sage: from sage.rpc.core.common import ProxyCaller
            sage: def dummy(x): print 'calling "{0}"'.format(x)
            sage: proxy = ProxyCaller(dummy, ['a', 'b', 'c.aa', 'c.bb', 'd.c.b.a'])
            sage: proxy.a()
            calling "a"
            sage: proxy.b()
            calling "b"
            sage: proxy.c.aa()
            calling "c.aa"
            sage: proxy.c.bb()
            calling "c.bb"
            sage: proxy.d.c.b.a()
            calling "d.c.b.a"
        """
        self._rpc_caller = rpc_caller
        self._rpc_table = rpc_table
        self._make(rpc_table, prefix)
        
    def __repr__(self):
        """
        Return a string representation

        EXAMPLES::

            sage: from sage.rpc.core.common import ProxyCaller
            sage: def dummy(x): print 'calling "{0}"'.format(x)
            sage: ProxyCaller(dummy, ['a', 'b', 'c.aa', 'c.bb', 'd.c.b.a'])
            Available RPC calls:
            * a
            * b
            * c.aa
            * c.bb
            * d.c.b.a
        """
        s = 'Available RPC calls:\n'
        s += '\n'.join(['* ' + name for name in sorted(self._rpc_table)])
        return s

    def _make(self, rpc_table, base_prefix):
        table_by_prefix = dict()
        for rpc in rpc_table:
            rpc = rpc.split('.', 1)
            if len(rpc) == 1:
                self._make_caller(rpc[0], base_prefix)
            else:
                prefix, name = rpc
                table = table_by_prefix.get(prefix, [])
                table.append(name)
                table_by_prefix[prefix] = table
        for extra_prefix, table in table_by_prefix.iteritems():
            attr = ProxyCaller(self._rpc_caller, table, base_prefix + '.' + extra_prefix)
            setattr(self, extra_prefix, attr)

    def _make_caller(self, rpc_name, prefix):
        def rpc_call(*args, **kwds):
            name = (prefix + '.' + rpc_name).lstrip('.')
            self._rpc_caller(name, *args, **kwds)
        setattr(self, rpc_name, rpc_call)
            

    
        
class RemoteProcedureCaller(object):

    class UtilsImplementation(object):
    
        def __init__(self, rpc_caller):
            self._rpc_caller = rpc_caller

        def ping(self, count, start_time):
            self._rpc_caller.log.debug('ping #%s', count)
            self._rpc_caller('util.pong', count, start_time)

        def pong(self, count, start_time):
            import time
            elapsed_ms = int(1000*(time.time() - start_time))            
            self._rpc_caller.log.debug('pong #%s (%sms)', count, elapsed_ms)
            print('pong #{0} ({1}ms)'.format(count, elapsed_ms))
    
        def quit(self):
            self._rpc_caller.log.debug('received quit command')
            self._rpc_caller.close()
            import sys
            sys.exit(0)


    def __init__(self, transport, cookie):
        self._rpc_count = 0
        self._ping_count = 0
        self._transport = transport
        self._cookie = cookie
        self._initialized_local_rpc = False
        self._initialized_remote_rpc = False
        self._rpc = None
        self._init_rpc_table()

    def construct_rpc_table(self):
        """
        """
        if self._rpc is not None:
            raise RuntimeError('table must be constructed only once')
        rpc = dict()
        utils = RemoteProcedureCaller.UtilsImplementation(self)
        rpc['util.ping'] = utils.ping
        rpc['util.pong'] = utils.pong
        rpc['util.quit'] = utils.quit
        return rpc

    def _init_rpc_table(self):
        """
        Initialize the list of methods that the remote can call on us.
        """
        self._rpc = self.construct_rpc_table()
        if self._initialized_local_rpc:
            error = 'multiple initialization of local rpc table'
            self.log.critical(error)
            raise RemoteProcedureException(error)
        self._initialized_local_rpc = True

    def _init_remote_rpc(self, rpc_table):
        """
        Construct the ``rpc`` attribute.

        INPUT:

        - ``rpc_table`` -- list of strings.
        """
        for rpc in rpc_table:
            self._validate_name(rpc)
        rpc = ProxyCaller(self, rpc_table)
        setattr(self, 'rpc', rpc)
        if self._initialized_remote_rpc:
            error = 'multiple initialization of remote rpc table'
            self.log.critical(error)
            raise RemoteProcedureException(error)
        self._initialized_remote_rpc = True

    def local_rpc_table(self):
        """
        Return the list of rpc calls that the remote can make on us.
        """
        return self._rpc

    def api_version(self):
        raise NotImplementedError('derived classes must implement the api_version()')

    def check_api_version(self, api_version):
        """
        Verify that the remote api version is sufficient.

        INPUT:

        - ``api_version`` -- the output of :meth:`api_version` on the
          remote end.

        OUTPUT:

        Boolean. If ``False``, the connection will be refused.
        """
        return self.api_version() == api_version

    def _validate_name(self, rpc_name):
        """
        Validate a name as remote procedure name
        
        INPUT:

        - ``rpc_name`` -- string.

        OUTPUT:

        Nothing. A ``ValueError`` is raised if the name is invalid.
        
        EXAMPLES::

            sage: from sage.rpc.core.common import RemoteProcedureCaller
            sage: rpc = RemoteProcedureCaller(None, 'test')
            sage: rpc._validate_name('a-b')
            Traceback (most recent call last):
            ...
            ValueError: contains invalid characters: a-b
            sage: rpc._validate_name('.a')
            Traceback (most recent call last):
            ...
            ValueError: must not start with dot: .a
            sage: rpc._validate_name('a.')
            Traceback (most recent call last):
            ...
            ValueError: must not end with dot: a.
            sage: rpc._validate_name('b..a')
            Traceback (most recent call last):
            ...
            ValueError: separation must be by a single dot: b..a
            sage: rpc._validate_name('abc.3de.org')
            Traceback (most recent call last):
            ...
            ValueError: identifiers must start with a letter: 3de
        """
        import string
        allowed_characters = string.ascii_letters + string.digits + '._'
        if not all (ch in allowed_characters for ch in rpc_name):
            raise ValueError('contains invalid characters: '+rpc_name)
        if rpc_name.startswith('.'):
            raise ValueError('must not start with dot: '+rpc_name)
        if rpc_name.endswith('.'):
            raise ValueError('must not end with dot: '+rpc_name)
        for identifier in rpc_name.split('.'):
            if len(identifier) == 0:
                raise ValueError('separation must be by a single dot: '+rpc_name)
            if identifier[0] not in string.ascii_letters:
                raise ValueError('identifiers must start with a letter: '+identifier)

    def close(self):
        """
        Close down
        """
        try:
            self._transport.close()
        except TransportError:
            pass
        self._rpc = None   # simplify garbage collection
        
    def call(self, cmd, *args, **kwds):
        call = {'type': TYPE_RPC_METHOD_CALL,
                'cmd': cmd,
                'args': args,
                'kwds': kwds,
                'id': self._rpc_count}
        self._transport.write(call)
        self._rpc_count += 1

    __call__ = call

    def ping(self):
        import time
        self('util.ping', self._ping_count, time.time())
        self._ping_count += 1

    def can_handle(self):
        return self._transport.can_read()

    def loop(self, timeout=None):
        """
        One iteration of the main loop

        This method exist mostly for pedagogical reasons, in real
        applications the select call should be integrated into the app
        main loop.

        OUTPUT:

        Boolean. Whether anything was read or written during the loop.
        """
        import select
        rlist, wlist, xlist = self.select_args()
        rlist, wlist, xlist = select.select(rlist, wlist, xlist, timeout)
        if rlist == [] and wlist == [] and xlist == []:
            return False
        return self.select_handle(rlist, wlist, xlist)

    def select_args(self):
        """
        Arguments for a select call
        """
        transport = self._transport
        is_written = transport.is_written(False)
        fd = transport.fileno()
        return ([fd], [] if is_written else [fd], [fd])

    def select_handle(self, rlist, wlist, xlist):
        """
        Handle the result of a select call

        INPUT:

        - ``rlist``, ``wlist``, ``xlist`` -- lists of file
          descriptors. The output of a ``select()`` call.

        OUTPUT:

        Boolean. Whether anything was read or written.
        """
        transport = self._transport
        fd = transport.fileno()
        r = w = 0
        if fd in rlist:
            r = transport.nonblocking_read()
            while transport.can_read():
                self.handle()
        if fd in wlist:
            w = transport.nonblocking_write()
        if fd in xlist:
            # can this happen?
            raise RemoteProcedureException('socket in exception state')
        # print 'select', r,w, rlist, wlist, xlist
        if (r == w == 0) and (fd in rlist+wlist+xlist):
            self.log.debug('Nothing read or written: %s, %s, %s', rlist, wlist, xlist)
        return not(r == w == 0)

    def handle(self):
        """
        Read and deal with request.

        This is the central entry point for handling incomming
        requests.
        """
        msg = self._transport.read()
        # print '***', msg
        return self.handle_msg(msg)

    def handle_msg(self, msg):
        msg_type = msg['type']
        if msg_type == TYPE_RPC_METHOD_CALL:   # most common
            return self.handle_rpc(msg)
        elif msg_type == TYPE_REMOTE_LOG:
            return self.handle_logging(msg)
        elif msg_type == TYPE_INIT_CONNECTION:
            return self.handle_init_connection(msg)
        elif msg_type == TYPE_INIT_REPLY:
            return self.handle_init_reply(msg)
        raise RemoteProcedureException('rpc type {0} does not exist'.format(msg_type))

    def handle_init_connection(self, msg):
        """
        Implementations must call :meth:`_init_remote_rpc`.
        """
        raise RemoteProcedureException('initialization not defined')
        # Derived clasess must obtain the initialize the list of rpc calls
        self._init_remote_rpc(msg['rpc_table'])   # like this, for example

    def handle_init_reply(self, msg):
        """
        Implementations must call :meth:`_init_remote_rpc`.
        """
        raise RemoteProcedureException('initialization reply not defined')
        # Derived clasess must obtain the initialize the list of rpc calls
        self._init_remote_rpc(msg['rpc_table'])   # like this, for example

    def handle_logging(self, log):
        """
        Handle a message that was read in :meth:`handle`.

        Logging is implemented separately from rpc calls so the
        logging mechanism doesn't show up in rpc debug logs.
        """
        level = log['level']
        msg  = log['msg']
        args = log.get('args', ())
        kwds = log.get('kwds', {})
        self.remote_log.log(level, msg, *args, **kwds)

    def handle_rpc(self, msg):
        """
        Handle a message that was read in :meth:`handle`.

        You can override this method to implement custom handlers.
        """
        self.log.debug('rpc call %s', msg)
        if not self._initialized_local_rpc:
            raise RemoteProcedureException('derived class must call RemoteProcedureCaller.__init__()')
        if not self._initialized_remote_rpc:
            raise RemoteProcedureException('RPC call before negotiaton with remote end')
        cmd = msg.get('cmd', None)
        args = msg.get('args', ())
        kwds = msg.get('kwds', {})
        return self.handle_method_call(cmd ,args, kwds)
        
    def handle_method_call(self, cmd, args, kwds):
        """
        Handle a rpc method call.
        """
        try:
            method = self._rpc[cmd]
        except KeyError:
            raise RemoteProcedureException('no RPC command {0} registered'.format(cmd))
        return method(*args, **kwds)
