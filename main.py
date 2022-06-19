import requests
import json
import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtNetwork import QNetworkProxy
from about_dlg import AboutPBrowser
from res_path import res_path, flag_path
from proxy_finder import find_proxies


class PBMainWindow(QMainWindow):
    """Главное окно приложения"""
    htmlFinished = pyqtSignal()
    def __init__(self, *args, **kwargs):
        super(PBMainWindow, self).__init__(*args, **kwargs)
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)
        self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)
        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.create_menu_bar()
        self.proxies = find_proxies()
        self.create_navigation_toolbar()
        self.webrtc_enabled = True
        self.create_privacy_toolbar()
        self.add_new_tab(QUrl(config_data['application']['homepage']), 'Homepage')
        self.update_url_bar(url=QUrl(config_data['application']['homepage']))
        self.setWindowTitle(config_data['application']['name'])
        self.setWindowIcon(QIcon(res_path(('logo_pb.png'))))
        self.show()

    def set_proxy(self, index):
        try:
            sel_proxy = self.proxies[index]
            proxy = QNetworkProxy()
            proxy.setType(QNetworkProxy.HttpProxy)
            proxy.setHostName(sel_proxy[1])
            proxy.setPort(int(sel_proxy[2]))
            QNetworkProxy.setApplicationProxy(proxy)
        except:
            pass

    def create_privacy_toolbar(self):
        privacy_toolbar = QToolBar("Privacy")
        privacy_toolbar.setIconSize(QSize(18, 18))
        self.addToolBar(Qt.LeftToolBarArea, privacy_toolbar)
        proxy_btn = QToolButton(privacy_toolbar)
        proxy_btn.setIcon(QIcon(res_path('ic_priv_location.png')))
        proxy_btn.setStatusTip("Change location")
        proxy_btn.setToolTip("Change location")
        proxy_menu = QMenu()
        no_proxy_item = QAction('Real location', self)
        no_proxy_item.triggered.connect(lambda: self.proxy_clicked(-1))
        proxy_menu.addAction(no_proxy_item)
        proxy_menu.addSeparator()
        for item in range(len(self.proxies)):
            proxy_item = QAction(f'{self.proxies[item][0]}, avg responce {self.proxies[item][3]}s', self)
            proxy_item.triggered.connect(lambda _, index=item: self.proxy_clicked(index))
            proxy_menu.addAction(proxy_item)
        proxy_btn.setMenu(proxy_menu)
        proxy_btn.setPopupMode(QToolButton.MenuButtonPopup)
        self.proxy_btn = privacy_toolbar.addWidget(proxy_btn)
        webrtc_btn = QAction(QIcon(res_path(('ic_priv_eye_on.png'))), "Toggle WebRTC", self)
        webrtc_btn.setStatusTip("Toggle WebRTC & Javascript")
        webrtc_btn.triggered.connect(lambda _, button=webrtc_btn: self.toggle_webrtc(button))
        privacy_toolbar.addAction(webrtc_btn)

    def proxy_clicked(self, index):
        if index == -1:
            QNetworkProxy.setApplicationProxy(QNetworkProxy(QNetworkProxy.DefaultProxy))
        else:
            self.set_proxy(index)

    def toggle_webrtc(self, button):
        if self.webrtc_enabled:
            self.webrtc_enabled = False
            button.setIcon(QIcon(res_path(('ic_priv_eye_off.png'))))
        else:
            self.webrtc_enabled = True
            button.setIcon(QIcon(res_path(('ic_priv_eye_on.png'))))

    def create_navigation_toolbar(self):
        nav_toolbar = QToolBar("Navigation")
        nav_toolbar.setIconSize(QSize(18, 18))
        self.addToolBar(Qt.TopToolBarArea, nav_toolbar)
        back_btn = QAction(QIcon(res_path(('ic_nav_prev.png'))), "Back", self)
        back_btn.setStatusTip("Back to previous page")
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        nav_toolbar.addAction(back_btn)
        next_btn = QAction(QIcon(res_path('ic_nav_next.png')), "Forward", self)
        next_btn.setStatusTip("Forward to next page")
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        nav_toolbar.addAction(next_btn)
        reload_btn = QAction(QIcon(res_path('ic_nav_reload.png')), "Reload", self)
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        nav_toolbar.addAction(reload_btn)
        home_btn = QAction(QIcon(res_path('ic_nav_home.png')), "Home", self)
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        nav_toolbar.addAction(home_btn)
        self.urlbar = QLineEdit()
        self.urlbar.setClearButtonEnabled(True)
        self.urlbar.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.urlbar.returnPressed.connect(self.navigate_to_url)
        nav_toolbar.addWidget(self.urlbar)
        stop_btn = QAction(QIcon(res_path('ic_nav_stop.png')), "Stop", self)
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        nav_toolbar.addAction(stop_btn)

    def create_menu_bar(self):
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)
        file_menu = menu_bar.addMenu('&File')
        new_tab_action = QAction(QIcon(res_path('ic_tab_plus.png')), 'New Tab', self)
        new_tab_action.setStatusTip('Open a new tab')
        new_tab_action.triggered.connect(lambda _: self.add_new_tab())
        file_menu.addAction(new_tab_action)
        file_menu.addSeparator()
        open_file_action = QAction(QIcon(res_path('ic_open_file.png')), 'Open file', self)
        open_file_action.setStatusTip('Open from file')
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)
        save_file_action = QAction(QIcon(res_path('ic_save_file.png')), "Save file", self)
        save_file_action.setStatusTip("Save current page to file")
        save_file_action.triggered.connect(self.save_file)
        file_menu.addAction(save_file_action)
        file_menu.addSeparator()
        exit_app_action = QAction(QIcon(res_path('ic_exit.png')), f'Exit {config_data["application"]["name"]}', self)
        exit_app_action.setStatusTip(f'Exit {config_data["application"]["name"]}')
        exit_app_action.triggered.connect(qApp.quit)
        file_menu.addAction(exit_app_action)
        tools_menu = menu_bar.addMenu("&IP Tools")
        navigate_iplocation_action = QAction(QIcon(res_path('ic_ext_link.png')), "Visit iplocation.net", self)
        navigate_iplocation_action.setStatusTip("Go to iplocation.net page")
        navigate_iplocation_action.triggered.connect(self.navigate_iplocation)
        tools_menu.addAction(navigate_iplocation_action)
        tools_menu.addSeparator()
        navigate_browserleaks_action = QAction(QIcon(res_path('ic_ext_link.png')), "Visit browserleaks.com", self)
        navigate_browserleaks_action.setStatusTip("Go to browserleaks.com page")
        navigate_browserleaks_action.triggered.connect(self.navigate_browserleaks)
        tools_menu.addAction(navigate_browserleaks_action)
        tools_menu.addSeparator()
        navigate_ipleak_action = QAction(QIcon(res_path('ic_ext_link.png')), "Visit ipleak.net", self)
        navigate_ipleak_action.setStatusTip("Go to ipleak.net page")
        navigate_ipleak_action.triggered.connect(self.navigate_ipleak)
        tools_menu.addAction(navigate_ipleak_action)
        help_menu = menu_bar.addMenu("&Help")
        about_action = QAction(QIcon(res_path('ic_about.png')), f"About {config_data['application']['name']}", self)
        about_action.setStatusTip("Show About Info")
        about_action.triggered.connect(self.show_about_dlg)
        help_menu.addAction(about_action)

    def add_new_tab(self, qurl=None, label="Blank"):
        if qurl is None:
            qurl = QUrl('')
        browser = QWebEngineView()
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_url_bar(qurl, browser))
        browser.loadFinished.connect(lambda _, i=i, browser=browser: self.page_load_finished_handler(i, browser))
        browser.loadStarted.connect(lambda: self.page_load_started_handler(browser))

    def page_load_started_handler(self, browser):
        if self.webrtc_enabled:
            browser.settings().setAttribute(QWebEngineSettings.WebAttribute.WebRTCPublicInterfacesOnly, False)
            browser.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        else:
            browser.settings().setAttribute(QWebEngineSettings.WebAttribute.WebRTCPublicInterfacesOnly, True)
            browser.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, False)

    def page_load_finished_handler(self, i, browser):
        self.tabs.setTabText(i, browser.page().title())
        self.tabs.setTabToolTip(i, browser.page().title())
        try:
            favicon = requests.get(f'https://www.google.com/s2/favicons?domain='
                                   f'{self.tabs.widget(i).url().toString()}&sz=16')
            pixmap = QPixmap()
            pixmap.loadFromData(favicon.content)
            tab_icon = QIcon(pixmap)
            self.tabs.setTabIcon(i, QIcon(tab_icon))
        except:
            pass

    def tab_open_doubleclick(self, i):
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        qurl = self.tabs.widget(i).url()
        self.update_url_bar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            return
        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle(f"{title} - {config_data['application']['name']}")

    def navigate_iplocation(self):
        self.tabs.currentWidget().setUrl(QUrl("https://www.iplocation.net/"))

    def navigate_browserleaks(self):
        self.tabs.currentWidget().setUrl(QUrl("https://browserleaks.com/ip"))

    def navigate_ipleak(self):
        self.tabs.currentWidget().setUrl(QUrl("https://ipleak.net/"))

    @staticmethod
    def show_about_dlg():
        dlg = AboutPBrowser()
        dlg.exec_()

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", "", "HTML (*.htm *.html);;" "All files (*.*)")
        if filename:
            with open(filename, 'r') as f:
                html_file = f.read()
            self.tabs.currentWidget().setHtml(html_file)
            self.urlbar.setText(filename)

    def callback(self, html):
        self.mHtml = html
        self.htmlFinished.emit()

    def save_file(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Page", "", "HTML (*.htm *html);;" "All files (*.*)")
        if filename:
            self.tabs.currentWidget().page().toHtml(self.callback)
            loop = QEventLoop()
            self.htmlFinished.connect(loop.quit)
            loop.exec_()
            with open(filename, 'w') as f:
                f.write(self.mHtml)

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl(config_data['application']['homepage']))

    def navigate_to_url(self):
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")
        self.tabs.currentWidget().setUrl(q)

    def update_url_bar(self, url, browser=None):
        if browser != self.tabs.currentWidget():
            return
        if url.scheme() == 'https':
            ssl_icon_path = res_path("ic_ssl_on.png")
        else:
            ssl_icon_path = res_path("ic_ssl_off.png")
        self.urlbar.setStyleSheet(f'background-image: url({ssl_icon_path});\n'
                                  'background-repeat: no-repeat;\n'
                                  'background-position: left;\n'
                                  'padding: 0 0 0 20;\n'
                                  'border: 2px solid #a8a8a8;\n'
                                  'border-radius: 10;\n')
        self.urlbar.setText(url.toString())
        self.urlbar.setCursorPosition(0)

if __name__ == '__main__':
    with open('config.json') as config_file:
        config_data = json.load(config_file)
    private_browser_app = QApplication(sys.argv)
    private_browser_app.setApplicationName(config_data['application']['name'])
    private_browser_app.setApplicationVersion(config_data['application']['version'] +
                                              f"({config_data['application']['build']})")
    private_browser_app.setOrganizationName(config_data['application']['org'])
    private_browser_app.setOrganizationDomain(config_data['application']['url'])
    window = PBMainWindow()
    sys.exit(private_browser_app.exec_())
