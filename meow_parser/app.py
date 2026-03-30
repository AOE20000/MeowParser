#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MeowParser 主应用模块
"""

import os
import sys
import json
import time
import ctypes
import threading
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtGui import QCursor

import keyboard
import psutil

from .constants import IS_WINDOWS, IS_LINUX, IS_MACOS
from .core import ConfigFileManager, TextProcessor, check_single_instance
from .ui import (
    FloatingInputWindow,
    DebugWindow,
    WindowSelector,
    ConfigFileEditor,
    TrayIconManager
)
from .platform import get_active_window_info

if IS_WINDOWS:
    import win32gui
    import win32process
    import win32api


class MeowParser(QObject):
    """MeowParser 主应用类"""
    
    log_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # 检查单实例
        self.instance_lock = check_single_instance()
        if not self.instance_lock:
            QMessageBox.warning(None, "MeowParser", "程序已在运行中")
            sys.exit(0)
        
        # 基本状态
        self.enabled = False
        self.is_admin = self.check_admin()
        self.allowed_windows = self.load_window_settings()
        
        # 配置管理
        self.config_manager = ConfigFileManager(".meowparser/rules")
        self.text_processor = TextProcessor(self.config_manager)
        
        # 加载默认配置
        configs = self.config_manager.list_configs()
        if configs:
            self.config_manager.load_config(configs[0]['path'])
        
        # 迁移旧配置（如果存在）
        self._migrate_old_config_if_needed()
        
        # 输入监听相关
        self.input_buffer = ""
        self.last_input_time = 0
        self.last_window = None
        self.click_position = None
        self.input_activated = False
        
        # 创建UI组件
        self.floating_window = FloatingInputWindow(self)
        self.floating_window.hide()
        
        self.debug_window = None
        self.window_manager = None
        self.config_editor = None
        
        # 创建系统托盘
        self.tray_manager = TrayIconManager(self)
        self.tray_manager.show()
        
        # 连接日志信号
        self.log_signal.connect(self._log_to_debug)
    
    def check_admin(self):
        """检查管理员权限"""
        if IS_WINDOWS:
            try:
                return ctypes.windll.shell32.IsUserAnAdmin()
            except:
                return False
        else:
            return os.geteuid() == 0
    
    def toggle(self):
        """切换启用/禁用状态"""
        if not self.is_admin:
            self.tray_manager.show_message(
                "权限不足",
                "需要管理员权限才能使用此功能",
                2
            )
            return
        
        self.enabled = not self.enabled
        self.tray_manager.update_icon(self.enabled)
        
        if self.enabled:
            self.start_input_listener()
        else:
            self.stop_input_listener()
    
    def start_input_listener(self):
        """启动输入监听"""
        try:
            self.input_buffer = ""
            self.last_input_time = 0
            self.last_window = None
            self.input_activated = False
            
            keyboard.hook(self.on_key_event)
            keyboard.add_hotkey('ctrl+shift+alt+m', self.toggle_current_window)
            
            self.debug_log("输入监听已启动")
        except Exception as e:
            self.tray_manager.show_message("错误", f"启动失败: {str(e)}", 2)
    
    def stop_input_listener(self):
        """停止输入监听"""
        try:
            # 先移除所有热键
            try:
                keyboard.remove_all_hotkeys()
                print("已移除所有热键")
            except Exception as e:
                print(f"移除热键错误: {e}")
            
            # 等待一小段时间确保事件处理完成
            time.sleep(0.1)
            
            # 清理所有钩子
            keyboard.unhook_all()
            print("已清理键盘钩子")
            
            # 隐藏悬浮窗
            if self.floating_window:
                self.floating_window.hide()
            
            # 重置状态
            self.input_buffer = ""
            self.last_input_time = 0
            self.last_window = None
            self.input_activated = False
            
        except Exception as e:
            print(f"停止监听错误: {e}")
    
    def on_key_event(self, event):
        """键盘事件处理"""
        if not self.enabled:
            return
        
        if event.event_type != 'down':
            return
        
        # 检查当前窗口是否在白名单中
        window = get_active_window_info()
        if not window:
            self.input_buffer = ""
            self.input_activated = False
            if self.floating_window.isVisible():
                self.floating_window.hide()
            return
        
        # 检查窗口是否在白名单中
        window_key = window['title']
        if window_key not in self.allowed_windows or not self.allowed_windows[window_key]:
            self.input_buffer = ""
            self.input_activated = False
            if self.floating_window.isVisible():
                self.floating_window.hide()
            return
        
        # 检测窗口切换
        if self.last_window != window_key:
            self.input_buffer = ""
            self.last_window = window_key
            self.input_activated = False
            if self.floating_window.isVisible():
                self.floating_window.hide()
            return
        
        key_name = event.name
        current_time = time.time()
        
        # 检查悬浮窗是否已显示
        floating_visible = self.floating_window.isVisible()
        
        # 处理回车键
        if key_name == 'enter':
            if floating_visible:
                return
            self.input_buffer = ""
            self.input_activated = False
            return
        
        # 如果悬浮窗已显示，不再处理输入
        if floating_visible:
            return
        
        # 处理退格键
        if key_name == 'backspace':
            if len(self.input_buffer) > 0:
                self.input_buffer = self.input_buffer[:-1]
                self.last_input_time = current_time
            return
        
        # 处理空格 - 在输入激活状态下触发悬浮窗
        if key_name == 'space':
            if self.input_activated and not floating_visible:
                self.input_buffer = ""
                
                # 获取当前鼠标位置
                try:
                    if IS_WINDOWS:
                        self.click_position = win32api.GetCursorPos()
                    else:
                        pos = QCursor.pos()
                        self.click_position = (pos.x(), pos.y())
                except:
                    self.click_position = (100, 100)
                
                # 显示悬浮窗
                x, y = self.click_position
                self.debug_log(f"显示悬浮窗: 位置({x}, {y})")
                self.floating_window.show_at(x, y, window.get('hwnd'))
                
                # 阻止空格键事件传递
                try:
                    keyboard.block_key('space')
                    def unblock_space():
                        try:
                            keyboard.unblock_key('space')
                        except:
                            pass
                    threading.Timer(0.2, unblock_space).start()
                except:
                    pass
            else:
                self.input_buffer += ' '
                self.last_input_time = current_time
                self.input_activated = True
            return
        
        # 处理Tab
        if key_name == 'tab':
            self.input_buffer += '\t'
            self.last_input_time = current_time
            return
        
        # 处理单字符按键
        if len(key_name) == 1:
            self.input_buffer += key_name
            self.last_input_time = current_time
            self.input_activated = True
            return
        
        # 处理光标移动键
        if key_name in ['left', 'right', 'up', 'down', 'home', 'end', 'page up', 'page down']:
            self.input_buffer = ""
            self.input_activated = False
            if self.floating_window.isVisible():
                self.floating_window.hide()
            return
        
        # 处理ESC键
        if key_name in ['esc', 'escape']:
            self.input_buffer = ""
            self.input_activated = False
            if self.floating_window.isVisible():
                self.floating_window.hide()
            return
    
    def process_text(self, text):
        """处理文本"""
        return self.text_processor.process(text)
    
    def debug_log(self, message):
        """记录调试日志"""
        print(message)
        self.log_signal.emit(message)
    
    def _log_to_debug(self, message):
        """将日志输出到调试窗口"""
        if self.debug_window:
            self.debug_window.log(message)
    
    def show_debug_window(self):
        """显示调试窗口"""
        if self.debug_window is None:
            self.debug_window = DebugWindow(self)
            self._add_debug_window_to_whitelist()
        self.debug_window.show()
        self.debug_window.raise_()
        self.debug_window.activateWindow()
    
    def toggle_current_window(self):
        """切换当前窗口的启用状态"""
        try:
            window = get_active_window_info()
            if not window:
                self.tray_manager.show_message(
                    "无法切换",
                    "无法获取当前窗口信息",
                    2
                )
                return
            
            window_key = window['title']
            
            # 检查是否是调试窗口
            if "MeowParser 调试窗口" in window_key or "MeowParser调试窗口" in window_key:
                self.tray_manager.show_message(
                    "无法切换",
                    "调试窗口已锁定为启用状态",
                    1
                )
                return
            
            # 切换状态
            if window_key in self.allowed_windows and self.allowed_windows[window_key]:
                del self.allowed_windows[window_key]
                status = "已禁用"
            else:
                self.allowed_windows[window_key] = True
                status = "已启用"
            
            self.save_window_settings()
            
            # 显示通知
            parts = window_key.split(" - ", 1)
            display_title = parts[1] if len(parts) > 1 else window_key
            if len(display_title) > 50:
                display_title = display_title[:47] + "..."
            
            self.tray_manager.show_message(
                f"窗口{status}",
                f"{display_title}",
                1
            )
            
            self.debug_log(f"快捷键切换窗口状态: {window_key} -> {status}")
            
            # 刷新窗口管理器
            if hasattr(self, 'window_manager') and self.window_manager and self.window_manager.isVisible():
                self.window_manager.refresh_windows()
                
        except Exception as e:
            self.debug_log(f"切换窗口状态错误: {e}")
            self.tray_manager.show_message(
                "切换失败",
                f"错误: {str(e)}",
                2
            )
    
    def _add_debug_window_to_whitelist(self):
        """自动将调试窗口添加到白名单"""
        try:
            QTimer.singleShot(500, self._do_add_debug_window)
        except Exception as e:
            self.debug_log(f"添加调试窗口到白名单错误: {e}")
    
    def _do_add_debug_window(self):
        """执行添加调试窗口到白名单"""
        try:
            if IS_WINDOWS:
                def find_debug_window(hwnd, _):
                    try:
                        title = win32gui.GetWindowText(hwnd)
                        if "MeowParser 调试窗口" in title or "MeowParser调试窗口" in title:
                            _, pid = win32process.GetWindowThreadProcessId(hwnd)
                            process_name = psutil.Process(pid).name()
                            window_key = f"{process_name} - {title}"
                            self.allowed_windows[window_key] = True
                            self.save_window_settings()
                            self.debug_log(f"已自动添加调试窗口到白名单: {window_key}")
                    except:
                        pass
                    return True
                
                win32gui.EnumWindows(find_debug_window, None)
            else:
                # Linux 实现
                import subprocess
                result = subprocess.run(['wmctrl', '-l'], capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if "MeowParser 调试窗口" in line or "MeowParser调试窗口" in line:
                            parts = line.split(None, 3)
                            if len(parts) >= 4:
                                title = parts[3]
                                window_key = f"Python - {title}"
                                self.allowed_windows[window_key] = True
                                self.save_window_settings()
                                self.debug_log(f"已自动添加调试窗口到白名单: {window_key}")
                                break
        except Exception as e:
            self.debug_log(f"自动添加调试窗口错误: {e}")
    
    def show_window_manager(self):
        """显示窗口管理器"""
        try:
            if hasattr(self, 'window_manager') and self.window_manager:
                self.window_manager.show()
                self.window_manager.raise_()
                self.window_manager.activateWindow()
                self.window_manager.refresh_windows()
            else:
                self.window_manager = WindowSelector(None, self.allowed_windows, self.save_window_settings)
                self.window_manager.show()
        except Exception as e:
            self.debug_log(f"窗口管理器错误: {e}")
    
    def show_replacement_editor(self):
        """显示配置文件编辑器"""
        try:
            if hasattr(self, 'config_editor') and self.config_editor:
                self.config_editor.show()
                self.config_editor.raise_()
                self.config_editor.activateWindow()
                self.config_editor.refresh_config_list()
            else:
                self.config_editor = ConfigFileEditor(None, self.config_manager, self.on_config_changed)
                self.config_editor.show()
        except Exception as e:
            self.debug_log(f"配置编辑器错误: {e}")
    
    def load_window_settings(self):
        """加载窗口设置"""
        try:
            if os.path.exists('window_settings.json'):
                with open('window_settings.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_window_settings(self):
        """保存窗口设置"""
        try:
            with open('window_settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.allowed_windows, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def _migrate_old_config_if_needed(self):
        """迁移旧配置（如果需要）"""
        old_config_path = Path("replacement_rules.json")
        
        if not old_config_path.exists():
            return
        
        try:
            with open(old_config_path, 'r', encoding='utf-8') as f:
                old_config = json.load(f)
            
            new_config = self.config_manager.migrate_old_config(old_config)
            
            migrated_path = self.config_manager.config_dir / "migrated_from_old.json"
            self.config_manager.current_config = new_config
            self.config_manager.current_config_path = migrated_path
            self.config_manager.save_config()
            
            self.debug_log(f"✅ 配置已迁移到: {migrated_path}")
            
            # 备份旧配置
            backup_path = old_config_path.with_suffix('.json.old')
            import shutil
            shutil.copy(old_config_path, backup_path)
            self.debug_log(f"✅ 旧配置已备份到: {backup_path}")
            
            self.config_manager.load_config(migrated_path)
            
        except Exception as e:
            self.debug_log(f"❌ 配置迁移失败: {e}")
    
    def on_config_changed(self):
        """配置更改回调"""
        if self.config_manager.current_config:
            config_name = self.config_manager.current_config.get('name', '')
            self.debug_log(f"配置已更新: {config_name}")
    
    def quit_app(self):
        """退出应用"""
        import threading
        
        # 添加超时保护，防止卡死
        def force_quit():
            """3秒后强制退出"""
            time.sleep(3)
            print("⚠️ 超时强制退出")
            os._exit(0)
        
        timeout_thread = threading.Thread(target=force_quit, daemon=True)
        timeout_thread.start()
        
        try:
            print("开始退出程序...")
            
            # 1. 先停止输入监听（最重要）
            self.stop_input_listener()
            time.sleep(0.2)  # 等待清理完成
            
            # 2. 隐藏托盘图标
            if hasattr(self, 'tray_manager') and self.tray_manager:
                try:
                    self.tray_manager.hide()
                    print("已隐藏托盘图标")
                except Exception as e:
                    print(f"隐藏托盘错误: {e}")
            
            # 3. 按顺序关闭窗口
            windows_to_close = [
                ('floating_window', self.floating_window),
                ('debug_window', self.debug_window),
                ('window_manager', self.window_manager),
                ('config_editor', self.config_editor),
            ]
            
            for name, window in windows_to_close:
                if window:
                    try:
                        print(f"关闭 {name}...")
                        window.close()
                        window.deleteLater()  # 标记删除
                    except Exception as e:
                        print(f"关闭 {name} 错误: {e}")
            
            # 4. 保存设置
            try:
                self.save_window_settings()
                print("已保存窗口设置")
            except Exception as e:
                print(f"保存设置错误: {e}")
            
            # 5. 清理单实例锁
            if IS_WINDOWS and self.instance_lock:
                try:
                    ctypes.windll.kernel32.CloseHandle(self.instance_lock)
                    print("已释放单实例锁")
                except Exception as e:
                    print(f"释放锁错误: {e}")
            elif IS_LINUX and self.instance_lock:
                try:
                    self.instance_lock.unlink()
                    print("已删除锁文件")
                except Exception as e:
                    print(f"删除锁文件错误: {e}")
            
            # 6. 处理待处理的事件
            QApplication.processEvents()
            
            # 7. 退出应用
            print("✅ 退出完成")
            QApplication.quit()
            
        except Exception as e:
            print(f"❌ 退出错误: {e}")
            import traceback
            traceback.print_exc()
            # 强制退出
            QApplication.quit()
