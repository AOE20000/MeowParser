#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单实例检查模块
"""

import os
import ctypes
from pathlib import Path
import psutil
from ..constants import IS_WINDOWS


def check_single_instance():
    """检查是否已有实例运行"""
    if IS_WINDOWS:
        event_name = r"Global\MeowParser_SingleInstance_Event"
        try:
            event = ctypes.windll.kernel32.CreateEventW(None, True, False, event_name)
            if event == 0:
                return False
            if ctypes.get_last_error() == 183:
                ctypes.windll.kernel32.CloseHandle(event)
                return False
            return event
        except:
            return False
    else:
        # Linux: 使用文件锁
        lock_file = Path.home() / '.meowparser.lock'
        try:
            if lock_file.exists():
                # 检查进程是否还在运行
                try:
                    with open(lock_file, 'r') as f:
                        pid = int(f.read().strip())
                    if psutil.pid_exists(pid):
                        return False
                except:
                    pass
            # 写入当前进程 PID
            with open(lock_file, 'w') as f:
                f.write(str(os.getpid()))
            return lock_file
        except:
            return False
