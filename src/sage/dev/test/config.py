r"""
Configuration wrapper for doctesting

This module provides a wrapper for ``devrc`` which can be used for doctesting
without tampering with the user's ``devrc`` file.

AUTHORS:

- Julian Rueth: initial version

"""
#*****************************************************************************
#       Copyright (C) 2013 Julian Rueth <julian.rueth@fsfe.org>
#
#  Distributed under the terms of the GNU General Public License (GPL)
#  as published by the Free Software Foundation; either version 2 of
#  the License, or (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************
import sage.dev.config

class DoctestConfig(sage.dev.config.Config):
    r"""
    A :class:`sage.dev.config.Config` which lives in a temporary file and sets
    some sensible defaults for doctesting.

    This also initializes an empty git repository in a temporary directory.

    INPUT:

    - ``trac_username`` -- a string (default: ``'doctest'``), a (fake) username
    on trac

    - ``repository`` - a string or ``None`` (default: ``None``), a remote
    repository to push to and pull from

    EXAMPLES::

        sage: from sage.dev.test.config import DoctestConfig
        sage: DoctestConfig()
        Config('''
        [trac]
        username = doctest
        [UI]
        log_level = 0
        [git]
        repository = remote_repository_undefined
        src = ...
        dot_git = ...
        [sagedev]
        ticketfile = ...
        branchfile = ...
        dependenciesfile = ...
        remotebranchesfile = ...
        ''')

    """
    def __init__(self, trac_username = "doctest", repository=None):
        r"""
        Initialization.

        TESTS::

            sage: from sage.dev.test.config import DoctestConfig
            sage: type(DoctestConfig())
            <class 'sage.dev.test.config.DoctestConfig'>

        """
        import tempfile, atexit, shutil, os
        devrc = tempfile.mkstemp()[1]
        atexit.register(lambda: os.path.exists(devrc) or os.unlink(devrc))

        sage.dev.config.Config.__init__(self, devrc = devrc)

        self['trac'] = {'username': trac_username}
        self['UI'] = {'log_level': 0}
        self['git'] = {}
        self['sagedev'] = {}

        self['git']['repository'] = repository if repository else "remote_repository_undefined"

        self._tmp_dir = tempfile.mkdtemp()
        atexit.register(shutil.rmtree, self._tmp_dir)
        self['git']['src'] = self._tmp_dir
        self['git']['dot_git'] = os.path.join(self._tmp_dir,".git")
        os.mkdir(self['git']['dot_git'])

        self['sagedev']['ticketfile'] = os.path.join(self._tmp_dir,"branch_to_ticket")
        self['sagedev']['branchfile'] = os.path.join(self._tmp_dir,"ticket_to_branch")
        self['sagedev']['dependenciesfile'] = os.path.join(self._tmp_dir,"dependencies")
        self['sagedev']['remotebranchesfile'] = os.path.join(self._tmp_dir,"remote_branches")

        from sage.dev.git_interface import GitInterface
        from sage.dev.test.user_interface import DoctestUserInterface
        old_cwd = os.getcwd()
        os.chdir(self['git']['src'])
        try:
            GitInterface(self['git'], DoctestUserInterface(self["UI"])).silent.init(self['git']['src'])
        finally:
            os.chdir(old_cwd)
