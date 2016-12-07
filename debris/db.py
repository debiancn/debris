#!/usr/bin/env python3
#
# debris.db -- database-related operations for debris

import sqlite3

from . import common
from .common import run_process
from .common import getconfig
from .common import log


class DebrisDB(object):
    """Object that can represent the database connection.

    We are using sqlite3 as db.
    """

    conn = None

    def __init__(self, dbpath: str = None):
        """Init the DebrisDB object.

        By default, the dbpath is given by loading config.
        """
        if dbpath:
            my_dbpath = dbpath
        else:
            my_dbpath = getconfig('DEBRIS_DB_FILE')
        self.conn = sqlite3.connect(my_dbpath)
        # TODO: Complete me

    def _sanity_check(self):
        """Run a sanity check.

        If there are any missing tables, create them.
        """
        c = self.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS `builtpkg` (`package` TEXT, `version` TEXT);')
        c.execute('CREATE TABLE IF NOT EXISTS `command_history` (`timestamp` INTEGER, `CMDTYPE` TEXT, `OPERATION` TEXT);')
# TODO: recheck this
        pass

    def get_builtlist(self) -> list:
        """Retrieve a list for previously built packages.

        :example::
            [{'package': 'nixnote2', 'version': '2.0~beta9-1'},
             {'package': 'qevercloud', 'version': '3.0.3+ds-1'}]
        """
        builtlist = []
        c = self.cursor()
        result = c.execute('SELECT * FROM `builtpkg`;').fetchall()
# TODO: finish me
        return builtlist
        pass
# TODO FIXME
