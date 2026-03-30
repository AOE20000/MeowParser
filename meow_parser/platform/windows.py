#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows 平台特定功能
"""

import psutil

try:
    import win32gui
    import win32process
    import win32api
    import win32con
    WINDOWS_AVAILABLE = True
except ImportError:
    WINDOWS_AVAILABLE = False


def get_active_window_info():
    """
    获取当前活动窗口信息
    
    Returns:
        dict: 包含 hwnd, pid, title 的字典，失败返回 None
    """
    if not WINDOWS_AVAILABLE:
        return None
    
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return None
        
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        title = win32gui.GetWindowText(hwnd)
        if not title:
            return None
        
        process_name = psutil.Process(pid).name()
        window_key = f"{process_name} - {title}"
        
        return {
            'hwnd': hwnd,
            'pid': pid,
            'title': window_key
        }
    except Exception as e:
        print(f"获取窗口信息错误: {e}")
        return None


def enumerate_windows():
    """
    枚举所有窗口
    
    Returns:
        list: 窗口信息列表，每个元素包含 hwnd, pid, title, process_name
    """
    if not WINDOWS_AVAILABLE:
        return []
    
    windows = []
    
    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                try:
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    process_name = psutil.Process(pid).name()
                    windows.append({
                        'hwnd': hwnd,
                        'pid': pid,
                        'title': title,
                        'process_name': process_name
                    })
                except:
                    pass
        return True
    
    try:
        win32gui.EnumWindows(callback, None)
    except Exception as e:
        print(f"枚举窗口错误: {e}")
    
    return windows


def set_foreground_window(hwnd):
    """
    设置前台窗口
    
    Args:
        hwnd: 窗口句柄
        
    Returns:
        bool: 是否成功
    """
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        win32gui.SetForegroundWindow(hwnd)
        return True
    except Exception as e:
        print(f"设置前台窗口错误: {e}")
        return False


def click_position(x, y):
    """
    在指定位置点击鼠标
    
    Args:
        x: X 坐标
        y: Y 坐标
        
    Returns:
        bool: 是否成功
    """
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        win32api.SetCursorPos((x, y))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
        return True
    except Exception as e:
        print(f"点击位置错误: {e}")
        return False


def set_window_topmost(hwnd, x, y, width, height):
    """
    设置窗口置顶
    
    Args:
        hwnd: 窗口句柄
        x, y: 窗口位置
        width, height: 窗口大小
        
    Returns:
        bool: 是否成功
    """
    if not WINDOWS_AVAILABLE:
        return False
    
    try:
        win32gui.SetWindowPos(
            hwnd,
            win32con.HWND_TOPMOST,
            x, y, width, height,
            win32con.SWP_SHOWWINDOW | win32con.SWP_NOACTIVATE
        )
        return True
    except Exception as e:
        print(f"设置窗口置顶错误: {e}")
        return False
