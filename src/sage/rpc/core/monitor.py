"""
The Monitor Process

The monitor sits between the client (your code trying to perform a
remote computation) and the sage compute server. The monitor is a
separate process so that it does not block while a computation is
running::

    MonitorClient <-> [MonitorServer, MonitoredComputeClient] <-> Sage Compute Server
"""

import os
import sys

from sage.rpc.core.transport import Transport, TransportListen, TransportError
from sage.rpc.core.client_base import ClientBase
from sage.rpc.core.compute_client import ComputeClient
from sage.rpc.core.server_base import ServerBase
from sage.rpc.core.stream_with_marker import StreamWithMarker, StreamStoppedException
from sage.rpc.core.decorator import remote_callable


class MonitorClient(ClientBase):
    
    def api_version(self):
        return 'monitor v1'

    def __init__(self, transport, cookie):
        """
        This is the end-user visible client.

        Your code should use it to make queries to the compute server
        via the monitor, and in return receive callbacks.
        """
        super(MonitorClient, self).__init__(transport, cookie)
        self._label_counter = 0
        self.log.info('MonitorClient started')

    def random_label(self):
        """
        Return a new random label.

        OUTPUT:

        A JSON-serializable value.
        """
        self._label_counter += 1
        return self._label_counter

    def sage_eval(self, code_string, label=None):
        """
        Initiate the evaluation of code
        
        INPUT:

        - ``code_string`` -- string. The code to evaluate.

        - ``label`` -- anything JSON-serializable. A label to attach
          to the compute request. Can be ``None``, in which case one
          is randomly chosen for you. See also :meth:`random_label`.

        OUTPUT:
    
        The label of the compute request. Equals ``label`` if one was
        specified.
        """
        if label is None:
            label = self.random_label()
        self.rpc.sage_eval.start(code_string, label)
        return label

    @remote_callable('sage_eval.result')
    def _impl_sage_eval_result(self, cpu_time, wall_time, label):
        """
        RPC callback when evaluation is finished
        """
        print('Evaluation finished in cpu={0}ms, wall={1}ms'
              .format(int(1000*cpu_time), int(1000*wall_time)))

    @remote_callable('sage_eval.stdin')
    def _impl_sage_eval_stdin(self, label):
        """
        RPC callback when evaluation requests stdin
        """
        self.log.debug('stdin')
        print('Input requested')

    @remote_callable('sage_eval.stdout')
    def _impl_sage_eval_stdout(self, stdout, label):
        """
        RPC callback when evaluation produces stdout
        """
        self.log.debug('stdout %s', stdout.strip())
        print('STDOUT ' + stdout)

    @remote_callable('sage_eval.stderr')
    def _impl_sage_eval_stderr(self, stderr, label):
        """
        RPC callback when evaluation produces stderr
        """
        self.log.debug('stderr %s', stderr.strip())
        print('STDERR ' + stderr)

    @remote_callable('sage_eval.crash')
    def _impl_sage_eval_crash(self, label):
        """
        RPC callback when the compute server crashed
        """
        print('Compute server crashed.')

    def code_complete(self, code_string, cursor_position, label=None):
        """
        Initiate code completion (tab completion)
        
        INPUT:

        - ``code_string`` -- string. The input source code.

        - ``cursor_position`` -- integer. The cursor position.

        - ``label`` -- anything JSON-serializable. A label to attach
          to the compute request. Can be ``None``, in which case one
          is randomly chosen for you. See also :meth:`random_label`.

        OUTPUT:
    
        The label of the request. Equals ``label`` if one was
        specified.
        """
        if label is None:
            label = self.random_label()
        self.rpc.code_completion.start(code_string, cursor_position, label)
        return label

    @remote_callable('code_completion.finished')
    def _impl_code_completion_finished(self, base, completions, label):
        """
        RPC callback for the tab completion result
        
        INPUT:
        
        - ``base`` -- string. substring of the input string ending at
          the cursor position.

        - ``completions`` -- list of strings. The suggested
          completions (starting with ``base``). 
        """
        self.log.debug('tab completion for %s<tab>', base)
        


class MonitorServer(ServerBase):
    
    def api_version(self):
        return 'monitor v1'

    def __init__(self, monitor, transport, cookie):
        """
        The server half of the monitor
        
        This part connects to the :class:`MonitorClient`.
        """
        self.monitor = monitor
        super(MonitorServer, self).__init__(transport, cookie)
        self.log.info('MonitorServer started')
        print('server', self)

    @remote_callable('sage_eval.start')
    def _impl_sage_eval_start(self, code_string, label):
        self.monitor.server_sage_eval_start(code_string, label)

    @remote_callable('code_completion.start')
    def _impl_code_completion_start(self, code_string, cursor_position, label):
        self.monitor.server_code_completion_start(code_string, cursor_position, label)

    @remote_callable('util.ping')
    def _impl_ping(self, time, label):
        self.log.debug('ping #%s', label)
        self.monitor.server_ping(time, label)

    @remote_callable('util.quit')
    def _impl_quit(self):
        self.monitor.server_quit()


class MonitoredComputeClient(ComputeClient):

    def __init__(self, monitor, transport, cookie):
        """
        The client to the Sage compute server.

        This is part of the Monitor process and connects to the
        compute server.

        It is almost identical to
        :class:`~sage.rpc.core.compute_client.ComputeClient`, except
        that we forward some rpc calls to the :class:`Monitor`.
        """
        self.monitor = monitor
        super(MonitoredComputeClient, self).__init__(transport, cookie)
        from sage.rpc.core.server_base import RemoteProcedureLogger
        self.log = RemoteProcedureLogger(monitor.server, origin='compute')
        self.log.info('MonitoredComputeClient started')

    @remote_callable('sage_eval.finished')
    def _impl_sage_eval_finished(self, cpu_time, wall_time, label):
        self.monitor.client_sage_eval_finished(cpu_time, wall_time, label)

    @remote_callable('code_completion.finished')
    def _impl_code_completion_finished(self, basestr, completions, label):
        self.monitor.client_code_completion_finished(basestr, completions, label)

    @remote_callable('util.pong')
    def _impl_pong(self, time, label):
        self.log.debug('pong #%s', label)
        self.monitor.client_pong(time, label)


 
class Monitor(object):

    def __init__(self, process, server_transport, client_transport, cookie):
        """
        The monitor
        """
        self.server = MonitorServer(self, server_transport, cookie)
        self.client = MonitoredComputeClient(self, client_transport, cookie)
        self.process = process
        self.log = self.server.log
        self.current_label = None
        
    def server_sage_eval_start(self, code_string, label):
        """
        Implementation of the RPC call to start evaluation
        """
        assert self.current_label is None  # no current computation
        self.current_label = label
        self.client.rpc.sage_eval(code_string, label)

    def client_sage_eval_finished(self, cpu_time, wall_time, label):
        """
        Callback when the compute server finished.

        The evaluation might have been successful or ended in an
        error, but at least the compute server did not crash.
        
        We still need to flush the stdout/stderr of the compute
        server. This will then call :meth:`on_end_marker_received`,
        which concludes the computation.
        """
        assert label == self.current_label
        self.process.stop_at(self.client.end_marker)
        self.client.rpc.print_end_marker()
        self._eval_cpu_time = cpu_time
        self._eval_wall_time = cpu_time
        
    def on_end_marker_received(self):
        self.process.stop_at(None)
        self.server.rpc.sage_eval.result(
            self._eval_cpu_time, self._eval_wall_time, self.current_label)        
        self._eval_cpu_time = self._eval_wall_time = None
        self.current_label = None

    def loop(self):
        try:
            crl, cwl, cxl = self.client.select_args()
        except TransportError:
            self.handle_client_disconnect()
        try:
            srl, swl, sxl = self.server.select_args()
        except TransportError:
            self.handle_server_disconnect()
        prl, pwl, pxl = self.process.select_args()
        rlist = srl + crl + prl
        wlist = swl + cwl + pwl
        xlist = sxl + cxl + pxl
        import select
        rlist, wlist, xlist = select.select(rlist, wlist, xlist)
        if rlist == [] and wlist == [] and xlist == []:
            return True   # timeout
        try:
            self.client.select_handle(rlist, wlist, xlist)
        except TransportError:
            self.handle_client_disconnect()
        try:
            self.server.select_handle(rlist, wlist, xlist)
        except TransportError:
            self.handle_server_disconnect()
        self.process.select_handle(self, rlist, wlist, xlist)

    def handle_server_disconnect(self):
        """
        React to the server disconnecting from the user.
        
        Compare with :meth:`handle_client_disconnect`.
        """
        print('Monitor: disconnected, killing subprocess and exiting.')
        try:
            self.client.rpc.util.quit()
            self.client._transport.flush()
            self.process.wait()
            self.client.close()
        except TransportError:
            pass
        sys.exit(0)                    

    def handle_client_disconnect(self):
        """
        React to the client disconnecting from the compute server

        Compare with :meth:`handle_server_disconnect`.
        """
        print('Monitor: Compute server died.')
        self.server.rpc.sage_eval.crash(self.current_label)
        self.server._transport.flush()
        # todo: restart?
        self.process.wait()
        sys.exit(0)                    
        
    def server_ping(self, time, label):
        """
        Implementation of the RPC ping call
        """
        self.client.rpc.util.ping(time, label)

    def client_pong(self, time, label):
        """
        Implementation of the RPC pong response
        """
        self.server.rpc.util.pong(time, label)

    def server_quit(self):
        self.quit()

    def server_code_completion_start(self, code_string, cursor_position, label):
        assert self.current_label is None  # no current computation
        self.current_label = label
        self.client.rpc.code_completion.start(code_string, cursor_position, label)

    def client_code_completion_finished(self, basestr, completions, label):
        assert self.current_label == label
        self.current_label = None
        self.server.rpc.code_completion.finished(basestr, completions, label)

    def quit(self):
        print('monitor quit')
        self.log.debug('quit')
        self.client.rpc.util.quit()
        self.client._transport.flush()
        self.process.wait()
        self.client.close()

        # todo: send a notification to the Client that we are about to close
        self.server.close()
        self.server._transport.flush()
        sys.exit(0)
        
    def need_stdin(self):
        """
        Called by the monitored process if it requests user input
        """
        print('need stdin')
        # self.server.rpc.sage_eval.stdin(self.current_label)

    def got_stdout(self, stdout):
        """
        Called by the monitored process if it produces stderr
        """
        if stdout != '':
            self.server.rpc.sage_eval.stdout(stdout, self.current_label)

    def got_stderr(self, stderr):
        """
        Called by the monitored process if it produces stderr
        """
        if stderr != '':
            self.server.rpc.sage_eval.stderr(stderr, self.current_label)




class MonitoredProcess(object):

    def __init__(self, argv):
        """
        A monitored external process
        
        INPUT:

        - ``argv`` -- list of string.
        """
        self._init_listen()
        self._init_process(argv)
        self.transport().accept()
        self._stdout = StreamWithMarker()
        self._stderr = StreamWithMarker()

    def stop_at(self, end_marker=None):
        self._stdout.stop_at(end_marker)
        self._stderr.stop_at(end_marker)
        
    def is_stopped(self):
        return self._stdout.is_stopped() and self._stderr.is_stopped()

    def _init_listen(self):
        client_uri = 'tcp://localhost:0'
        self._transport = TransportListen(client_uri)

    def _init_process(self, argv):
        t = self.transport()
        self._cmd = [cmd.format(port=t.port(), interface=t.interface())
                     for cmd in argv]
        from subprocess import Popen, PIPE
        self._proc = Popen(self._cmd, stdin=None, stdout=PIPE, stderr=PIPE)
        import fcntl
        for fd in [self._proc.stdout.fileno(), self._proc.stderr.fileno()]:
            fl = fcntl.fcntl(fd, fcntl.F_GETFL)
            fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    def select_args(self):
        proc = self._proc
        fd_out = proc.stdout.fileno()
        fd_err = proc.stderr.fileno()
        return ([fd_out, fd_err], [], [fd_out, fd_err])

    def select_handle(self, monitor, rlist, wlist, xlist):
        proc_stdout, proc_stderr = self._proc.stdout, self._proc.stderr
        fd_out = proc_stdout.fileno()
        fd_err = proc_stderr.fileno()
        if fd_out in rlist:
            buf = self._stdout
            buf.write(proc_stdout.read())
            if not buf.is_stopped():
                monitor.got_stdout(buf.read())
            if self.is_stopped():
                monitor.on_end_marker_received()
        if fd_err in rlist:
            buf = self._stderr
            buf.write(proc_stderr.read())
            if not buf.is_stopped():
                monitor.got_stderr(buf.read())
            if self.is_stopped():
                monitor.on_end_marker_received()

    def transport(self):
        return self._transport

    def port(self):
        return self.transport().port()

    def close(self):
        self._proc.kill()
        
    def wait(self):
        self._proc.wait()


def start_monitor(port, interface):
    print('starting monitor process')

    # set up the transport 1: connecting to the client
    uri = 'tcp://{0}:{1}'.format(interface, port)
    transport = Transport(uri)
    transport.connect()

    # set up transport part 2: listen for and launch the compute server
    cmd = ['sage', '-c', 
           'from sage.rpc.compute_server import start_server; '
           'start_server({port}, "{interface}")']
    process = MonitoredProcess(cmd)

    # start up
    cookie = os.environ['COOKIE']
    monitor = Monitor(process, transport, process.transport(), cookie)
    while True:
        # print('monitor loop')
        monitor.loop()
