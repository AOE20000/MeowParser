#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统托盘图标管理模块
"""

from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont, QAction
from PyQt6.QtCore import Qt


class TrayIconManager:
    """系统托盘图标管理器"""
    
    def __init__(self, parent_app):
        """
        初始化托盘图标管理器
        
        Args:
            parent_app: 父应用实例，需要提供以下方法：
                - toggle(): 切换启用/禁用
                - show_window_manager(): 显示窗口管理器
                - show_replacement_editor(): 显示规则编辑器
                - show_debug_window(): 显示调试窗口
                - quit_app(): 退出应用
                - is_admin: 是否管理员权限（属性）
        """
        self.parent_app = parent_app
        self.tray_icon = None
        self.toggle_action = None
        self.setup_tray()
    
    def create_icon(self, color):
        """
        创建托盘图标
        
        Args:
            color: 图标颜色 ('red' 或 'green')
            
        Returns:
            QIcon: 创建的图标
        """
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor(color))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor('white'))
        font = QFont('SimHei', 20)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "喵")
        painter.end()
        
        return QIcon(pixmap)
    
    def setup_tray(self):
        """设置系统托盘"""
        self.tray_icon = QSystemTrayIcon(self.create_icon('red'))
        self.tray_icon.setToolTip("MeowParser (禁用)")
        
        # 创建菜单
        menu = QMenu()
        
        self.toggle_action = QAction("启用/禁用", menu)
        self.toggle_action.triggered.connect(self.parent_app.toggle)
        menu.addAction(self.toggle_action)
        
        menu.addSeparator()
        
        window_action = QAction("窗口管理", menu)
        window_action.triggered.connect(self.parent_app.show_window_manager)
        menu.addAction(window_action)
        
        rules_action = QAction("替换规则", menu)
        rules_action.triggered.connect(self.parent_app.show_replacement_editor)
        menu.addAction(rules_action)
        
        debug_action = QAction("调试窗口", menu)
        debug_action.triggered.connect(self.parent_app.show_debug_window)
        menu.addAction(debug_action)
        
        menu.addSeparator()
        
        status_text = f"权限状态: {'✓ 管理员' if self.parent_app.is_admin else '✗ 普通用户'}"
        status_action = QAction(status_text, menu)
        status_action.setEnabled(False)
        menu.addAction(status_action)
        
        # 快捷键提示
        hotkey_text = "快捷键: Ctrl+Shift+Alt+M 切换当前窗口"
        hotkey_action = QAction(hotkey_text, menu)
        hotkey_action.setEnabled(False)
        menu.addAction(hotkey_action)
        
        menu.addSeparator()
        
        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(self.parent_app.quit_app)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
    
    def show(self):
        """显示托盘图标"""
        if self.tray_icon:
            self.tray_icon.show()
    
    def hide(self):
        """隐藏托盘图标"""
        if self.tray_icon:
            self.tray_icon.hide()
    
    def update_icon(self, enabled):
        """
        更新图标状态
        
        Args:
            enabled: 是否启用状态
        """
        if self.tray_icon:
            color = 'green' if enabled else 'red'
            status = "启用" if enabled else "禁用"
            self.tray_icon.setIcon(self.create_icon(color))
            self.tray_icon.setToolTip(f"MeowParser ({status})")
    
    def show_message(self, title, message, icon=QSystemTrayIcon.MessageIcon.Information, duration=2000):
        """
        显示托盘消息
        
        Args:
            title: 消息标题
            message: 消息内容
            icon: 消息图标类型
            duration: 显示时长（毫秒）
        """
        if self.tray_icon:
            self.tray_icon.showMessage(title, message, icon, duration)
