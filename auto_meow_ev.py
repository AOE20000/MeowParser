import keyboard
import time
import pystray
from PIL import Image, ImageDraw, ImageFont
import threading
import sys
import ctypes
import ctypes.wintypes
from sys import exit
import win32gui
import win32process
import win32api
import win32con
import json
import os
import tkinter as tk
from tkinter import ttk
import psutil

def check_single_instance():
    """检查是否已有实例运行"""
    event_name = r"Global\AutoMeowEV_SingleInstance_Event"
    
    try:
        event = ctypes.windll.kernel32.CreateEventW(
            None, True, False, event_name
        )
        
        if event == 0:
            return False
            
        if ctypes.get_last_error() == 183:
            ctypes.windll.kernel32.CloseHandle(event)
            return False
            
        return event
    except:
        if 'event' in locals():
            ctypes.windll.kernel32.CloseHandle(event)
        return False

class DebugWindow:
    """调试窗口"""
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.window = None
        self.log_text = None
        self.test_entry = None
        self.is_closing = False
        
    def show(self):
        """显示调试窗口"""
        if self.window is not None:
            try:
                self.window.lift()
                self.window.focus_force()
                return
            except:
                self.window = None
        
        self.window = tk.Toplevel()
        self.window.title("AutoMeowEV 调试窗口")
        self.window.geometry("800x600")
        
        # 日志区域
        log_frame = ttk.LabelFrame(self.window, text="日志输出", padding=5)
        log_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # 创建滚动条
        scrollbar = ttk.Scrollbar(log_frame)
        scrollbar.pack(side='right', fill='y')
        
        # 创建文本框
        self.log_text = tk.Text(log_frame, wrap='word', yscrollcommand=scrollbar.set, height=20)
        self.log_text.pack(fill='both', expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # 按钮区域
        button_frame = ttk.Frame(log_frame)
        button_frame.pack(fill='x', pady=(5, 0))
        ttk.Button(button_frame, text="清空日志", command=self.clear_log).pack(side='left', padx=2)
        ttk.Button(button_frame, text="复制日志", command=self.copy_log).pack(side='left', padx=2)
        
        # 测试输入区域
        test_frame = ttk.LabelFrame(self.window, text="测试输入（此窗口默认在白名单中）", padding=5)
        test_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(test_frame, text="在此输入框中测试替换功能：").pack(anchor='w', pady=(0, 5))
        self.test_entry = tk.Entry(test_frame, font=('Microsoft YaHei UI', 11))
        self.test_entry.pack(fill='x', pady=5)
        
        ttk.Label(test_frame, text="提示：开始输入时会自动弹出悬浮窗", foreground='gray').pack(anchor='w')
        
        # 关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.hide)
        
        # 将此窗口添加到白名单
        self.add_to_whitelist()
        
        # 记录初始日志
        self.log("调试窗口已打开")
        self.log(f"当前启用状态: {'启用' if self.parent_app.enabled else '禁用'}")
        self.log(f"白名单窗口数量: {len(self.parent_app.allowed_windows)}")
    
    def add_to_whitelist(self):
        """将调试窗口添加到白名单"""
        try:
            # 获取窗口信息
            hwnd = self.window.winfo_id()
            # 使用固定的窗口标识
            window_key = "python.exe - AutoMeowEV 调试窗口"
            self.parent_app.allowed_windows[window_key] = True
            self.log(f"调试窗口已添加到白名单: {window_key}")
        except Exception as e:
            self.log(f"添加到白名单失败: {e}")
    
    def hide(self):
        """隐藏调试窗口"""
        if self.window and not self.is_closing:
            try:
                self.window.withdraw()
            except:
                pass
    
    def close(self):
        """关闭调试窗口"""
        if self.is_closing:
            return
        self.is_closing = True
        
        try:
            if self.window:
                self.window.destroy()
                self.window = None
        except:
            pass
    
    def log(self, message):
        """添加日志"""
        if self.log_text and not self.is_closing:
            try:
                timestamp = time.strftime("%H:%M:%S")
                self.log_text.insert('end', f"[{timestamp}] {message}\n")
                self.log_text.see('end')
            except:
                pass
    
    def clear_log(self):
        """清空日志"""
        if self.log_text:
            try:
                self.log_text.delete('1.0', 'end')
            except:
                pass
    
    def copy_log(self):
        """复制日志到剪贴板"""
        if self.log_text:
            try:
                import pyperclip
                log_content = self.log_text.get('1.0', 'end')
                pyperclip.copy(log_content)
                self.log("日志已复制到剪贴板")
            except:
                self.log("复制失败：未安装 pyperclip")


class WindowSelector:
    def __init__(self, parent, allowed_windows):
        self.window = tk.Toplevel(parent)
        self.window.title("窗口管理")
        self.window.geometry("800x600")
        self.allowed_windows = allowed_windows
        self.window_list = {}
        
        search_frame = ttk.Frame(self.window)
        search_frame.pack(fill='x', padx=5, pady=5)
        ttk.Label(search_frame, text="搜索窗口：").pack(side='left')
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_windows)
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side='left', fill='x', expand=True)
        
        self.tree = ttk.Treeview(self.window, columns=('process', 'title', 'enabled'), show='headings')
        self.tree.heading('process', text='进程名')
        self.tree.heading('title', text='窗口标题')
        self.tree.heading('enabled', text='状态')
        self.tree.column('process', width=150)
        self.tree.column('title', width=500)
        self.tree.column('enabled', width=100, anchor='center')
        self.tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.tree.bind('<Double-1>', self.toggle_window)
        
        ttk.Label(self.window, text="双击窗口项目可切换启用状态").pack(pady=2)
        ttk.Button(self.window, text="刷新窗口列表", command=self.refresh_windows).pack(pady=5)
        
        self.refresh_windows()
        
    def get_process_name(self, pid):
        try:
            return psutil.Process(pid).name()
        except:
            return "未知进程"
    
    def toggle_window(self, event):
        try:
            selection = self.tree.selection()
            if not selection:
                return
            item = selection[0]
            values = self.tree.item(item, 'values')
            window_key = f"{values[0]} - {values[1]}"
            if window_key in self.allowed_windows:
                del self.allowed_windows[window_key]
            else:
                self.allowed_windows[window_key] = True
            self.refresh_windows()
        except Exception as e:
            print(f"切换窗口状态错误: {e}")
        
    def refresh_windows(self):
        """刷新窗口列表"""
        # 清空现有列表
        self.tree.delete(*self.tree.get_children())
        self.window_list.clear()
        
        # 显示加载提示
        loading_item = self.tree.insert('', 'end', values=('', '正在加载窗口列表...', ''))
        
        def do_refresh():
            """在后台线程中枚举窗口"""
            try:
                temp_list = {}
                
                def enum_windows_callback(hwnd, _):
                    try:
                        if win32gui.IsWindowVisible(hwnd):
                            title = win32gui.GetWindowText(hwnd)
                            if title and len(title.strip()) > 0:
                                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                                process_name = self.get_process_name(pid)
                                window_key = f"{process_name} - {title}"
                                temp_list[window_key] = hwnd
                    except:
                        pass
                    return True
                
                win32gui.EnumWindows(enum_windows_callback, None)
                
                # 在主线程中更新UI
                self.window.after(0, lambda: self.update_tree(temp_list, loading_item))
            except Exception as e:
                print(f"枚举窗口错误: {e}")
                self.window.after(0, lambda: self.tree.delete(loading_item))
        
        # 在后台线程中执行
        thread = threading.Thread(target=do_refresh, daemon=True)
        thread.start()
    
    def update_tree(self, temp_list, loading_item):
        """更新树形控件（在主线程中调用）"""
        try:
            # 删除加载提示
            self.tree.delete(loading_item)
            
            # 更新窗口列表
            self.window_list = temp_list
            
            # 添加到树形控件
            for window_key, hwnd in self.window_list.items():
                try:
                    process_name, title = window_key.split(" - ", 1)
                    enabled = "✓ 已启用" if window_key in self.allowed_windows else "✗ 未启用"
                    self.tree.insert('', 'end', values=(process_name, title, enabled))
                except:
                    pass
        except Exception as e:
            print(f"更新树形控件错误: {e}")
        
    def filter_windows(self, *args):
        search_text = self.search_var.get().lower()
        self.tree.delete(*self.tree.get_children())
        for window_key, hwnd in self.window_list.items():
            if search_text in window_key.lower():
                process_name, title = window_key.split(" - ", 1)
                enabled = "✓ 已启用" if window_key in self.allowed_windows else "✗ 未启用"
                self.tree.insert('', 'end', values=(process_name, title, enabled))


class ReplacementRuleEditor:
    def __init__(self, parent, replacement_rules, save_callback):
        self.window = tk.Toplevel(parent)
        self.window.title("替换规则管理")
        self.window.geometry("700x500")
        self.replacement_rules = replacement_rules
        self.save_callback = save_callback
        
        control_frame = ttk.Frame(self.window)
        control_frame.pack(fill='x', padx=5, pady=5)
        
        self.enabled_var = tk.BooleanVar(value=self.replacement_rules.get("enabled", True))
        ttk.Checkbutton(control_frame, text="启用文本替换功能", 
                       variable=self.enabled_var,
                       command=self.toggle_replacement).pack(side='left')
        
        list_frame = ttk.Frame(self.window)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        ttk.Label(list_frame, text="替换规则列表（匹配到的文本将被替换）：").pack(anchor='w')
        
        self.tree = ttk.Treeview(list_frame, columns=('pattern', 'replacement'), show='headings', height=10)
        self.tree.heading('pattern', text='匹配文本')
        self.tree.heading('replacement', text='替换为')
        self.tree.column('pattern', width=300)
        self.tree.column('replacement', width=300)
        self.tree.pack(fill='both', expand=True)
        
        button_frame = ttk.Frame(self.window)
        button_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Button(button_frame, text="添加规则", command=self.add_rule).pack(side='left', padx=2)
        ttk.Button(button_frame, text="编辑规则", command=self.edit_rule).pack(side='left', padx=2)
        ttk.Button(button_frame, text="删除规则", command=self.delete_rule).pack(side='left', padx=2)
        ttk.Button(button_frame, text="上移", command=self.move_up).pack(side='left', padx=2)
        ttk.Button(button_frame, text="下移", command=self.move_down).pack(side='left', padx=2)
        
        info_frame = ttk.Frame(self.window)
        info_frame.pack(fill='x', padx=5, pady=5)
        info_text = "说明：按回车时，程序会扫描当前行文本，将所有匹配的词替换为指定内容。\n规则按顺序依次应用，每个规则会替换文本中所有匹配的位置。\n示例：\"我\" → \"喵\"，则\"我的\"会变成\"喵的\"。"
        ttk.Label(info_frame, text=info_text, wraplength=650, justify='left').pack()
        
        self.refresh_rules()
        
    def toggle_replacement(self):
        self.replacement_rules["enabled"] = self.enabled_var.get()
        self.save_callback()
        
    def refresh_rules(self):
        self.tree.delete(*self.tree.get_children())
        for rule in self.replacement_rules.get("rules", []):
            self.tree.insert('', 'end', values=(rule.get("pattern", ""), rule.get("replacement", "")))
    
    def add_rule(self):
        dialog = RuleDialog(self.window, "添加规则")
        if dialog.result:
            pattern, replacement = dialog.result
            if pattern:
                self.replacement_rules.setdefault("rules", []).append({
                    "pattern": pattern,
                    "replacement": replacement
                })
                self.refresh_rules()
                self.save_callback()
    
    def edit_rule(self):
        selection = self.tree.selection()
        if not selection:
            return
        
        index = self.tree.index(selection[0])
        rule = self.replacement_rules["rules"][index]
        
        dialog = RuleDialog(self.window, "编辑规则", rule["pattern"], rule["replacement"])
        if dialog.result:
            pattern, replacement = dialog.result
            if pattern:
                self.replacement_rules["rules"][index] = {
                    "pattern": pattern,
                    "replacement": replacement
                }
                self.refresh_rules()
                self.save_callback()
    
    def delete_rule(self):
        selection = self.tree.selection()
        if not selection:
            return
        
        index = self.tree.index(selection[0])
        del self.replacement_rules["rules"][index]
        self.refresh_rules()
        self.save_callback()
    
    def move_up(self):
        selection = self.tree.selection()
        if not selection:
            return
        
        index = self.tree.index(selection[0])
        if index > 0:
            rules = self.replacement_rules["rules"]
            rules[index], rules[index-1] = rules[index-1], rules[index]
            self.refresh_rules()
            self.save_callback()
            self.tree.selection_set(self.tree.get_children()[index-1])
    
    def move_down(self):
        selection = self.tree.selection()
        if not selection:
            return
        
        index = self.tree.index(selection[0])
        rules = self.replacement_rules["rules"]
        if index < len(rules) - 1:
            rules[index], rules[index+1] = rules[index+1], rules[index]
            self.refresh_rules()
            self.save_callback()
            self.tree.selection_set(self.tree.get_children()[index+1])


class RuleDialog:
    def __init__(self, parent, title, pattern="", replacement=""):
        self.result = None
        
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry("500x200")
        dialog.transient(parent)
        dialog.grab_set()
        
        ttk.Label(dialog, text="匹配文本：").pack(padx=10, pady=(10, 0), anchor='w')
        pattern_entry = ttk.Entry(dialog, width=60)
        pattern_entry.pack(padx=10, pady=5, fill='x')
        pattern_entry.insert(0, pattern)
        
        ttk.Label(dialog, text="替换为：").pack(padx=10, pady=(10, 0), anchor='w')
        replacement_entry = ttk.Entry(dialog, width=60)
        replacement_entry.pack(padx=10, pady=5, fill='x')
        replacement_entry.insert(0, replacement)
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=20)
        
        def on_ok():
            self.result = (pattern_entry.get(), replacement_entry.get())
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        ttk.Button(button_frame, text="确定", command=on_ok).pack(side='left', padx=5)
        ttk.Button(button_frame, text="取消", command=on_cancel).pack(side='left', padx=5)
        
        pattern_entry.focus()
        dialog.bind('<Return>', lambda e: on_ok())
        dialog.bind('<Escape>', lambda e: on_cancel())
        
        dialog.wait_window()


class FloatingInputWindow:
    """悬浮输入窗口"""
    def __init__(self, parent_app):
        self.parent_app = parent_app
        self.window = None
        self.entry = None
        self.click_pos = None
        self.target_window = None
        self.is_processing = False
        self.tk_thread = None
        self.is_visible = False
        self.is_closing = False  # 标记是否正在关闭
        
        # 在单独的线程中启动 tkinter
        self.start_tk_thread()
    
    def start_tk_thread(self):
        """在独立线程中启动 tkinter 主循环"""
        def run_tk():
            try:
                self.window = tk.Tk()
                self.window.withdraw()  # 初始隐藏
                self.window.overrideredirect(True)
                self.window.attributes('-topmost', True)
                self.window.attributes('-alpha', 0.95)
                
                # 设置窗口背景色，便于调试
                self.window.configure(bg='#f0f0f0')
                
                # 创建输入框
                self.entry = tk.Entry(
                    self.window, 
                    font=('Microsoft YaHei UI', 12), 
                    width=50,
                    relief='solid',
                    borderwidth=1
                )
                self.entry.pack(padx=5, pady=5)
                
                # 绑定事件
                self.entry.bind('<Return>', self.on_enter)
                self.entry.bind('<Control-Return>', self.on_ctrl_enter)
                self.entry.bind('<Escape>', self.on_escape)
                
                # 设置关闭协议
                self.window.protocol("WM_DELETE_WINDOW", self.close)
                
                # 启动主循环
                self.window.mainloop()
            except Exception as e:
                print(f"悬浮窗线程错误: {e}")
        
        self.tk_thread = threading.Thread(target=run_tk, daemon=True)
        self.tk_thread.start()
        
        # 等待窗口创建完成
        time.sleep(0.2)
    
    def close(self):
        """关闭悬浮窗"""
        if self.is_closing:
            return
        self.is_closing = True
        
        try:
            if self.window:
                self.window.quit()
        except:
            pass
        
    def show(self, x, y, target_window):
        """在指定位置显示悬浮窗"""
        if self.is_processing or not self.window:
            return
            
        self.click_pos = (x, y)
        self.target_window = target_window
        
        def _show():
            try:
                # 获取屏幕尺寸
                screen_width = self.window.winfo_screenwidth()
                screen_height = self.window.winfo_screenheight()
                
                # 更新窗口以获取实际尺寸
                self.window.update_idletasks()
                window_width = self.window.winfo_reqwidth()
                window_height = self.window.winfo_reqheight()
                
                # 调整位置避免超出屏幕
                final_x = min(x, screen_width - window_width - 10)
                final_y = min(y, screen_height - window_height - 10)
                final_x = max(10, final_x)
                final_y = max(10, final_y)
                
                # 设置位置并显示
                self.window.geometry(f"+{final_x}+{final_y}")
                self.window.deiconify()
                self.window.lift()
                self.window.focus_force()
                self.entry.delete(0, tk.END)
                self.entry.focus_set()
                self.is_visible = True
            except Exception as e:
                print(f"显示悬浮窗错误: {e}")
        
        if self.window:
            self.window.after(0, _show)
        
    def hide(self):
        """隐藏悬浮窗"""
        if not self.window:
            return
            
        def _hide():
            try:
                self.window.withdraw()
                self.is_visible = False
            except:
                pass
        
        if self.window:
            self.window.after(0, _hide)
    
    def on_escape(self, event):
        """ESC键 - 取消输入"""
        self.hide()
        if self.target_window:
            try:
                win32gui.SetForegroundWindow(self.target_window)
            except:
                pass
        return 'break'
    
    def on_ctrl_enter(self, event):
        """Ctrl+回车 - 发送原始内容"""
        if self.is_processing:
            return 'break'
            
        self.is_processing = True
        text = self.entry.get()
        self.hide()
        
        threading.Thread(target=self._send_text, args=(text, False), daemon=True).start()
        return 'break'
    
    def on_enter(self, event):
        """回车键 - 应用替换规则"""
        if self.is_processing:
            return 'break'
            
        self.is_processing = True
        text = self.entry.get()
        self.hide()
        
        threading.Thread(target=self._send_text, args=(text, True), daemon=True).start()
        return 'break'
    
    def _send_text(self, text, apply_rules):
        """发送文本到目标位置"""
        try:
            # 应用替换规则
            if apply_rules:
                final_text = self.parent_app.process_text(text)
            else:
                final_text = text
            
            # 调试信息
            self.parent_app.debug_log(f"原文本: {text}")
            self.parent_app.debug_log(f"处理后: {final_text}")
            self.parent_app.debug_log(f"点击位置: {self.click_pos}")
            self.parent_app.debug_log(f"目标窗口: {self.target_window}")
            
            # 等待悬浮窗完全隐藏
            time.sleep(0.15)
            
            # 方案1：尝试恢复焦点并点击
            focus_restored = False
            if self.click_pos and self.target_window:
                try:
                    # 恢复目标窗口焦点
                    win32gui.SetForegroundWindow(self.target_window)
                    time.sleep(0.08)
                    
                    # 获取坐标
                    x, y = self.click_pos
                    
                    # 模拟鼠标点击
                    win32api.SetCursorPos((x, y))
                    time.sleep(0.05)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
                    time.sleep(0.03)
                    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
                    time.sleep(0.1)
                    focus_restored = True
                    self.parent_app.debug_log("焦点恢复成功")
                except Exception as e:
                    self.parent_app.debug_log(f"点击错误: {e}")
            
            # 方案2：如果点击失败，尝试使用 Alt+Tab 切换回去
            if not focus_restored:
                self.parent_app.debug_log("尝试使用 Alt+Tab 切换")
                try:
                    keyboard.press_and_release('alt+tab')
                    time.sleep(0.1)
                except:
                    pass
            
            # 打字机输入
            if final_text:
                self.parent_app.debug_log(f"开始输入文本: {final_text}")
                try:
                    # 先尝试整体输入
                    keyboard.write(final_text)
                    time.sleep(0.05)
                    self.parent_app.debug_log("文本输入成功")
                except Exception as e:
                    self.parent_app.debug_log(f"整体输入失败: {e}，尝试逐字符输入")
                    # 如果失败，逐字符输入
                    for i, char in enumerate(final_text):
                        try:
                            keyboard.write(char)
                            time.sleep(0.01)
                        except Exception as ce:
                            self.parent_app.debug_log(f"字符 {i} ({char}) 输入失败: {ce}")
                    time.sleep(0.05)
            
            # 发送回车
            time.sleep(0.05)
            keyboard.press_and_release('enter')
            self.parent_app.debug_log("回车已发送")
            
        except Exception as e:
            self.parent_app.debug_log(f"发送文本错误: {e}")
            import traceback
            self.parent_app.debug_log(traceback.format_exc())
        finally:
            self.is_processing = False
    
    def set_text(self, text):
        """设置输入框文本"""
        if not self.window or not self.entry:
            return
            
        def _set():
            try:
                self.entry.delete(0, tk.END)
                self.entry.insert(0, text)
            except:
                pass
        
        self.window.after(0, _set)


class AutoMeowEV:
    def __init__(self):
        self.event = check_single_instance()
        if not self.event:
            sys.exit(0)
            
        self.enabled = False
        self.last_time = 0
        self.icon = None
        self.is_admin = self.check_admin()
        self.allowed_windows = self.load_window_settings()
        self.replacement_rules = self.load_replacement_rules()
        self.window_manager = None
        self.root = None
        
        # 悬浮输入窗口
        self.floating_window = None
        
        # 输入监听相关
        self.input_buffer = ""
        self.last_input_time = 0
        self.last_window = None
        self.click_position = None
        self.input_activated = False  # 标记输入框是否已激活
        
        # 调试窗口
        self.debug_window = None
        
        self.setup_tray()

    def check_admin(self):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def create_icon(self, color):
        image = Image.new('RGB', (32, 32), color)
        draw = ImageDraw.Draw(image)
        try:
            font = ImageFont.truetype("simhei.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        text = "喵"
        left, top, right, bottom = draw.textbbox((0, 0), text, font=font)
        x = (32 - (right - left)) // 2
        y = (32 - (bottom - top)) // 2
        draw.text((x, y), text, font=font, fill='white')
        return image

    def load_window_settings(self):
        try:
            if os.path.exists('window_settings.json'):
                with open('window_settings.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}

    def save_window_settings(self):
        try:
            with open('window_settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.allowed_windows, f, ensure_ascii=False, indent=2)
        except:
            pass

    def load_replacement_rules(self):
        try:
            if os.path.exists('replacement_rules.json'):
                with open('replacement_rules.json', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {
            "enabled": True,
            "rules": [
                {"pattern": "我", "replacement": "喵"},
                {"pattern": "你", "replacement": "喵"},
                {"pattern": "他", "replacement": "喵"},
                {"pattern": "她", "replacement": "喵"},
            ]
        }

    def save_replacement_rules(self):
        try:
            with open('replacement_rules.json', 'w', encoding='utf-8') as f:
                json.dump(self.replacement_rules, f, ensure_ascii=False, indent=2)
        except:
            pass

    def get_active_window_info(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            _, pid = win32process.GetWindowThreadProcessId(hwnd)
            title = win32gui.GetWindowText(hwnd)
            process_name = psutil.Process(pid).name()
            window_key = f"{process_name} - {title}"
            return {'hwnd': hwnd, 'pid': pid, 'title': window_key}
        except:
            return None

    def toggle_current_window(self):
        window = self.get_active_window_info()
        if not window:
            self.icon.notify("无法获取当前窗口信息", "错误")
            return

        title = window['title']
        if title in self.allowed_windows:
            del self.allowed_windows[title]
            self.icon.notify(f"已禁用窗口：{title}", "窗口设置")
        else:
            self.allowed_windows[title] = True
            self.icon.notify(f"已启用窗口：{title}", "窗口设置")
        
        self.save_window_settings()
        
    def toggle(self, *args):
        if not self.is_admin:
            self.icon.notify("需要管理员权限才能使用此功能", "权限不足")
            return

        self.enabled = not self.enabled
        if self.icon:
            color = 'green' if self.enabled else 'red'
            self.icon.icon = self.create_icon(color)
            self.icon.title = f"AutoMeowEV ({'启用' if self.enabled else '禁用'})"
            
            if not self.enabled:
                self.stop_input_listener()
            else:
                self.start_input_listener()
    
    def start_input_listener(self):
        """启动输入监听"""
        try:
            # 创建悬浮窗
            if self.floating_window is None:
                self.floating_window = FloatingInputWindow(self)
            
            # 重置状态
            self.input_buffer = ""
            self.last_input_time = 0
            self.last_window = None
            self.input_activated = False
            
            # 监听所有按键
            keyboard.hook(self.on_key_event)
            
            # 添加调试快捷键 Ctrl+Shift+M
            keyboard.add_hotkey('ctrl+shift+m', self.show_debug_window)
            
            self.debug_log("输入监听已启动")
            
        except Exception as e:
            if self.icon:
                self.icon.notify(f"启动失败: {str(e)}", "错误")
    
    def show_debug_window(self):
        """显示调试窗口"""
        try:
            if self.debug_window is None:
                self.debug_window = DebugWindow(self)
            self.debug_window.show()
        except Exception as e:
            if self.icon:
                self.icon.notify(f"打开调试窗口失败: {str(e)}", "错误")
    
    def debug_log(self, message):
        """记录调试日志"""
        print(message)  # 控制台输出
        if self.debug_window:
            try:
                self.debug_window.log(message)
            except:
                pass
    
    def stop_input_listener(self):
        """停止输入监听"""
        try:
            keyboard.unhook_all()
            
            if self.floating_window:
                self.floating_window.hide()
            
            self.input_buffer = ""
            self.last_input_time = 0
            self.last_window = None
            self.input_activated = False
        except Exception as e:
            pass
    
    def on_key_event(self, event):
        """键盘事件处理 - 监听输入状态"""
        if not self.enabled:
            return
        
        # 只处理按下事件
        if event.event_type != 'down':
            return
        
        # 检查当前窗口是否在白名单中
        window = self.get_active_window_info()
        if not window or window['title'] not in self.allowed_windows:
            # 如果不在白名单，清空缓冲区并隐藏悬浮窗
            if self.input_buffer:
                self.input_buffer = ""
                if self.floating_window:
                    self.floating_window.hide()
            return
        
        # 检测窗口切换
        if self.last_window != window['title']:
            self.input_buffer = ""
            self.last_window = window['title']
            self.input_activated = False  # 窗口切换时重置激活状态
            if self.floating_window:
                self.floating_window.hide()
        
        key_name = event.name
        current_time = time.time()
        
        # 检查悬浮窗是否已显示
        floating_visible = self.floating_window and self.floating_window.is_visible
        
        # 处理回车键 - 如果悬浮窗已显示，不处理（由悬浮窗处理）
        if key_name == 'enter':
            if floating_visible:
                return
            # 清空缓冲区和激活状态
            self.input_buffer = ""
            self.input_activated = False
            return
        
        # 如果悬浮窗已显示，不再处理输入（让用户在悬浮窗中输入）
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
            # 检查是否已激活输入状态
            if self.input_activated:
                # 已激活输入状态，按空格时触发悬浮窗
                # 清空缓冲区，不预填充内容
                self.input_buffer = ""
                
                # 获取当前鼠标位置作为点击位置
                try:
                    self.click_position = win32api.GetCursorPos()
                except:
                    self.click_position = (100, 100)
                
                # 显示悬浮窗，不预填充内容
                x, y = self.click_position
                if self.floating_window:
                    self.debug_log(f"显示悬浮窗: 位置({x}, {y})")
                    self.floating_window.show(x + 10, y + 10, window['hwnd'])
            else:
                # 还未激活输入状态，空格作为普通字符添加到缓冲区
                self.input_buffer += ' '
                self.last_input_time = current_time
                self.input_activated = True  # 标记为已激活
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
            self.input_activated = True  # 标记为已激活
            # 不再在输入单字符时触发悬浮窗
            return
        
        # 处理光标移动键 - 清空缓冲区但保持激活状态
        if key_name in ['left', 'right', 'up', 'down', 'home', 'end', 'page up', 'page down']:
            self.input_buffer = ""
            # 保持 input_activated 状态，因为用户可能只是移动光标
            if self.floating_window:
                self.floating_window.hide()
            return
        
        # 处理ESC键
        if key_name in ['esc', 'escape']:
            self.input_buffer = ""
            self.input_activated = False  # 重置激活状态
            if self.floating_window:
                self.floating_window.hide()
            return
    

    
    def show_window_manager(self, *args):
        """显示窗口管理器"""
        if self.window_manager is not None:
            try:
                self.window_manager.window.lift()
                self.window_manager.window.focus_force()
                return
            except:
                self.window_manager = None
        
        def run_window_manager():
            try:
                self.root = tk.Tk()
                self.root.withdraw()
                self.window_manager = WindowSelector(self.root, self.allowed_windows)
                
                def on_closing():
                    try:
                        self.save_window_settings()
                        self.window_manager.window.destroy()
                        self.root.quit()
                    except:
                        pass
                    finally:
                        self.window_manager = None
                        self.root = None
                
                self.window_manager.window.protocol("WM_DELETE_WINDOW", on_closing)
                self.root.mainloop()
            except Exception as e:
                self.debug_log(f"窗口管理器错误: {e}")
        
        # 在独立线程中运行
        thread = threading.Thread(target=run_window_manager, daemon=True)
        thread.start()
    
    def show_replacement_editor(self, *args):
        """显示替换规则编辑器"""
        def run_editor():
            try:
                root = tk.Tk()
                root.withdraw()
                editor = ReplacementRuleEditor(root, self.replacement_rules, self.save_replacement_rules)
                
                def on_closing():
                    try:
                        editor.window.destroy()
                        root.quit()
                    except:
                        pass
                
                editor.window.protocol("WM_DELETE_WINDOW", on_closing)
                root.mainloop()
            except Exception as e:
                self.debug_log(f"替换规则编辑器错误: {e}")
        
        # 在独立线程中运行
        thread = threading.Thread(target=run_editor, daemon=True)
        thread.start()
    
    def setup_tray(self):
        menu = pystray.Menu(
            pystray.MenuItem("启用/禁用", self.toggle),
            pystray.MenuItem("窗口管理", self.show_window_manager),
            pystray.MenuItem("替换规则", self.show_replacement_editor),
            pystray.MenuItem("调试窗口 (Ctrl+Shift+M)", self.show_debug_window),
            pystray.MenuItem(
                f"权限状态: {'✓ 管理员' if self.is_admin else '✗ 普通用户'}",
                lambda: None,
                enabled=False
            ),
            pystray.MenuItem("退出", self.quit_app)
        )
        self.icon = pystray.Icon("AutoMeowEV", 
                                self.create_icon('red'),
                                "AutoMeowEV (禁用)", 
                                menu)

    def quit_app(self, *args):
        """确保程序退出时清理所有资源"""
        def force_exit():
            """强制退出"""
            time.sleep(2)  # 等待2秒
            os._exit(0)  # 强制退出
        
        # 启动强制退出线程作为保险
        force_exit_thread = threading.Thread(target=force_exit, daemon=True)
        force_exit_thread.start()
        
        try:
            self.debug_log("开始退出程序...")
            
            # 停止输入监听
            try:
                keyboard.unhook_all()
                self.debug_log("键盘监听已停止")
            except Exception as e:
                self.debug_log(f"停止键盘监听失败: {e}")
            
            # 关闭调试窗口
            if self.debug_window is not None:
                try:
                    self.debug_window.close()
                    self.debug_log("调试窗口已关闭")
                except Exception as e:
                    self.debug_log(f"关闭调试窗口失败: {e}")
                self.debug_window = None
            
            # 关闭窗口管理器
            if self.window_manager is not None:
                try:
                    if self.window_manager.window:
                        self.window_manager.window.destroy()
                    self.debug_log("窗口管理器已关闭")
                except Exception as e:
                    self.debug_log(f"关闭窗口管理器失败: {e}")
                self.window_manager = None
            
            # 关闭根窗口
            if self.root is not None:
                try:
                    self.root.destroy()
                    self.debug_log("根窗口已关闭")
                except Exception as e:
                    self.debug_log(f"关闭根窗口失败: {e}")
                self.root = None
            
            # 关闭悬浮窗
            if self.floating_window:
                try:
                    self.floating_window.close()
                    self.debug_log("悬浮窗已关闭")
                except Exception as e:
                    self.debug_log(f"关闭悬浮窗失败: {e}")
            
            # 保存设置
            try:
                self.save_window_settings()
                self.debug_log("设置已保存")
            except Exception as e:
                self.debug_log(f"保存设置失败: {e}")
            
            # 停止托盘图标
            if self.icon:
                try:
                    self.icon.stop()
                    self.debug_log("托盘图标已停止")
                except Exception as e:
                    self.debug_log(f"停止托盘图标失败: {e}")
            
            # 关闭事件句柄
            if hasattr(self, 'event') and self.event:
                try:
                    ctypes.windll.kernel32.CloseHandle(self.event)
                    self.debug_log("事件句柄已关闭")
                except Exception as e:
                    self.debug_log(f"关闭事件句柄失败: {e}")
            
            self.debug_log("程序退出完成")
            
        except Exception as e:
            print(f"退出时发生错误: {e}")
        finally:
            # 确保退出
            sys.exit(0)
        sys.exit(0)
    
    def process_text(self, text):
        """处理文本（替换或添加喵）"""
        try:
            if not text or len(text.strip()) == 0:
                return text
            
            # 尝试应用替换规则
            if self.replacement_rules.get("enabled", True):
                replaced = False
                result_text = text
                
                rules = self.replacement_rules.get("rules", [])
                for rule in rules:
                    pattern = rule.get("pattern", "")
                    replacement = rule.get("replacement", "")
                    
                    if not pattern:
                        continue
                    
                    if pattern in result_text:
                        result_text = result_text.replace(pattern, replacement)
                        replaced = True
                
                if replaced:
                    return result_text
            
            # 如果没有替换，在末尾添加"喵"
            return text + "喵"
        except Exception as e:
            # 出错时返回原文本
            return text

    def run(self):
        self.icon.run()

if __name__ == "__main__":
    event = check_single_instance()
    if not event:
        sys.exit(0)
        
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        ctypes.windll.kernel32.CloseHandle(event)
        sys.exit(0)
        
    if getattr(sys, 'frozen', False):
        import os
        os.environ['PYTHONUNBUFFERED'] = '1'
        
    meow = AutoMeowEV()
    try:
        meow.run()
    finally:
        if hasattr(meow, 'event') and meow.event:
            ctypes.windll.kernel32.CloseHandle(meow.event)
