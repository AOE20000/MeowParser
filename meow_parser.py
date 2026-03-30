#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MeowParser - 主入口文件

使用方法:
    python meow_parser.py        # 直接运行
    python -m meow_parser         # 作为模块运行
"""

import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from meow_parser.core.privilege import ensure_admin


def main():
    """主函数"""
    # 在创建 QApplication 之前检查权限
    if not ensure_admin():
        # 权限提升失败，显示错误消息
        app = QApplication(sys.argv)
        QMessageBox.critical(
            None,
            "MeowParser - 权限不足",
            "MeowParser 需要管理员/root 权限才能运行。\n\n"
            "权限提升失败或被拒绝。\n\n"
            "Windows: 请右键程序，选择\"以管理员身份运行\"\n"
            "Linux/macOS: 请使用 sudo 运行程序"
        )
        sys.exit(1)
    
    # 已有管理员权限，继续启动
    from meow_parser import MeowParser
    from meow_parser.ui.styles import StyleManager
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # 创建应用实例
    parser = MeowParser()
    
    # 应用主题（使用样式管理器）
    parser.style_manager.apply_theme(app)
    
    # 如果是自动模式，启动主题监控
    if parser.style_manager.current_theme == parser.style_manager.THEME_AUTO:
        parser.style_manager.start_theme_monitoring(app)
    
    sys.exit(app.exec())
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
