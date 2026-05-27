from PySide6.QtCore import Qt, QDateTime, QTimer
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import FluentIcon as FIF, SubtitleLabel, BodyLabel, PrimaryPushButton
from my_functools import PluginBase, Func

import random

class HelloPlugin(PluginBase):

    def __init__(self):
        super().__init__()
        # 一段很神秘的代码
        global random_list
        random_list=["越过长城，走向世界。","世界，你好。","I am because you are."]
        self.name = "你好，世界。"
        self.icon = FIF.GLOBE
        self.description = random.choice(random_list)

    def get_widget(self, parent=None) -> QWidget:
        widget = QWidget(parent)
        widget.setObjectName("helloPluginWidget")
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # 标题
        title_label = SubtitleLabel("🌍 你好，世界！", widget)
        layout.addWidget(title_label, alignment=Qt.AlignCenter)

        self.time_label = BodyLabel(widget)
        layout.addWidget(self.time_label, alignment=Qt.AlignCenter)

        self.greeting_label = BodyLabel(widget)
        layout.addWidget(self.greeting_label, alignment=Qt.AlignCenter)

        self.update_time()
        self.update_greeting()

        self.timer = QTimer(widget)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        self.hour_timer = QTimer(widget)
        self.hour_timer.timeout.connect(self.update_greeting)
        self.hour_timer.start(60000)

        # 刷新按钮（手动触发也可）
        refresh_btn = PrimaryPushButton(FIF.SYNC, "刷新", widget)
        refresh_btn.clicked.connect(self.manual_refresh)
        layout.addWidget(refresh_btn, alignment=Qt.AlignCenter)

        return widget

    def manual_refresh(self):
        self.update_time()
        self.update_greeting()
        Func.log("插件: 手动刷新", "info")

    def update_time(self):
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
        self.time_label.setText(f"当前时间：{current_time}")

    def update_greeting(self):
        hour = QDateTime.currentDateTime().time().hour()
        if 5 <= hour < 12:
            text = "早上好！☀️"
        elif 12 <= hour < 18:
            text = "下午好！🌤️"
        else:
            text = "晚上好！🌙"
        self.greeting_label.setText(text)
