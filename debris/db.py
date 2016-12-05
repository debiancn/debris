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
