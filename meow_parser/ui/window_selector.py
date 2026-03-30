#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
窗口管理器模块
"""

import threading
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
import psutil
from ..constants import IS_WINDOWS, IS_LINUX

if IS_WINDOWS:
    import win32gui
    import win32process


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
        self.tree.setHeaderLabels(['进程名', '窗口标题', '状态'])
        self.tree.setColumnWidth(0, 150)
        self.tree.setColumnWidth(1, 500)
        self.tree.setColumnWidth(2, 100)
        self.tree.itemDoubleClicked.connect(self.toggle_window)
        
        # 启用排序功能
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(2, Qt.SortOrder.DescendingOrder)
        
        layout.addWidget(self.tree)
        
        # 提示标签
        hint_label = QLabel("双击窗口项目可切换启用状态 | 点击列标题可排序")
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
                    self.allowed_windows[window_key] = True
                    self.refresh_windows()
                return
            
            # 切换状态
            if window_key in self.allowed_windows:
                del self.allowed_windows[window_key]
            else:
                self.allowed_windows[window_key] = True
            
            self.refresh_windows()
        except Exception as e:
            print(f"切换窗口状态错误: {e}")
    
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
                    
                    if is_debug_window:
                        self.allowed_windows[window_key] = True
                        enabled = "✓ 已启用（锁定）"
                        sort_key = "0"
                    else:
                        if window_key in self.allowed_windows:
                            enabled = "✓ 已启用"
                            sort_key = "1"
                        else:
                            enabled = "✗ 未启用"
                            sort_key = "2"
                    
                    item = QTreeWidgetItem(self.tree)
                    item.setText(0, process_name)
                    item.setText(1, title)
                    item.setText(2, enabled)
                    
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
