import json
from res_path import res_path
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QVBoxLayout, QLabel


class AboutPBrowser(QDialog):
    """ Диалог 'О программе' """
    def __init__(self, *args, **kwargs):
        super(AboutPBrowser, self).__init__(*args, **kwargs)
        with open('config.json') as config_file:            # Из файла конфигурации будем брать данные о программе
            config_data = json.load(config_file)
        layout = QVBoxLayout()                              # Будем виджеты располагать по вертикали (Vertical layout)
        pb_title = QLabel(config_data['application']['name'])   # QLabel с названием
        title_font = pb_title.font()
        title_font.setPointSize(24)                             # Размер шрифта
        title_font.setWeight(78)                                # Жирный шрифт
        pb_title.setFont(title_font)
        layout.addWidget(pb_title)
        pb_logo = QLabel()                                      # Логотип приложения
        pb_logo.setPixmap(QPixmap(res_path('logo_pb.png')))
        layout.addWidget(pb_logo)
        layout.addWidget(QLabel(f"Version: {config_data['application']['version']} "
                                f"Build {config_data['application']['build']}"))
        layout.addWidget(QLabel(config_data['application']['about']))
        ok_btn = QDialogButtonBox.Ok                            # На виджете расположим кнопку ОК
        self.buttonBox = QDialogButtonBox(ok_btn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.accept)
        layout.addWidget(self.buttonBox)
        for i in range(0, layout.count()):                      # Выравнивание виджетов
            layout.itemAt(i).setAlignment(Qt.AlignHCenter)
        self.setLayout(layout)
        self.setWindowIcon(QIcon(res_path(('logo_pb.png'))))
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.WindowCloseButtonHint)  # Оставим только кнопку Close
