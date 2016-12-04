#!/usr/bin/env python3
#
# debris.common -- common things for debris autobuild system

import configparser
import subprocess

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
            'DEBRIS_SBUILD_CHROOT_ARCH' : 'amd64',
            'DEBRIS_SBUILD_CHROOT_SUITE' : 'stretch',
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

def run_process(arglist, timeout=None) -> subprocess.CompletedProcess:
    """
    Wrapper for subprocess.run()

    Require python 3.5+
    """
    try:
        result = subprocess.run(
                arglist,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                check=True,
                );
    except subprocess.TimeoutExpired as e:
        # TODO: deal with it
        raise
        return e
    except subprocess.CalledProcessError as e:
        # TODO: deal with it
        raise
        return e
    except:
        raise

    return result