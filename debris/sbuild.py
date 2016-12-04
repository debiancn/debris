#!/usr/bin/env python3
#
# debris.sbuild -- sbuild handler for debris autobuild system

from . import common
import configparser

from .common import run_process
from .common import getconfig

class SBuilder(object):
    class SBInstance(object):
        """
        The instance to represent the schroot instance.

        Note: self.ready is a bool. True or False or None.
        TODO: use subprocess + communicate() to obtain information.
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
        
        def _update(self):
            """
            Update the instance by calling 'sbuild-update'.

            NOTE: By default, we are modifying the original "source:"-prefixed
            chroot, which means we need permission called source-root-users in
            config file.
            
            Same notice applies to the following methods.
            """
            run_process(['sbuild-update', self.chroot], 1800)
            pass

        def _upgrade(self):
            """
            Call 'sbuild-update --upgrade'.
            """
            run_process(['sbuild-update', '--upgrade', self.chroot], 3600)
            pass

        def _full_upgrade(self):
            """
            Call 'sbuild-update --dist-upgrade'.
            """
            run_process(['sbuild-update', '--dist-upgrade', self.chroot], 3600)
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
            if buildtype == "dsc":
                if self.arch and self.suite:
                    run_process([
                        'sbuild',
                        '--dist={}'.format(self.suite),
                        '--arch={}'.format(self.arch),
                        keyfilepath.dsc,
                        ])
            pass


    def __init__(self, config: configparser.ConfigParser):
        """
        Initialize the Sbuilder object.

        the config prefix: 'DEBRIS_SBUILD'
        """
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

    def buildall():
        """
        Build all packages that need to be built.
        """
        pass
