#!/usr/bin/env python3
#
# debris.sbuild -- sbuild handler for debris autobuild system

from . import common
import configparser

class Sbuilder(object):
    class SBInstance(object):
        """
        The instance to represent the schroot instance.

        Note: self.ready is a bool. True or False or None.
        TODO: use subprocess + communicate() to obtain information.
        """
        def __init__(self, path: str, arch: str, suite: str):
            self.path = path
            self.arch = arch
            self.suite = suite
            self.ready = None
        
        def _update(self):
            """
            Update the instance by calling 'sbuild-update'.
            """
            pass

        def _upgrade(self):
            """
            Call 'sbuild-update --upgrade'.
            """
            pass

        def _full_upgrade(self):
            """
            Call 'sbuild-update --dist-upgrade'.
            """
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

        def buildpkg(self, keyfilepath : str, type: str = "dsc"):
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

