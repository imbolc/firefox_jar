'''
firefox_jar
===========
Load firefox cookies to CookieJar (requests compatible format).

Install
-------
    pip install firefox_jar

Usage
-----
    >>> import requests
    >>> from firefox_jar import firefox_jar

    >>> with requests.session() as s:
    ...     s.cookies = firefox_jar()
    ...     r = s.get('http://yandex.ru')
    ...     assert 'imbolc' in r.text  # you should be logged in ff
'''
from __future__ import unicode_literals
import os
import sqlite3
import io
try:
    import cookielib
except ImportError:
    import http.cookiejar as cookielib
try:
    import ConfigParser as configparser
except ImportError:
    import configparser

__version__ = '0.0.2'

NETSCAPE_SIGN = '''# Netscape HTTP Cookie File
# http://www.netscape.com/newsref/std/cookie_spec.html
# This is a generated file!  Do not edit.
'''


def firefox_jar(firefox_config_dir='~/.mozilla/firefox',
                profile_name='default'):
    dbpath = get_dbpath(firefox_config_dir, profile_name)
    return sqlite_to_jar(dbpath)


def get_dbpath(dirname, profile_name='default'):
    dirname = os.path.expanduser(dirname)
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(os.path.join(dirname, 'profiles.ini'))

    for section in config.sections():
        if config.has_option(section, 'Name'):
            if config.get(section, 'Name') == profile_name:
                profile_dirname = config.get(section, 'Path')
                break
    else:
        raise Exception('Profile with name "%s" not found' % profile_name)

    profile_dirname = os.path.join(dirname, profile_dirname)
    return os.path.join(profile_dirname, 'cookies.sqlite')


def sqlite_to_jar(filename):
    '''
    Orig: http://blog.mithis.net/archives/python/94-reading-cookies-firefox
    '''
    con = sqlite3.connect(filename)
    cur = con.cursor()
    cur.execute(
        'select host, path, isSecure, expiry, name, value from moz_cookies'
    )

    ftstr = ['FALSE', 'TRUE']
    s = io.StringIO()
    s.write(NETSCAPE_SIGN)
    for item in cur.fetchall():
        s.write("%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (
            item[0], ftstr[item[0].startswith('.')], item[1],
            ftstr[item[2]], item[3], item[4], item[5]))
    s.seek(0)

    cookie_jar = cookielib.MozillaCookieJar()
    cookie_jar._really_load(s, '', True, True)
    return cookie_jar


if __name__ == "__main__":
    import doctest
    doctest.testmod(verbose=True)
