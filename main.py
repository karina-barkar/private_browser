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
        self.tabs = QTabWidget()                                # Виджет с вкладками страниц браузера
        self.tabs.setDocumentMode(True)
        self.tabs.tabBarDoubleClicked.connect(self.tab_open_doubleclick)    # по двойному клику на пустое место будем
                                                                            # открывать новую вкладку
        self.tabs.currentChanged.connect(self.current_tab_changed)          # обработка изменений в текущей вкладке
        self.tabs.setTabsClosable(True)                                     # табы можно закрывть
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)
        self.status = QStatusBar()                                          # строка статуса пригодится
        self.setStatusBar(self.status)
        self.create_menu_bar()                                              # Создание основного меню
        self.proxies = find_proxies()                                       # вызов функции поиска списка прокси
        self.create_navigation_toolbar()                                    # Один тулбар - для навигации
        self.webrtc_enabled = True
        self.create_privacy_toolbar()                                       # Второй тулбар - анонимности
        self.add_new_tab(QUrl(config_data['application']['homepage']), 'Homepage')  # откроем Homepage
        self.update_url_bar(url=QUrl(config_data['application']['homepage']))
        self.setWindowTitle(config_data['application']['name'])
        self.setWindowIcon(QIcon(res_path(('logo_pb.png'))))
        self.show()

    def set_proxy(self, index):
        """Метод установки HTTP/HTTPS прокси для приложения"""
        try:
            sel_proxy = self.proxies[index]             # index - номер прокси в выпадающем меню
            proxy = QNetworkProxy()
            proxy.setType(QNetworkProxy.HttpProxy)
            proxy.setHostName(sel_proxy[1])             # установим host
            proxy.setPort(int(sel_proxy[2]))            # и порт
            QNetworkProxy.setApplicationProxy(proxy)    # Установим прокси для приложения
        except:
            pass        # если что-то пошло не так - еще есть другие прокси в запасе

    def create_privacy_toolbar(self):
        """Метод создания тулбара для анонимности"""
        privacy_toolbar = QToolBar("Privacy")           # Сам тулбар
        privacy_toolbar.setIconSize(QSize(18, 18))      # Размер иконок
        self.addToolBar(Qt.LeftToolBarArea, privacy_toolbar)    # Будет располагаться слева
        proxy_btn = QToolButton(privacy_toolbar)        # Кнопка с выпадающим меню выбора прокси-сервера
        proxy_btn.setIcon(QIcon(res_path('ic_priv_location.png')))
        proxy_btn.setStatusTip("Change location")       # Подсказка в статус баре
        proxy_btn.setToolTip("Change location")         # Тултип
        proxy_menu = QMenu()                            # По кнопке будет выпадать меню
        no_proxy_item = QAction('Real location', self)  # Пункт меню без прокси
        no_proxy_item.triggered.connect(lambda: self.proxy_clicked(-1))
        proxy_menu.addAction(no_proxy_item)
        proxy_menu.addSeparator()                       # Разделитель в меню
        for item in range(len(self.proxies)):           # Формирование пунктов меню из списка прокси-серверов
            proxy_item = QAction(f'{self.proxies[item][0]}, avg responce {self.proxies[item][3]}s', self)
            proxy_item.triggered.connect(lambda _, index=item: self.proxy_clicked(index))   # и добавим слот
            proxy_menu.addAction(proxy_item)
        proxy_btn.setMenu(proxy_menu)
        proxy_btn.setPopupMode(QToolButton.MenuButtonPopup)
        self.proxy_btn = privacy_toolbar.addWidget(proxy_btn)
        webrtc_btn = QAction(QIcon(res_path(('ic_priv_eye_on.png'))), "Toggle WebRTC", self)    # Кнопка WebRTC
        webrtc_btn.setStatusTip("Toggle WebRTC & Javascript")
        webrtc_btn.triggered.connect(lambda _, button=webrtc_btn: self.toggle_webrtc(button))   # и слот
        privacy_toolbar.addAction(webrtc_btn)

    def proxy_clicked(self, index):
        """Метод обработки выбора прокси в выпадающем меню"""
        if index == -1:             # Без прокси
            QNetworkProxy.setApplicationProxy(QNetworkProxy(QNetworkProxy.DefaultProxy))
        else:
            self.set_proxy(index)   # Установка прокси

    def toggle_webrtc(self, button):
        """ Метод обработки нажатия на кнопку включения/выключения WebRTC и Javascript """
        if self.webrtc_enabled:                                         # Инвертируем состояние вкл WebRTC и Javascript
            self.webrtc_enabled = False
            button.setIcon(QIcon(res_path(('ic_priv_eye_off.png'))))    # Изменяем иконку кнопки на закрытый глаз
        else:
            self.webrtc_enabled = True
            button.setIcon(QIcon(res_path(('ic_priv_eye_on.png'))))     # Изменяем иконку кнопки на открытый глаз

    def create_navigation_toolbar(self):
        """Метод создания тулбара навигации браузера"""
        nav_toolbar = QToolBar("Navigation")                # Сам тулбар
        nav_toolbar.setIconSize(QSize(18, 18))              # Размер иконок
        self.addToolBar(Qt.TopToolBarArea, nav_toolbar)     # Расположить сверху
        back_btn = QAction(QIcon(res_path(('ic_nav_prev.png'))), "Back", self)  # Навигация - Back
        back_btn.setStatusTip("Back to previous page")
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        nav_toolbar.addAction(back_btn)
        next_btn = QAction(QIcon(res_path('ic_nav_next.png')), "Forward", self) # Навигация - Forward
        next_btn.setStatusTip("Forward to next page")
        next_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        nav_toolbar.addAction(next_btn)
        reload_btn = QAction(QIcon(res_path('ic_nav_reload.png')), "Reload", self)  # Кнопка обновления страницы
        reload_btn.setStatusTip("Reload page")
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        nav_toolbar.addAction(reload_btn)
        home_btn = QAction(QIcon(res_path('ic_nav_home.png')), "Home", self)        # Кнопка перехода на Homepage
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        nav_toolbar.addAction(home_btn)
        self.urlbar = QLineEdit()                               # Адресная строка браузера
        self.urlbar.setClearButtonEnabled(True)                 # включим кнопку очистки инпута
        self.urlbar.setAttribute(Qt.WA_MacShowFocusRect, 0)
        self.urlbar.returnPressed.connect(self.navigate_to_url) # начало загрузки страницы по Enter
        nav_toolbar.addWidget(self.urlbar)
        stop_btn = QAction(QIcon(res_path('ic_nav_stop.png')), "Stop", self)    # Кнопка остановки загрузки страницы
        stop_btn.setStatusTip("Stop loading current page")
        stop_btn.triggered.connect(lambda: self.tabs.currentWidget().stop())
        nav_toolbar.addAction(stop_btn)

    def create_menu_bar(self):
        """Метод создания основного меню приложения"""
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)    # Выключение нативного меню ОС - расположение меню будет как на Windows
        file_menu = menu_bar.addMenu('&File')   # Меню File
        new_tab_action = QAction(QIcon(res_path('ic_tab_plus.png')), 'New Tab', self) # Новая вкладка
        new_tab_action.setStatusTip('Open a new tab')
        new_tab_action.triggered.connect(lambda _: self.add_new_tab())
        file_menu.addAction(new_tab_action)
        file_menu.addSeparator()
        open_file_action = QAction(QIcon(res_path('ic_open_file.png')), 'Open file', self)  # Открыть html
        open_file_action.setStatusTip('Open from file')
        open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(open_file_action)
        save_file_action = QAction(QIcon(res_path('ic_save_file.png')), "Save file", self)  # Сохранить html
        save_file_action.setStatusTip("Save current page to file")
        save_file_action.triggered.connect(self.save_file)
        file_menu.addAction(save_file_action)
        file_menu.addSeparator()
        exit_app_action = QAction(QIcon(res_path('ic_exit.png')), f'Exit {config_data["application"]["name"]}', self)
        exit_app_action.setStatusTip(f'Exit {config_data["application"]["name"]}')          # Выход из программы
        exit_app_action.triggered.connect(qApp.quit)
        file_menu.addAction(exit_app_action)
        tools_menu = menu_bar.addMenu("&IP Tools")                                          # Меню с полезными ссылками
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
        help_menu = menu_bar.addMenu("&Help")                                       # Меню Help с пунктом About
        about_action = QAction(QIcon(res_path('ic_about.png')), f"About {config_data['application']['name']}", self)
        about_action.setStatusTip("Show About Info")
        about_action.triggered.connect(self.show_about_dlg)
        help_menu.addAction(about_action)

    def add_new_tab(self, qurl=None, label="Blank"):
        """Метод создания новой вкладки браузера"""
        if qurl is None:
            qurl = QUrl('')
        browser = QWebEngineView()  # Класс, на котором построен браузер
        browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        browser.urlChanged.connect(lambda qurl, browser=browser:
                                   self.update_url_bar(qurl, browser))  # связать сигнал подключения и
                                                                        # хэндлер обновления адресной строки
        browser.loadFinished.connect(lambda _, i=i, browser=browser:    # после окончания загрузки страницы будем
                                     self.page_load_finished_handler(i, browser))   # вызывать этот обработчик
        browser.loadStarted.connect(lambda: self.page_load_started_handler(browser)) # свяжем вкл/выкл WebRTC при старте

    def page_load_started_handler(self, browser):
        """Метод включения/выключения WebRTC и Javascript (к сожалению, выключить WebRTC без Javascript здесь нельзя"""
        if self.webrtc_enabled:                 # Пользователь включил WebRTC
            browser.settings().setAttribute(QWebEngineSettings.WebAttribute.WebRTCPublicInterfacesOnly, False)
            browser.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        else:                                   # Пользователь выключил WebRTC
            browser.settings().setAttribute(QWebEngineSettings.WebAttribute.WebRTCPublicInterfacesOnly, True)
            browser.settings().setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, False)

    def page_load_finished_handler(self, i, browser):
        """Метод вызывается когда страница браузера полностью загружена"""
        self.tabs.setTabText(i, browser.page().title())     # в названии табы отобразим настрание страницы
        self.tabs.setTabToolTip(i, browser.page().title())  # и тултип на всякий случай, если табов будет много
        try:    # favicon странички получим из недокументированного API Google (зато работает безотказно)
            favicon = requests.get(f'https://www.google.com/s2/favicons?domain='
                                   f'{self.tabs.widget(i).url().toString()}&sz=16')
            pixmap = QPixmap()                              # в табу добавим favicon загруженного сайта
            pixmap.loadFromData(favicon.content)
            tab_icon = QIcon(pixmap)
            self.tabs.setTabIcon(i, QIcon(tab_icon))
        except:
            pass                                            # если не получилось получить favicon - ничего страшного

    def tab_open_doubleclick(self, i):
        """Метод добавления новой вкладки по двойному клику на свободном месте"""
        if i == -1:
            self.add_new_tab()

    def current_tab_changed(self, i):
        """Метод обновления адресной строки и названия окна приложения в зависимости от выбранной вкладки браузера"""
        qurl = self.tabs.widget(i).url()
        self.update_url_bar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        """Метод закрытия текущей вкладки браузера (кроме единственной)"""
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def update_title(self, browser):
        """Метод обновления названия окна приложения в зависимости от выбранной вкладки браузера"""
        if browser != self.tabs.currentWidget():
            return
        title = self.tabs.currentWidget().page().title()                        # Получаем имя текущей табы
        self.setWindowTitle(f"{title} - {config_data['application']['name']}")  # обновление названия окна приложения

    def navigate_iplocation(self):
        """Метод открывает страницу iplocation.net в текущей вкладке браузера"""
        self.tabs.currentWidget().setUrl(QUrl("https://www.iplocation.net/"))

    def navigate_browserleaks(self):
        """Метод открывает страницу browserleaks.com/ip в текущей вкладке браузера"""
        self.tabs.currentWidget().setUrl(QUrl("https://browserleaks.com/ip"))

    def navigate_ipleak(self):
        """Метод открывает страницу ipleak.net в текущей вкладке браузера"""
        self.tabs.currentWidget().setUrl(QUrl("https://ipleak.net/"))

    @staticmethod
    def show_about_dlg():
        """Метод отображает диалог 'О программе' """
        dlg = AboutPBrowser()
        dlg.exec_()

    def open_file(self):
        """Метод открывает html-файл текущей вкладке браузера"""
                                                                        # вызов диалога открытия файла
        filename, _ = QFileDialog.getOpenFileName(self, "Open file", "", "HTML (*.htm *.html);;" "All files (*.*)")
        if filename:
            with open(filename, 'r') as f:                              # откываем файл на чтение
                html_file = f.read()                                    # читаем файл
            self.tabs.currentWidget().setHtml(html_file)                # добавляем его содержимое в текущую вкладку
            self.urlbar.setText(filename)                               # в адресной строке теперь будет имя файла

    def callback(self, html):
        """Метод нужен для сохранения html-странички"""
        self.mHtml = html
        self.htmlFinished.emit()

    def save_file(self):
        """Метод открывает html-файл текущей вкладке браузера"""
                                                                        # вызов диалога сохранения файла
        filename, _ = QFileDialog.getSaveFileName(self, "Save Page", "", "HTML (*.htm *html);;" "All files (*.*)")
        if filename:                                                    # если имя не пустое - сохраняем страницу
            self.tabs.currentWidget().page().toHtml(self.callback)
            loop = QEventLoop()
            self.htmlFinished.connect(loop.quit)
            loop.exec_()
            with open(filename, 'w') as f:                              # открываем файл на запись
                f.write(self.mHtml)                                     # сохраняем в файл

    def navigate_home(self):
        """Метод открывает домашнюю страницу текущей вкладке браузера"""
        self.tabs.currentWidget().setUrl(QUrl(config_data['application']['homepage']))

    def navigate_to_url(self):
        """Метод открытия странички по нажатию Enter в адресной строке"""
        q = QUrl(self.urlbar.text())
        if q.scheme() == "":
            q.setScheme("http")     # по умолчанию - будет http
        self.tabs.currentWidget().setUrl(q)

    def update_url_bar(self, url, browser=None):
        """Метод обновления вида адресной строки в зависимости от протокола. Иконка слева покажет http или https"""
        if browser != self.tabs.currentWidget():
            return
        if url.scheme() == 'https':
            ssl_icon_path = res_path("ic_ssl_on.png")               # зеленая иконка для https
        else:
            ssl_icon_path = res_path("ic_ssl_off.png")              # красная иконка для http
        self.urlbar.setStyleSheet(f'background-image: url({ssl_icon_path});\n'  # CSS для адресной строки
                                  'background-repeat: no-repeat;\n'
                                  'background-position: left;\n'
                                  'padding: 0 0 0 20;\n'
                                  'border: 2px solid #a8a8a8;\n'
                                  'border-radius: 10;\n')
        self.urlbar.setText(url.toString())
        self.urlbar.setCursorPosition(0)

if __name__ == '__main__':                          # точка начала выполнения программы
    with open('config.json') as config_file:        # читаем конфигурацию
        config_data = json.load(config_file)
    private_browser_app = QApplication(sys.argv)    # само приложение и установка его свойств
    private_browser_app.setApplicationName(config_data['application']['name'])
    private_browser_app.setApplicationVersion(config_data['application']['version'] +
                                              f"({config_data['application']['build']})")
    private_browser_app.setOrganizationName(config_data['application']['org'])
    private_browser_app.setOrganizationDomain(config_data['application']['url'])
    window = PBMainWindow()                         # виджет главного окна приложения
    sys.exit(private_browser_app.exec_())
