"""Ol Browser Login Utility"""
##################################################
# MIT License
##################################################
# File: olbrowserlogin.py
# Description: Overleaf Browser Login Utility
# Author: Moritz Glöckl
# License: MIT
# Version: 1.1.6
##################################################

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
try:
    # Import for pip installation / wheel
    from olsync.olclient import LOGIN_URL,PROJECT_URL
except ImportError:
    # Import for development
    from olclient import LOGIN_URL,PROJECT_URL


# JS snippets to extract the csrfToken
JAVASCRIPT_CSRF_EXTRACTORS = ["document.getElementsByName('ol-csrfToken')[0].content","window.csrfToken"]

# Name of the cookies we want to extract
COOKIE_NAMES = ["overleaf_session2", "GCLB","sharelatex.sid"]


class OlBrowserLoginWindow(QMainWindow):
    """
    Overleaf Browser Login Utility
    Opens a browser window to securely login the user and returns relevant login data.
    """

    def __init__(self, *args, **kwargs):
        super(OlBrowserLoginWindow, self).__init__(*args, **kwargs)

        self.webview = QWebEngineView()

        self._cookies = {}
        self._csrf = ""
        self._login_success = False

        self.profile = QWebEngineProfile(self.webview)
        self.cookie_store = self.profile.cookieStore()
        self.cookie_store.cookieAdded.connect(self.handle_cookie_added)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)

        self.profile.settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)

        webpage = QWebEnginePage(self.profile, self)
        self.webview.setPage(webpage)
        self.webview.load(QUrl.fromUserInput(LOGIN_URL))
        self.webview.loadFinished.connect(self.handle_load_finished)

        self.setCentralWidget(self.webview)
        self.resize(600, 700)

    def handle_load_finished(self):
        
            def callback(result):
                if result is not None:
                    self._csrf = result
                    self._login_success = True
                    QCoreApplication.quit()

            if self.webview.url().toString() == PROJECT_URL:
                for extractor in JAVASCRIPT_CSRF_EXTRACTORS:
                    self.webview.page().runJavaScript(
                        extractor, callback
                    )

                    if self.login_success:
                        break

    def handle_cookie_added(self, cookie):
        cookie_name = cookie.name().data().decode('utf-8')
        if cookie_name in COOKIE_NAMES:
            self._cookies[cookie_name] = cookie.value().data().decode('utf-8')

    @property
    def cookies(self):
        return self._cookies

    @property
    def csrf(self):
        return self._csrf

    @property
    def login_success(self):
        return self._login_success


def login():
    app = QApplication([])
    ol_browser_login_window = OlBrowserLoginWindow()
    ol_browser_login_window.show()
    app.exec()

    if not ol_browser_login_window.login_success:
        return None

    return {"cookie": ol_browser_login_window.cookies, "csrf": ol_browser_login_window.csrf}
