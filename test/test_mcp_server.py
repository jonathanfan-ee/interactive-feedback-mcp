#!/usr/bin/env python3
"""
简单的MCP客户端测试脚本
用于测试MCP服务器是否正常工作
"""

import json
import subprocess
import sys
import time

def test_mcp_server():
    """测试MCP服务器的基本功能"""
    print("🧪 测试MCP服务器...")
    
    # 启动服务器进程
    process = subprocess.Popen(
        [sys.executable, "server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    try:
        # 1. 发送初始化请求
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("📤 发送初始化请求...")
        process.stdin.write(json.dumps(init_request) + "\n")
        process.stdin.flush()
        
        # 读取响应
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line.strip())
            print(f"📥 初始化响应: {response}")
            
            if "result" in response:
                print("✅ 初始化成功")
                
                # 2. 发送initialized通知
                initialized_notification = {
                    "jsonrpc": "2.0",
                    "method": "notifications/initialized"
                }
                
                print("📤 发送initialized通知...")
                process.stdin.write(json.dumps(initialized_notification) + "\n")
                process.stdin.flush()
                
                # 3. 请求工具列表
                tools_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/list"
                }
                
                print("📤 请求工具列表...")
                process.stdin.write(json.dumps(tools_request) + "\n")
                process.stdin.flush()
                
                # 读取工具列表响应
                tools_response_line = process.stdout.readline()
                if tools_response_line:
                    tools_response = json.loads(tools_response_line.strip())
                    print(f"📥 工具列表响应: {tools_response}")
                    
                    if "result" in tools_response and "tools" in tools_response["result"]:
                        tools = tools_response["result"]["tools"]
                        print(f"✅ 找到 {len(tools)} 个工具:")
                        for tool in tools:
                            print(f"   - {tool['name']}: {tool['description']}")
                        return True
                    else:
                        print("❌ 工具列表响应格式错误")
                        return False
                else:
                    print("❌ 未收到工具列表响应")
                    return False
            else:
                print(f"❌ 初始化失败: {response}")
                return False
        else:
            print("❌ 未收到初始化响应")
            return False
            
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        return False
    finally:
        # 清理进程
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()

if __name__ == "__main__":
    success = test_mcp_server()
    if success:
        print("\n🎉 MCP服务器测试通过！")
        sys.exit(0)
    else:
        print("\n💥 MCP服务器测试失败！")
        sys.exit(1) 