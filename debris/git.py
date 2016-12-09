#!/usr/bin/env python3

"""debris.git -- git repo integration on building packages for debris."""

import os
import tempfile

import apt
from apt import apt_pkg
import git
import debian
import debian.changelog
from debian.changelog import Changelog


from git import Repo
from . import common
from .common import run_process
from .common import getconfig
from .common import log, flags


class DebrisRepo(Repo):
    """
    An object representation for given git repository that contains subprojects.

    We should keep all submodules updated
    """

    class PkgRepo(object):
        """Contains information of submodule-like source package.
        """

        repo = None
        _changelog = None
        package = None
        version = None

        def __init__(self, repo: Repo):
            self.repo = repo
            self._changelog = Changelog(
                    open(
                        os.path.join(
                            repo.working_dir, 'debian/changelog'
                            )
                        ).read()
                    )
            self.package = str(self._changelog.package)
            self.version = str(self._changelog.get_version())


    def __init__(self, *args, **kwargs):
        """Init with the git repo at given path.

        * type I: firstrun
          - git clone.
          - git submodule init (all)
        * type II: update
          - git update (default)
          - update all submodules and init deinit-ed modules.

        .. note: Internet connection is mandatory.
        """
# TODO: determine if the git repo already exist! FIXME
        super().__init__(*args, **kwargs)
        assert not self.bare
        self.debris_cleanup()

    def debris_cleanup(self):
        """Update Git repo from remote.

        The following steps may apply:

          * for all submodules:
            - If already called init, reset to HEAD.
            - If not init, don't touch anything.
          * hard-reset main module to HEAD.
        """
        if 'UPDATE_GIT_REPO' in flags.keys() and flags['UPDATE_GIT_REPO']:
            log.info('pulling git repo from remote...')
            self.git.pull() # XXX: replace with wrapper
            log.info('updating git repo submodules...')
            self.submodule_update(
                    recursive=True,
                    force_remove=True,
                    force_reset=True,
                    keep_going=False,
                    )
        self.git.reset('--hard', 'HEAD') # XXX: replace with wrapper
        self.git.submodule('update', '--force', '--recursive')
        if 'UPDATE_GIT_REPO' in flags.keys() and flags['UPDATE_GIT_REPO']:
            log.info('WORKAROUND: pulling in any pristine-tar branch.')
            _local_pkglist = self.get_pkglist()
            for i in _local_pkglist:
                _local_subrepo = i.repo
                try:
                    _local_subrepo.git.fetch('--tags')
                    _local_subrepo.git.checkout('origin/master', '-b', 'master')
                    _local_subrepo.git.checkout('-')
                except:
                    pass
                try:
                    _local_subrepo.git.checkout('origin/pristine-tar', '-b', 'pristine-tar')
                    _local_subrepo.git.checkout('-')
                except:
                    try:
                        _local_subrepo.git.checkout('upstream/pristine-tar', '-b', 'pristine-tar')
                        _local_subrepo.git.checkout('-')
                    except:
                        log.warn('repo "{}" does not have pristine-tar, ignoring...'.format(i.package))
                    pass
        self.git.reset('--hard', 'HEAD')
        self.git.submodule('update', '--force', '--recursive')

    def get_pkglist(self) -> list:
        """Obtain a list about the information of existing repo.
        """
        pkglist = []
        for i in self.submodules:
            subrepo = i.module()
            pkglist.append(self.PkgRepo(subrepo))
        assert not (pkglist == [])
        return pkglist

    def get_todo_pkglist(self, builtlist: list) -> list:
        """Deal with external information about built packages.

        Return filtered pkglist."""
        original_pkglist = self.get_pkglist()
        filtered_pkglist = []
        for i in original_pkglist:
            package_exist = False
            should_package = False
            repo_package = i.package
            repo_version = i.version
            for j in builtlist:
                if j['package'] == repo_package:
                    package_exist = True
                    if apt_pkg.version_compare(repo_version, j['version']) > 0:
                        "an outdated package exist."
                        should_package = True
            if not package_exist:
                should_package = True

            if 'ONLY_BUILD' in flags:
               if repo_package == flags['ONLY_BUILD']:
                    should_package = True
               else:
                    should_package = False

            if should_package:
                log.info('Needs-Build: {}/{};'.format(i.package, i.version))
                filtered_pkglist.append(i)

        return filtered_pkglist


class ClonedRepoContext(object):
    """A special object to act as the ContextManager for building environment.

    All building process should be inside the directory represented by this
    context manager object. By default, the building dir should be in /tmp.

    Entering will also chdir.

    /
    |
    -- ..
    |
    -- tmp
       |
       --- ...
       |
       --- debris_XXXXXXX
           |
           --- package_1_gitdir
           |   |
           |   --- debian/
           |   |
           |   --- ...
           |
           --- package_2_gitdir
           |   |
           |   --- debian/
           |   |
           |   --- ...
           |
           --- ...
    """

    def __init__(self, orig_repo: DebrisRepo, todo_list: list, blacklisted_packages: list = []):
        self.orig_repo = orig_repo
        self.todo_list = todo_list
        self.cloned_repo_list = []
        self.tmpdir = tempfile.TemporaryDirectory(prefix='debris_')
        self.path = self.tmpdir.name
        self.blacklisted_packages = blacklisted_packages
        self._old_cwd = os.getcwd()
        log.debug('generating building tmpdir: {}'.format(self.tmpdir))

    def __enter__(self):
        os.chdir(self.path)
        for i in self.todo_list:
            "clone all the repos in the list into tmpdir."
            if i.package in self.blacklisted_packages:
                continue
            log.debug('cloning {}...'.format(i.package))
            cloned_repo = i.repo.clone(os.path.join(self.path, str(i.package)))
            self.cloned_repo_list.append(cloned_repo)

# XXX: is there guarantee that the cloned one has the absolutely correct checkout?
        return self

    def __exit__(self, type, value, traceback):
        log.debug('cleaning up tmpdir...')
        os.chdir(self._old_cwd)
        self.tmpdir.cleanup()

    def reset(self):
        """Clean up built files; return to completely clean."""
        # go back to topdir
        os.chdir(self.path)
        for i in self.cloned_repo_list:
            i.git.reset('--hard')
            i.git.clean('-df')
            i.git.clean('-Xdf')
        # also remove non-directories in buildpath
        _local_path = self.path
        for i in os.listdir(_local_path):
            _local_filepath = os.path.join(self.path, i)
            if not os.path.isdir(_local_filepath):
                os.unlink(_local_filepath)

def repo_is_debian_native(repo: Repo):
    """Determine if the package is debian native.
    """

    _changelog = Changelog(open(os.path.join(repo.working_dir, 'debian/changelog')).read())
    _version = _changelog.get_version()
    if _version._BaseVersion__debian_revision == None: # XXX: using private member
        return True
    else:
        return False

def _repo_get_changelog(repo: Repo) -> Changelog:
    return Changelog(open(os.path.join(repo.working_dir, 'debian/changelog')).read())

def repo_get_package_name(repo: Repo) -> str:
    _changelog = _repo_get_changelog(repo)
    return _changelog.package

def repo_get_latest_version(repo: Repo) -> str:
    _changelog = _repo_get_changelog(repo)
    return str(_changelog.version)

def repo_get_upstream_tag_version(repo: Repo) -> str:
    """Get the upstream tag version.

    .. note: this is not a upstream version. Epoch is included here.
    """

    _changelog = _repo_get_changelog(repo)
    _version = _changelog.get_version()
    log.debug('full version string is: {}'.format(_version))
    _target_str = ""
    if repo_is_debian_native(repo):
        log.debug('this is native debian package.')
        _target_str = str(_version)
    else:
        log.debug('this is not native debian package, demangling...')
        _local_debian_revision = '-' + _version._BaseVersion__debian_revision
        log.debug('the debian revision is {}'.format(_local_debian_revision))
        _target_str = str(_version).split(str(_local_debian_revision))[0]
    log.debug('final unmangled upstream version is: {}'.format(_target_str))

    "Version mangling according to DEP-14."
    _target_str = _target_str.replace(':', '%').replace('~', '_')
    while '..' in _target_str:
        _target_str = _target_str.replace('..', '.#.')
    if _target_str[-1] == '.':
        _target_str = _target_str + '#'
    if _target_str[-5:] == '.lock':
        _target_str = _target_str[:-5] + '.#lock'

    return _target_str
