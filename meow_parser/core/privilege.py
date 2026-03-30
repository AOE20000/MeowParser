#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
权限提升模块
"""

import os
import sys
import ctypes
from pathlib import Path


def is_admin():
    """检查是否有管理员/root权限"""
    if sys.platform == 'win32':
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        return os.geteuid() == 0


def request_admin_windows():
    """Windows: 请求管理员权限"""
    try:
        # 获取当前脚本路径
        if getattr(sys, 'frozen', False):
            # 打包后的可执行文件
            script = sys.executable
            params = ' '.join(sys.argv[1:])
        else:
            # Python 脚本
            script = sys.executable
            params = ' '.join([f'"{sys.argv[0]}"'] + sys.argv[1:])
        
        # 使用 ShellExecute 请求管理员权限
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",  # 以管理员身份运行
            script,
            params,
            None,
            1  # SW_SHOWNORMAL
        )
        
        # 返回值 > 32 表示成功
        return ret > 32
    except Exception as e:
        print(f"请求管理员权限失败: {e}")
        return False


def request_admin_unix():
    """Unix/Linux/macOS: 请求 root 权限"""
    try:
        # 检查是否在终端中运行
        if not sys.stdin.isatty():
            print("请在终端中使用 sudo 运行此程序")
            return False
        
        # 获取当前脚本路径
        if getattr(sys, 'frozen', False):
            script = sys.executable
        else:
            script = sys.argv[0]
        
        # 构建 sudo 命令
        args = [script] + sys.argv[1:]
        
        print("MeowParser 需要 root 权限才能运行")
        print(f"请输入密码以继续...")
        
        # 使用 sudo 重新启动
        os.execvp('sudo', ['sudo'] + args)
        
        # 如果 execvp 成功，这里不会执行
        return True
    except Exception as e:
        print(f"请求 root 权限失败: {e}")
        return False


def ensure_admin():
    """
    确保程序以管理员/root权限运行
    
    Returns:
        bool: True 表示已有权限或成功获取权限，False 表示获取失败
    """
    # 检查是否已有权限
    if is_admin():
        return True
    
    print("检测到程序未以管理员/root权限运行")
    print("正在请求权限提升...")
    
    # 根据平台请求权限
    if sys.platform == 'win32':
        success = request_admin_windows()
        if success:
            # Windows: ShellExecute 会启动新进程，当前进程应该退出
            sys.exit(0)
        else:
            print("权限提升失败或被拒绝")
            return False
    else:
        # Unix/Linux/macOS: execvp 会替换当前进程
        # 如果返回 False，说明失败了
        success = request_admin_unix()
        if not success:
            print("权限提升失败或被拒绝")
            return False
    
    return False
