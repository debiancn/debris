#!/usr/bin/env python3
#
# debris.db -- database-related operations for debris

import sqlite3
import time

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
        log.debug('connection sqlite db: {}'.format(my_dbpath))
        self.conn = sqlite3.connect(my_dbpath)
        self._sanity_check()
        # TODO: Complete me

    def _sanity_check(self):
        """Run a sanity check.

        If there are any missing tables, create them.
        """
        c = self.conn.cursor()
        c.execute('CREATE TABLE IF NOT EXISTS `builtpkg` (`package` TEXT NOT NULL, `version` TEXT NOT NULL);')
        c.execute('CREATE TABLE IF NOT EXISTS `command_history` (`timestamp` INTEGER NOT NULL, `CMDTYPE` TEXT NOT NULL, `OPERATION` TEXT);')
        c.execute('CREATE TABLE IF NOT EXISTS `build_history` (`timestamp` INTEGER NOT NULL, `package` TEXT NOT NULL, `version` TEXTNOT NULL, `status` INTEGER NOT NULL, `stdout` BLOB, `stderr` BLOB);')
# TODO: recheck this
        pass

    def get_builtlist(self) -> list:
        """Retrieve a list for previously built packages.

        :example::
            [{'package': 'nixnote2', 'version': '2.0~beta9-1'},
             {'package': 'qevercloud', 'version': '3.0.3+ds-1'}]
        """
        builtlist = []
        c = self.conn.cursor()
        result = c.execute('SELECT `package`, `version` FROM `builtpkg`;').fetchall()
        for i in result:
            builtlist.append(dict(package=i[0], version=i[1]))
        return builtlist

    def log_transaction(
            self,
            package: str,
            version: str,
            status: bool,
            stdout: bytes = None,
            stderr: bytes = None,
            ):
        """Log one building attempt into the database.
        """
        log.debug('logging build attempt...')
        _current_time = int(time.time())
        c = self.conn.cursor()
        c.execute('INSERT INTO `build_history` (`timestamp`, `package`, `version`, `status`, `stdout`, `stderr`) VALUES (?, ?, ?, ?, ?, ?)', (_current_time, package, version, int(status), stdout, stderr,))
        c.commit()
