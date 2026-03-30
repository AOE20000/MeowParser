#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MeowParser - 主入口文件

使用方法：
    python meow_parser.py        # 直接运行
    python -m meow_parser         # 作为模块运行
"""

import sys
from PyQt6.QtWidgets import QApplication
from meow_parser import MeowParser


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    parser = MeowParser()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
