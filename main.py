import sys
import os
import json
import random
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from qframelesswindow import FramelessWindow, TitleBar
from qfluentwidgets import FluentWindow, NavigationItemPosition, SplashScreen, \
                            TitleLabel, CardWidget, IconWidget, BodyLabel, \
                            Pivot, SettingCardGroup, \
                            ComboBoxSettingCard, PrimaryPushSettingCard, \
                            OptionsConfigItem, QConfig, OptionsValidator, \
                            qconfig, setTheme, Theme, SubtitleLabel, FluentIcon as FIF, \
                            GroupHeaderCardWidget, ComboBox, SwitchButton, CheckBox, \
                            ToolButton, ToolTipPosition, ToolTipFilter, LineEdit, ScrollArea, \
                            PrimaryPushButton, TextEdit, RadioButton, PushButton, MessageBox
from qframelesswindow import *
from my_functools import *

CONFIG_PATH = Func.resource_path("assets/config.json")
SETTINGS_PATH = Func.resource_path("assets/settings.json")

class Config(QConfig):
    theme = OptionsConfigItem(
        "Settings", "Theme", "light",
        OptionsValidator(["light", "dark", "sunset", "system"]),
        restart=False
    )
    defaultPage = OptionsConfigItem(
        "Settings", "DefaultPage", "home",
        OptionsValidator(["home", "new"]),
        restart=False
    )
    defaultWindowSize = OptionsConfigItem(
        "Settings", "DefaultWindowSize", "16:9",
        OptionsValidator(["16:9", "maximized"]),
        restart=False
    )
    high_dpi_enabled = OptionsConfigItem(
        "Settings", "HighDpiEnabled", True,
        OptionsValidator([True, False]),
        restart=False
    )


cfg = None


class AppearanceCard(GroupHeaderCardWidget):
    def __init__(self, cfg, parent=None):
        super().__init__(parent)
        self.cfg = cfg
        self.setTitle(Func.get_info("appearance_group_title"))
        self.setBorderRadius(8)

        self.themeComboBox = ComboBox(self)
        self.themeComboBox.addItems([
            Func.get_info("theme_light"),
            Func.get_info("theme_dark"),
            Func.get_info("theme_sunset"),
            Func.get_info("theme_system")
        ])
        current_theme = self.cfg.theme.value
        theme_options = ["light", "dark", "sunset", "system"]
        theme_index = theme_options.index(current_theme) if current_theme in theme_options else 0
        self.themeComboBox.setCurrentIndex(theme_index)
        self.themeComboBox.currentIndexChanged.connect(self.onThemeChanged)

        self.defaultPageComboBox = ComboBox(self)
        self.defaultPageComboBox.addItems([
            Func.get_info("page_home"),
            Func.get_info("page_new")
        ])
        current_page = self.cfg.defaultPage.value
        page_index = 0 if current_page == "home" else 1
        self.defaultPageComboBox.setCurrentIndex(page_index)
        self.defaultPageComboBox.currentIndexChanged.connect(self.onDefaultPageChanged)

        self.windowSizeComboBox = ComboBox(self)
        self.windowSizeComboBox.addItems([
            Func.get_info("window_size_16_9"),
            Func.get_info("window_size_maximized")
        ])
        current_size = self.cfg.defaultWindowSize.value
        size_index = 0 if current_size == "16:9" else 1
        self.windowSizeComboBox.setCurrentIndex(size_index)
        self.windowSizeComboBox.currentIndexChanged.connect(self.onWindowSizeChanged)

        self.addGroup(
            FIF.PALETTE,
            Func.get_info("theme_setting_title"),
            Func.get_info("theme_setting_content"),
            self.themeComboBox
        )
        self.addGroup(
            FIF.HOME,
            Func.get_info("default_page_title"),
            Func.get_info("default_page_content"),
            self.defaultPageComboBox
        )
        self.addGroup(
            FIF.FIT_PAGE,
            Func.get_info("window_size_title"),
            Func.get_info("window_size_content"),
            self.windowSizeComboBox
        )

    def onThemeChanged(self, index: int):
        theme_map = ["light", "dark", "sunset", "system"]
        if 0 <= index < len(theme_map):
            self.cfg.set(self.cfg.theme, theme_map[index])

    def onDefaultPageChanged(self, index: int):
        page_map = ["home", "new"]
        if 0 <= index < len(page_map):
            self.cfg.set(self.cfg.defaultPage, page_map[index])

    def onWindowSizeChanged(self, index: int):
        size_map = ["16:9", "maximized"]
        if 0 <= index < len(size_map):
            self.cfg.set(self.cfg.defaultWindowSize, size_map[index])

class HomePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("homePage")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 30, 0, 10)
        homeTitle = TitleLabel(title, self)
        homeTitle.setAlignment(Qt.AlignHCenter)
        font = homeTitle.font()
        font.setPointSize(16)
        homeTitle.setFont(font)
        layout.addWidget(homeTitle)

        card_layout = QHBoxLayout()
        card_layout.setAlignment(Qt.AlignHCenter)

        self.card_new = self.create_card(FIF.ADD, Func.get_info("new"), Func.get_info("new_content"), card_layout)
        self.card_plugins = self.create_card(FIF.APPLICATION, "插件", "为站务平台的功能添砖加瓦", card_layout)
        self.card_exit = self.create_card(FIF.CLOSE, Func.get_info("exit"), Func.get_info("exit_content"), card_layout)

        layout.addLayout(card_layout)
        layout.addStretch()

        self.card_new.clicked.connect(self.on_new_clicked)
        self.card_plugins.clicked.connect(self.on_plugins_clicked)
        self.card_exit.clicked.connect(self.on_exit_clicked)

    def create_card(self, icon, title, content, layout):
        card = ClickableCard(self)
        card.setFixedSize(200, 150)
        inner_layout = QVBoxLayout(card)
        inner_layout.setSpacing(5)
        inner_layout.setAlignment(Qt.AlignCenter)
        icon_widget = IconWidget(icon, card)
        icon_widget.setFixedSize(40, 40)
        inner_layout.addWidget(icon_widget)
        title_label = SubtitleLabel(title, card)
        title_label.setTextColor(QColor(0, 0, 0), QColor(255, 255, 255))
        title_label.setStyleSheet("font-weight: bold;")
        inner_layout.addWidget(title_label)
        content_label = BodyLabel(content, card)
        content_label.setStyleSheet("color: gray;")
        inner_layout.addWidget(content_label)
        layout.addWidget(card)
        return card

    def on_new_clicked(self):
        Func.log(Func.get_info("new_clicked"), "task")
        main_win = self.window()
        if main_win and hasattr(main_win, 'new_page'):
            main_win.switchTo(main_win.new_page)

    def on_plugins_clicked(self):
        Func.log("导引到插件被点击", "task")
        main_win = self.window()
        if main_win and hasattr(main_win, 'plugins_page'):
            main_win.switchTo(main_win.plugins_page)

    def on_exit_clicked(self):
        Func.log(Func.get_info("exit_clicked"), "task")
        self.window().close()


class SettingPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settingPage")
        self.vBoxLayout = QVBoxLayout(self)
        self.pivot = Pivot(self)
        self.stackedWidget = QStackedWidget(self)
        self.vBoxLayout.addWidget(self.pivot)
        self.vBoxLayout.addWidget(self.stackedWidget)

        self.appearanceInterface = QWidget()
        self.testInterface = QWidget()
        self.aboutInterface = QWidget()
        self.appearanceInterface.setObjectName("appearanceInterface")
        self.testInterface.setObjectName("testInterface")
        self.aboutInterface.setObjectName("aboutInterface")

        self.stackedWidget.addWidget(self.appearanceInterface)
        self.stackedWidget.addWidget(self.testInterface)
        self.stackedWidget.addWidget(self.aboutInterface)

        self.pivot.addItem(
            routeKey="appearanceInterface",
            text=Func.get_info("appearance_group_title"),
            onClick=lambda: self.stackedWidget.setCurrentWidget(self.appearanceInterface)
        )
        self.pivot.addItem(
            routeKey="testInterface",
            text=Func.get_info("test_group_title"),
            onClick=lambda: self.stackedWidget.setCurrentWidget(self.testInterface)
        )
        self.pivot.addItem(
            routeKey="aboutInterface",
            text=Func.get_info("about_group_title"),
            onClick=lambda: self.stackedWidget.setCurrentWidget(self.aboutInterface)
        )

        self.setupAppearanceInterface()
        self.setupTestInterface()
        self.setupAboutInterface()

        self.stackedWidget.setCurrentWidget(self.appearanceInterface)
        self.pivot.setCurrentItem("appearanceInterface")

    def setupAppearanceInterface(self):
        layout = QVBoxLayout(self.appearanceInterface)
        self.appearanceCard = AppearanceCard(cfg, self.appearanceInterface)
        layout.addWidget(self.appearanceCard)
        layout.addStretch()

    def setupTestInterface(self):
        layout = QVBoxLayout(self.testInterface)

        # 高DPI卡片
        self.testCard = GroupHeaderCardWidget(self.testInterface)
        self.testCard.setTitle(Func.get_info("display_test_group_title"))
        self.testCard.setBorderRadius(8)

        screen = QApplication.primaryScreen()
        dpi = screen.logicalDotsPerInch() if screen else 96
        system_supported = Func.is_high_dpi_supported()
        self.highDpiSupported = system_supported and dpi >= 120
        high_dpi_enabled = cfg.high_dpi_enabled.value

        self.highDpiSwitch = SwitchButton(self.testCard)
        self.highDpiSwitch.setChecked(high_dpi_enabled)
        self.highDpiSwitch.setEnabled(self.highDpiSupported)
        self.highDpiSwitch.checkedChanged.connect(self.onHighDpiToggled)

        high_dpi_content = Func.get_info("high_dpi_content") if self.highDpiSupported else Func.get_info("high_dpi_not_supported")

        self.testCard.addGroup(
            FIF.ZOOM,
            Func.get_info("high_dpi_title"),
            high_dpi_content,
            self.highDpiSwitch
        )

        layout.addWidget(self.testCard)

        # 机器人配置卡片（自动保存）
        self.botCard = GroupHeaderCardWidget(self.testInterface)
        self.botCard.setTitle("自动化操作测试")
        self.botCard.setBorderRadius(8)

        config = Func.read_json(SETTINGS_PATH)
        default_api = config.get("bot_api", "https://mirror.backroomszh.org/api.php")
        default_user = config.get("bot_username", "")
        default_pass = config.get("bot_password", "")

        self.api_edit = LineEdit(self.botCard)
        self.api_edit.setPlaceholderText("MediaWiki API 地址")
        self.api_edit.setText(default_api)
        self.user_edit = LineEdit(self.botCard)
        self.user_edit.setPlaceholderText("机器人用户名（例如：Name@BotName）")
        self.user_edit.setText(default_user)
        self.pass_edit = LineEdit(self.botCard)
        self.pass_edit.setPlaceholderText("机器人密码")
        self.pass_edit.setText(default_pass)
        self.pass_edit.setEchoMode(QLineEdit.Password)

        # 🔥 使用 textChanged 即时保存，避免依赖焦点变化
        self.api_edit.textChanged.connect(self.on_bot_config_changed)
        self.user_edit.textChanged.connect(self.on_bot_config_changed)
        self.pass_edit.textChanged.connect(self.on_bot_config_changed)

        self.botCard.addGroup(FIF.GLOBE, "API地址", "Wiki 的 API 入口地址", self.api_edit)
        self.botCard.addGroup(FIF.PEOPLE, "用户名", "机器人账号，格式为 用户名@机器人标识", self.user_edit)
        self.botCard.addGroup(FIF.VPN, "密码", "机器人密码", self.pass_edit)

        layout.addWidget(self.botCard)
        layout.addStretch()

    def onHighDpiToggled(self, checked: bool):
        cfg.set(cfg.high_dpi_enabled, checked)
        QMessageBox.information(
            self,
            Func.get_info("restart_title"),
            Func.get_info("restart_content")
        )

    def on_bot_config_changed(self):
        config = Func.read_json(SETTINGS_PATH)
        config["bot_api"] = self.api_edit.text().strip()
        config["bot_username"] = self.user_edit.text().strip()
        config["bot_password"] = self.pass_edit.text().strip()
        Func.write_json(SETTINGS_PATH, config)

    def setupAboutInterface(self):
        layout = QVBoxLayout(self.aboutInterface)
        group = SettingCardGroup(Func.get_info("about_group_title"), self.aboutInterface)
        layout.addWidget(group)

        version = Func.read_json(CONFIG_PATH)["version"]
        about_title = Func.get_info("about_card_title")
        about_content = Func.get_info("about_card_content").format(version=version)
        button_text = Func.get_info("about_card_button")

        self.aboutCard = PrimaryPushSettingCard(
            text=button_text,
            icon=FIF.INFO,
            title=about_title,
            content=about_content,
            parent=self.aboutInterface
        )
        self.aboutCard.clicked.connect(self.onAboutButtonClicked)
        self.aboutCard.setToolTip(Func.get_info('about_tool_tip'))
        self.aboutCard.setToolTipDuration(1000)

        self.aboutCard.installEventFilter(ToolTipFilter(self.aboutCard, showDelay=3000, position=ToolTipPosition.TOP))
        group.addSettingCard(self.aboutCard)
        layout.addStretch()

    def onAboutButtonClicked(self):
        QDesktopServices.openUrl(QUrl("https://wiki.backroomszh.org/%E7%AB%99%E5%8A%A1%E7%BB%84"))


class NewPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("newPage")
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(30, 0, 30, 30)

        self.pivot = Pivot(self)
        self.stackedWidget = QStackedWidget(self)

        self.noticeGeneratorInterface = self.createNoticeGeneratorInterface()
        self.test2Interface = self.createtest2Interface()

        self.addSubInterface(self.noticeGeneratorInterface, 'noticeGeneratorInterface', '职员通知生成器')
        self.addSubInterface(self.test2Interface, 'test2Interface', '咕咕咕')

        self.stackedWidget.currentChanged.connect(self.onCurrentIndexChanged)
        self.stackedWidget.setCurrentWidget(self.noticeGeneratorInterface)
        self.pivot.setCurrentItem(self.noticeGeneratorInterface.objectName())

        self.vBoxLayout.addWidget(self.pivot)
        self.vBoxLayout.addWidget(self.stackedWidget)

    def createNoticeGeneratorInterface(self):
        container = QWidget()
        container.setObjectName("noticeGeneratorInterface")
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(12)

        id_layout = QHBoxLayout()
        id_layout.setSpacing(8)
        id_layout.addWidget(BodyLabel("占用编号："))
        self.lineEdit_name = LineEdit()
        self.lineEdit_name.setPlaceholderText("例如 Level CN 418 或 Level 114.5")
        self.lineEdit_name.setClearButtonEnabled(True)
        self.lineEdit_name.setMaximumWidth(300)
        id_layout.addWidget(self.lineEdit_name)
        id_layout.addStretch()
        main_layout.addLayout(id_layout)

        main_layout.addWidget(BodyLabel("违规类型："))

        try:
            config = Func.read_json("assets/config.json")
            content_list = config.get("content_list", [])
        except Exception as e:
            Func.log(f"读取配置文件失败: {e}", "err")
            content_list = []

        self.checkboxes = []
        grid = QGridLayout()
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setSpacing(10)
        row, col, max_cols = 0, 0, 3
        for text in content_list:
            cb = CheckBox(text, container)
            self.checkboxes.append(cb)
            grid.addWidget(cb, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        main_layout.addLayout(grid)

        other_layout = QHBoxLayout()
        other_layout.setContentsMargins(0, 5, 0, 0)
        self.other_checkbox = CheckBox("其他", container)
        self.other_checkbox.toggled.connect(self.on_other_toggled)
        other_layout.addWidget(self.other_checkbox)
        self.other_lineedit = LineEdit(container)
        self.other_lineedit.setPlaceholderText("请输入其他内容...")
        self.other_lineedit.setMaxLength(150)
        self.other_lineedit.setEnabled(False)
        other_layout.addWidget(self.other_lineedit)
        other_layout.addStretch()
        main_layout.addLayout(other_layout)

        main_layout.addWidget(BodyLabel("您已经如何处理："))
        action_options = [
            "已经将此页面删除",
            "计划在下个周日删除",
            "计划在下个10日删除",
            "计划在下个20日删除",
            "计划在下个30日删除",
            "已将此页面标记为 Fail",
            "已将其移动到您的个人沙盒",
        ]
        action_group = QButtonGroup(self)
        action_layout = QGridLayout()
        action_layout.setSpacing(8)
        self.action_buttons = []
        for i, opt in enumerate(action_options):
            rb = RadioButton(opt, container)
            action_group.addButton(rb)
            action_layout.addWidget(rb, i // 2, i % 2, Qt.AlignLeft)
            self.action_buttons.append(rb)
        action_group.setExclusive(True)
        self.action_buttons[0].setChecked(True)
        main_layout.addLayout(action_layout)

        main_layout.addWidget(BodyLabel("对于受到警告的人，他应该如何做："))
        how_options = [
            "对于主层群文章，先在个人沙盒翻译/改编，征求社群意见通过审核得到绿灯码后再发布，以确保内容高质量",
            "对于CN层群文章，先在个人沙盒完成文章，征求社群意见通过审核并得到认可后再发布，以确保内容质量达标"
        ]
        how_group = QButtonGroup(self)
        self.how_buttons = []
        for opt in how_options:
            row_layout = QHBoxLayout()
            rb = RadioButton(container)
            how_group.addButton(rb)
            row_layout.addWidget(rb, alignment=Qt.AlignTop)
            label = ClickableBodyLabel(opt, container)
            label.setWordWrap(True)
            label.clicked.connect(lambda rb=rb: rb.setChecked(True))
            row_layout.addWidget(label, stretch=1)
            main_layout.addLayout(row_layout)
            self.how_buttons.append(rb)
        self.how_buttons[0].setChecked(True)

        staff_layout = QHBoxLayout()
        staff_layout.addWidget(BodyLabel("职员名称："))
        self.lineEdit_staff = LineEdit(container)
        self.lineEdit_staff.setPlaceholderText("不需要带User:前缀")
        self.lineEdit_staff.setClearButtonEnabled(True)
        staff_layout.addWidget(self.lineEdit_staff, stretch=1)
        main_layout.addLayout(staff_layout)

        btn_layout = QHBoxLayout()
        self.generate_btn = PrimaryPushButton("生成通知", container, icon=FIF.SEND)
        self.generate_btn.clicked.connect(self.generate_notice)
        reset_btn = PushButton("重置", container, icon=FIF.SYNC)
        reset_btn.clicked.connect(self.reset_notice_form)
        btn_layout.addStretch()
        btn_layout.addWidget(self.generate_btn)
        btn_layout.addWidget(reset_btn)
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)

        self.result_text = TextEdit(container)
        self.result_text.setPlaceholderText("生成的通知将显示在这里...")
        self.result_text.setReadOnly(False)
        self.result_text.setMinimumHeight(200)
        self.result_text.setStyleSheet("""
            QTextEdit {
                color: palette(text);
                background-color: palette(base);
                selection-background-color: palette(highlight);
                selection-color: palette(highlighted-text);
            }
        """)
        main_layout.addWidget(self.result_text, stretch=1)

        self.lineEdit_name.textChanged.connect(self.on_number_changed)

        scroll = ScrollArea()
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)
        scroll.setObjectName("noticeGeneratorInterface_scroll")
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        container.setStyleSheet("background: transparent;")
        return scroll

    def on_other_toggled(self, checked):
        self.other_lineedit.setEnabled(checked)
        if not checked:
            self.other_lineedit.clear()

    def on_number_changed(self, text):
        if 'cn' in text.lower():
            if len(self.how_buttons) >= 2:
                self.how_buttons[1].setChecked(True)

    def get_selected_violations(self):
        selected = []
        for cb in self.checkboxes:
            if cb.isChecked():
                selected.append(cb.text())
        if self.other_checkbox.isChecked():
            other_text = self.other_lineedit.text().strip()
            if other_text:
                selected.append(f"其他：{other_text}")
            else:
                selected.append("其他（未填写）")
        return selected

    def get_occupied_id(self):
        return self.lineEdit_name.text().strip()

    def get_action(self):
        for rb in self.action_buttons:
            if rb.isChecked():
                return rb.text()
        return self.action_buttons[0].text()

    def get_how_text(self):
        for rb in self.how_buttons:
            if rb.isChecked():
                idx = self.how_buttons.index(rb)
                return [
                    "对于主层群文章，先在个人沙盒翻译/改编，征求社群意见通过审核得到绿灯码后再发布，以确保内容高质量",
                    "对于CN层群文章，先在个人沙盒完成文章，征求社群意见通过审核并得到认可后再发布，以确保内容质量达标"
                ][idx]
        return self.how_buttons[0].text()

    def get_staff_name(self):
        name = self.lineEdit_staff.text().strip()
        if name == self.lineEdit_staff.placeholderText():
            return ""
        return name

    def generate_notice(self):
        number = self.get_occupied_id()
        if not number:
            number = "（未填写）"

        selected = self.get_selected_violations()
        if selected:
            if len(selected) == 1:
                content_str = selected[0]
            else:
                connect_word = ["和", "及", "与", "跟", "以及", "且", "还有"]
                content_str = "、".join(selected[:-1]) + random.choice(connect_word) + selected[-1]
        else:
            content_str = "未选择任何内容类型"

        action = self.get_action()
        how_text = self.get_how_text()
        staff = self.get_staff_name()

        template = f"""您好！

    关注到您占用了 {number} 编号，并在对应页面中添加包含不适宜内容（具体来说，您的内容存在{content_str}的问题）的文章。您所发布的内容不符合[[The Backrooms Wiki:内容质量标准|《内容质量标准》]]对于语言的要求，且发布流程有违[[The Backrooms Wiki:站规|《站规》]]，编号占用不符合申请策略。

    鉴于此，我{action}，并发送此职员帖记一次警告，依据[[The Backrooms Wiki:站规|《站规》]]，再次收到警告可能导致封禁，请重视。

    为了更好地进行创作，请先仔细阅读[[The Backrooms Wiki:站规|《站规》]]和[[The Backrooms Wiki:内容质量标准|《内容质量标准》]]；{how_text}

    同时，如果您对此通知或本站创作方针有任何疑问，或希望交流创作，我们十分欢迎您在相应讨论页中提出，也可以给我留言或提出申诉，同样亦可加入QQ群组1019251088

    依据[[The Backrooms Wiki:职员通知条例|《职员通知暂行条例》]]，请在看到后第一时间此职员帖并尽快回复，谢谢您。

    ——版主{staff}"""

        self.result_text.setPlainText(template)
        self.result_text.moveCursor(QTextCursor.Start)

    def reset_notice_form(self):
        self.lineEdit_name.clear()
        for cb in self.checkboxes:
            cb.setChecked(False)
        self.other_checkbox.setChecked(False)
        self.other_lineedit.clear()
        self.other_lineedit.setEnabled(False)
        self.action_buttons[0].setChecked(True)
        self.how_buttons[0].setChecked(True)
        self.lineEdit_staff.clear()
        self.result_text.clear()

    def createtest2Interface(self):
        widget = QWidget()
        widget.setObjectName("test2Interface")
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.addWidget(BodyLabel("咕咕咕"))
        return widget

    def addSubInterface(self, widget, objectName, text):
        widget.setObjectName(objectName)
        self.stackedWidget.addWidget(widget)
        self.pivot.addItem(
            routeKey=objectName,
            text=text,
            onClick=lambda: self.stackedWidget.setCurrentWidget(widget)
        )

    def onCurrentIndexChanged(self, index):
        widget = self.stackedWidget.widget(index)
        self.pivot.setCurrentItem(widget.objectName())


class PluginCard(ClickableCard):
    def __init__(self, plugin, parent=None):
        super().__init__(parent)
        self.plugin = plugin
        self.setFixedSize(300, 169)
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(5)
        layout.setContentsMargins(30, 10, 30, 10)

        self.icon_widget = IconWidget(self)
        self.icon_widget.setIcon(plugin.icon)
        self.icon_widget.setFixedSize(48, 48)
        layout.addWidget(self.icon_widget)

        self.name_label = SubtitleLabel(plugin.name, self)
        self.name_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.name_label)

        desc = plugin.description
        if len(desc) > 20:
            desc = desc[:20] + "..."
        self.desc_label = BodyLabel(desc, self)
        self.desc_label.setWordWrap(True)
        self.desc_label.setAlignment(Qt.AlignCenter)
        self.desc_label.setMaximumWidth(560)
        self.desc_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        layout.addWidget(self.desc_label)


class PluginsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("pluginsPage")
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.stacked_widget = QStackedWidget(self)
        self.main_layout.addWidget(self.stacked_widget)

        self.cards_scroll = ScrollArea()
        self.cards_scroll.setWidgetResizable(True)
        self.cards_scroll.setStyleSheet("""
            QScrollArea, QScrollArea > QWidget, QScrollArea > QWidget > QWidget {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                background: transparent;
                width: 12px;
            }
            QScrollBar::handle:vertical {
                background: rgba(128,128,128,0.5);
                border-radius: 6px;
            }
        """)
        self.cards_content = QWidget()
        self.cards_content.setStyleSheet("background: transparent;")
        self.cards_scroll.setWidget(self.cards_content)

        self.cards_layout = QGridLayout(self.cards_content)
        self.cards_layout.setContentsMargins(20, 20, 20, 20)
        self.cards_layout.setHorizontalSpacing(20)
        self.cards_layout.setVerticalSpacing(20)
        self.cards_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)

        self.stacked_widget.addWidget(self.cards_scroll)

        self.plugins = Func.load_plugins()
        self.cards = []

        if not self.plugins:
            no_plugin_label = BodyLabel(Func.get_info("NoThing_Application"))
            no_plugin_label.setAlignment(Qt.AlignCenter)
            self.cards_layout.addWidget(no_plugin_label, 0, 0)
        else:
            self.populate_cards()

        self.parent().installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Resize and obj is self.parent():
            self.rearrange_cards()
        return super().eventFilter(obj, event)

    def populate_cards(self):
        for plugin in self.plugins:
            card = PluginCard(plugin, self.cards_content)
            card.clicked.connect(lambda p=plugin: self.show_plugin(p))
            self.cards.append(card)
        self.rearrange_cards()

    def rearrange_cards(self):
        if not self.cards:
            return
        viewport_width = self.cards_scroll.viewport().width()
        if viewport_width <= 0:
            viewport_width = self.parent().width() - 60
        card_width = 300
        spacing = self.cards_layout.horizontalSpacing()
        cols = max(1, (viewport_width + spacing) // (card_width + spacing))

        for i in reversed(range(self.cards_layout.count())):
            item = self.cards_layout.takeAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        for i, card in enumerate(self.cards):
            row = i // cols
            col = i % cols
            self.cards_layout.addWidget(card, row, col)

    def switch_to_widget(self, widget):
        current = self.stacked_widget.currentWidget()
        if current == widget:
            return

        if self.stacked_widget.indexOf(widget) == -1:
            self.stacked_widget.addWidget(widget)

        if hasattr(self, '_current_anim') and self._current_anim:
            self._current_anim.stop()
            self._current_anim.deleteLater()
            self._current_anim = None

        effect = widget.graphicsEffect()
        if not effect or not isinstance(effect, QGraphicsOpacityEffect):
            effect = QGraphicsOpacityEffect()
            widget.setGraphicsEffect(effect)

        effect.setOpacity(0)
        self.stacked_widget.setCurrentWidget(widget)

        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(200)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.finished.connect(lambda: effect.setOpacity(1))
        self._current_anim = anim
        anim.start()

    def show_plugin(self, plugin):
        for i in range(1, self.stacked_widget.count()):
            w = self.stacked_widget.widget(i)
            if w.property("plugin") == plugin:
                self.switch_to_widget(w)
                return

        container = QWidget()
        container.setProperty("plugin", plugin)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)

        try:
            back_icon = FIF.LEFT_ARROW
        except AttributeError:
            back_icon = FIF.CHEVRON_LEFT
        back_btn = PrimaryPushButton(back_icon, Func.get_info("back_to_plugins"))
        back_btn.clicked.connect(lambda: self.switch_to_widget(self.cards_scroll))
        back_btn.setMinimumWidth(100)
        back_btn.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        container_layout.addWidget(back_btn, alignment=Qt.AlignLeft)

        plugin_widget = plugin.get_widget(container)
        container_layout.addWidget(plugin_widget)

        self.switch_to_widget(container)

# ============================================================
#  审核页面 - ViewPage
#  需求：获取最近更改、预览、Pass/Fail、刷新、缓存加载
#  使用 QFluentWidgets，纯控件，无标题栏等原生部件
# ============================================================

class AuditDataSignals(QObject):
    finished = Signal(dict)   # 字典：unreviewed, failed, orphaned, counts
    error = Signal(str)

class AuditDataWorker(QRunnable):
    """获取审核数据：新API列表 + 批量作者信息"""
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
        self.signals = AuditDataSignals()

    def run(self):
        try:
            # 1. 获取新API数据
            raw = self.bot.fetch_unreviewed_list()
            unreviewed = raw.get('unreviewed', [])
            failed = raw.get('failed', [])
            orphaned = raw.get('orphanedStatus', [])

            # 2. 批量获取作者信息
            titles = [item['title'] for item in unreviewed]
            author_info = {}
            if titles:
                author_info = self.bot.get_batch_page_info(titles)

            # 3. 组装带作者的数据
            enriched_unreviewed = []
            for item in unreviewed:
                info = author_info.get(item['title'], {})
                enriched_unreviewed.append({
                    "pageid": item['pageid'],
                    "ns": item['ns'],
                    "title": item['title'],
                    "user": info.get('user', '未知'),
                    "edit_time": info.get('edit_time', '')
                })

            # 4. 返回完整数据
            global payload
            payload= {
                "unreviewed": enriched_unreviewed,
                "failed": failed,
                "orphaned": orphaned,
                "unreviewed_count": len(unreviewed),
                "failed_count": len(failed),
                "orphaned_count": len(orphaned)
            }
            self.signals.finished.emit(payload)
        except Exception as e:
            self.signals.error.emit(str(e))


class CreateStatusWorkerSignals(QObject):
    finished = Signal(bool)
    error = Signal(str)

class CreateStatusWorker(QRunnable):
    def __init__(self, bot, title, status):
        super().__init__()
        self.bot = bot
        self.title = title
        self.status = status
        self.signals = CreateStatusWorkerSignals()

    def run(self):
        try:
            self.bot._login()
            created = self.bot.create_status_if_not_exists(self.title, self.status)
            self.signals.finished.emit(created)
        except Exception as e:
            self.signals.error.emit(str(e))


class ViewCard(QFrame):
    def __init__(self, data, view_page, parent=None):
        super().__init__(parent)
        self.data = data
        self.view_page = view_page
        self.setFixedHeight(80)
        self.setStyleSheet("""
            ViewCard {
                background-color: rgba(255,255,255,0.05);
                border-radius: 8px;
                border: 1px solid rgba(128,128,128,0.3);
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        # 左侧：标题 + 作者
        left = QVBoxLayout()
        title_btn = PrimaryPushButton(data["title"], icon=FIF.DOCUMENT)
        title_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                border: none;
                background: transparent;
                font-weight: bold;
                color: #2c7da0;
                padding: 0;
            }
            QPushButton:hover { color: #1a5b7a; }
        """)
        title_btn.clicked.connect(self.preview)
        left.addWidget(title_btn)

        # 作者信息
        author_str = f"作者: {data.get('user', '未知')}"
        if data.get('edit_time'):
            author_str += f"  |  最后编辑: {data['edit_time']}"
        author_label = BodyLabel(author_str)
        author_label.setStyleSheet("color: gray; font-size: 12px;")
        left.addWidget(author_label)

        layout.addLayout(left, stretch=2)

        # 右侧按钮
        btn_layout = QHBoxLayout()
        pass_btn = PrimaryPushButton(FIF.ACCEPT, "Pass")
        fail_btn = PushButton(FIF.CANCEL, "Fail")
        pass_btn.clicked.connect(lambda: self.do_create_status("Pass"))
        fail_btn.clicked.connect(lambda: self.do_create_status("Fail"))
        btn_layout.addWidget(pass_btn)
        btn_layout.addWidget(fail_btn)
        layout.addLayout(btn_layout)

    def preview(self):
        """预览页面内容"""
        bot = self.view_page.get_bot()
        if bot is None:
            self.view_page.show_message("无法预览", "请先刷新列表以连接机器人。")
            return

        win = FramelessWindow()
        win.setWindowTitle(f"预览：{self.data['title']}")
        win.setWindowIcon(QIcon(Func.resource_path('assets/mhbkr.ico')))
        win.resize(800, 600)
        win.setAttribute(Qt.WA_DeleteOnClose)

        # 标题栏（显示最小化、最大化、关闭按钮）
        title_bar = TitleBar(win)
        win.setTitleBar(title_bar)
        # 确保按钮显示（默认即可，这里显式调用以防万一）
        title_bar.minBtn.show()
        title_bar.maxBtn.show()
        title_bar.closeBtn.show()

        # 主区域
        central = QWidget()
        v = QVBoxLayout(central)
        v.setContentsMargins(20, 20, 20, 20)

        text_edit = TextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlaceholderText("加载中…")
        text_edit.setStyleSheet("color: black; background: white; border: 1px solid #ddd; border-radius: 8px;")
        v.addWidget(text_edit, stretch=1)

        close_btn = PrimaryPushButton(FIF.CLOSE, "关闭预览")
        close_btn.clicked.connect(win.close)
        v.addWidget(close_btn, alignment=Qt.AlignRight)

        win_layout = QVBoxLayout(win)
        win_layout.setContentsMargins(0, 0, 0, 0)
        win_layout.addWidget(central)
        win.show()

        # 异步获取内容
        class ContentFetcher(QRunnable):
            def __init__(self, bot, title):
                super().__init__()
                self.bot = bot
                self.title = title
                self.signals = ContentSignals()
            def run(self):
                try:
                    content = self.bot.get_page_content(self.title)
                    self.signals.finished.emit(content)
                except Exception as e:
                    self.signals.error.emit(str(e))
        class ContentSignals(QObject):
            finished = Signal(str)
            error = Signal(str)

        fetcher = ContentFetcher(bot, self.data['title'])
        fetcher.signals.finished.connect(text_edit.setPlainText)
        fetcher.signals.error.connect(lambda e: text_edit.setPlainText(f"加载失败：{e}"))
        QThreadPool.globalInstance().start(fetcher)

    def do_create_status(self, status):
        bot = self.view_page.get_bot()
        if bot is None:
            self.view_page.show_message("操作失败", "机器人未连接。")
            return
        self.setEnabled(False)
        worker = CreateStatusWorker(bot, self.data['title'], status)
        worker.signals.finished.connect(lambda created: self.on_created(created, status))
        worker.signals.error.connect(lambda e: self.on_create_error(e, status))
        QThreadPool.globalInstance().start(worker)

    def on_created(self, created, status):
        self.setEnabled(True)
        if created:
            self.view_page.show_message("成功", f"已为 {self.data['title']} 添加 {status} 票")
            Func.log(f"上票：{self.data['title']} → {status}", "task")
            self.view_page.remove_card(self)
        else:
            self.view_page.show_message("跳过", "状态页面已存在")
            Func.log(f"上票跳过：{self.data['title']}", "info")
            self.view_page.remove_card(self)   # 已处理也移除

    def on_create_error(self, err, status):
        self.setEnabled(True)
        self.view_page.show_message("失败", str(err))
        Func.log(f"上票失败：{self.data['title']} → {status}，错误：{err}", "err")


class ViewPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("viewPage")
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # ---------- 顶部统计 + 排序 ----------
        top_layout = QHBoxLayout()
        self.stats_label = BodyLabel("待审核: 0 | 未过审: 0 | 孤立Status: 0")
        self.stats_label.setStyleSheet("font-weight: bold;")
        top_layout.addWidget(self.stats_label, stretch=2)

        # 刷新按钮
        self.refresh_btn = PrimaryPushButton(FIF.SYNC, "刷新列表")
        self.refresh_btn.clicked.connect(self.refresh_list)
        top_layout.addWidget(self.refresh_btn)

        # 排序下拉框
        self.sort_combo = ComboBox()
        self.sort_combo.addItems(["按标题", "按ID", "按编辑时间", "按编辑者"])
        self.sort_combo.currentIndexChanged.connect(self.sort_cards)
        top_layout.addWidget(self.sort_combo, alignment=Qt.AlignRight)
        self.layout.addLayout(top_layout)

        # ---------- 滚动卡片区域 ----------
        self.scroll = ScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        self.cards_container = QWidget()
        self.cards_container.setStyleSheet("background: transparent;")
        self.cards_layout = QVBoxLayout(self.cards_container)
        self.cards_layout.setAlignment(Qt.AlignTop)
        self.cards_layout.setSpacing(10)
        self.scroll.setWidget(self.cards_container)
        self.layout.addWidget(self.scroll)

        self.empty_label = BodyLabel("暂无未审核文章")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setVisible(False)
        self.layout.addWidget(self.empty_label)

        self.bot = None
        self.cards = []          # ViewCard 列表
        self.all_data = []       # 原始 enriched 数据
        self.failed = []
        self.orphaned = []

        # 尝试加载缓存（可选，为了简化这里省略，需要可自行添加）
        Func.log("新审核页面初始化完成", "info")

    def get_bot(self):
        return self.bot

    def refresh_list(self):
        config = Func.read_json(SETTINGS_PATH)
        api_url = config.get("bot_api", "")
        username = config.get("bot_username", "")
        password = config.get("bot_password", "")
        if not api_url or not username or not password:
            self.show_message("配置缺失", "请先在设置页面配置机器人账号。")
            return

        self.bot = MediaWikiManage(api_url, username, password)
        self.refresh_btn.setEnabled(False)
        self.refresh_btn.setText("加载中…")
        Func.log("开始刷新审核数据", "task")

        worker = AuditDataWorker(self.bot)
        worker.signals.finished.connect(self.on_data_ready)
        worker.signals.error.connect(self.on_data_error)
        QThreadPool.globalInstance().start(worker)

    def on_data_ready(self, payload):
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("刷新列表")

        # 保存统计数据
        self.all_data = payload['unreviewed']
        self.failed = payload['failed']
        self.orphaned = payload['orphaned']
        self.update_stats_label()

        # 生成卡片
        self.clear_cards()
        for item in self.all_data:
            card = ViewCard(item, self)
            self.cards_layout.addWidget(card)
            self.cards.append(card)

        self.show_content(bool(self.cards))
        Func.log(f"审核数据加载完成：待审核{len(self.all_data)}条", "task")

    def on_data_error(self, err):
        self.refresh_btn.setEnabled(True)
        self.refresh_btn.setText("刷新列表")
        self.show_message("加载失败", str(err))
        Func.log(f"审核数据加载失败: {err}", "err")

    def update_stats_label(self):
        self.stats_label.setText(
            f"待审核: {payload.get('unreviewed_count',0)}  |  "
            f"未过审: {payload.get('failed_count',0)}  |  "
            f"孤立Status: {payload.get('orphaned_count',0)}"
        )
        # 注意：此处 payload 在 on_data_ready 中使用局部变量，需保存到 self 或直接使用 self 的计数
        # 下面修复：在 on_data_ready 中保存 counts
        self.unreviewed_count = payload['unreviewed_count']
        self.failed_count = payload['failed_count']
        self.orphaned_count = payload['orphaned_count']
        self.stats_label.setText(
            f"待审核: {self.unreviewed_count}  |  "
            f"未过审: {self.failed_count}  |  "
            f"孤立Status: {self.orphaned_count}"
        )

    def sort_cards(self, index):
        """根据下拉框索引排序当前卡片"""
        key_map = {
            0: lambda x: x.data['title'].lower(),
            1: lambda x: x.data['pageid'],
            2: lambda x: x.data.get('edit_time', ''),
            3: lambda x: x.data.get('user', '')
        }
        key_func = key_map.get(index, key_map[0])
        self.cards.sort(key=key_func)
        # 重新布局
        self.clear_layout()
        for card in self.cards:
            self.cards_layout.addWidget(card)

    def clear_layout(self):
        while self.cards_layout.count():
            child = self.cards_layout.takeAt(0)
            if child.widget():
                child.widget().setParent(None)  # 保留对象，不delete

    def clear_cards(self):
        self.clear_layout()
        self.cards.clear()

    def remove_card(self, card):
        """从界面和列表中移除指定卡片"""
        if card in self.cards:
            self.cards.remove(card)
            self.cards_layout.removeWidget(card)
            card.deleteLater()
            # 更新统计数据
            self.unreviewed_count -= 1
            self.update_stats_label_direct()
            if not self.cards:
                self.show_content(False)

    def update_stats_label_direct(self):
        self.stats_label.setText(
            f"待审核: {self.unreviewed_count}  |  "
            f"未过审: {self.failed_count}  |  "
            f"孤立Status: {self.orphaned_count}"
        )

    def show_content(self, has_content):
        self.cards_container.setVisible(has_content)
        self.empty_label.setVisible(not has_content)

    def show_message(self, title, text):
        msg = MessageBox(title, text, self)
        msg.yesButton.setText("确定")
        msg.cancelButton.hide()
        msg.exec()

class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(Func.resource_path('assets/mhbkr.ico')))
        self.setWindowTitle(title)

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(204, 204))
        self.show()

        loop = QEventLoop(self)
        QTimer.singleShot(3000, loop.quit)
        loop.exec()

        self.initNavigation()
        self.applyStyleSheet()

        cfg.theme.valueChanged.connect(self.onThemeChanged)
        self.onThemeChanged(cfg.theme.value)

        self.sunset_timer = QTimer(self)
        self.sunset_timer.timeout.connect(self.checkSunsetTheme)
        self.sunset_timer.start(60000)

        # 修复最大化挡住任务栏
        screen_geom = QApplication.primaryScreen().availableGeometry()
        if cfg.defaultWindowSize.value == "maximized":
            self.setGeometry(screen_geom)
        else:
            target_width = int(screen_geom.width() * 0.8)
            target_height = int(target_width * 9 / 16)
            if target_height > screen_geom.height():
                target_height = int(screen_geom.height() * 0.8)
                target_width = int(target_height * 16 / 9)
            x = (screen_geom.width() - target_width) // 2
            y = (screen_geom.height() - target_height) // 2
            self.setGeometry(x, y, target_width, target_height)

        self.show()
        self.splashScreen.finish()

        if cfg.defaultPage.value == "new":
            self.switchTo(self.new_page)
        else:
            self.switchTo(self.home_page)

    def checkSunsetTheme(self):
        if cfg.theme.value == "sunset":
            self.onThemeChanged("sunset")

    def initNavigation(self):
        self.home_page = HomePage(self)
        self.setting_page = SettingPage(self)
        self.new_page = NewPage(self)
        self.plugins_page = PluginsPage(self)
        self.view_page = ViewPage(self)

        self.addSubInterface(
            self.home_page,
            FIF.HOME,
            Func.get_info("home"),
            position=NavigationItemPosition.TOP
        )
        self.addSubInterface(
            self.new_page,
            FIF.ADD,
            Func.get_info("new"),
            position=NavigationItemPosition.SCROLL
        )
        self.addSubInterface(
            self.view_page,
            FIF.VIEW,
            "审核",
            position=NavigationItemPosition.SCROLL
        )
        self.addSubInterface(
            self.plugins_page,
            FIF.APPLICATION,
            Func.get_info("plugins"),
            position=NavigationItemPosition.SCROLL
        )
        self.addSubInterface(
            self.setting_page,
            FIF.SETTING,
            Func.get_info("settings"),
            position=NavigationItemPosition.BOTTOM
        )

    def onThemeChanged(self, theme: str):
        if theme == "light":
            setTheme(Theme.LIGHT)
        elif theme == "dark":
            setTheme(Theme.DARK)
        elif theme == "sunset":
            hour = Func.time_now()[0]
            if hour >= 18 or hour < 6:
                setTheme(Theme.DARK)
            else:
                setTheme(Theme.LIGHT)
        elif theme == "system":
            setTheme(Theme.AUTO)
        else:
            Func.log(f"Unknown theme: {theme}", "warn")

        try:
            self.applyStyleSheet()
        except Exception as e:
            Func.log(f"应用样式表失败: {e}", "err")

    def applyStyleSheet(self):
        theme = cfg.theme.value
        if theme in ["light", "dark"]:
            qss_file = Func.resource_path(f"assets/style/{theme}.qss")
            if os.path.exists(qss_file):
                with open(qss_file, 'r', encoding='utf-8') as f:
                    qss = f.read()
                QApplication.instance().setStyleSheet(qss)
            else:
                Func.log(f"样式文件 {qss_file} 不存在", "warn")
        else:
            QApplication.instance().setStyleSheet("")

if __name__ == "__main__":
    Func.log(Func.get_info("ProgramAlready"), "STARTEND")

    cfg = Config()
    qconfig.load(SETTINGS_PATH, cfg)

    high_dpi_enabled = cfg.high_dpi_enabled.value

    if not Func.is_high_dpi_supported():
        if high_dpi_enabled:
            high_dpi_enabled = False
            cfg.set(cfg.high_dpi_enabled, False)

    Func.set_high_dpi(high_dpi_enabled)

    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)
    app.aboutToQuit.connect(lambda: Func.log(Func.get_info("scsExited"), "STARTEND"))

    title = Func.get_info("title") + " v" + Func.read_json(CONFIG_PATH)["version"]

    window = MainWindow()
    window.show()
    sys.exit(app.exec())