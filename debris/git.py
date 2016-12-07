#!/usr/bin/env python3

"""debris.git -- git repo integration on building packages for debris."""

import os

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
from .common import log


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
        self.git.pull() # XXX: replace with wrapper
        self.submodule_update(
                recursive=True,
                force_remove=True,
                force_reset=True,
                keep_going=False,
                )
        self.git.reset('--hard', 'HEAD') # XXX: replace with wrapper
        self.git.submodule('update', '--force')

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
            if should_package:
                log.debug('Needs-Build: {}/{};'.format(i.package, i.version))
                filtered_pkglist.append(i)

        return filtered_pkglist
