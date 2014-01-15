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