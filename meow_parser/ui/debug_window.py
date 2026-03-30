#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试窗口模块
"""

import time
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QTextEdit, QPushButton, QLineEdit
)


class DebugWindow(QWidget):
    """调试窗口"""
    
    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("MeowParser 调试窗口")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout()
        
        # 日志区域
        log_label = QLabel("日志输出：")
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        clear_btn = QPushButton("清空日志")
        clear_btn.clicked.connect(self.clear_log)
        button_layout.addWidget(clear_btn)
        
        copy_btn = QPushButton("复制日志")
        copy_btn.clicked.connect(self.copy_log)
        button_layout.addWidget(copy_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        # 测试输入区域
        test_label = QLabel("测试输入：")
        layout.addWidget(test_label)
        
        self.test_entry = QLineEdit()
        layout.addWidget(self.test_entry)
        
        hint_label = QLabel("提示：开始输入时会自动弹出悬浮窗")
        hint_label.setStyleSheet("color: gray;")
        layout.addWidget(hint_label)
        
        self.setLayout(layout)
        
    def log(self, message):
        """添加日志"""
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        
    def clear_log(self):
        """清空日志"""
        self.log_text.clear()
        
    def copy_log(self):
        """复制日志"""
        try:
            import pyperclip
            pyperclip.copy(self.log_text.toPlainText())
            self.log("日志已复制到剪贴板")
        except:
            self.log("复制失败：未安装 pyperclip")
