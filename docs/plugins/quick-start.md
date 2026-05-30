## 代码规范

您的应用主类必须继承自 `PluginBase`，并提供一个get_widget函数以便于控制界面。

## 最小示例

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout
from qfluentwidgets import FluentIcon as FIF, BodyLabel
from my_functools import PluginBase

class MinimalPlugin(PluginBase):
    name = "Plugins Name" # 填入插件名称
    description = "Plugins Description" # 插件描述，需要短于 20 字，超出 20 字的部分将省略。
    icon = FIF.INFO # 插件图标，可以使用 FluentIcon 或 QIcon。为了统一，最好使用的是 FluentIcon。

    def get_widget(self, parent=None) -> QWidget: # 界面内容
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)

        label = BodyLabel("Plugin Content", widget)
        layout.addWidget(label)

        return widget
```

## 最小 MediaWiki 操作示例

如果您需要更多的 MediaWiki 操作类的帮助，请参阅[操作类列表](mediawiki/list.md)。

```python
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHeaderView, QHBoxLayout
from qfluentwidgets import (FluentIcon as FIF, SubtitleLabel, BodyLabel,
                            LineEdit, PrimaryPushButton, TableWidget)
from my_functools import PluginBase, Func, MediaWikiManage

class AuditTablePlugin(PluginBase):
    name = "审核列表"
    icon = FIF.APPLICATION
    description = "查看未审核页面"

    def get_widget(self, parent=None) -> QWidget:
        widget = QWidget(parent)
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)

        # 标题
        title = SubtitleLabel("审核列表", widget)
        layout.addWidget(title)

        hint = BodyLabel("输入机器人密码后点击按钮获取数据", widget)
        layout.addWidget(hint)

        # 输入框

        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)

        self.name_input = LineEdit(widget)
        self.name_input.setPlaceholderText("机器人用户名")
        input_layout.addWidget(self.name_input)

        self.pwd_input = LineEdit(widget)
        self.pwd_input.setPlaceholderText("机器人密码")
        self.pwd_input.setEchoMode(LineEdit.Password)
        input_layout.addWidget(self.pwd_input)

        layout.addLayout(input_layout)

        # 获取按钮
        self.fetch_btn = PrimaryPushButton(FIF.SYNC, "获取列表", widget)
        self.fetch_btn.clicked.connect(self.fetch_data)
        layout.addWidget(self.fetch_btn)

        # 表格
        self.table = TableWidget(widget)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["页面标题", "状态"])
        # 让表格列自动拉伸
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)  # 隐藏行号
        layout.addWidget(self.table)

        return widget

    def fetch_data(self):
        username = self.name_input.text().strip()
        pwd = self.pwd_input.text().strip()
        if not pwd:
            self.table.setRowCount(1)
            self.table.setCellWidget(0, 0, BodyLabel("⚠️ 请输入密码"))
            return
        elif not username:
            self.table.setRowCount(1)
            self.table.setCellWidget(0, 0, BodyLabel("⚠️ 请输入用户名"))
            return

        api_url = "https://wiki.backroomszh.org/w/api.php"

        Func.log("开始获取审核列表...", "info")

        try:
            wiki = MediaWikiManage(api_url, username, pwd)
            data = wiki.fetch_unreviewed_list()

            unreviewed = data.get("unreviewed", [])
            # 清空表格旧数据
            self.table.setRowCount(0)

            if not unreviewed:
                self.table.setRowCount(1)
                self.table.setItem(0, 0, "暂无待审核页面")
                self.table.setSpan(0, 0, 1, 2)  # 合并单元格
                return

            for item in unreviewed:
                row = self.table.rowCount()
                self.table.insertRow(row)
                title = item.get('title', '无标题')
                # 注意：TableWidget 的 setItem 需要 QTableWidgetItem，这里我们直接创建
                from PySide6.QtWidgets import QTableWidgetItem
                self.table.setItem(row, 0, QTableWidgetItem(title))
                self.table.setItem(row, 1, QTableWidgetItem("待审核"))

            Func.log(f"成功加载 {len(unreviewed)} 条数据", "task")

        except Exception as e:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, f"❌ 出错: {str(e)}")
```
