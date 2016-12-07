#!/usr/bin/env python3
#
# debris.common -- common things for debris autobuild system

import os
import configparser
import subprocess
import logging
import fcntl

def get_log_verbosity(offset: int, base=1):
    """Get logging verbosity according to verbosity offset.

    The offset is determined by user input in argv.
    The more '-v' given, the larger offset is.
    The more '-q' given, the smaller offset is.

    By default, we set verbosity to show logging.INFO.
    """
    offset_list = [
            logging.DEBUG,
            logging.INFO,
            logging.WARN,
            logging.ERROR,
            logging.CRITICAL,
            ]
    level_select = base - offset
    if level_select < 0:
        level_select = 0
    elif level_select > 4:
        level_select = 4
    return offset_list[level_select]

# init a logger here
def __init_logger() -> logging.Logger:
    # TODO: properly determine logging level
    l = logging.getLogger('debris')
    l.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s %(name)s: %(levelname)s: %(message)s')

    ch.setFormatter(formatter)
    l.addHandler(ch)

    return l

log = __init_logger()

def load_config(filepath: str) -> configparser.ConfigParser:
    """
    load configuration file using configparser.

    return a ConfigParser instance.
    """
    config = configparser.ConfigParser()
    try:
        config.read(filepath)
    except:
        raise
# TODO: exception handler
    return config

def getconfig(config_key: str, returntype: type = str):
    """
    Obtain config information.

    Priority:
     * envvar
     * config file
     * builtin
    """
    BUILTIN_CONFIG = {
            'DEBRIS_DB_FILE' : '/var/cache/debris/history.db',
            'DEBRIS_SBUILD_MIRRORURI' : 'http://ftp2.cn.debian.org/debian',
            'DEBRIS_SBUILD_EXTRAURI' : 'http://repo.debiancn.org/',
            'DEBRIS_SBUILD_OUTPUTDIR' : '/var/cache/debris/output/',
            'DEBRIS_SBUILD_CHROOT_ARCH' : ['amd64',],
            'DEBRIS_SBUILD_CHROOT_SUITE' : ['stretch',],
            'DEBRIS_SBUILD_CHROOT_SUFFIX' : 'sbuild',
            'DEBRIS_SBUILD_CHROOT_TARGET_DIRECTORY_BASE': '/var/cache/debris/',
            'DEBRIS_GIT_REPO_URL' : 'https://github.com/debiancn/repo',
            'DEBRIS_GIT_REPO_LOCAL' : '/home/hosiet/src/debiancn/repo',
            }


    config = BUILTIN_CONFIG
    # TODO: load config file here
    # TODO: load envvar here

    if config_key in config.keys():
        return returntype(config[config_key])
    else:
        raise Exception('ERR_CONFIG_KEY_NOT_RECOGNIZED')

class DebrisGlobalLock(object):
    """A global lock Context Manager class."""

    class DebrisInstanceLockedError(Exception): pass

    def __init__(self, lockfile=os.getenv('HOME')+'/.debris-start.pid'): # XXX: fixme not ideal
        self.lockfile = lockfile
        self.f = None

    def __enter__(self):
        self.f = open(self.lockfile, 'a+')
        self.f.seek(0)
        try:
            fcntl.lockf(self.f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            "Yes, locked by others. Give up."
            raise DebrisInstanceLockedError('fcntl locking failed, path {}, pid {}.'.format(self.lockfile, self.f.read()))
        self.f.write(str(os.getpid()))
        self.f.seek(0)
        pass

    def __exit__(self, type, value, traceback):
        os.unlink(self.f.name)
        fcntl.lockf(self.f.fileno(), fcntl.LOCK_UN)
        self.f.close()

def run_process(arglist, timeout=None) -> subprocess.CompletedProcess:
    """
    Wrapper for subprocess.run()

    Require python 3.5+
    """
    try:
        log.debug('executing subprocess: {}, timeout {}.'.format(
                str(arglist),
                timeout))
        result = subprocess.run(
                arglist,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                check=True,
                );
    except subprocess.TimeoutExpired as e:
        # TODO: deal with it
        log.error('subprocess timed out! Exception: {}.'.format(
                str(e)))
        raise
        return e
    except subprocess.CalledProcessError as e:
        # TODO: deal with it
        log.error('subprocess returned with non-zero! Exception: {}.'.format(
                str(e)))
        raise
        return e
    except Exception as e:
        log.critical('unhandled exception raised! Exception: {}.'.format(
                str(e)))
        raise

    return result


