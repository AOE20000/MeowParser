#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
程序入口模块
"""

import sys
from PyQt6.QtWidgets import QApplication
from .app import MeowParser


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    parser = MeowParser()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
