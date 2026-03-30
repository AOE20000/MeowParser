#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MeowParser 稳定性测试
测试程序启动和退出的稳定性
"""

import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer


def test_quick_exit():
    """测试快速启动和退出"""
    print("\n" + "="*60)
    print("测试 1: 快速启动和退出")
    print("="*60)
    
    try:
        from meow_parser import MeowParser
        
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        
        parser = MeowParser()
        print("✅ 程序已启动")
        
        # 等待 1 秒后退出
        def quit_test():
            print("开始退出测试...")
            parser.quit_app()
        
        QTimer.singleShot(1000, quit_test)
        
        # 设置超时
        def force_quit():
            print("⚠️ 测试超时，强制退出")
            sys.exit(1)
        
        QTimer.singleShot(5000, force_quit)
        
        app.exec()
        print("✅ 测试 1 通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试 1 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_with_windows():
    """测试打开窗口后退出"""
    print("\n" + "="*60)
    print("测试 2: 打开窗口后退出")
    print("="*60)
    
    try:
        from meow_parser import MeowParser
        
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        
        parser = MeowParser()
        print("✅ 程序已启动")
        
        # 打开调试窗口
        def open_windows():
            print("打开调试窗口...")
            parser.show_debug_window()
            print("✅ 调试窗口已打开")
        
        QTimer.singleShot(500, open_windows)
        
        # 等待 2 秒后退出
        def quit_test():
            print("开始退出测试...")
            parser.quit_app()
        
        QTimer.singleShot(2000, quit_test)
        
        # 设置超时
        def force_quit():
            print("⚠️ 测试超时，强制退出")
            sys.exit(1)
        
        QTimer.singleShot(6000, force_quit)
        
        app.exec()
        print("✅ 测试 2 通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试 2 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_enable_disable():
    """测试启用/禁用后退出"""
    print("\n" + "="*60)
    print("测试 3: 启用/禁用后退出")
    print("="*60)
    
    try:
        from meow_parser import MeowParser
        
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        
        parser = MeowParser()
        print("✅ 程序已启动")
        
        # 检查是否有管理员权限
        if not parser.is_admin:
            print("⚠️ 没有管理员权限，跳过启用测试")
            parser.quit_app()
            print("✅ 测试 3 通过（跳过）")
            return True
        
        # 启用功能
        def enable_test():
            print("启用功能...")
            parser.toggle()
            print("✅ 功能已启用")
        
        QTimer.singleShot(500, enable_test)
        
        # 禁用功能
        def disable_test():
            print("禁用功能...")
            parser.toggle()
            print("✅ 功能已禁用")
        
        QTimer.singleShot(1500, disable_test)
        
        # 退出
        def quit_test():
            print("开始退出测试...")
            parser.quit_app()
        
        QTimer.singleShot(2500, quit_test)
        
        # 设置超时
        def force_quit():
            print("⚠️ 测试超时，强制退出")
            sys.exit(1)
        
        QTimer.singleShot(6000, force_quit)
        
        app.exec()
        print("✅ 测试 3 通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试 3 失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试函数"""
    print("="*60)
    print("MeowParser 稳定性测试")
    print("="*60)
    print("\n⚠️ 注意：")
    print("- 这些测试会自动启动和关闭程序")
    print("- 请不要手动操作")
    print("- 如果测试卡住超过 10 秒，请手动终止")
    print()
    
    input("按 Enter 开始测试...")
    
    results = []
    
    # 运行测试
    print("\n开始运行测试...")
    
    # 测试 1
    results.append(("快速启动和退出", test_quick_exit()))
    time.sleep(1)
    
    # 测试 2
    results.append(("打开窗口后退出", test_with_windows()))
    time.sleep(1)
    
    # 测试 3
    results.append(("启用/禁用后退出", test_enable_disable()))
    
    # 统计结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过 ({passed*100//total}%)")
    
    if passed == total:
        print("\n🎉 所有稳定性测试通过！")
        return 0
    else:
        print(f"\n⚠️ {total - passed} 个测试失败")
        print("请检查 STABILITY_ANALYSIS.md 了解详情")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
