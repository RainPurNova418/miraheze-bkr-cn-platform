import sys
import os
import time
import locale
import subprocess
import json
import requests
import importlib.util
import inspect
import pytz
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QApplication
from qfluentwidgets import (CardWidget, IconWidget, TitleLabel, BodyLabel, FluentIcon as FIF,
                            FluentIconBase, ToolButton, TextEdit, PrimaryPushButton)
from qframelesswindow import FramelessWindow, TitleBar
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from PySide6.QtSvg import QSvgRenderer
import functools

class Func:
    # 类变量，用于标记是否已初始化 Windows ANSI 支持
    _ansi_initialized = False

    # ==================== 硬编码中文映射表 ====================
    _texts = {
        "locale": "zh_CN",
        "ProgramAlready": "应用启动成功!",
        "scsExited": "已退出应用。",
        "title": "Miraheze 后室中文站务平台",
        "err": "错误",
        "task": "后台任务",
        "warn": "警告",
        "info": "提示",
        "other": "其他",
        "startend": "开始/结束",
        "white": "白色",
        "home": "主页",
        "settings": "设置",
        "new": "新建",
        "new_clicked": "新建卡片已点击。",
        "recover_clicked": "恢复卡片已点击。",
        "exit_clicked": "退出卡片已点击。",
        "theme_light": "亮色",
        "theme_dark": "暗色",
        "theme_sunset": "根据日落时间",
        "theme_system": "根据电脑设置",
        "page_home": "主页",
        "page_new": "新建",
        "appearance_group_title": "外观与调节",
        "theme_setting_title": "主题模式",
        "theme_setting_content": "选择应用的配色方案",
        "default_page_title": "默认启动界面",
        "default_page_content": "选择应用启动时显示的页面",
        "display_test_group_title": "显示测试",
        "test_group_title": "测试",
        "about_group_title": "关于",
        "about_card_title": "关于应用",
        "about_card_content": "版本 {version}\n许可证: GPLv3",
        "about_card_button": "访问主页",
        "window_size_title": "默认启动大小",
        "window_size_content": "选择窗口启动时的大小",
        "window_size_16_9": "16:9",
        "window_size_maximized": "最大化",
        "high_dpi_title": "启用高DPI缩放",
        "high_dpi_content": "启用高DPI缩放以优化在高分辨率屏幕上的显示效果",
        "high_dpi_not_supported": "此设备似乎无法正常启用高DPI设置。",
        "restart_title": "重启应用",
        "restart_content": "高DPI设置将在下次启动时生效。",
        "new_content": "开始新的项目",
        "recover": "恢复到上次",
        "recover_content": "恢复上次编辑的内容",
        "exit": "退出",
        "exit_content": "关闭应用",
        "about_tool_tip": "单击跳转至站务组页面。",
        "plugins": "插件",
        "api_init": "正在初始化 API 连接...",
        "fetch_token": "正在获取登录令牌...",
        "logging_in": "正在登录...",
        "login_success": "登录成功！",
        "login_failed": "登录失败：{reason}",
        "fetch_changes": "正在获取最近更改...",
        "fetched_count": "共获取到 {count} 条原始记录",
        "processing_complete": "处理完成！已保存 {count} 条记录到 {file}",
        "missing_deps": "缺少依赖库: {error}，请执行 pip install cloudscraper pytz tqdm",
        "exception_login_failed": "登录失败",
        "processing_changes": "处理更改记录：",
        "cache_dir_created": "创建缓存目录: {dir}",
        "cache_dir_exists": "缓存目录已存在: {dir}",
        "unit_1": "条",
        "NoThing_Application": "暂无插件",
        "back_to_plugins": "返回插件列表"
    }

    @classmethod
    def log(cls, msg, msgtype=None):
        if cls.log_frequency(msgtype):
            cls.LogBase(msg, msgtype)

    @classmethod
    def LogBase(cls, msg, msgtype=None):
        """
        输出带颜色的文本到控制台
        Args:
            msg (str): 需要处理的文本
            msgtype (str): 日志的类型
        Returns:
            经过 ANSI 处理过后的 Log
        Example:
            >>> Func.log("It's a simple log!","info")
            [2026/02/27 13:41:46] [INFO] It's a simple log!
        """
        # 颜色名称到 ANSI 颜色码的映射
        map_codes = {
            'err': '31',
            'task': '32',
            'warn': '33',
            'info': '34',
            'other': '35',
            'startend': '36',
            'white': '37',
            'reset': '0'
        }

        if msgtype and msgtype.lower() in map_codes and sys.stdout.isatty():
            if sys.platform == 'win32' and not cls._ansi_initialized:
                cls._enable_windows_ansi()
                cls._ansi_initialized = True
            timestrap = time.strftime('%Y-%m-%d %H:%M:%S')
            sys.stdout.write(f'\033[{map_codes[msgtype.lower()]}m[{timestrap}] [{cls.get_info(msgtype.lower())}] {msg}\033[0m\n')
        else:
            print(msg)

    @staticmethod
    def _enable_windows_ansi():
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            h = kernel32.GetStdHandle(-11)
            mode = ctypes.c_ulong()
            if kernel32.GetConsoleMode(h, ctypes.byref(mode)):
                mode.value |= 0x0004
                kernel32.SetConsoleMode(h, mode)
        except Exception:
            pass

    @staticmethod
    def get_info(index: str):
        """返回硬编码的中文字符串"""
        return Func._texts.get(index, index)

    @staticmethod
    def read_json(fileName: str):
        with open(Func.resource_path(fileName), 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data

    @staticmethod
    def write_json(fileName: str, data):
        """写入 JSON 文件"""
        with open(Func.resource_path(fileName), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)

    @staticmethod
    def get_system_language():
        lang = None

        if sys.platform == 'win32':
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                lang_id = kernel32.GetUserDefaultUILanguage()
                lang = locale.windows_locale.get(lang_id)
                if lang:
                    lang = lang.replace('-', '_')
            except Exception:
                pass
        else:
            for env_var in ['LC_ALL', 'LC_MESSAGES', 'LANG']:
                full_lang = os.environ.get(env_var, '')
                if full_lang and full_lang.lower() != 'c':
                    lang = full_lang.split('.')[0].split(':')[0]
                    break

            if not lang:
                try:
                    default_locale = locale.getdefaultlocale()
                    if default_locale and default_locale[0]:
                        lang = default_locale[0]
                except Exception:
                    pass

            if not lang and sys.platform == 'darwin':
                try:
                    result = subprocess.run(
                        ['defaults', 'read', '-g', 'AppleLocale'],
                        capture_output=True, text=True, check=True
                    )
                    lang = result.stdout.strip()
                except Exception:
                    pass
        if not lang or lang.lower() == 'c':
            lang = 'en_US'
        return lang

    @staticmethod
    def log_frequency(msgtype: str):
        config = Func.read_json("assets/config.json")
        if config["log_requency"] == "off":
            return False
        elif config["log_requency"] == "basic" and msgtype and msgtype.lower() != "err":
            return False
        elif config["log_requency"] == "normal" and msgtype and (msgtype.lower() not in ("err", "warn")):
            return False
        else:
            return True

    @staticmethod
    def time_now():
        t = time.strftime('%H:%M:%S').split(":")
        return [int(t[0]), int(t[1])]

    @staticmethod
    def is_high_dpi_supported():
        """
        检测当前设备是否支持高DPI缩放。
        支持条件：
        - Windows: 不在远程桌面会话中，且系统版本 >= Windows 8 (6.2)
        - 其他平台：默认支持
        """
        if sys.platform == 'win32':
            try:
                import ctypes
                # 检测是否在远程桌面会话中
                user32 = ctypes.windll.user32
                SM_REMOTESESSION = 0x1000
                is_remote = user32.GetSystemMetrics(SM_REMOTESESSION) != 0
                if is_remote:
                    return False

                # 检测Windows版本（低于Windows 8可能不支持良好）
                version = sys.getwindowsversion()
                if version.major < 6 or (version.major == 6 and version.minor < 2):
                    # Windows 7 (6.1) 及以下
                    return False
            except Exception:
                pass
        # 默认认为支持
        return True

    @staticmethod
    def set_high_dpi(enable: bool):
        """
        设置Qt的高DPI缩放属性（必须在QApplication创建前调用）
        """
        if enable:
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        else:
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, False)

    # ========== 其他方法 ==========
    @staticmethod
    def ensure_cache_dir(cache_dir: str = "cache") -> str:
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            Func.log(Func.get_info("cache_dir_created").format(dir=cache_dir), "info")
        else:
            Func.log(Func.get_info("cache_dir_exists").format(dir=cache_dir), "info")
        return cache_dir

    def fetch_recent_changes(
        api_url: str,
        username: str,
        password: str,
        output_file: str = "processed_changes.json",
        limit: int = 150,
        tz_name: str = "Asia/Shanghai"
    ) -> list:
        manager = MediaWikiManage(api_url, username, password)
        return manager.fetch_recent_changes(output_file=output_file, limit=limit, tz_name=tz_name)

    @staticmethod
    def load_plugins(plugin_dir="plugins"):
        plugins = []
        if not os.path.exists(plugin_dir):
            Func.log(f"插件目录 {plugin_dir} 不存在", "warn")
            return plugins
        Func.log(f"扫描插件目录: {plugin_dir}", "info")
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                module_name = filename[:-3]
                filepath = os.path.join(plugin_dir, filename)
                Func.log(f"尝试加载 {filepath}", "info")
                spec = importlib.util.spec_from_file_location(module_name, filepath)
                module = importlib.util.module_from_spec(spec)
                try:
                    spec.loader.exec_module(module)
                    Func.log(f"成功加载模块 {module_name}", "info")
                except Exception as e:
                    Func.log(f"加载模块 {filename} 失败: {e}", "err")
                    continue
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, PluginBase) and obj is not PluginBase:
                        try:
                            plugin_instance = obj()
                            plugins.append(plugin_instance)
                            Func.log(f"成功实例化插件 {name}", "info")
                        except Exception as e:
                            Func.log(f"实例化插件 {name} 失败: {e}", "err")
        Func.log(f"共加载 {len(plugins)} 个插件", "info")
        return plugins


class ClickableCard(CardWidget):
    clicked = Signal()
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.rect().contains(event.pos()):
            self.clicked.emit()


class ClickableBodyLabel(BodyLabel):
    """可点击的 BodyLabel，发出 clicked 信号"""
    clicked = Signal()
    def mouseReleaseEvent(self, event):
        self.clicked.emit()
        super().mouseReleaseEvent(event)


class SvgIcon(FluentIconBase):
    """从 SVG 字符串创建 FluentIcon"""
    def __init__(self, svg_data: str):
        super().__init__()
        self._svg_data = svg_data

    def icon(self, theme=None) -> QIcon:
        renderer = QSvgRenderer(QByteArray(self._svg_data.encode()))
        pixmap = QPixmap(24, 24)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        return QIcon(pixmap)


def create_svg_icon(svg_data: str, color: QColor, size: int = 24) -> QIcon:
    hex_color = color.name()
    modified_svg = svg_data.replace('currentColor', hex_color)
    renderer = QSvgRenderer(QByteArray(modified_svg.encode()))
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return QIcon(pixmap)


# ==================== 警告框图标 SVG 数据 ====================
INFO_SVG = '''<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path fill="currentColor" d="M12 2c5.524 0 10.002 4.478 10.002 10.002 0 5.523-4.478 10.001-10.002 10.001-5.524 0-10.002-4.478-10.002-10.001C1.998 6.477 6.476 2 12 2Zm-.004 8.25a1 1 0 0 0-.992.885l-.007.116.003 5.502.007.117a1 1 0 0 0 1.987-.002L13 16.75l-.003-5.501-.007-.117a1 1 0 0 0-.994-.882ZM12 6.5a1.251 1.251 0 1 0 0 2.503A1.251 1.251 0 0 0 12 6.5Z"/>
</svg>'''

ERROR_SVG = '''<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path fill="currentColor" d="M12 2c5.523 0 10 4.478 10 10s-4.477 10-10 10S2 17.522 2 12 6.477 2 12 2Zm.002 13.004a.999.999 0 1 0 0 1.997.999.999 0 0 0 0-1.997ZM12 7a1 1 0 0 0-.993.884L11 8l.002 5.001.007.117a1 1 0 0 0 1.986 0l.007-.117L13 8l-.007-.117A1 1 0 0 0 12 7Z"/>
</svg>'''

WARNING_SVG = '''<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path fill="currentColor" d="M9.5 3a7.5 7.5 0 0 0-6.797 10.675 68.094 68.094 0 0 0-.681 3.142.996.996 0 0 0 1.153 1.17c.623-.11 1.978-.36 3.236-.65A7.5 7.5 0 1 0 9.5 3Zm-.038 16a7.473 7.473 0 0 0 5.1 2c1.1 0 2.145-.237 3.088-.663 1.043.244 2.186.488 2.913.64a1.244 1.244 0 0 0 1.467-1.5c-.162-.703-.418-1.795-.671-2.803A7.503 7.503 0 0 0 17.015 6.41a8.44 8.44 0 0 1 .8 2.048 5.995 5.995 0 0 1 2.747 5.042c0 .992-.24 1.925-.665 2.747l-.13.253.07.276c.228.895.467 1.9.642 2.65-.774-.163-1.818-.39-2.74-.61l-.264-.062-.243.121c-.804.4-1.71.625-2.67.625a5.974 5.974 0 0 1-2.92-.756 8.517 8.517 0 0 1-2.18.256Z"/>
</svg>'''

MERGE_SVG = '''<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path fill="currentColor" d="M10.498 12.504a1 1 0 0 1 .993.884l.007.116v7.504a1 1 0 0 1-1.993.117l-.007-.117v-5.093l-5.79 5.792a1 1 0 0 1-1.32.083l-.095-.083a1 1 0 0 1-.083-1.32l.083-.095 5.788-5.788H2.997a1 1 0 0 1-.117-1.993l.117-.007h7.501ZM13.5 2a1 1 0 0 1 .993.883L14.5 3v5.087l5.794-5.793a1 1 0 0 1 1.32-.084l.094.083a1 1 0 0 1 .083 1.32l-.083.095-5.796 5.795H21a1 1 0 0 1 .116 1.994l-.116.007h-7.502a1 1 0 0 1-.993-.883l-.007-.117V2.999a1 1 0 0 1 1-1Z"/>
</svg>'''

BLOCKED_SVG = '''<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path fill="currentColor" d="M12 2.001c5.524 0 10 4.477 10 10s-4.476 10-10 10c-5.522 0-10-4.477-10-10s4.478-10 10-10Zm4.25 9.25h-8.5a.75.75 0 0 0 0 1.5h8.5a.75.75 0 0 0 0-1.5Z"/>
</svg>'''

ADD_SVG = '''<svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path fill="currentColor" d="M5.5 2A2.5 2.5 0 0 0 3 4.5v15A2.5 2.5 0 0 0 5.5 22h7.31a6.518 6.518 0 0 1-1.078-1.5H5.5a1 1 0 0 1-1-1h6.813a6.5 6.5 0 0 1 8.187-8.187V4.5A2.5 2.5 0 0 0 17 2H5.5ZM7 5h8a1 1 0 0 1 1 1v1a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1Zm16 12.5a5.5 5.5 0 1 0-11 0 5.5 5.5 0 0 0 11 0Zm-5 .5.001 2.503a.5.5 0 1 1-1 0V18h-2.505a.5.5 0 1 1 0-1H17v-2.5a.5.5 0 1 1 1 0V17h2.503a.5.5 0 1 1 0 1h-2.502Z"/>
</svg>'''

LEVEL_COLORS = {
    "info": QColor(44, 125, 160),
    "error": QColor(217, 83, 79),
    "warning": QColor(230, 126, 34),
    "merge": QColor(90, 110, 154),
    "blocked": QColor(155, 89, 182),
    "add": QColor(46, 204, 113),
}


class WarningBox(QFrame):
    def __init__(self, title: str, content: str, level: str = "info", parent=None):
        super().__init__(parent)
        self.level = level
        self.setObjectName("warningBox")
        self.setProperty("level", level)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)

        svg_map = {
            "info": INFO_SVG,
            "error": ERROR_SVG,
            "warning": WARNING_SVG,
            "merge": MERGE_SVG,
            "blocked": BLOCKED_SVG,
            "add": ADD_SVG,
        }
        svg_data = svg_map.get(level, INFO_SVG)
        color = LEVEL_COLORS.get(level, QColor(243, 167, 18))
        icon = create_svg_icon(svg_data, color, size=20)

        icon_widget = IconWidget()
        icon_widget.setFixedSize(20, 20)
        icon_widget.setIcon(icon)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title_label = BodyLabel(title)
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        title_label.setStyleSheet(title_label.styleSheet() + f"color: {color.name()}; font-weight: bold;")

        content_label = BodyLabel(content)
        content_label.setWordWrap(True)
        content_label.setStyleSheet("color: #5c3b00;" if level in ["info","warning","merge"] else "color: #dddddd;")

        text_layout.addWidget(title_label)
        text_layout.addWidget(content_label)

        layout.addWidget(icon_widget)
        layout.addLayout(text_layout, 1)


class MediaWikiManage:
    """MediaWiki API 操作封装类（使用 requests）"""
    def __init__(self, api_url: str, username: str, password: str):
        self.api_url = api_url
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'UlimaBot/1.0 (contact@example.com)'})
        self._logged_in = False

    def _login(self):
        if self._logged_in:
            return

        Func.log(Func.get_info("fetch_token"), "info")
        params_token = {'action': 'query', 'meta': 'tokens', 'type': 'login', 'format': 'json'}
        r = self.session.get(self.api_url, params=params_token)
        r.raise_for_status()
        token = r.json()['query']['tokens']['logintoken']

        Func.log(Func.get_info("logging_in"), "info")
        params_login = {
            'action': 'login',
            'lgname': self.username,
            'lgpassword': self.password,
            'lgtoken': token,
            'format': 'json'
        }
        r = self.session.post(self.api_url, data=params_login)
        r.raise_for_status()
        login_data = r.json()
        if login_data['login']['result'] != 'Success':
            reason = login_data['login'].get('reason', Func.get_info("exception_login_failed"))
            Func.log(Func.get_info("login_failed").format(reason=reason), "err")
            raise Exception(Func.get_info("exception_login_failed"))
        self._logged_in = True
        Func.log(Func.get_info("login_success"), "task")

    def fetch_recent_changes(self, output_file: str = "processed_changes.json", limit: int = 150, tz_name: str = "Asia/Shanghai") -> list:
        self._login()

        try:
            import pytz
            from datetime import datetime
            from tqdm import tqdm
        except ImportError as e:
            Func.log(Func.get_info("missing_deps").format(error=e), "err")
            raise

        def _process(raw_data: list, limit: int, tz_name: str) -> list:
            filtered = [item for item in raw_data if item.get('type') in ('new', 'edit')][:limit]
            processed = []
            tz = pytz.timezone(tz_name)
            for item in tqdm(filtered, desc=Func.get_info("fetch_changes")):
                ts = item.get('timestamp', '')
                if ts:
                    dt_utc = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                    dt_utc = dt_utc.replace(tzinfo=pytz.utc)
                    dt_local = dt_utc.astimezone(tz)
                    time_parts = [dt_local.year, dt_local.month, dt_local.day,
                                  dt_local.hour, dt_local.minute, dt_local.second]
                    edit_time_local = dt_local.isoformat()
                else:
                    time_parts = [0, 0, 0, 0, 0, 0]
                    edit_time_local = ''

                entry = {
                    "user": item.get('user', ''),
                    "title": item.get('title', ''),
                    "edit_time": edit_time_local,
                    "time": time_parts,
                    "old_length": item.get('oldlen', 0),
                    "new_length": item.get('newlen', 0),
                    "comment": item.get('comment', '')
                }
                processed.append(entry)
            return processed

        Func.log(Func.get_info("fetch_changes"), "info")
        params_rc = {
            'action': 'query',
            'list': 'recentchanges',
            'rcprop': 'user|comment|timestamp|title|ids|sizes|flags|tags',
            'rclimit': 500,
            'rctype': 'new',
            'rcnamespace': 0,          # 限制主命名空间（0）
            'format': 'json'
        }

        r = self.session.get(self.api_url, params=params_rc)
        r.raise_for_status()
        data = r.json()
        raw_data = data.get('query', {}).get('recentchanges', [])

        pbar = tqdm(desc=Func.get_info("fetch_changes"), unit="条", total=None, initial=len(raw_data))
        while 'continue' in data:
            params_rc.update(data['continue'])
            r = self.session.get(self.api_url, params=params_rc)
            r.raise_for_status()
            data = r.json()
            new_data = data.get('query', {}).get('recentchanges', [])
            raw_data.extend(new_data)
            pbar.update(len(new_data))
        pbar.close()

        Func.log(Func.get_info("fetched_count").format(count=len(raw_data)), "info")

        result = _process(raw_data, limit, tz_name)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        Func.log(Func.get_info("processing_complete").format(count=len(result), file=output_file), "task")
        return result
    
    def get_page_content(self, title: str) -> str:
        """获取页面原始 wikitext"""
        self._login()
        params = {
            'action': 'query',
            'prop': 'revisions',
            'titles': title,
            'rvprop': 'content',
            'rvslots': 'main',
            'format': 'json'
        }
        r = self.session.get(self.api_url, params=params)
        r.raise_for_status()
        data = r.json()
        pages = data.get('query', {}).get('pages', {})
        for page_id, page_data in pages.items():
            if 'revisions' in page_data:
                return page_data['revisions'][0]['slots']['main']['*']  # 或直接 page_data['revisions'][0]['*']
        return ""   # 页面不存在时返回空字符串

    def edit_page(self, title: str, content: str, summary: str = "自动编辑") -> bool:
        """编辑页面内容"""
        self._login()
        # 获取编辑令牌
        params_token = {
            'action': 'query',
            'meta': 'tokens',
            'format': 'json'
        }
        r = self.session.get(self.api_url, params=params_token)
        r.raise_for_status()
        token = r.json()['query']['tokens']['csrftoken']

        # 执行编辑
        params_edit = {
            'action': 'edit',
            'title': title,
            'text': content,
            'summary': summary,
            'token': token,
            'format': 'json'
        }
        r = self.session.post(self.api_url, data=params_edit)
        r.raise_for_status()
        result = r.json()
        if 'edit' in result and result['edit'].get('result') == 'Success':
            return True
        else:
            # 记录错误信息
            error = result.get('edit', {}).get('error', {}).get('info', '未知错误')
            Func.log(f"编辑失败: {error}", "err")
            return False
    
    def fetch_unreviewed_list(self) -> dict:
        """从自定义审核 API 获取未审核列表及统计"""
        import time
        url = "https://admin.backroomszh.org/api/audit"
        max_retries = 3
        for attempt in range(max_retries):
            try:
                r = self.session.get(url, timeout=30)  # 增加到 30 秒
                r.raise_for_status()
                data = r.json()
                Func.log(f"审核数据获取成功：待审核{len(data.get('unreviewed',[]))}...", "info")
                return data
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    Func.log(f"获取审核数据失败（重试{max_retries}次后）: {e}", "err")
                    raise
            except Exception as e:
                Func.log(f"获取审核数据失败: {e}", "err")
                raise

    def create_status_if_not_exists(self, title: str, status: str) -> bool:
        """
        创建 Status:原标题 页面，内容为 {{Pass|~~~~}} 或 {{Fail|~~~~}}
        仅当页面不存在时才创建（createonly）
        返回 True 表示创建成功，False 表示页面已存在（跳过）
        """
        status_title = f"Status:{title}"
        content = "{{" + status + "|~~~~}}"

        # 获取编辑令牌
        params_token = {
            'action': 'query',
            'meta': 'tokens',
            'format': 'json'
        }
        r = self.session.get(self.api_url, params=params_token)
        r.raise_for_status()
        token = r.json()['query']['tokens']['csrftoken']

        # 编辑（创建）
        params_edit = {
            'action': 'edit',
            'title': status_title,
            'text': content,
            'summary': f"审核：标记为{status}",
            'token': token,
            'createonly': 1,          # 关键：仅创建
            'format': 'json'
        }
        r = self.session.post(self.api_url, data=params_edit)
        r.raise_for_status()
        result = r.json()

        if 'edit' in result and result['edit'].get('result') == 'Success':
            Func.log(f"创建状态页面成功：{status_title}", "task")
            return True
        else:
            # 如果页面已存在，createonly 会返回错误，但不会抛异常，我们要判断
            error = result.get('edit', {}).get('error', {}).get('code', '')
            if error == 'articleexists':
                Func.log(f"状态页面已存在，跳过：{status_title}", "info")
                return False
            else:
                err_info = result.get('edit', {}).get('error', {}).get('info', '未知错误')
                Func.log(f"创建状态页面失败：{status_title} - {err_info}", "err")
                raise Exception(f"创建状态页面失败：{err_info}")
    
    def fetch_unreviewed_list(self) -> dict:
        """从新API获取未审核列表及统计"""
        try:
            r = self.session.get("https://admin.backroomszh.org/api/audit", timeout=15)
            r.raise_for_status()
            data = r.json()
            Func.log(f"审核数据获取成功：待审核{len(data.get('unreviewed',[]))}，未过审{len(data.get('failed',[]))}，孤立{len(data.get('orphanedStatus',[]))}", "info")
            return data
        except Exception as e:
            Func.log(f"获取审核数据失败: {e}", "err")
            raise

    def get_batch_page_info(self, titles: list) -> dict:
        """
        批量获取页面的创建者信息（最早修订版本的用户）
        titles: 页面标题列表（最多50个一批）
        返回: {title: {"user": "创建者用户名", "timestamp": "创建时间ISO", "edit_time": "格式化时间"}}
        """
        from datetime import datetime
        result = {}
        for i in range(0, len(titles), 50):
            batch = titles[i:i+50]
            params = {
                'action': 'query',
                'prop': 'revisions',
                'titles': '|'.join(batch),
                'rvprop': 'user|timestamp',
                'rvlimit': 1,
                'rvdir': 'newer',          # 🔥 关键：按时间升序，取最早的修订（即创建版本）
                'format': 'json'
            }
            r = self.session.get(self.api_url, params=params)
            r.raise_for_status()
            pages = r.json().get('query', {}).get('pages', {})
            for page_id, info in pages.items():
                title = info.get('title', '')
                revs = info.get('revisions', [])
                if revs:
                    user = revs[0].get('user', '未知')
                    ts = revs[0].get('timestamp', '')
                    try:
                        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                        tz = pytz.timezone("Asia/Shanghai")
                        local_dt = dt.astimezone(tz)
                        edit_time = local_dt.strftime("%Y-%m-%d %H:%M")
                    except:
                        edit_time = ts
                    result[title] = {"user": user, "timestamp": ts, "edit_time": edit_time}
                else:
                    result[title] = {"user": "未知", "timestamp": "", "edit_time": ""}
        return result

class PluginBase:
    """插件基类，所有插件必须继承并实现以下方法和属性"""
    name = "未命名插件"
    description = "这个插件的作者很懒，没有写简介。"
    icon = None  # 可以是 FluentIcon 枚举值或 QIcon 实例

    def get_widget(self, parent=None) -> QWidget:
        """返回插件的界面，会在卡片点击时显示"""
        raise NotImplementedError