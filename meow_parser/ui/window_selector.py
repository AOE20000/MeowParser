#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
窗口管理器模块
"""

import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDialog,
    QLabel, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem,
    QCheckBox, QGroupBox, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
import psutil
from ..constants import IS_WINDOWS, IS_LINUX

if IS_WINDOWS:
    import win32gui
    import win32process


class WindowConfigDialog(QDialog):
    """窗口配置对话框"""
    
    def __init__(self, parent, window_key, config):
        super().__init__(parent)
        self.window_key = window_key
        self.config = config or {}
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle(f"窗口配置 - {self.window_key}")
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # 窗口信息
        info_label = QLabel(f"窗口：{self.window_key}")
        info_label.setStyleSheet("font-weight: bold; padding: 10px;")
        layout.addWidget(info_label)
        
        # 基本设置组
        basic_group = QGroupBox("基本设置")
        basic_layout = QVBoxLayout()
        
        self.enabled_checkbox = QCheckBox("启用此窗口")
        self.enabled_checkbox.setChecked(self.config.get("enabled", True))
        basic_layout.addWidget(self.enabled_checkbox)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # 触发器设置组
        trigger_group = QGroupBox("触发器设置")
        trigger_layout = QVBoxLayout()
        
        # 自定义触发器
        trigger_hint = QLabel("自定义触发器（留空使用默认空格键）：")
        trigger_hint.setStyleSheet("color: gray;")
        trigger_layout.addWidget(trigger_hint)
        
        trigger_input_layout = QHBoxLayout()
        trigger_input_layout.addWidget(QLabel("触发键："))
        self.trigger_input = QLineEdit()
        self.trigger_input.setPlaceholderText("例如：u（输入u后按空格触发）")
        self.trigger_input.setText(self.config.get("trigger_key", ""))
        self.trigger_input.setMaxLength(10)
        trigger_input_layout.addWidget(self.trigger_input)
        trigger_layout.addLayout(trigger_input_layout)
        
        trigger_example = QLabel("示例：设置为 'u'，则输入 'u' 后按空格触发悬浮窗")
        trigger_example.setStyleSheet("color: gray; font-size: 10px; padding-left: 20px;")
        trigger_layout.addWidget(trigger_example)
        
        trigger_group.setLayout(trigger_layout)
        layout.addWidget(trigger_group)
        
        # 输入模式设置组
        mode_group = QGroupBox("输入模式")
        mode_layout = QVBoxLayout()
        
        self.direct_input_checkbox = QCheckBox("直接输入模式")
        self.direct_input_checkbox.setChecked(self.config.get("direct_input", False))
        mode_layout.addWidget(self.direct_input_checkbox)
        
        mode_hint = QLabel(
            "启用后，回车时直接输入文本并回车，跳过重新激活输入框的流程。\n"
            "适用于不需要点击输入框即可直接输入的窗口。"
        )
        mode_hint.setStyleSheet("color: gray; font-size: 10px; padding-left: 20px;")
        mode_hint.setWordWrap(True)
        mode_layout.addWidget(mode_hint)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # 按钮
        button_layout = QHBoxLayout()
        
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def get_config(self):
        """获取配置"""
        trigger_key = self.trigger_input.text().strip()
        
        return {
            "enabled": self.enabled_checkbox.isChecked(),
            "trigger_key": trigger_key if trigger_key else "",
            "direct_input": self.direct_input_checkbox.isChecked()
        }


class WindowSelector(QWidget):
    """窗口管理器（非模态窗口）"""
    
    # 添加信号用于线程间通信
    update_signal = pyqtSignal(dict)
    
    def __init__(self, parent, allowed_windows, save_callback):
        super().__init__(parent)
        self.allowed_windows = allowed_windows
        self.save_callback = save_callback
        self.window_list = {}
        self._refreshing = False
        
        # 连接信号
        self.update_signal.connect(self.update_tree)
        
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("窗口管理")
        self.setGeometry(100, 100, 800, 600)
        
        # 设置窗口标志（独立窗口）
        self.setWindowFlags(Qt.WindowType.Window)
        
        layout = QVBoxLayout()
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索窗口：")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.filter_windows)
        search_layout.addWidget(self.search_input)
        
        layout.addLayout(search_layout)
        
        # 窗口列表
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['进程名', '窗口标题', '状态', '触发器', '模式'])
        self.tree.setColumnWidth(0, 150)
        self.tree.setColumnWidth(1, 350)
        self.tree.setColumnWidth(2, 100)
        self.tree.setColumnWidth(3, 80)
        self.tree.setColumnWidth(4, 80)
        self.tree.itemDoubleClicked.connect(self.toggle_window)
        
        # 启用右键菜单
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        
        # 启用排序功能
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(2, Qt.SortOrder.DescendingOrder)
        
        layout.addWidget(self.tree)
        
        # 提示标签
        hint_label = QLabel("双击切换启用状态 | 右键配置窗口 | 点击列标题排序")
        hint_label.setStyleSheet("color: gray;")
        layout.addWidget(hint_label)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("刷新窗口列表")
        self.refresh_btn.clicked.connect(self.refresh_windows)
        button_layout.addWidget(self.refresh_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # 延迟刷新，确保窗口已显示
        QTimer.singleShot(100, self.refresh_windows)
    
    def closeEvent(self, event):
        """关闭事件 - 保存设置"""
        try:
            # 停止所有定时器
            for timer in self.findChildren(QTimer):
                timer.stop()
            
            # 保存设置
            if self.save_callback:
                self.save_callback()
            
            # 接受关闭事件
            event.accept()
        except Exception as e:
            print(f"关闭窗口管理器错误: {e}")
            event.accept()
    
    def get_process_name(self, pid):
        """获取进程名"""
        try:
            return psutil.Process(pid).name()
        except:
            return "未知进程"
    
    def toggle_window(self, item, column):
        """切换窗口启用状态"""
        try:
            process_name = item.text(0)
            title = item.text(1)
            window_key = f"{process_name} - {title}"
            
            # 检查是否是调试窗口
            if title.strip() in ["MeowParser 调试窗口", "MeowParser调试窗口"]:
                # 调试窗口保持启用，不允许禁用
                if window_key not in self.allowed_windows:
                    self.allowed_windows[window_key] = {"enabled": True}
                    self.refresh_windows()
                return
            
            # 切换状态
            if window_key in self.allowed_windows:
                # 如果是字典，切换 enabled 状态
                if isinstance(self.allowed_windows[window_key], dict):
                    self.allowed_windows[window_key]["enabled"] = not self.allowed_windows[window_key].get("enabled", True)
                else:
                    # 旧格式（布尔值），删除
                    del self.allowed_windows[window_key]
            else:
                self.allowed_windows[window_key] = {"enabled": True}
            
            self.refresh_windows()
        except Exception as e:
            print(f"切换窗口状态错误: {e}")
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        item = self.tree.itemAt(position)
        if not item:
            return
        
        try:
            from PyQt6.QtWidgets import QMenu
            
            process_name = item.text(0)
            title = item.text(1)
            window_key = f"{process_name} - {title}"
            
            menu = QMenu(self)
            
            # 配置窗口
            config_action = menu.addAction("⚙️ 配置窗口...")
            config_action.triggered.connect(lambda: self.configure_window(window_key))
            
            menu.addSeparator()
            
            # 启用/禁用
            if window_key in self.allowed_windows:
                config = self.allowed_windows[window_key]
                enabled = config.get("enabled", True) if isinstance(config, dict) else config
                
                if enabled:
                    toggle_action = menu.addAction("❌ 禁用窗口")
                else:
                    toggle_action = menu.addAction("✅ 启用窗口")
            else:
                toggle_action = menu.addAction("✅ 启用窗口")
            
            toggle_action.triggered.connect(lambda: self.toggle_window(item, 0))
            
            menu.exec(self.tree.viewport().mapToGlobal(position))
            
        except Exception as e:
            print(f"显示右键菜单错误: {e}")
    
    def configure_window(self, window_key):
        """配置窗口"""
        try:
            # 获取当前配置
            if window_key in self.allowed_windows:
                config = self.allowed_windows[window_key]
                # 兼容旧格式
                if not isinstance(config, dict):
                    config = {"enabled": config}
            else:
                config = {"enabled": False}
            
            # 显示配置对话框
            dialog = WindowConfigDialog(self, window_key, config)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_config = dialog.get_config()
                self.allowed_windows[window_key] = new_config
                self.refresh_windows()
                
                if self.save_callback:
                    self.save_callback()
                
        except Exception as e:
            print(f"配置窗口错误: {e}")
            QMessageBox.critical(self, "错误", f"配置窗口失败: {e}")
    
    def refresh_windows(self):
        """刷新窗口列表"""
        # 防止重复刷新
        if self._refreshing:
            print("已在刷新中，跳过")
            return
        
        print("开始刷新窗口列表...")
        self._refreshing = True
        
        # 禁用刷新按钮，防止重复点击
        if hasattr(self, 'refresh_btn'):
            self.refresh_btn.setEnabled(False)
        
        self.tree.clear()
        self.window_list.clear()
        
        # 添加加载提示
        loading_item = QTreeWidgetItem(self.tree)
        loading_item.setText(1, "正在加载窗口列表...")
        
        # 在后台线程中枚举窗口
        def do_refresh():
            temp_list = {}
            
            try:
                if IS_WINDOWS:
                    print("Windows 平台，开始枚举窗口...")
                    
                    # 获取当前窗口管理器的 hwnd，避免枚举自己导致死锁
                    try:
                        window_handle = self.windowHandle()
                        if window_handle:
                            self_hwnd = int(window_handle.winId())
                        else:
                            self_hwnd = None
                    except:
                        self_hwnd = None
                    
                    print(f"窗口管理器 hwnd: {self_hwnd}")
                    
                    def enum_windows_callback(hwnd, _):
                        try:
                            # 跳过窗口管理器自己
                            if self_hwnd and hwnd == self_hwnd:
                                return True
                            
                            if win32gui.IsWindowVisible(hwnd):
                                title = win32gui.GetWindowText(hwnd)
                                if title and len(title.strip()) > 0:
                                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                                    process_name = self.get_process_name(pid)
                                    window_key = f"{process_name} - {title}"
                                    temp_list[window_key] = hwnd
                        except Exception as e:
                            print(f"枚举窗口错误: {e}")
                        return True
                    
                    try:
                        win32gui.EnumWindows(enum_windows_callback, None)
                        print(f"枚举完成，找到 {len(temp_list)} 个窗口")
                    except Exception as e:
                        print(f"EnumWindows 错误: {e}")
                else:
                    print("Linux 平台，开始枚举窗口...")
                    # Linux: 使用 wmctrl 或 xdotool
                    try:
                        import subprocess
                        result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True, timeout=2)
                        if result.returncode == 0:
                            for line in result.stdout.strip().split('\n'):
                                parts = line.split(None, 3)
                                if len(parts) >= 4:
                                    window_id = parts[0]
                                    title = parts[3]
                                    # 尝试获取进程名
                                    try:
                                        pid_result = subprocess.run(['xdotool', 'getwindowpid', window_id],
                                                                  capture_output=True, text=True, timeout=1)
                                        if pid_result.returncode == 0:
                                            pid = int(pid_result.stdout.strip())
                                            process_name = self.get_process_name(pid)
                                        else:
                                            process_name = "Unknown"
                                    except:
                                        process_name = "Unknown"
                                    
                                    window_key = f"{process_name} - {title}"
                                    temp_list[window_key] = window_id
                            print(f"枚举完成，找到 {len(temp_list)} 个窗口")
                    except FileNotFoundError:
                        print("wmctrl 未安装")
                    except Exception as e:
                        print(f"Linux 窗口枚举错误: {e}")
            except Exception as e:
                print(f"刷新窗口列表错误: {e}")
            finally:
                # 使用信号发送结果到主线程
                print(f"发送信号更新 UI，窗口数: {len(temp_list)}")
                try:
                    self.update_signal.emit(temp_list)
                except Exception as e:
                    print(f"发送信号错误: {e}")
        
        # 启动后台线程
        thread = threading.Thread(target=do_refresh, daemon=True)
        thread.start()
        print("后台线程已启动")
    
    def update_tree(self, temp_list):
        """更新树形控件"""
        print(f"update_tree 被调用，窗口数: {len(temp_list)}")
        try:
            # 临时禁用排序以提高性能
            self.tree.setSortingEnabled(False)
            self.tree.clear()
            self.window_list = temp_list
            
            if not temp_list:
                # 没有找到窗口
                no_window_item = QTreeWidgetItem(self.tree)
                no_window_item.setText(1, "未找到窗口")
                print("未找到任何窗口")
                return
            
            added_count = 0
            for window_key, hwnd in self.window_list.items():
                try:
                    parts = window_key.split(" - ", 1)
                    if len(parts) != 2:
                        continue
                    
                    process_name, title = parts
                    
                    # 检查是否是调试窗口
                    is_debug_window = title.strip() in ["MeowParser 调试窗口", "MeowParser调试窗口"]
                    
                    # 获取窗口配置
                    if window_key in self.allowed_windows:
                        config = self.allowed_windows[window_key]
                        # 兼容旧格式
                        if not isinstance(config, dict):
                            config = {"enabled": config}
                            self.allowed_windows[window_key] = config
                    else:
                        config = {"enabled": False}
                    
                    enabled = config.get("enabled", False)
                    trigger_key = config.get("trigger_key", "")
                    direct_input = config.get("direct_input", False)
                    
                    if is_debug_window:
                        self.allowed_windows[window_key] = {"enabled": True}
                        enabled_text = "✓ 已启用（锁定）"
                        sort_key = "0"
                    else:
                        if enabled:
                            enabled_text = "✓ 已启用"
                            sort_key = "1"
                        else:
                            enabled_text = "✗ 未启用"
                            sort_key = "2"
                    
                    # 触发器显示
                    if trigger_key:
                        trigger_text = f"'{trigger_key}'+空格"
                    else:
                        trigger_text = "空格"
                    
                    # 模式显示
                    if direct_input:
                        mode_text = "直接输入"
                    else:
                        mode_text = "标准"
                    
                    item = QTreeWidgetItem(self.tree)
                    item.setText(0, process_name)
                    item.setText(1, title)
                    item.setText(2, enabled_text)
                    item.setText(3, trigger_text)
                    item.setText(4, mode_text)
                    
                    # 设置隐藏的排序键
                    item.setData(2, Qt.ItemDataRole.UserRole, sort_key)
                    
                    added_count += 1
                except Exception as e:
                    print(f"添加窗口项错误: {e}")
            
            print(f"成功添加 {added_count} 个窗口到列表")
            
            # 重新启用排序
            self.tree.setSortingEnabled(True)
            self.tree.sortByColumn(2, Qt.SortOrder.DescendingOrder)
            
        except Exception as e:
            print(f"更新树形控件错误: {e}")
        finally:
            self._refreshing = False
            # 重新启用刷新按钮
            if hasattr(self, 'refresh_btn'):
                self.refresh_btn.setEnabled(True)
            print("刷新完成")
    
    def filter_windows(self, search_text):
        """过滤窗口列表"""
        search_text = search_text.lower()
        
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            process_name = item.text(0).lower()
            title = item.text(1).lower()
            
            # 显示或隐藏项目
            if search_text in process_name or search_text in title:
                item.setHidden(False)
            else:
                item.setHidden(True)
