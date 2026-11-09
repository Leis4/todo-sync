"""Окно списка дел. На втором ПК укажите адрес сервера в аргументе."""

import sys
import requests
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
    QLabel, QLineEdit, QPushButton, QListWidget, QListWidgetItem,
    QComboBox, QProgressBar, QMessageBox, QInputDialog, QFileDialog, QFrame,
)


class Window(QWidget):
    def __init__(self, address):
        super().__init__()
        self.setObjectName("root")
        self.address = address.rstrip("/")
        self.tasks = []
        self.setWindowTitle("Общий список дел")
        self.resize(780, 530)
        self.setStyleSheet("""
            QWidget {color:#26384b; font:12px 'Segoe UI';}
            QWidget#root {background:#f4f7fa;}
            QWidget#page {background:white;}
            QTabWidget::pane {background:white; border:1px solid #d9e3eb; border-radius:9px;}
            QTabBar::tab {background:#e8edf3; border:1px solid #d9e3eb; border-bottom:none;
                          border-top-left-radius:7px; border-top-right-radius:7px;
                          padding:10px 17px; margin-right:3px;}
            QTabBar::tab:selected {background:white; color:#197453; font-weight:bold;}
            QLabel#heading {color:#20344a; font-size:22px; font-weight:bold;}
            QLabel#muted {color:#65798b;}
            QLabel#status {color:#4c6679; font-size:11px;}
            QLineEdit, QListWidget, QComboBox {background:white; border:1px solid #cedce7;
                                               border-radius:7px; padding:8px;}
            QLineEdit:focus, QListWidget:focus, QComboBox:focus {border:1px solid #288964;}
            QListWidget::item {padding:9px;}
            QListWidget::item:selected {background:#e1f3e8; color:#175336;}
            QPushButton {background:#f0f4f7; border:1px solid #d2dfe7;
                         border-radius:7px; padding:9px 12px;}
            QPushButton:hover {background:#e4eee9;}
            QPushButton#primary {background:#20835f; color:white; font-weight:bold;
                                 border:1px solid #20835f;}
            QPushButton#primary:hover {background:#176a4c;}
            QPushButton#danger:hover {background:#f9e8e7; color:#9e3436;}
            QFrame#statCard {background:#f8fbfd; border:1px solid #dde7ed; border-radius:10px;}
            QLabel#statNumber {color:#21825e; font-size:30px; font-weight:bold; background:transparent;}
            QLabel#statCaption {color:#607487; background:transparent;}
            QProgressBar {background:#eaf0f4; border:none; border-radius:7px;
                          color:#173f31; font-weight:bold; text-align:center;}
            QProgressBar::chunk {background:#60ae83; border-radius:7px;}
        """)

        main = QVBoxLayout(self)
        main.setContentsMargins(12, 12, 12, 10)
        main.setSpacing(8)
        tabs = QTabWidget()
        main.addWidget(tabs)

        tasks_page = QWidget()
        tasks_page.setObjectName("page")
        layout = QVBoxLayout(tasks_page)
        layout.setContentsMargins(16, 15, 16, 14)
        layout.setSpacing(9)
        heading = QLabel("Мои задачи")
        heading.setObjectName("heading")
        layout.addWidget(heading)

        line = QHBoxLayout()
        self.title = QLineEdit()
        self.title.setMaxLength(120)
        self.title.setPlaceholderText("Название задачи")
        add = QPushButton("Добавить")
        add.setObjectName("primary")
        line.addWidget(self.title)
        line.addWidget(add)
        layout.addLayout(line)

        line = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Поиск")
        self.filter = QComboBox()
        self.filter.addItems(["Все", "В работе", "Выполнено"])
        line.addWidget(self.search)
        line.addWidget(self.filter)
        layout.addLayout(line)

        self.list = QListWidget()
        layout.addWidget(self.list)
        line = QHBoxLayout()
        change = QPushButton("Изменить")
        done = QPushButton("Готово / вернуть")
        delete = QPushButton("Удалить")
        delete.setObjectName("danger")
        save = QPushButton("Сохранить TXT")
        for button in (change, done, delete, save):
            line.addWidget(button)
        layout.addLayout(line)
        self.counter = QLabel("Задач: 0")
        layout.addWidget(self.counter)
        tabs.addTab(tasks_page, "Задачи")

        stats_page = QWidget()
        stats_page.setObjectName("page")
        stats_layout = QVBoxLayout(stats_page)
        stats_layout.setContentsMargins(20, 18, 20, 18)
        stats_layout.setSpacing(14)
        title = QLabel("Статистика задач")
        title.setObjectName("heading")
        stats_layout.addWidget(title)
        subtitle = QLabel("Состояние общего списка на данный момент")
        subtitle.setObjectName("muted")
        stats_layout.addWidget(subtitle)

        # Три показателя. Числа обновляются после ответа сервера.
        cards = QHBoxLayout()
        cards.setSpacing(10)
        self.total_value = QLabel("0")
        self.open_value = QLabel("0")
        self.done_value = QLabel("0")
        for text, number in (("Всего задач", self.total_value),
                             ("В работе", self.open_value),
                             ("Выполнено", self.done_value)):
            card = QFrame()
            card.setObjectName("statCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(16, 15, 16, 15)
            card_layout.setSpacing(4)
            number.setObjectName("statNumber")
            caption = QLabel(text)
            caption.setObjectName("statCaption")
            card_layout.addWidget(number)
            card_layout.addWidget(caption)
            cards.addWidget(card)
        stats_layout.addLayout(cards)

        progress_label = QLabel("Общий прогресс")
        progress_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        stats_layout.addWidget(progress_label)
        self.progress = QProgressBar()
        self.progress.setFixedHeight(29)
        self.progress.setFormat("Выполнено: %p%")
        self.progress.setValue(0)
        stats_layout.addWidget(self.progress)
        stats_layout.addStretch()
        tabs.addTab(stats_page, "Статистика")

        about = QLabel("Общий список дел для двух компьютеров.\n\n"
                       "Задачи хранятся в SQLite на сервере FastAPI.\n"
                       "Оба клиента обновляются каждые 2 секунды.\n\n"
                       f"Адрес сервера: {self.address}")
        about.setWordWrap(True)
        about.setAlignment(Qt.AlignmentFlag.AlignTop)
        about.setStyleSheet("background:white; padding:20px;")
        tabs.addTab(about, "О программе")
        self.status = QLabel("Подключение...")
        self.status.setObjectName("status")
        main.addWidget(self.status)

        add.clicked.connect(self.add_task)
        self.title.returnPressed.connect(self.add_task)
        change.clicked.connect(self.edit_task)
        done.clicked.connect(self.toggle_task)
        delete.clicked.connect(self.delete_task)
        save.clicked.connect(self.save_txt)
        self.search.textChanged.connect(self.show_tasks)
        self.filter.currentIndexChanged.connect(self.show_tasks)
        self.list.itemDoubleClicked.connect(self.toggle_task)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh)
        self.timer.start(2000)
        self.refresh()

    def selected(self):
        item = self.list.currentItem()
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None

    def show_tasks(self):
        chosen = self.selected()
        old_id = chosen["id"] if chosen else None
        self.list.clear()
        search = self.search.text().lower()
        mode = self.filter.currentIndex()
        for task in self.tasks:
            if search not in task["title"].lower():
                continue
            if mode == 1 and task["done"]:
                continue
            if mode == 2 and not task["done"]:
                continue
            mark = "[x]" if task["done"] else "[ ]"
            item = QListWidgetItem(f"{mark}  {task['title']}")
            item.setData(Qt.ItemDataRole.UserRole, task)
            self.list.addItem(item)
            if task["id"] == old_id:
                self.list.setCurrentItem(item)
        self.counter.setText(f"Показано: {self.list.count()} из {len(self.tasks)}")

    def refresh(self):
        try:
            answer = requests.get(self.address + "/tasks", timeout=2)
            answer.raise_for_status()
            tasks = answer.json()
        except (requests.RequestException, ValueError):
            self.status.setText("Нет связи с сервером")
            return
        self.status.setText("Подключено. Обновление каждые 2 секунды")
        if tasks != self.tasks:
            self.tasks = tasks
            self.show_tasks()
            done = sum(task["done"] for task in tasks)
            self.total_value.setText(str(len(tasks)))
            self.open_value.setText(str(len(tasks) - done))
            self.done_value.setText(str(done))
            percent = round(100 * done / len(tasks)) if tasks else 0
            self.progress.setValue(percent)

    def send(self, method, path, title=None):
        try:
            data = {"title": title} if title is not None else None
            answer = requests.request(method, self.address + path,
                                      json=data, timeout=2)
            answer.raise_for_status()
        except requests.RequestException:
            QMessageBox.warning(self, "Ошибка", "Не удалось выполнить действие")
            self.refresh()
            return False
        self.refresh()
        return True

    def add_task(self):
        title = self.title.text().strip()
        if not title:
            QMessageBox.information(self, "Задача", "Введите название")
        elif self.send("POST", "/tasks", title):
            self.title.clear()

    def edit_task(self):
        task = self.selected()
        if not task:
            QMessageBox.information(self, "Задача", "Выберите задачу")
            return
        text, ok = QInputDialog.getText(self, "Изменить", "Название:",
                                        text=task["title"])
        if ok and text.strip():
            self.send("PATCH", f"/tasks/{task['id']}/title", text.strip())

    def toggle_task(self, *args):
        task = self.selected()
        if task:
            self.send("PATCH", f"/tasks/{task['id']}")
        else:
            QMessageBox.information(self, "Задача", "Выберите задачу")

    def delete_task(self):
        task = self.selected()
        if not task:
            QMessageBox.information(self, "Задача", "Выберите задачу")
        elif QMessageBox.question(self, "Удалить", "Удалить выбранную задачу?") == QMessageBox.StandardButton.Yes:
            self.send("DELETE", f"/tasks/{task['id']}")

    def save_txt(self):
        if not self.tasks:
            QMessageBox.information(self, "Список", "Задач нет")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Сохранить", "Задачи.txt", "TXT (*.txt)")
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8-sig") as file:
                for task in self.tasks:
                    mark = "[x]" if task["done"] else "[ ]"
                    file.write(f"{mark} {task['title']}\n")
            QMessageBox.information(self, "Готово", "Список сохранён")
        except OSError:
            QMessageBox.warning(self, "Ошибка", "Не удалось сохранить файл")


if __name__ == "__main__":
    address = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = Window(address)
    window.show()
    sys.exit(app.exec())
