#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Linux 平台特定功能
"""

import subprocess
import psutil


def get_active_window_info():
    """
    获取当前活动窗口信息（使用 xdotool）
    
    Returns:
        dict: 包含 hwnd, pid, title 的字典，失败返回 None
    """
    try:
        # 获取活动窗口 ID
        result = subprocess.run(
            ['xdotool', 'getactivewindow'],
            capture_output=True,
            text=True,
            timeout=1
        )
        if result.returncode != 0:
            return None
        
        window_id = result.stdout.strip()
        if not window_id:
            return None
        
        # 获取窗口标题
        result = subprocess.run(
            ['xdotool', 'getwindowname', window_id],
            capture_output=True,
            text=True,
            timeout=1
        )
        if result.returncode != 0:
            return None
        
        title = result.stdout.strip()
        if not title:
            return None
        
        # 获取窗口 PID
        result = subprocess.run(
            ['xdotool', 'getwindowpid', window_id],
            capture_output=True,
            text=True,
            timeout=1
        )
        pid = None
        process_name = "Unknown"
        if result.returncode == 0:
            try:
                pid = int(result.stdout.strip())
                process_name = psutil.Process(pid).name()
            except:
                pass
        
        window_key = f"{process_name} - {title}"
        
        return {
            'hwnd': window_id,
            'pid': pid,
            'title': window_key
        }
    except FileNotFoundError:
        print("错误: 未安装 xdotool，Linux 平台需要安装: sudo apt-get install xdotool")
        return None
    except subprocess.TimeoutExpired:
        return None
    except Exception as e:
        print(f"Linux 窗口信息获取错误: {e}")
        return None


def enumerate_windows():
    """
    枚举所有窗口（使用 xdotool）
    
    Returns:
        list: 窗口信息列表，每个元素包含 hwnd, pid, title, process_name
    """
    windows = []
    
    try:
        # 获取所有窗口 ID
        result = subprocess.run(
            ['xdotool', 'search', '--onlyvisible', '--name', '.*'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode != 0:
            return windows
        
        window_ids = result.stdout.strip().split('\n')
        
        for window_id in window_ids:
            if not window_id:
                continue
            
            try:
                # 获取窗口标题
                result = subprocess.run(
                    ['xdotool', 'getwindowname', window_id],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                
                if result.returncode != 0:
                    continue
                
                title = result.stdout.strip()
                if not title:
                    continue
                
                # 获取 PID
                result = subprocess.run(
                    ['xdotool', 'getwindowpid', window_id],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                
                pid = None
                process_name = "Unknown"
                if result.returncode == 0:
                    try:
                        pid = int(result.stdout.strip())
                        process_name = psutil.Process(pid).name()
                    except:
                        pass
                
                windows.append({
                    'hwnd': window_id,
                    'pid': pid,
                    'title': title,
                    'process_name': process_name
                })
            except:
                continue
    except FileNotFoundError:
        print("错误: 未安装 xdotool")
    except Exception as e:
        print(f"枚举窗口错误: {e}")
    
    return windows


def set_foreground_window(window_id):
    """
    激活窗口
    
    Args:
        window_id: 窗口 ID
        
    Returns:
        bool: 是否成功
    """
    try:
        subprocess.run(
            ['xdotool', 'windowactivate', str(window_id)],
            timeout=1,
            check=False
        )
        return True
    except Exception as e:
        print(f"激活窗口错误: {e}")
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
    try:
        # 移动鼠标
        subprocess.run(
            ['xdotool', 'mousemove', str(x), str(y)],
            timeout=1,
            check=False
        )
        # 点击
        subprocess.run(
            ['xdotool', 'click', '1'],
            timeout=1,
            check=False
        )
        return True
    except Exception as e:
        print(f"点击位置错误: {e}")
        return False


def set_window_topmost(window_id, x, y, width, height):
    """
    设置窗口置顶（Linux 实现有限）
    
    Args:
        window_id: 窗口 ID
        x, y: 窗口位置
        width, height: 窗口大小
        
    Returns:
        bool: 是否成功
    """
    try:
        # 移动和调整窗口大小
        subprocess.run(
            ['xdotool', 'windowmove', str(window_id), str(x), str(y)],
            timeout=1,
            check=False
        )
        subprocess.run(
            ['xdotool', 'windowsize', str(window_id), str(width), str(height)],
            timeout=1,
            check=False
        )
        # 激活窗口
        subprocess.run(
            ['xdotool', 'windowactivate', str(window_id)],
            timeout=1,
            check=False
        )
        return True
    except Exception as e:
        print(f"设置窗口置顶错误: {e}")
        return False
