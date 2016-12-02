#!/usr/bin/env python3
#
# debris.sbuild -- sbuild handler for debris autobuild system

class Sbuilder(object):
    def __init__(self, definition):
        """
        Initialize the Sbuilder object.

        """
#FIXME: finish the definition.
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

