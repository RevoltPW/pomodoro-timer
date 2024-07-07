#!/usr/bin/env python3
import sys
import os
from PyQt5.QtCore import Qt, QTimer, QTime, QPoint, QUrl, QSize, QSettings, QCoreApplication
from PyQt5.QtGui import QIcon, QColor, QPalette
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QPushButton, QMenu, QAction, QSpinBox, QHBoxLayout, QSizeGrip, QInputDialog, QListWidget, QListWidgetItem, QDialog, QPlainTextEdit, QLineEdit, QDialogButtonBox, QColorDialog, QSlider, QStyle
from PyQt5.QtMultimedia import QSoundEffect

# Ensure you have a directory named "icons" in your project with the required icon files.
ICON_PATH = os.path.join(os.path.dirname(__file__), 'res')


class AddTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Add Task')
        layout = QVBoxLayout()
        self.task_input = QLineEdit(self)
        layout.addWidget(self.task_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        self.setLayout(layout)

        self.setFixedSize(300, 100)
        self.center()

    def center(self):
        screen_geometry = QApplication.desktop().screenGeometry()
        dialog_geometry = self.frameGeometry()
        dialog_geometry.moveCenter(screen_geometry.center())
        self.move(dialog_geometry.topLeft())

    def getTask(self):
        return self.task_input.text()

class PomodoroTimer(QWidget):
    def __init__(self):
        super().__init__()
        self.is_paused = False
        self.is_break = False
        self.is_running = False  # Add this attribute to track if the timer has started
        self.start_time = QTime(0, 25, 0)
        self.break_time = QTime(0, 5, 0)
        self.time_left = self.start_time
        self.sound_effect = QSoundEffect()
        self.sound_effect.setSource(QUrl.fromLocalFile(os.path.join(ICON_PATH, "complete.wav")))
        self.tasks = []
        self.completed_tasks = 0
        self.initUI()  # Initialize UI components first
        self.initTimer()
        self.load_tasks()  # Load tasks after initializing UI components
        self.load_ui_config()  # Load UI configuration after initializing UI components

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.X11BypassWindowManagerHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.timer_label = QLabel(self.time_left.toString('mm:ss'), self)
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet("font-size: 30px; color: white; background-color: rgba(0, 0, 0, 0.5); padding: 10px; border-radius: 10px;")

        self.play_pause_button = QPushButton(self)
        self.play_pause_button.setIcon(QIcon(os.path.join(ICON_PATH, "start.svg")))
        self.play_pause_button.clicked.connect(self.toggle_timer)
        self.play_pause_button.setStyleSheet("background-color: rgba(0, 0, 0, 0.5); padding: 5px; border-radius: 5px;")

        self.reset_button = QPushButton(self)
        self.reset_button.setIcon(QIcon(os.path.join(ICON_PATH, "reset.svg")))
        self.reset_button.clicked.connect(self.reset_timer)
        self.reset_button.setStyleSheet("background-color: rgba(0, 0, 0, 0.5); padding: 5px; border-radius: 5px;")

        self.break_button = QPushButton(self)
        self.break_button.setIcon(QIcon(os.path.join(ICON_PATH, "break.svg")))
        self.break_button.clicked.connect(self.toggle_break)
        self.break_button.setStyleSheet("background-color: rgba(0, 0, 0, 0.5); padding: 5px; border-radius: 5px;")

        self.menu_button = QPushButton(self)
        self.menu_button.setIcon(QIcon(os.path.join(ICON_PATH, "menu.svg")))
        self.menu_button.setStyleSheet("background-color: rgba(0, 0, 0, 0.5); padding: 5px; border-radius: 5px;")
        self.create_menu()

        self.task_list = QListWidget(self)
        self.task_list.setStyleSheet("background: transparent;")
        self.task_list.setFrameStyle(QListWidget.NoFrame)
        self.task_list.setAttribute(Qt.WA_TranslucentBackground)
        self.task_list.setPalette(QPalette(QColor(0, 0, 0, 0)))
        self.task_list.itemChanged.connect(self.complete_task)

        self.completed_tasks_label = QLabel(f'Tasks Completed: {self.completed_tasks}', self)
        self.completed_tasks_label.setAlignment(Qt.AlignLeft)
        self.completed_tasks_label.setStyleSheet("font-size: 14px; color: black; background: transparent; padding: 5px; border-radius: 5px;")

        self.edit_task_button = QPushButton(self)
        self.edit_task_button.setIcon(QIcon(os.path.join(ICON_PATH, "add_task.svg")))
        self.edit_task_button.clicked.connect(self.edit_tasks)
        self.edit_task_button.setStyleSheet("background-color: rgba(0, 0, 0, 0.5); padding: 5px; border-radius: 5px;")

        self.size_grip = QSizeGrip(self)

        layout = QVBoxLayout()
        layout.addWidget(self.timer_label)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.play_pause_button)
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.break_button)
        button_layout.addWidget(self.menu_button)
        layout.addLayout(button_layout)
        layout.addWidget(self.task_list)
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.completed_tasks_label)
        bottom_layout.addWidget(self.edit_task_button, 0, Qt.AlignRight)
        layout.addLayout(bottom_layout)
        layout.addWidget(self.size_grip, 0, Qt.AlignBottom | Qt.AlignRight)
        self.setLayout(layout)

    def create_menu(self):
        self.menu = QMenu()

        set_timer_action = QAction(QIcon(os.path.join(ICON_PATH, "timer.png")), 'Set Timer', self)
        set_timer_action.triggered.connect(self.show_set_timer_dialog)
        self.menu.addAction(set_timer_action)

        set_break_action = QAction(QIcon(os.path.join(ICON_PATH, "break.svg")), 'Set Break', self)
        set_break_action.triggered.connect(self.show_set_break_dialog)
        self.menu.addAction(set_break_action)

        add_task_action = QAction(QIcon(os.path.join(ICON_PATH, "add_task.svg")), 'Add Task', self)
        add_task_action.triggered.connect(self.add_task)
        self.menu.addAction(add_task_action)

        edit_tasks_action = QAction(QIcon(os.path.join(ICON_PATH, "edit_tasks.svg")), 'Edit Tasks', self)
        edit_tasks_action.triggered.connect(self.edit_tasks)
        self.menu.addAction(edit_tasks_action)

        change_color_action = QAction(QIcon(os.path.join(ICON_PATH, "change_color.svg")), 'Change Background Color', self)
        change_color_action.triggered.connect(self.change_color)
        self.menu.addAction(change_color_action)

        change_font_color_action = QAction(QIcon(os.path.join(ICON_PATH, "change_color.svg")), 'Change Font Color', self)
        change_font_color_action.triggered.connect(self.change_font_color)
        self.menu.addAction(change_font_color_action)

        change_opacity_action = QAction(QIcon(os.path.join(ICON_PATH, "change_opacity.svg")), 'Change Opacity', self)
        change_opacity_action.triggered.connect(self.change_opacity)
        self.menu.addAction(change_opacity_action)

        exit_action = QAction(QIcon(os.path.join(ICON_PATH, "exit.svg")), 'Exit', self)
        exit_action.triggered.connect(self.close)
        self.menu.addAction(exit_action)

        self.menu_button.setMenu(self.menu)

        self.menu_button.setMenu(self.menu)
    def initTimer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)

    def toggle_timer(self):
        if self.timer.isActive():
            self.pause_timer()
        else:
            self.start_timer()

    def start_timer(self):
        if not self.is_running:
            self.time_left = self.start_time if not self.is_break else self.break_time
            self.is_running = True
        self.timer.start(1000)
        self.play_pause_button.setIcon(QIcon(os.path.join(ICON_PATH, "pause.svg")))

    def toggle_break(self):
        if self.is_break:
            self.time_left = self.start_time
        else:
            self.time_left = self.break_time

        self.is_break = not self.is_break
        self.timer_label.setText(self.time_left.toString('mm:ss'))
        self.sound_effect.play()
        if not self.timer.isActive():
            self.timer.start(1000)
            self.play_pause_button.setIcon(QIcon(os.path.join(ICON_PATH, "pause.svg")))

    def pause_timer(self):
        self.timer.stop()
        self.play_pause_button.setIcon(QIcon(os.path.join(ICON_PATH, "start.svg")))

    def reset_timer(self):
        self.timer.stop()
        self.play_pause_button.setIcon(QIcon(os.path.join(ICON_PATH, "start.svg")))
        self.is_running = False  # Reset running state
        self.time_left = self.start_time if not self.is_break else self.break_time
        self.timer_label.setText(self.time_left.toString('mm:ss'))

    def update_timer(self):
        self.time_left = self.time_left.addSecs(-1)
        self.timer_label.setText(self.time_left.toString('mm:ss'))

        if self.time_left == QTime(0, 0, 0):
            self.timer.stop()
            self.play_pause_button.setIcon(QIcon(os.path.join(ICON_PATH, "start.svg")))
            self.sound_effect.play()
            self.time_left = self.start_time if not self.is_break else self.break_time
            self.is_running = False  # Reset running state

    def show_set_timer_dialog(self):
        self.timer_dialog = QWidget()
        self.timer_dialog.setWindowTitle('Set Timer')
        layout = QVBoxLayout()

        self.minutes_spinbox = QSpinBox()
        self.minutes_spinbox.setRange(1, 60)
        self.minutes_spinbox.setValue(self.start_time.minute())
        self.minutes_spinbox.setSuffix(' min')

        set_button = QPushButton('Set')
        set_button.clicked.connect(self.set_timer)

        layout.addWidget(QLabel('Minutes:'))
        layout.addWidget(self.minutes_spinbox)
        layout.addWidget(set_button)
        self.timer_dialog.setLayout(layout)
        self.timer_dialog.setGeometry(QStyle.alignedRect(Qt.LeftToRight, Qt.AlignCenter, self.timer_dialog.sizeHint(), app.desktop().availableGeometry()))
        self.timer_dialog.show()

    def set_timer(self):
        minutes = self.minutes_spinbox.value()
        self.start_time = QTime(0, minutes, 0)
        self.time_left = self.start_time
        self.timer_label.setText(self.time_left.toString('mm:ss'))
        self.timer_dialog.close()
        self.save_ui_config()

    def show_set_break_dialog(self):
        self.break_dialog = QWidget()
        self.break_dialog.setWindowTitle('Set Break')
        layout = QVBoxLayout()

        self.break_spinbox = QSpinBox()
        self.break_spinbox.setRange(1, 60)
        self.break_spinbox.setValue(self.break_time.minute())
        self.break_spinbox.setSuffix(' min')

        set_button = QPushButton('Set')
        set_button.clicked.connect(self.set_break)

        layout.addWidget(QLabel('Minutes:'))
        layout.addWidget(self.break_spinbox)
        layout.addWidget(set_button)
        self.break_dialog.setLayout(layout)
        self.break_dialog.setGeometry(QStyle.alignedRect(Qt.LeftToRight, Qt.AlignCenter, self.break_dialog.sizeHint(), app.desktop().availableGeometry()))
        self.break_dialog.show()

    def set_break(self):
        minutes = self.break_spinbox.value()
        self.break_time = QTime(0, minutes, 0)
        self.break_dialog.close()
        self.save_ui_config()

    def add_task(self):
        dialog = AddTaskDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            text = dialog.getTask()
            if text:
                self.tasks.append(text)
                self.save_tasks()
                self.update_task_list()

    def edit_tasks(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Edit Tasks')
        layout = QVBoxLayout()

        self.edit_task_text = QPlainTextEdit('\n'.join(self.tasks))
        save_button = QPushButton('Save')
        save_button.clicked.connect(lambda: self.save_edited_tasks(dialog))

        layout.addWidget(self.edit_task_text)
        layout.addWidget(save_button)
        dialog.setLayout(layout)
        dialog.setGeometry(QStyle.alignedRect(Qt.LeftToRight, Qt.AlignCenter, dialog.sizeHint(), app.desktop().availableGeometry()))
        dialog.exec_()

    def save_edited_tasks(self, dialog):
        self.tasks = self.edit_task_text.toPlainText().split('\n')
        self.update_task_list()
        self.save_tasks()
        dialog.accept()

    def update_task_list(self):
        self.task_list.clear()
        for index, task in enumerate(self.tasks, start=1):
            item = QListWidgetItem(f"{index}. {task}")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.task_list.addItem(item)

    def complete_task(self, item):
        if item.checkState() == Qt.Checked:
            task_text = item.text().split('. ', 1)[1]  # Get the task text without the number
            self.tasks.remove(task_text)
            self.completed_tasks += 1
            self.completed_tasks_label.setText(f'Tasks Completed: {self.completed_tasks}')
            self.sound_effect.play()
            self.update_task_list()
            self.save_tasks()

    def save_tasks(self):
        settings = QSettings('PomodoroApp', 'PomodoroTimer')
        settings.setValue('tasks', self.tasks)

    def load_tasks(self):
        settings = QSettings('PomodoroApp', 'PomodoroTimer')
        self.tasks = settings.value('tasks', [])
        if self.tasks is None:
            self.tasks = []
        self.update_task_list()

    def change_font_color(self):
        current_color = self.timer_label.palette().color(QPalette.WindowText)
        color = QColorDialog.getColor(current_color, self, "Choose Font Color")
        if color.isValid():
            font_color = color.name()
            self.set_font_color(font_color)
            self.save_ui_config()

    def set_font_color(self, color):
        background_color = self.timer_label.styleSheet().split("background-color: rgba(")[-1].split(");")[0]
        self.timer_label.setStyleSheet(f"font-size: 30px; color: {color}; background-color: rgba({background_color}); padding: 10px; border-radius: 10px;")
        self.completed_tasks_label.setStyleSheet(f"font-size: 14px; color: {color}; background: transparent; padding: 5px; border-radius: 5px;")
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            item.setForeground(QColor(color))

    def change_color(self):
        current_color = QColor(0, 0, 0, int(0.5 * 255))
        color = QColorDialog.getColor(current_color, self, "Choose Background Color")
        if color.isValid():
            rgba = color.getRgb()
            background_color = f"background-color: rgba({rgba[0]}, {rgba[1]}, {rgba[2]}, {rgba[3]/255});"
            font_color = self.timer_label.palette().color(QPalette.WindowText).name()
            self.timer_label.setStyleSheet(f"font-size: 30px; color: {font_color}; {background_color} padding: 10px; border-radius: 10px;")
            self.play_pause_button.setStyleSheet(f"{background_color} padding: 5px; border-radius: 5px;")
            self.reset_button.setStyleSheet(f"{background_color} padding: 5px; border-radius: 5px;")
            self.break_button.setStyleSheet(f"{background_color} padding: 5px; border-radius: 5px;")
            self.menu_button.setStyleSheet(f"{background_color} padding: 5px; border-radius: 5px;")
            self.edit_task_button.setStyleSheet(f"{background_color} padding: 5px; border-radius: 5px;")
            #self.completed_tasks_label.setStyleSheet(f"font-size: 14px; color: {font_color}; {background_color} padding: 5px; border-radius: 5px;")
            self.save_ui_config()

    def change_opacity(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('Change Opacity')
        layout = QVBoxLayout()

        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setRange(30, 100)
        self.opacity_slider.setValue(int(self.windowOpacity() * 100))
        self.opacity_slider.valueChanged.connect(self.set_opacity)

        layout.addWidget(QLabel('Opacity:'))
        layout.addWidget(self.opacity_slider)
        dialog.setLayout(layout)
        dialog.setGeometry(QStyle.alignedRect(Qt.LeftToRight, Qt.AlignCenter, dialog.sizeHint(), app.desktop().availableGeometry()))
        dialog.exec_()

    def set_opacity(self, value):
        opacity = value / 100
        self.setWindowOpacity(opacity)
        self.save_ui_config()

    def save_ui_config(self):
        settings = QSettings('PomodoroApp', 'PomodoroTimer')
        settings.setValue('windowOpacity', self.windowOpacity())
        color_styles = self.timer_label.styleSheet().split("background-color: rgba(")[-1].split(");")[0]
        settings.setValue('backgroundColor', color_styles)
        settings.setValue('fontColor', self.timer_label.palette().color(QPalette.WindowText).name())
        settings.setValue('geometry', self.saveGeometry())
        settings.setValue('startTime', self.start_time.toString())
        settings.setValue('breakTime', self.break_time.toString())

    def load_ui_config(self):
        settings = QSettings('PomodoroApp', 'PomodoroTimer')
        opacity = settings.value('windowOpacity', 0.5, type=float)
        self.setWindowOpacity(opacity)
        background_color = settings.value('backgroundColor', "0, 0, 0, 0.5")
        font_color = settings.value('fontColor', "#FFFFFF")  # Default to white if not set
        self.timer_label.setStyleSheet(f"font-size: 30px; color: {font_color}; background-color: rgba({background_color}); padding: 10px; border-radius: 10px;")
        self.play_pause_button.setStyleSheet(f"background-color: rgba({background_color}); padding: 5px; border-radius: 5px;")
        self.reset_button.setStyleSheet(f"background-color: rgba({background_color}); padding: 5px; border-radius: 5px;")
        self.break_button.setStyleSheet(f"background-color: rgba({background_color}); padding: 5px; border-radius: 5px;")
        self.menu_button.setStyleSheet(f"background-color: rgba({background_color}); padding: 5px; border-radius: 5px;")
        self.edit_task_button.setStyleSheet(f"background-color: rgba({background_color}); padding: 5px; border-radius: 5px;")
        self.completed_tasks_label.setStyleSheet(f"font-size: 14px; color: {font_color}; background: transparent; padding: 5px; border-radius: 5px;")
        if settings.contains('geometry'):
            self.restoreGeometry(settings.value('geometry'))
        if settings.contains('startTime'):
            self.start_time = QTime.fromString(settings.value('startTime'))
            self.time_left = self.start_time
            self.timer_label.setText(self.time_left.toString('mm:ss'))
        if settings.contains('breakTime'):
            self.break_time = QTime.fromString(settings.value('breakTime'))
        self.set_font_color(font_color)


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.save_ui_config()
            event.accept()

    def resizeEvent(self, event):
        self.save_ui_config()
        super().resizeEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    timer = PomodoroTimer()
    timer.show()
    sys.exit(app.exec_())

