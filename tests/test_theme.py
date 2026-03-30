#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主题切换功能测试脚本
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt
from meow_parser.ui.styles import StyleManager, ThemeDetector


class ThemeTestWindow(QMainWindow):
    """主题测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MeowParser 主题测试")
        self.setGeometry(100, 100, 600, 400)
        
        # 创建样式管理器
        self.style_manager = StyleManager()
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 添加标题
        title = QLabel("MeowParser 主题切换测试")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(title)
        
        # 系统主题信息
        system_theme = ThemeDetector.get_system_theme()
        info_label = QLabel(f"系统主题: {system_theme}\n当前设置: {self.style_manager.current_theme}")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        self.info_label = info_label
        
        # 添加按钮
        auto_btn = QPushButton("🌓 自动（跟随系统）")
        auto_btn.clicked.connect(lambda: self.change_theme("auto"))
        layout.addWidget(auto_btn)
        
        dark_btn = QPushButton("🌙 深色主题")
        dark_btn.clicked.connect(lambda: self.change_theme("dark"))
        layout.addWidget(dark_btn)
        
        light_btn = QPushButton("☀️ 浅色主题")
        light_btn.clicked.connect(lambda: self.change_theme("light"))
        layout.addWidget(light_btn)
        
        # 添加测试组件
        layout.addWidget(QLabel("测试组件:"))
        
        test_input = QLabel("这是一个标签")
        layout.addWidget(test_input)
        
        test_btn = QPushButton("这是一个按钮")
        layout.addWidget(test_btn)
        
        # 应用初始主题
        self.style_manager.apply_theme(QApplication.instance())
    
    def change_theme(self, theme_mode):
        """切换主题"""
        app = QApplication.instance()
        self.style_manager.set_theme(theme_mode, app)
        
        # 更新信息
        system_theme = ThemeDetector.get_system_theme()
        effective_theme = self.style_manager.get_current_effective_theme()
        self.info_label.setText(
            f"系统主题: {system_theme}\n"
            f"当前设置: {self.style_manager.current_theme}\n"
            f"实际生效: {effective_theme}"
        )
        
        print(f"已切换到: {theme_mode} (实际: {effective_theme})")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    window = ThemeTestWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
