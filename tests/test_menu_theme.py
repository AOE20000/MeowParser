#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
托盘菜单主题测试脚本
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel, QSystemTrayIcon, QMenu
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QFont
from meow_parser.ui.styles import StyleManager, ThemeDetector


class MenuThemeTestWindow(QMainWindow):
    """菜单主题测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MeowParser 菜单主题测试")
        self.setGeometry(100, 100, 600, 500)
        
        # 创建样式管理器
        self.style_manager = StyleManager()
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 添加标题
        title = QLabel("托盘菜单主题测试")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(title)
        
        # 系统主题信息
        system_theme = ThemeDetector.get_system_theme()
        info_label = QLabel(
            f"系统主题: {system_theme}\n"
            f"当前设置: {self.style_manager.current_theme}\n"
            f"实际生效: {self.style_manager.get_current_effective_theme()}"
        )
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        self.info_label = info_label
        
        # 说明
        instruction = QLabel(
            "点击下方按钮切换主题，然后右键点击托盘图标查看菜单样式变化"
        )
        instruction.setWordWrap(True)
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(instruction)
        
        # 添加按钮
        auto_btn = QPushButton("🌓 切换到自动模式")
        auto_btn.clicked.connect(lambda: self.change_theme("auto"))
        layout.addWidget(auto_btn)
        
        dark_btn = QPushButton("🌙 切换到深色主题")
        dark_btn.clicked.connect(lambda: self.change_theme("dark"))
        layout.addWidget(dark_btn)
        
        light_btn = QPushButton("☀️ 切换到浅色主题")
        light_btn.clicked.connect(lambda: self.change_theme("light"))
        layout.addWidget(light_btn)
        
        # 测试菜单按钮
        menu_btn = QPushButton("📋 显示测试菜单（模拟托盘菜单）")
        menu_btn.clicked.connect(self.show_test_menu)
        layout.addWidget(menu_btn)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 创建托盘图标
        self.setup_tray()
        
        # 应用初始主题
        self.style_manager.apply_theme(QApplication.instance())
    
    def setup_tray(self):
        """设置托盘图标"""
        # 创建图标
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor('green'))
        painter = QPainter(pixmap)
        painter.setPen(QColor('white'))
        font = QFont('SimHei', 20)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "喵")
        painter.end()
        
        self.tray_icon = QSystemTrayIcon(QIcon(pixmap))
        self.tray_icon.setToolTip("MeowParser 菜单测试")
        
        # 创建菜单
        self.menu = QMenu()
        self.update_menu_style()
        
        # 添加菜单项
        action1 = self.menu.addAction("🌓 自动模式")
        action1.triggered.connect(lambda: self.change_theme("auto"))
        
        action2 = self.menu.addAction("🌙 深色主题")
        action2.triggered.connect(lambda: self.change_theme("dark"))
        
        action3 = self.menu.addAction("☀️ 浅色主题")
        action3.triggered.connect(lambda: self.change_theme("light"))
        
        self.menu.addSeparator()
        
        info_action = self.menu.addAction("当前主题信息")
        info_action.setEnabled(False)
        
        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.show()
    
    def update_menu_style(self):
        """更新菜单样式"""
        style = self.style_manager.get_menu_style()
        self.menu.setStyleSheet(style)
    
    def show_test_menu(self):
        """显示测试菜单"""
        # 更新菜单样式
        self.update_menu_style()
        
        # 在按钮位置显示菜单
        sender = self.sender()
        pos = sender.mapToGlobal(sender.rect().bottomLeft())
        self.menu.exec(pos)
    
    def change_theme(self, theme_mode):
        """切换主题"""
        app = QApplication.instance()
        self.style_manager.set_theme(theme_mode, app)
        
        # 更新菜单样式
        self.update_menu_style()
        
        # 更新信息
        system_theme = ThemeDetector.get_system_theme()
        effective_theme = self.style_manager.get_current_effective_theme()
        self.info_label.setText(
            f"系统主题: {system_theme}\n"
            f"当前设置: {self.style_manager.current_theme}\n"
            f"实际生效: {effective_theme}"
        )
        
        # 更新状态
        theme_names = {
            "auto": "自动模式",
            "dark": "深色主题",
            "light": "浅色主题"
        }
        self.status_label.setText(
            f"✅ 已切换到{theme_names[theme_mode]}\n"
            f"右键点击托盘图标查看菜单样式"
        )
        
        print(f"已切换到: {theme_mode} (实际: {effective_theme})")
        print(f"菜单样式已更新")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    window = MenuThemeTestWindow()
    window.show()
    
    print("=" * 60)
    print("托盘菜单主题测试")
    print("=" * 60)
    print("1. 点击窗口中的按钮切换主题")
    print("2. 右键点击托盘图标查看菜单样式")
    print("3. 或点击'显示测试菜单'按钮查看菜单")
    print("=" * 60)
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
