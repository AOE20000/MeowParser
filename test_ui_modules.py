#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新提取的 UI 模块
"""

import sys

def test_imports():
    """测试模块导入"""
    print("测试 UI 模块导入...")
    
    try:
        from meow_parser.ui import (
            DebugWindow,
            FloatingInputWindow,
            WindowSelector,
            ConfigFileEditor,
            RuleEditDialog,
            ReplacementRuleEditor,
            RuleDialog,
            TrayIconManager
        )
        print("✅ 所有 UI 模块导入成功 (8/8)")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False

def test_core_modules():
    """测试核心模块"""
    print("\n测试核心模块...")
    
    try:
        from meow_parser.core import (
            ConfigFileManager,
            TextProcessor,
            check_single_instance
        )
        print("✅ 核心模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 核心模块导入失败: {e}")
        return False

def test_platform_modules():
    """测试平台模块"""
    print("\n测试平台模块...")
    
    try:
        from meow_parser.platform import (
            get_active_window_info,
            enumerate_windows,
            set_foreground_window,
            click_position,
            set_window_topmost,
            IS_WINDOWS,
            IS_LINUX,
            IS_MACOS
        )
        
        platform_name = "Windows" if IS_WINDOWS else "Linux" if IS_LINUX else "macOS" if IS_MACOS else "Unknown"
        print(f"  当前平台: {platform_name}")
        print("✅ 平台模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 平台模块导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_manager():
    """测试配置管理器"""
    print("\n测试配置管理器...")
    
    try:
        from meow_parser.core import ConfigFileManager
        
        # 创建配置管理器实例
        config_mgr = ConfigFileManager()
        
        # 列出配置
        configs = config_mgr.list_configs()
        print(f"  找到 {len(configs)} 个配置文件")
        
        # 获取所有规则
        rules = config_mgr.get_all_rules()
        print(f"  当前配置包含 {len(rules)} 条规则")
        
        print("✅ 配置管理器测试通过")
        return True
    except Exception as e:
        print(f"❌ 配置管理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_text_processor():
    """测试文本处理器"""
    print("\n测试文本处理器...")
    
    try:
        from meow_parser.core import ConfigFileManager, TextProcessor
        
        # 创建配置管理器和文本处理器
        config_mgr = ConfigFileManager()
        processor = TextProcessor(config_mgr)
        
        # 测试文本处理
        test_text = "你好世界"
        result = processor.process(test_text)
        print(f"  输入: {test_text}")
        print(f"  输出: {result}")
        
        print("✅ 文本处理器测试通过")
        return True
    except Exception as e:
        print(f"❌ 文本处理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("MeowParser 模块测试")
    print("=" * 60)
    
    results = []
    
    # 运行测试
    results.append(("UI 模块导入", test_imports()))
    results.append(("核心模块导入", test_core_modules()))
    results.append(("平台模块导入", test_platform_modules()))
    results.append(("配置管理器", test_config_manager()))
    results.append(("文本处理器", test_text_processor()))
    
    # 统计结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过 ({passed*100//total}%)")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
