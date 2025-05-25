#!/usr/bin/env python3
# Interactive Feedback MCP CLI Version
# Command-line version for headless environments
import os
import sys
import json
import argparse
from typing import Optional, List, Dict

def get_user_input(prompt: str, predefined_options: Optional[List[str]] = None) -> Dict[str, str]:
    """获取用户输入的命令行版本"""
    print("\n" + "="*60)
    print("📝 Interactive Feedback")
    print("="*60)
    print(f"\n{prompt}\n")
    
    selected_options = []
    user_text = ""
    
    # 处理预定义选项
    if predefined_options:
        print("可选选项:")
        for i, option in enumerate(predefined_options, 1):
            print(f"  {i}. {option}")
        
        print("\n请选择选项 (输入数字，多个选项用空格分隔，直接回车跳过):")
        try:
            choice_input = input("选择: ").strip()
            if choice_input:
                choices = choice_input.split()
                for choice in choices:
                    try:
                        idx = int(choice) - 1
                        if 0 <= idx < len(predefined_options):
                            selected_options.append(predefined_options[idx])
                        else:
                            print(f"⚠️  无效选项: {choice}")
                    except ValueError:
                        print(f"⚠️  无效输入: {choice}")
        except KeyboardInterrupt:
            print("\n\n❌ 用户取消操作")
            return {"interactive_feedback": ""}
    
    # 获取自由文本输入
    print("\n请输入您的反馈 (输入完成后按 Ctrl+D 或输入 'END' 结束):")
    print("-" * 40)
    
    lines = []
    try:
        while True:
            try:
                line = input()
                if line.strip() == 'END':
                    break
                lines.append(line)
            except EOFError:
                break
    except KeyboardInterrupt:
        print("\n\n❌ 用户取消操作")
        return {"interactive_feedback": ""}
    
    user_text = '\n'.join(lines).strip()
    
    # 组合结果
    final_feedback_parts = []
    
    if selected_options:
        final_feedback_parts.append("; ".join(selected_options))
    
    if user_text:
        final_feedback_parts.append(user_text)
    
    final_feedback = "\n\n".join(final_feedback_parts)
    
    print("\n" + "="*60)
    if final_feedback:
        print("✅ 反馈已收集")
        print(f"📄 内容预览: {final_feedback[:100]}{'...' if len(final_feedback) > 100 else ''}")
    else:
        print("ℹ️  未提供反馈内容")
    print("="*60)
    
    return {"interactive_feedback": final_feedback}

def main():
    parser = argparse.ArgumentParser(description="Interactive Feedback CLI Tool")
    parser.add_argument("--prompt", required=True, help="The feedback prompt")
    parser.add_argument("--output-file", required=True, help="Output JSON file path")
    parser.add_argument("--predefined-options", default="", help="Predefined options separated by |||")
    
    args = parser.parse_args()
    
    # 解析预定义选项
    predefined_options = None
    if args.predefined_options.strip():
        predefined_options = [opt.strip() for opt in args.predefined_options.split("|||") if opt.strip()]
    
    try:
        # 获取用户反馈
        result = get_user_input(args.prompt, predefined_options)
        
        # 保存结果
        with open(args.output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 结果已保存到: {args.output_file}")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        # 确保即使出错也创建输出文件
        with open(args.output_file, 'w', encoding='utf-8') as f:
            json.dump({"interactive_feedback": ""}, f)
        sys.exit(1)

if __name__ == "__main__":
    main() 