## -*- encoding: utf-8 -*-
"""
Build Stuff for Doctests
"""

##############################################################################
#  The "git trac ..." command extension for git
#  Copyright (C) 2013  Volker Braun <vbraun.name@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
##############################################################################




POPULATE_GIT_REPO = """
git init .
git config --local --add user.email "committer@example.com"
git config --local --add user.name "Jäne Developer (弄火)"
git config --local --add trac.username trac_user
git config --local --add trac.password trac_pass

# create conflicting branches
echo 'version 0' > file.txt
git add file.txt
git commit -m 'initial commit'
git checkout -q -b branch1
echo 'version branch 1' > file.txt
git add file.txt
git commit -m 'branch 2 is here'
git checkout -q master
git checkout -q -b branch2
echo 'version branch 2' > file.txt
git add file.txt
git commit -m 'branch 2 conflicts branch 1'
git checkout -q master 

# a bunch of branches
echo '123' > foo1.txt && git add . && git commit -m 'initial commit'
git checkout -q -b 'my_branch'
echo '234' > foo2.txt && git add . && git commit -m 'secønd commit'
git checkout -q -b 'u/user/description'
echo '345' > foo3.txt
mv foo2.txt foo2_moved.txt 
git add --all
git commit -m 'third commit'
git checkout -q -b 'u/user/1000/description'
echo '456' > foo4.txt && git add . && git commit -m 'føurth commit'
git checkout -q -b 'u/bob/1001/work'
echo '567' > foo5.txt && git add . && git commit -m 'fifth commit'
git checkout -q -b 'u/alice/1001/work'
mkdir 'bar' && echo '678' > bar/foo6.txt && git add bar && git commit -m 'sixth commit'

# finally, some changes to the working tree
git checkout -q -b 'public/1002/anything'
touch staged_file && git add staged_file
echo 'another line' >> foo4.txt
touch untracked_file
"""

import os
import tempfile
import shutil
import atexit

try: 
    from subprocess import check_output
except ImportError:
    from git_trac.py26_compat import check_output

temp_dirs = []

@atexit.register
def delete_temp_dirs():
    global temp_dirs
    for temp_dir in temp_dirs:
        # print 'deleting '+temp_dir
        shutil.rmtree(temp_dir)


class GitRepoBuilder(object):
    
    def make_repo(self, verbose, user_email_set):
        from git_trac.git_repository import GitRepository
        repo = GitRepository(verbose=verbose)
        repo.git._user_email_set = user_email_set
        return repo

    def make_trac(self):
        from git_trac.app import Application
        return Application().trac

    def _make_fake_remote(self, temp_dir):
        self.trac_remote = os.path.abspath(os.path.join(temp_dir, 'trac_remote'))
        try:
            cwd = os.getcwd()
            os.mkdir(self.trac_remote)
            os.chdir(self.trac_remote)
            for line in POPULATE_GIT_REPO.splitlines():
                check_output(line, shell=True)
        finally:
            os.chdir(cwd)

    def reset_repo(self):
        """
        Return a newly populated git repository
        """
        try:
            cwd = os.getcwd()
            shutil.rmtree(self.repo_path, ignore_errors=True)
            os.mkdir(self.repo_path)
            os.chdir(self.repo_path)
            for line in POPULATE_GIT_REPO.splitlines():
                check_output(line, shell=True)
            check_output('git remote add trac file://' + self.trac_remote, shell=True)
        finally:
            os.chdir(cwd)

    def setUp(self):
        temp_dir = tempfile.mkdtemp()
        global temp_dirs
        temp_dirs.append(temp_dir)
        self._make_fake_remote(temp_dir)
        self.repo_path = os.path.abspath(os.path.join(temp_dir, 'git_repo'))
        self.reset_repo()
        self.old_cwd = os.getcwd()
        os.chdir(self.repo_path)
        # print('set up test repo ' + self.repo_path)

    def tearDown(self):
        os.chdir(self.old_cwd)
