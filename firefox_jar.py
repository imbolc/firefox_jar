'''
firefox_jar
===========
Load firefox cookies to CookieJar (requests compatible format).

Install
-------
    pip install firefox_jar

Usage
-----
    import requests
    from firefox_jar import firefox_jar

    with requests.session() as s:
        s.cookies = firefox_jar()

        r = s.get('http://yandex.ru/')
        assert 'imbolc' in r.text  # check my username on the page
'''
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

__version__ = '0.0.1'

NETSCAPE_SIGN = '''# Netscape HTTP Cookie File
# http://www.netscape.com/newsref/std/cookie_spec.html
# This is a generated file!  Do not edit.
'''


def firefox_jar(firefox_config_dir='~/.mozilla/firefox',
                profile_name='default'):
    dbpath = get_dbpath(firefox_config_dir, profile_name)
    return sqlite_to_jar(dbpath)


def get_dbpath(dirname, name='default'):
    dirname = os.path.expanduser(dirname)
    config = configparser.ConfigParser(allow_no_value=True)
    config.read(os.path.join(dirname, 'profiles.ini'))
    paths = [config.get(s, 'Path') for s in config.sections()
             if config.get(s, 'Name') == name]
    if len(paths) >= 1:
        prof_name = paths[0]
    else:
        prof_name = config.get('Profile0', 'Path')

    profile_dirname = os.path.join(dirname, prof_name)
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
