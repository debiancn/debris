#!/usr/bin/env python3

"""debris.sbuild -- sbuild handler for debris autobuild system."""

__license__ = "BSD-3-Clause"
__docformat__ = "reStructuredText"

from . import common
import configparser

from .common import run_process
from .common import getconfig
from .common import log

class SBuilder(object):
    class SBInstance(object):
        """
        The instance to represent the schroot instance.

        .. note::
            self.ready is a bool. True or False or None.

        .. todo::
            use subprocess + communicate() to obtain information.
        """
        def __init__(self, CHROOT: str = None, arch: str = None, suite: str = None):
            if CHROOT:
                self.arch = CHROOT.split('-')[1]
                self.suite = CHROOT.split('-')[0]
                self.chroot = CHROOT
            elif not arch or not suite:
                raise Exception('ERR_INVALID_SBInstance')
            else:
                self.arch = arch
                self.suite = suite
                self.chroot = '-'.join(
                        (self.suite,
                         self.arch,
                         getconfig('DEBRIS_SBUILD_CHROOT_SUFFIX', str),
                        ))
            self.ready = None
            log.debug('new SBInstance, chroot: {}, arch: {}, suite: {}'.format(
                    self.chroot,
                    self.arch,
                    self.suite,
                    ))

        def _update(self):
            """
            Update the instance by calling 'sbuild-update'.

            .. note:
                By default, we are modifying the original "source:"-prefixed
                chroot, which means we need permission called source-root-users in
                config file.

            Same notice applies to the following methods.
            """
            log.debug('running sbuild-update (update), chroot: {}'.format(
                    self.chroot,
                    ))
            result = run_process(['sbuild-update', self.chroot], 1800)
            log.debug('finished sbuild-update (update), chroot: {}'.format(
                    self.chroot,
                    ))
            pass

        def _upgrade(self):
            """
            Call 'sbuild-update --upgrade'.
            """
            log.debug('running sbuild-update (upgrade), chroot: {}'.format(
                    self.chroot,
                    ))
            result = run_process(['sbuild-update', '--upgrade', self.chroot], 3600)
            log.debug('finished sbuild-update (upgrade), chroot: {}'.format(
                    self.chroot,
                    ))
            pass

        def _full_upgrade(self):
            """
            Call 'sbuild-update --dist-upgrade'.
            """
            log.debug('running sbuild-update (dist-upgrade), chroot: {}'.format(
                    self.chroot,
                    ))
            result = run_process(['sbuild-update', '--dist-upgrade', self.chroot], 3600)
            log.debug('finished sbuild-update (dist-upgrade), chroot: {}'.format(
                    self.chroot,
                    ))
            pass

        def _dist_upgrade(self):
            return self._full_upgrade()

        def _distupgrade(self):
            return self._full_upgrade()

        def prepare(self):
            """
            Prepare the instance to enter ready state.
            """
            self._update()
            self._full_upgrade()
            pass

        def buildpkg(self, keyfilepath : str, buildtype: str = "dsc"):
            # prefer using arch + suite rather than hardcoded schroot option
            log.info('trying to build pkg, path: {}, type: {}.'.format(
                    keyfilepath,
                    buildtype,
                    ))
            # determine the place to put the packages
            _sbuild_outputdir = getconfig('DEBRIS_SBUILD_OUTPUTDIR')
            if _sbuild_outputdir == None:
                log.critical('PACKAGE OUTPUT DIR NOT SET!')
                raise Exception('ERR_MISSING_DEBRIS_SBUILD_OUTPUTDIR_CONFIG')
            if buildtype == "dsc":
                if self.arch and self.suite:
                    run_process([
                        'sbuild',
                        '--dist={}'.format(self.suite),
                        '--arch={}'.format(self.arch),
                        keyfilepath,
                        ])
            pass


    def __init__(self):
        """
        Initialize the Sbuilder object.

        the config prefix: 'DEBRIS_SBUILD'
        """
        self._chroot_list = []
        self.instances = []
        for i in getconfig('DEBRIS_SBUILD_CHROOT_SUITE', list):
            for j in getconfig('DEBRIS_SBUILD_CHROOT_ARCH', list):
                self._chroot_list.append(
                        '-'.join(
                            [i, j, getconfig('DEBRIS_SBUILD_CHROOT_SUFFIX')]
                            )
                        )
        for i in self._chroot_list:
            self.instances.append(self.SBInstance(CHROOT=i))

#TODO FINISH ME
        pass

    @staticmethod
    def is_firstrun():
        """
        Detect if we should need a firstrun procedure.
        """
        pass
#TODO: finish firstrun detection

    @classmethod
    def firstrun(conflist: list):
        """
        A first-run convenient function to set up working environment.

        The detailed description is from debris.conf.
        """

    def prepare(self):
        """
        Prepare all instances, using sbuild-update.
        """
        log.info('starting to update all chroot instances...')
        for i in self.instances:
            i.prepare()
        log.info('all chroot instances updated.')
        return

    def buildall(self):
        """
        Build all packages that need to be built.
        """
        pass

