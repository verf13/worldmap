import sys
import json
import os
import re

# PyQt5 Imports
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QLineEdit, QPushButton, QLabel, QSplitter,
    QListWidgetItem, QDialog, QGridLayout, QScrollArea, QSizePolicy, QRadioButton,
    QGroupBox, QMessageBox, QSpinBox
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont


# -------------------------
# Допоміжні функції та дані
# -------------------------

def parse_population(population_str):
    """Конвертує текстовий розмір населення в ціле число."""
    if not isinstance(population_str, str):
        return 0
    population_str = population_str.lower().strip().replace('~', '').replace(',', '.').strip()

    if 'мільярд' in population_str or 'biljoen' in population_str or 'bilion' in population_str:
        # Приймаємо 'biljoen' (нід.) або 'мільярд' за 1,000,000,000
        num_str = re.sub(r'[^\d\.]', '',
                         population_str.replace('мільярд', '').replace('mld', '').replace('biljoen', '').replace(
                             'bilion', ''))
        return int(float(num_str) * 1_000_000_000) if num_str else 0
    elif 'млрд' in population_str or 'mld.' in population_str:
        # Приймаємо 'млрд' (укр.) або 'mld.' (нід. скорочення) за 1,000,000,000
        num_str = re.sub(r'[^\d\.]', '', population_str.replace('млрд', '').replace('mld.', ''))
        return int(float(num_str) * 1_000_000_000) if num_str else 0
    elif 'мільйон' in population_str or 'miljoen' in population_str:
        num_str = re.sub(r'[^\d\.]', '', population_str.replace('мільйон', '').replace('miljoen', ''))
        return int(float(num_str) * 1_000_000) if num_str else 0
    try:
        return int(re.sub(r'[^\d]', '', population_str))
    except ValueError:
        return 0


def parse_gdp(gdp_str):
    """Конвертує текстовий ВВП (наприклад, '~1.1 трильйона USD') в ціле число USD."""
    if not isinstance(gdp_str, str):
        return 0

    gdp_str = gdp_str.lower().strip().replace('~', '').replace(',', '.').replace('usd', '').replace(' ', '').strip()

    if 'трильйона' in gdp_str or 'biljoen' in gdp_str or 'bilion' in gdp_str:
        num_str = re.sub(r'[^\d\.]', '',
                         gdp_str.replace('трильйона', '').replace('biljoen', '').replace('bilion', '').replace('тлн.',
                                                                                                               ''))
        return int(float(num_str) * 1_000_000_000_000) if num_str else 0
    elif 'mld' in gdp_str or 'млрд' in gdp_str:
        num_str = re.sub(r'[^\d\.]', '', gdp_str.replace('mld', '').replace('млрд', ''))
        return int(float(num_str) * 1_000_000_000) if num_str else 0
    elif 'm.' in gdp_str or 'м.' in gdp_str or 'мільйон' in gdp_str:
        num_str = re.sub(r'[^\d\.]', '', gdp_str.replace('m.', '').replace('м.', '').replace('мільйон', ''))
        return int(float(num_str) * 1_000_000) if num_str else 0

    # Спроба прямого парсингу, якщо це вже чисте число
    try:
        return int(re.sub(r'[^\d]', '', gdp_str))
    except ValueError:
        return 0


def format_population(number):
    """Форматує ціле число з точками як роздільник тисяч."""
    return f"{number:,}".replace(',', '.')


def builtin_sample_data():
    # Той самий вбудований набір даних, перекладений на українську.
    sample = {
        "Афганістан": {"name": "Афганістан", "population": "41 мільйон", "gdp": "~14.5 млрд. USD",
                       "main_sector": "Сільське господарство, Гірничодобувна промисловість",
                       "analysis": "Сільське господарство є основою економіки. Безпека та інфраструктура є ключовими викликами.",
                       "young": 40, "teens": 20, "elderly": 3},
        "Алжир": {"name": "Алжир", "population": "46 мільйонів", "gdp": "~270 млрд. USD",
                  "main_sector": "Нафта, Газ, Промисловість",
                  "analysis": "Економіка сильно залежить від експорту вуглеводнів; необхідна диверсифікація.",
                  "young": 29, "teens": 18, "elderly": 8},
        "Аргентина": {"name": "Аргентина", "population": "47 мільйонів", "gdp": "~630 млрд. USD",
                      "main_sector": "Сільське господарство, Автомобільна промисловість",
                      "analysis": "Багаті природні ресурси, але бореться з постійними фінансовими кризами та високою інфляцією.",
                      "young": 24, "teens": 15, "elderly": 12},
        "Австралія": {"name": "Австралія", "population": "27 мільйонів", "gdp": "~1.9 трильйона USD",
                      "main_sector": "Послуги, Гірничодобувна промисловість, Освіта",
                      "analysis": "Сильний експорт сировини та фінансовий сектор.", "young": 18, "teens": 12,
                      "elderly": 16},
        "Австрія": {"name": "Австрія", "population": "9.1 мільйона", "gdp": "~520 млрд. USD",
                    "main_sector": "Послуги, Виробництво, Туризм",
                    "analysis": "Квітуча ринкова економіка з високою якістю життя.", "young": 14, "teens": 10,
                    "elderly": 20},
        "Азербайджан": {"name": "Азербайджан", "population": "10.4 мільйона", "gdp": "~90 млрд. USD",
                        "main_sector": "Нафта, Газ, Промисловість",
                        "analysis": "Економіка, заснована на нафті, прагне до модернізації.", "young": 23,
                        "teens": 15, "elderly": 9},
        "Бангладеш": {"name": "Бангладеш", "population": "175 мільйонів", "gdp": "~450 млрд. USD",
                      "main_sector": "Одяг, Фармацевтика, Сільське господарство",
                      "analysis": "Швидке зростання завдяки виробництву одягу. Виклики: інфраструктура та зміна клімату.",
                      "young": 25, "teens": 18, "elderly": 7},
        "Бельгія": {"name": "Бельгія", "population": "11.8 мільйона", "gdp": "~630 млрд. USD",
                    "main_sector": "Послуги, Логістика, Хімія",
                    "analysis": "Центральне розташування в Європі з відкритою, експортоорієнтованою економікою.",
                    "young": 15,
                    "teens": 11, "elderly": 19},
        "Бразилія": {"name": "Бразилія", "population": "218 мільйонів", "gdp": "~2.08 трильйона USD",
                     "main_sector": "Сільське господарство, Сировина, Енергетика",
                     "analysis": "Одна з країн БРІКС. Великий потенціал, але бореться з нерівністю та політичними циклами.",
                     "young": 21, "teens": 16, "elderly": 11},
        "Канада": {"name": "Канада", "population": "40 мільйонів", "gdp": "~2.2 трильйона USD",
                   "main_sector": "Послуги, Природні ресурси, Енергетика",
                   "analysis": "Багата країна з акцентом на технології та відновлювані джерела енергії.", "young": 16,
                   "teens": 11,
                   "elderly": 18},
        "Китай": {"name": "Китай", "population": "1.425 мільярда", "gdp": "~18.0 трильйона USD",
                  "main_sector": "Виробництво, Експорт, Технології",
                  "analysis": "Найбільша фабрика світу. Перехід до внутрішнього споживання та високотехнологічної промисловості.",
                  "young": 16, "teens": 12, "elderly": 14},
        "Німеччина": {"name": "Німеччина", "population": "84 мільйони", "gdp": "~4.5 трильйона USD",
                      "main_sector": "Виробництво, Автомобільна промисловість, Хімія",
                      "analysis": "Найбільша та найстабільніша економіка єврозони, що спеціалізується на високоякісній промисловості.",
                      "young": 13, "teens": 10, "elderly": 22},
        "Франція": {"name": "Франція", "population": "68 мільйонів", "gdp": "~2.9 трильйона USD",
                    "main_sector": "Послуги, Туризм, Предмети розкоші",
                    "analysis": "Змішана економіка з сильною соціальною безпекою та акцентом на інновації.",
                    "young": 17,
                    "teens": 11, "elderly": 20},
        "Індія": {"name": "Індія", "population": "1.43 мільярда", "gdp": "~3.7 трильйона USD",
                  "main_sector": "Послуги, IT, Сільське господарство",
                  "analysis": "Найшвидше зростаюча велика економіка у світі, з дуже молодим населенням.",
                  "young": 28, "teens": 18, "elderly": 7},
        "Індонезія": {"name": "Індонезія", "population": "280 мільйонів", "gdp": "~1.4 трильйона USD",
                      "main_sector": "Сировина, Виробництво, Послуги",
                      "analysis": "Найбільша економіка Південно-Східної Азії. Великий внутрішній ринок.", "young": 27,
                      "teens": 16, "elderly": 7},
        "Ірландія": {"name": "Ірландія", "population": "5.1 мільйона", "gdp": "~560 млрд. USD",
                     "main_sector": "Фармацевтика, IT, Фінанси",
                     "analysis": "Привабливий податковий режим для транснаціональних корпорацій.", "young": 20,
                     "teens": 13,
                     "elderly": 15},
        "Італія": {"name": "Італія", "population": "59 мільйонів", "gdp": "~2.0 трильйона USD",
                   "main_sector": "Виробництво, Мода, Туризм",
                   "analysis": "Сильний експорт 'Made in Italy'. Бореться з регіональними відмінностями та високим державним боргом.",
                   "young": 13, "teens": 9, "elderly": 23},
        "Японія": {"name": "Японія", "population": "125 мільйонів", "gdp": "~4.03 трильйона USD",
                   "main_sector": "Технології, Автомобільна промисловість, Фінанси",
                   "analysis": "Високорозвинена економіка, але має серйозну та постійну проблему старіння населення.",
                   "young": 12, "teens": 9, "elderly": 29},
        "Кенія": {"name": "Кенія", "population": "57 мільйонів", "gdp": "~115 млрд. USD",
                  "main_sector": "Послуги, Сільське господарство, Туризм",
                  "analysis": "Економічний центр Східної Африки. Лідер у мобільних платежах (M-Pesa).", "young": 39,
                  "teens": 20, "elderly": 4},
        "Мексика": {"name": "Мексика", "population": "128 мільйонів", "gdp": "~1.4 трильйона USD",
                    "main_sector": "Виробництво, Експорт, Нафта",
                    "analysis": "Важливий торговий партнер Північної Америки. Близькість до США має вирішальне значення.",
                    "young": 24, "teens": 16, "elderly": 9},
        "Нідерланди": {"name": "Нідерланди", "population": "18 мільйонів", "gdp": "~1.1 трильйона USD",
                       "main_sector": "Послуги, Логістика, Агротехнології",
                       "analysis": "Дуже відкрита та процвітаюча економіка, важливі ворота до Європи.", "young": 16,
                       "teens": 12, "elderly": 20},
        "Нігерія": {"name": "Нігерія", "population": "230 мільйонів", "gdp": "~500 млрд. USD",
                    "main_sector": "Нафта, Послуги, Сільське господарство",
                    "analysis": "Найбільше населення та економіка Африки. Високий демографічний тиск та залежність від нафти.",
                    "young": 42, "teens": 20, "elderly": 4},
        "Панама": {"name": "Панама", "population": "4.5 мільйона", "gdp": "~95 млрд. USD",
                   "main_sector": "Канал, Логістика, Фінанси",
                   "analysis": "Економіка сильно залежить від доходів Панамського каналу та фінансових послуг.",
                   "young": 25, "teens": 15, "elderly": 10},
        "Польща": {"name": "Польща", "population": "37 мільйонів", "gdp": "~750 млрд. USD",
                   "main_sector": "Виробництво, Послуги, Автоматизація",
                   "analysis": "Успішний 'новачок' у ЄС, зі значним зростанням у виробничому секторі.", "young": 17,
                   "teens": 12, "elderly": 17},
        "Саудівська Аравія": {"name": "Саудівська Аравія", "population": "37 мільйонів", "gdp": "~1.1 трильйона USD",
                              "main_sector": "Енергетика, Нафтохімія",
                              "analysis": "Великий виробник нафти. Програма 'Vision 2030' спрямована на економічну диверсифікацію.",
                              "young": 30, "teens": 15, "elderly": 4},
        "Іспанія": {"name": "Іспанія", "population": "48 мільйонів", "gdp": "~1.6 трильйона USD",
                    "main_sector": "Туризм, Послуги, Автомобільна промисловість",
                    "analysis": "Одне з найбільших туристичних напрямків у світі. Високе безробіття серед молоді є проблемою.",
                    "young": 15, "teens": 11, "elderly": 21},
        "Південна Корея": {"name": "Південна Корея", "population": "51 мільйон", "gdp": "~1.8 трильйона USD",
                           "main_sector": "Технології, Автомобільна промисловість, Експорт",
                           "analysis": "Один з 'Азіатських Тигрів'. Надзвичайно експортоорієнтований, зі світовими лідерами в галузі технологій.",
                           "young": 13, "teens": 11, "elderly": 16},
        "Швеція": {"name": "Швеція", "population": "10.6 мільйона", "gdp": "~600 млрд. USD",
                   "main_sector": "Послуги, Інновації, Обробка деревини",
                   "analysis": "Високотехнологічна держава загального добробуту, лідер у сталому розвитку.",
                   "young": 17,
                   "teens": 11, "elderly": 20},
        "Швейцарія": {"name": "Швейцарія", "population": "9 мільйонів", "gdp": "~900 млрд. USD",
                      "main_sector": "Фінанси, Фармацевтика, Прецизійні інструменти",
                      "analysis": "Найвищий ВВП на душу населення у світі. Дуже стабільна та спеціалізована.",
                      "young": 14, "teens": 10, "elderly": 20},
        "Туреччина": {"name": "Туреччина", "population": "86 мільйонів", "gdp": "~1.1 трильйона USD",
                      "main_sector": "Виробництво, Послуги, Сільське господарство",
                      "analysis": "Динамічна, велика регіональна економіка. Бореться з високою інфляцією та волатильністю обмінного курсу.",
                      "young": 24, "teens": 15, "elderly": 8},
        "Україна": {"name": "Україна", "population": "~40 мільйонів (до війни)",
                    "gdp": "~150 млрд. USD (до війни)",
                    "main_sector": "Сільське господарство, IT, Металургійна промисловість",
                    "analysis": "Має значний аграрний та промисловий потенціал. Відновлення є найбільшим економічним викликом.",
                    "young": 15, "teens": 12, "elderly": 19},
        "Сполучені Штати": {"name": "Сполучені Штати", "population": "342 мільйони", "gdp": "~29.18 трильйона USD",
                            "main_sector": "Послуги, Технології, Фінанси",
                            "analysis": "Найбільша та найбільш диверсифікована економіка у світі. Лідер у галузі технологій та R&D.",
                            "young": 18, "teens": 12, "elderly": 17},
        "В'єтнам": {"name": "В'єтнам", "population": "100 мільйонів", "gdp": "~460 млрд. USD",
                    "main_sector": "Виробництво, Експорт, Сільське господарство",
                    "analysis": "Швидке зростання завдяки переміщенню виробництва з Китаю.", "young": 22, "teens": 17,
                    "elderly": 8},
    }
    return {k: v for k, v in sample.items()}


def load_country_data():
    """Завантажує дані з JSON-файлу або використовує вбудовані зразки даних."""
    json_path = os.path.join(os.getcwd(), "countries_data.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return {c['name']: c for c in data}
            elif isinstance(data, dict):
                return data
        except Exception:
            return builtin_sample_data()
    return builtin_sample_data()


# -------------------------
# Фільтр Багатства (Новий Компонент)
# -------------------------

class WealthFilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Фільтр Економічного Багатства (ВВП)")
        self.setGeometry(200, 200, 400, 250)
        self.setModal(True)
        self.result_filter = None  # (Тип: 'total_gdp' або 'gdp_per_capita')
        self.result_threshold = 500  # Початковий поріг у млрд. USD або тис. USD

        main_layout = QVBoxLayout(self)

        group_box = QGroupBox("Критерій Фільтрації:")
        group_layout = QVBoxLayout()

        self.radio_total_gdp = QRadioButton("Високий Загальний ВВП (> X млрд. USD)")
        self.radio_gdp_per_capita = QRadioButton("Високий ВВП на душу населення (> X тис. USD)")
        self.radio_none = QRadioButton("Не застосовувати фільтр")
        self.radio_none.setChecked(True)

        # Поле для введення порогу
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Введіть поріг (число):"))
        self.threshold_input = QSpinBox()
        self.threshold_input.setRange(10, 3000)  # Від 10 до 3000
        self.threshold_input.setValue(self.result_threshold)
        self.threshold_input.setToolTip("Для ВВП - млрд. USD; для ВВП на душу - тис. USD.")
        threshold_layout.addWidget(self.threshold_input)

        group_layout.addWidget(self.radio_total_gdp)
        group_layout.addWidget(self.radio_gdp_per_capita)
        group_layout.addLayout(threshold_layout)
        group_layout.addWidget(self.radio_none)

        group_box.setLayout(group_layout)
        main_layout.addWidget(group_box)

        button_layout = QHBoxLayout()
        apply_button = QPushButton("Застосувати Фільтр")
        apply_button.clicked.connect(self.accept_selection)
        cancel_button = QPushButton("Скасувати")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(apply_button)
        main_layout.addLayout(button_layout)

    def accept_selection(self):
        """Зберігає обраний фільтр та поріг і закриває діалог."""
        self.result_threshold = self.threshold_input.value()

        if self.radio_total_gdp.isChecked():
            self.result_filter = 'total_gdp'
        elif self.radio_gdp_per_capita.isChecked():
            self.result_filter = 'gdp_per_capita'
        else:
            self.result_filter = None

        self.accept()

    def get_filter_settings(self):
        """Повертає обраний фільтр та поріг."""
        return self.result_filter, self.result_threshold


# -------------------------
# Діалог фільтра (Демографія) - Без змін
# -------------------------

class DemographicFilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Демографічний Фільтр")
        self.setGeometry(200, 200, 400, 250)
        self.setModal(True)
        self.result_filter = None

        main_layout = QVBoxLayout(self)

        group_box = QGroupBox("Оберіть демографічний фокус (один вибір):")
        group_layout = QVBoxLayout()

        self.radio_elderly = QRadioButton("Багато літніх людей (65+ > 20%)")
        self.radio_young = QRadioButton("Багато молоді (0-14 > 30%)")
        self.radio_working = QRadioButton("Велике працездатне населення (25-64 > 50%)")
        self.radio_none = QRadioButton("Не застосовувати фільтр")
        self.radio_none.setChecked(True)

        group_layout.addWidget(self.radio_elderly)
        group_layout.addWidget(self.radio_young)
        group_layout.addWidget(self.radio_working)
        group_layout.addWidget(self.radio_none)
        group_box.setLayout(group_layout)
        main_layout.addWidget(group_box)

        button_layout = QHBoxLayout()
        apply_button = QPushButton("Застосувати Фільтр")
        apply_button.clicked.connect(self.accept_selection)
        cancel_button = QPushButton("Скасувати")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(cancel_button)
        button_layout.addWidget(apply_button)
        main_layout.addLayout(button_layout)

    def accept_selection(self):
        if self.radio_elderly.isChecked():
            self.result_filter = 'elderly'
        elif self.radio_young.isChecked():
            self.result_filter = 'young'
        elif self.radio_working.isChecked():
            self.result_filter = 'working'
        else:
            self.result_filter = None

        self.accept()

    def get_filter(self):
        return self.result_filter


# -------------------------
# Детальний Поп-ап (QDialog) - Без змін
# -------------------------

class DetailDialog(QDialog):
    def __init__(self, country_data, parent=None):
        super().__init__(parent)
        self.country_data = country_data
        self.setWindowTitle(f"Детальний Аналіз: {country_data.get('name', 'N/A')}")
        self.setGeometry(100, 100, 750, 650)
        self.setModal(True)
        self.setStyleSheet("background-color: #f3f4f6;")

        self.total_population_int = parse_population(country_data.get('population', '0'))

        main_layout = QVBoxLayout(self)

        # Заголовок
        title_label = QLabel(f"📈 <b>Економічний та Демографічний Аналіз</b> — {country_data.get('name', 'N/A')}")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #1e40af;")
        main_layout.addWidget(title_label)

        # Ключові дані та Вікова структура (Горизонтально)
        h_info_layout = QHBoxLayout()
        h_info_layout.addWidget(self._create_key_data_panel(), 1)
        h_info_layout.addWidget(self._create_demographic_panel(), 1)
        main_layout.addLayout(h_info_layout, 1)

        # Текст звіту
        main_layout.addWidget(QLabel("<b>Розширений Економічний Звіт:</b>"))

        analysis_area = self._create_analysis_text_area(country_data.get('analysis', 'Аналіз недоступний.'))
        main_layout.addWidget(analysis_area, 2)

        # Кнопка закриття
        close_button = QPushButton("Закрити")
        close_button.setFont(QFont("Arial", 12))
        close_button.setStyleSheet("background-color: #ef4444; color: white; padding: 10px; border-radius: 5px;")
        close_button.clicked.connect(self.accept)
        main_layout.addWidget(close_button)

    def _create_key_data_panel(self):
        panel = QWidget()
        vbox = QVBoxLayout(panel)
        vbox.setAlignment(Qt.AlignTop)

        panel.setStyleSheet("background-color: white; border: 1px solid #d1d5db; border-radius: 8px; padding: 15px;")

        vbox.addWidget(QLabel("<b>Ключові Дані</b>"))
        vbox.addSpacing(10)

        data_pairs = [
            ("Загальна чисельність населення:", self.country_data.get('population', 'N/A')),
            ("ВВП (Номінальний):", self.country_data.get('gdp', 'N/A')),
            ("Основний сектор:", self.country_data.get('main_sector', 'N/A')),
        ]

        # Додавання ВВП на душу населення
        gdp_int = parse_gdp(self.country_data.get('gdp', '0'))
        pop_int = parse_population(self.country_data.get('population', '0'))

        if gdp_int > 0 and pop_int > 0:
            gdp_per_capita = round(gdp_int / pop_int / 1000)  # У тисячах USD
            gdp_per_capita_str = f"~{format_population(gdp_per_capita)} тис. USD"
        else:
            gdp_per_capita_str = "N/A"

        data_pairs.append(("ВВП на душу населення:", gdp_per_capita_str))

        for label, value in data_pairs:
            l = QLabel(f"{label} <b>{value}</b>")
            l.setFont(QFont("Arial", 10))
            vbox.addWidget(l)

        vbox.addStretch(1)
        return panel

    def _create_demographic_panel(self):
        panel = QWidget()
        vbox = QVBoxLayout(panel)
        panel.setStyleSheet("background-color: white; border: 1px solid #d1d5db; border-radius: 8px; padding: 15px;")
        vbox.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        vbox.addWidget(QLabel("<b>Розподіл за віком (%)</b>"))
        vbox.addSpacing(10)

        pie_data_perc = {
            'Young': self.country_data.get('young', 0),
            'Teens': self.country_data.get('teens', 0),
            'Elderly': self.country_data.get('elderly', 0),
            # Працездатне населення - це залишок
            'Working': max(0, 100 - (self.country_data.get('young', 0) +
                                     self.country_data.get('teens', 0) +
                                     self.country_data.get('elderly', 0)))
        }

        demographic_widget = self._create_demographic_visual_bar(pie_data_perc)
        vbox.addWidget(demographic_widget)
        vbox.addSpacing(10)

        legend_widget = self._create_demographic_legend(pie_data_perc)
        vbox.addWidget(legend_widget)

        vbox.addStretch(1)

        return panel

    def _create_demographic_visual_bar(self, pie_data_perc):
        """Створює горизонтальну візуальну смужку, що показує розподіл."""
        bar_widget = QWidget()
        hbox = QHBoxLayout(bar_widget)
        hbox.setContentsMargins(0, 0, 0, 0)
        hbox.setSpacing(0)

        # Кольори та дані для сегментів
        data_segments = [
            (pie_data_perc.get('Young', 0), '#4ede7a'),  # Зелений (Молодь)
            (pie_data_perc.get('Teens', 0), '#fbc02d'),  # Жовтий (Підлітки)
            (pie_data_perc.get('Working', 0), '#3b82f6'),  # Синій (Працездатні)
            (pie_data_perc.get('Elderly', 0), '#f87171')  # Червоний (Літні)
        ]

        for percentage, color_hex in data_segments:
            if percentage > 0:
                segment = QLabel()
                segment.setToolTip(f"{percentage}%")
                segment.setStyleSheet(f"background-color: {color_hex};")
                hbox.addWidget(segment, int(percentage))

        bar_widget.setStyleSheet("border: 1px solid #d1d5db; border-radius: 4px; height: 20px;")
        bar_widget.setFixedHeight(20)
        bar_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        return bar_widget

    def _create_demographic_legend(self, pie_data_perc):
        """Створює легенду з кольоровими квадратами та абсолютними/відносними значеннями."""
        legend = QWidget()
        grid = QGridLayout(legend)
        grid.setHorizontalSpacing(15)
        grid.setVerticalSpacing(5)

        labels = ['Молодь (0-14)', 'Підлітки (15-24)', 'Працездатне населення (25-64)', 'Літні люди (65+)']
        colors = ['#4ede7a', '#fbc02d', '#3b82f6', '#f87171']
        data_keys = ['Young', 'Teens', 'Working', 'Elderly']

        for i, (label, color_hex, key) in enumerate(zip(labels, colors, data_keys)):
            perc = pie_data_perc.get(key, 0)

            # Розрахунок абсолютного значення
            abs_val = round(self.total_population_int * perc / 100)
            abs_str = format_population(abs_val) if self.total_population_int > 0 else "N/A"

            display_text = f"{label}: <b>{int(perc)}%</b> (прибл. {abs_str})"

            # Кольоровий квадрат
            color_box = QLabel()
            color_box.setFixedSize(QSize(15, 15))
            color_box.setStyleSheet(f"background-color: {color_hex}; border-radius: 3px;")

            # Текстовий напис
            text_label = QLabel(display_text)
            text_label.setFont(QFont("Arial", 10))

            grid.addWidget(color_box, i, 0, Qt.AlignLeft)
            grid.addWidget(text_label, i, 1, Qt.AlignLeft)

        legend.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        return legend

    def _create_analysis_text_area(self, text):
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: 1px solid #d1d5db; border-radius: 6px; background-color: white;")

        content_widget = QWidget()
        vbox = QVBoxLayout(content_widget)

        text_label = QLabel(text)
        text_label.setWordWrap(True)
        text_label.setFont(QFont("Arial", 10))
        text_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        text_label.setContentsMargins(10, 10, 10, 10)

        vbox.addWidget(text_label)
        vbox.addStretch(1)

        content_widget.setLayout(vbox)
        scroll_area.setWidget(content_widget)
        return scroll_area


# -------------------------
# Головне Вікно Програми (QMainWindow)
# -------------------------

class CountryAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Аналіз Світової Економіки (PyQt5 Фільтри)")
        self.setGeometry(100, 100, 1000, 700)

        self.all_country_data = load_country_data()
        self.current_country_names = sorted(self.all_country_data.keys())
        self.selected_country = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self._setup_ui()
        self.populate_list(self.current_country_names)

    def _setup_ui(self):
        # Заголовок
        title_label = QLabel("🌍 <b>Аналіз Світової Економіки</b> — Оберіть Країну")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setStyleSheet("color: #1e40af; padding-bottom: 10px;")
        self.main_layout.addWidget(title_label)

        # Панель пошуку та кнопок
        controls_layout = QHBoxLayout()

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введіть для пошуку за назвою...")
        self.search_input.setFont(QFont("Arial", 10))
        self.search_input.textChanged.connect(self.filter_list_by_name)
        controls_layout.addWidget(self.search_input, 3)

        # КНОПКА 1: Демографічний Фільтр
        demographic_filter_button = QPushButton("Фільтр за Демографією 👶👵")
        demographic_filter_button.setStyleSheet("background-color: #d1fae5; color: #065f46; font-weight: bold;")
        demographic_filter_button.clicked.connect(self.open_demographic_filter)
        controls_layout.addWidget(demographic_filter_button, 1)

        # КНОПКА 2: Фільтр Багатства (НОВИЙ)
        wealth_filter_button = QPushButton("Фільтр за Багатством 💰📈")
        wealth_filter_button.setStyleSheet("background-color: #ffe4e6; color: #be185d; font-weight: bold;")
        wealth_filter_button.clicked.connect(self.open_wealth_filter)
        controls_layout.addWidget(wealth_filter_button, 1)

        clear_button = QPushButton("Очистити Фільтри")
        clear_button.setStyleSheet("background-color: #fef3c7; color: #92400e;")
        clear_button.clicked.connect(self.clear_all_filters)
        controls_layout.addWidget(clear_button, 1)

        self.main_layout.addLayout(controls_layout)

        # Основний вміст: Список і Попередній перегляд (QSplitter)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)

        # 1. Список Країн
        self.list_widget = QListWidget()
        self.list_widget.setFont(QFont("Arial", 10))
        self.list_widget.itemClicked.connect(self.on_list_selection_change)
        self.list_widget.itemDoubleClicked.connect(self.open_analysis)
        self.splitter.addWidget(self.list_widget)

        # 2. Панель Попереднього Перегляду
        self.preview_panel = self._create_preview_panel()
        self.splitter.addWidget(self.preview_panel)

        self.splitter.setSizes([400, 600])
        self.main_layout.addWidget(self.splitter)

    def _create_preview_panel(self):
        panel = QWidget()
        panel.setStyleSheet("background-color: white; border-radius: 10px; padding: 20px;")
        vbox = QVBoxLayout(panel)
        vbox.setAlignment(Qt.AlignTop)

        vbox.addWidget(QLabel("<b>Огляд Обраної Країни</b>"))

        self.preview_label = QLabel("Оберіть країну зі списку, щоб побачити попередній перегляд.")
        self.preview_label.setWordWrap(True)
        self.preview_label.setFont(QFont("Arial", 11))
        self.preview_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        vbox.addWidget(self.preview_label)

        vbox.addStretch(1)

        self.analysis_button = QPushButton("Показати Аналіз")
        self.analysis_button.setFont(QFont("Arial", 12))
        self.analysis_button.setStyleSheet(
            "background-color: #3b82f6; color: white; padding: 10px; border-radius: 5px;")
        self.analysis_button.clicked.connect(lambda: self.open_analysis(self.selected_country))
        self.analysis_button.setEnabled(False)
        vbox.addWidget(self.analysis_button)

        return panel

    # --- Методи Фільтрації ---

    def populate_list(self, country_names):
        self.list_widget.clear()
        if not country_names:
            self.list_widget.addItem(QListWidgetItem("Країни за цими фільтрами не знайдено."))
        else:
            for name in country_names:
                item = QListWidgetItem(name)
                self.list_widget.addItem(item)
        self.current_country_names = country_names
        self.selected_country = None
        self.analysis_button.setEnabled(False)
        self._update_preview(None)

    def filter_list_by_name(self, text):
        """Фільтрує поточний список на основі введеної назви."""
        text = text.strip().lower()

        matches = [name for name in self.all_country_data.keys() if text in name.lower()]

        self.populate_list(matches)

    def open_demographic_filter(self):
        """Відкриває діалог для вибору демографічних фільтрів."""
        dialog = DemographicFilterDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            selected_filter = dialog.get_filter()
            self.filter_list_by_demographics(selected_filter)

    def filter_list_by_demographics(self, filter_type):
        """Фільтрує список на основі обраної демографічної категорії."""
        if filter_type is None:
            QMessageBox.information(self, "Фільтр Скинуто", "Демографічний фільтр вимкнено.")
            self.populate_list(sorted(self.all_country_data.keys()))
            return

        self.search_input.clear()

        filtered_names = []
        thresholds = {
            'elderly': 20,
            'young': 30,
            'working': 50
        }

        threshold = thresholds.get(filter_type)

        for name, data in self.all_country_data.items():
            if filter_type == 'elderly' and data.get('elderly', 0) > threshold:
                filtered_names.append(name)
            elif filter_type == 'young' and data.get('young', 0) > threshold:
                filtered_names.append(name)
            elif filter_type == 'working':
                working_perc = max(0, 100 - (data.get('young', 0) + data.get('teens', 0) + data.get('elderly', 0)))
                if working_perc > threshold:
                    filtered_names.append(name)

        if not filtered_names:
            QMessageBox.information(self, "Немає Результатів", f"Не знайдено країн з критерієм: {filter_type}.")

        self.populate_list(sorted(filtered_names))

    def open_wealth_filter(self):
        """Відкриває діалог для вибору фільтрів багатства."""
        dialog = WealthFilterDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            selected_filter, threshold = dialog.get_filter_settings()
            self.filter_list_by_wealth(selected_filter, threshold)

    def filter_list_by_wealth(self, filter_type, threshold):
        """Фільтрує список на основі ВВП (загального або на душу населення)."""
        if filter_type is None:
            QMessageBox.information(self, "Фільтр Скинуто", "Фільтр багатства вимкнено.")
            self.populate_list(sorted(self.all_country_data.keys()))
            return

        self.search_input.clear()

        filtered_names = []

        for name, data in self.all_country_data.items():
            gdp_str = data.get('gdp', '0')
            pop_str = data.get('population', '0')

            gdp_int = parse_gdp(gdp_str)
            pop_int = parse_population(pop_str)

            is_match = False

            if filter_type == 'total_gdp':
                # Поріг у діалозі - млрд. USD. Конвертуємо у USD.
                threshold_value = threshold * 1_000_000_000
                if gdp_int >= threshold_value:
                    is_match = True

            elif filter_type == 'gdp_per_capita':
                # Поріг у діалозі - тис. USD. Конвертуємо у USD.
                threshold_value = threshold * 1_000
                if gdp_int > 0 and pop_int > 0:
                    gdp_per_capita = gdp_int / pop_int
                    if gdp_per_capita >= threshold_value:
                        is_match = True

            if is_match:
                filtered_names.append(name)

        if not filtered_names:
            criteria_str = f"ВВП (загальний) > {threshold} млрд. USD" if filter_type == 'total_gdp' else f"ВВП на душу > {threshold} тис. USD"
            QMessageBox.information(self, "Немає Результатів",
                                    f"Не знайдено країн, що відповідають критерію: {criteria_str}.")

        self.populate_list(sorted(filtered_names))

    def clear_all_filters(self):
        """Очищає як пошук за назвою, так і всі додаткові фільтри."""
        self.search_input.clear()
        self.populate_list(sorted(self.all_country_data.keys()))
        self.preview_label.setText("Оберіть країну зі списку, щоб побачити попередній перегляд.")
        self.analysis_button.setEnabled(False)

    # --- Методи Взаємодії ---

    def on_list_selection_change(self, item):
        country_name = item.text()
        if country_name == "Країни за цими фільтрами не знайдено.":
            self.selected_country = None
            self.analysis_button.setEnabled(False)
            self._update_preview(None)
            return

        self.selected_country = self.all_country_data.get(country_name)

        if self.selected_country:
            self.analysis_button.setEnabled(True)
            self._update_preview(self.selected_country)
        else:
            self.analysis_button.setEnabled(False)

    def _update_preview(self, country_data):
        if not country_data:
            self.preview_label.setText("Оберіть країну зі списку, щоб побачити попередній перегляд.")
            return

        name = country_data.get('name', 'N/A')
        pop = country_data.get('population', 'N/A')
        gdp = country_data.get('gdp', 'N/A')
        sector = country_data.get('main_sector', 'N/A')

        gdp_int = parse_gdp(gdp)
        pop_int = parse_population(pop)

        gdp_per_capita_str = "N/A"
        if gdp_int > 0 and pop_int > 0:
            gdp_per_capita = round(gdp_int / pop_int / 1000)
            gdp_per_capita_str = f"~{format_population(gdp_per_capita)} тис. USD"

        preview = (f"<b><font size='5'>{name}</font></b>\n"
                   f"\n<font color='#4b5563'>Населення:</font> <b>{pop}</b>\n"
                   f"<font color='#4b5563'>ВВП (Ном.):</font> <b>{gdp}</b>\n"
                   f"<font color='#4b5563'>ВВП на душу населення:</font> <b>{gdp_per_capita_str}</b>\n"
                   f"<font color='#4b5563'>Основний сектор:</font> <b>{sector}</b>\n"
                   f"\nДвічі клацніть на назві або натисніть 'Показати Аналіз' для отримання додаткових деталей.")
        self.preview_label.setText(preview)

    def open_analysis(self, item):
        if isinstance(item, QListWidgetItem):
            country_name = item.text()
            data = self.all_country_data.get(country_name)
        elif self.selected_country:
            data = self.selected_country
        else:
            QMessageBox.warning(self, "Помилка Вибору", "Будь ласка, спочатку оберіть країну.")
            return

        if data:
            dialog = DetailDialog(data, self)
            dialog.exec_()


if __name__ == '__main__':
    # Встановлення необхідних налаштувань для високої роздільної здатності
    # if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    #     QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    # if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    #     QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    window = CountryAnalysisApp()
    window.show()
    sys.exit(app.exec_())