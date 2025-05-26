#!/usr/bin/env python3
# Interactive Feedback MCP Web Version
# Web-based version for headless environments
import os
import sys
import json
import argparse
import threading
import time
import webbrowser
import tempfile
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from typing import Optional, List, Dict

class FeedbackHandler(BaseHTTPRequestHandler):
    def __init__(self, prompt, predefined_options, result_container, *args, **kwargs):
        self.prompt = prompt
        self.predefined_options = predefined_options or []
        self.result_container = result_container
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = self.generate_html()
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/submit':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # 解析表单数据
            data = parse_qs(post_data.decode('utf-8'))
            
            # 处理选择的选项
            selected_options = []
            for i, option in enumerate(self.predefined_options):
                if f'option_{i}' in data:
                    selected_options.append(option)
            
            # 获取自由文本
            user_text = data.get('feedback_text', [''])[0].strip()
            
            # 组合结果
            final_feedback_parts = []
            if selected_options:
                final_feedback_parts.append("; ".join(selected_options))
            if user_text:
                final_feedback_parts.append(user_text)
            
            final_feedback = "\n\n".join(final_feedback_parts)
            
            # 保存结果
            self.result_container['feedback'] = final_feedback
            self.result_container['completed'] = True
            
            # 发送成功页面
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            
            success_html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>反馈已提交</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        max-width: 500px; 
                        margin: 80px auto; 
                        padding: 20px; 
                        background-color: #f5f5f5;
                    }
                    .container {
                        background: white;
                        padding: 40px;
                        border-radius: 12px;
                        border: 1px solid #ddd;
                        text-align: center;
                    }
                    .success-icon {
                        font-size: 64px;
                        margin-bottom: 20px;
                    }
                    .success-title {
                        color: #155724;
                        font-size: 24px;
                        font-weight: 600;
                        margin-bottom: 15px;
                    }
                    .success-message {
                        color: #666;
                        font-size: 16px;
                        line-height: 1.5;
                        margin-bottom: 30px;
                    }
                    .close-instruction {
                        background: #e3f2fd;
                        border: 1px solid #bbdefb;
                        border-radius: 8px;
                        padding: 20px;
                        margin: 20px 0;
                    }
                    .close-instruction h4 {
                        margin: 0 0 10px 0;
                        color: #1976d2;
                        font-size: 16px;
                    }
                    .close-instruction p {
                        margin: 5px 0;
                        color: #555;
                        font-size: 14px;
                    }
                    .keyboard-shortcut {
                        background: #e9ecef;
                        padding: 3px 8px;
                        border-radius: 4px;
                        font-family: monospace;
                        font-weight: bold;
                    }
                    .footer-note {
                        color: #999;
                        font-size: 12px;
                        margin-top: 30px;
                        font-style: italic;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="success-icon">✅</div>
                    <div class="success-title">反馈已成功提交！</div>
                    <div class="success-message">
                        现在可以关闭此页面，返回到 Cursor 继续工作。
                    </div>
                    
                    <div class="close-instruction">
                        <h4>💡 如何关闭此页面</h4>
                        <p>• 键盘快捷键：<span class="keyboard-shortcut">Ctrl + W</span> (Windows/Linux) 或 <span class="keyboard-shortcut">Cmd + W</span> (Mac)</p>
                        <p>• 点击浏览器标签页上的 ✕ 按钮</p>
                        <p>• 或直接切换回 Cursor 继续工作</p>
                    </div>
                    
                    <div class="footer-note">
                        此页面可以安全关闭，不会影响您的工作流程
                    </div>
                </div>
            </body>
            </html>
            """
            self.wfile.write(success_html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

    def generate_html(self):
        options_html = ""
        if self.predefined_options:
            options_html = "<h3>可选选项：</h3>"
            for i, option in enumerate(self.predefined_options):
                options_html += f"""
                <label>
                    <input type="checkbox" name="option_{i}" value="1"> {option}
                </label>
                """

        # 安全地转义prompt内容
        prompt_escaped = json.dumps(self.prompt)

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Interactive Feedback</title>
            <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    font-size: 13px;
                    max-width: 800px;
                    margin: 15px auto;
                    padding: 15px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    background: white;
                    padding: 20px;
                    border: 1px solid #ddd;
                }}
                .prompt {{
                    background: #e3f2fd;
                    padding: 15px;
                    margin-bottom: 20px;
                    border-left: 4px solid #2196f3;
                    line-height: 1.3;
                    font-size: 13px;
                }}
                
                /* Markdown 样式 */
                .prompt h1, .prompt h2, .prompt h3, .prompt h4, .prompt h5, .prompt h6 {{
                    margin-top: 0;
                    margin-bottom: 8px;
                    font-weight: 600;
                    line-height: 1.2;
                }}
                .prompt h1 {{ font-size: 1.6em; border-bottom: 1px solid #eaecef; padding-bottom: 8px; }}
                .prompt h2 {{ font-size: 1.3em; border-bottom: 1px solid #eaecef; padding-bottom: 6px; }}
                .prompt h3 {{ font-size: 1.1em; }}
                .prompt h4 {{ font-size: 1em; }}
                .prompt h5 {{ font-size: 0.9em; }}
                .prompt h6 {{ font-size: 0.85em; color: #6a737d; }}
                
                .prompt p {{
                    margin-bottom: 8px;
                }}
                
                .prompt ul, .prompt ol {{
                    padding-left: 25px;
                    margin-bottom: 8px;
                    margin-top: 4px;
                }}
                
                .prompt li {{
                    margin-bottom: 1px;
                    line-height: 1.3;
                }}
                
                .prompt strong {{
                    font-weight: 600;
                }}
                
                .prompt em {{
                    font-style: italic;
                }}
                
                .prompt code {{
                    background-color: rgba(27,31,35,0.05);
                    font-size: 85%;
                    margin: 0;
                    padding: 0.2em 0.4em;
                    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                }}
                
                .prompt pre {{
                    background-color: #f6f8fa;
                    font-size: 12px;
                    line-height: 1.3;
                    overflow: auto;
                    padding: 10px;
                    margin-bottom: 8px;
                }}
                
                .prompt pre code {{
                    background-color: transparent;
                    border: 0;
                    display: inline;
                    line-height: inherit;
                    margin: 0;
                    max-width: auto;
                    overflow: visible;
                    padding: 0;
                    word-wrap: normal;
                }}
                
                .prompt blockquote {{
                    border-left: 4px solid #dfe2e5;
                    color: #6a737d;
                    padding: 0 16px;
                    margin: 0 0 16px 0;
                }}
                
                .prompt table {{
                    border-collapse: collapse;
                    border-spacing: 0;
                    width: 100%;
                    margin-bottom: 16px;
                }}
                
                .prompt table th, .prompt table td {{
                    border: 1px solid #dfe2e5;
                    padding: 6px 13px;
                }}
                
                .prompt table th {{
                    background-color: #f6f8fa;
                    font-weight: 600;
                }}
                
                textarea {{
                    width: 100%;
                    min-height: 100px;
                    padding: 8px;
                    border: 1px solid #ddd;
                    font-size: 14px;
                    resize: vertical;
                }}
                button {{
                    background: #4caf50;
                    color: white;
                    padding: 8px 16px;
                    border: none;
                    cursor: pointer;
                    font-size: 13px;
                    margin-top: 12px;
                }}
                button:hover {{
                    background: #45a049;
                }}
                .cancel-btn {{
                    background: #f44336;
                    margin-left: 8px;
                }}
                .cancel-btn:hover {{
                    background: #da190b;
                }}
                h1 {{
                    color: #333;
                    text-align: center;
                    margin-bottom: 20px;
                    font-size: 20px;
                }}
                h3 {{
                    font-size: 14px;
                    margin-bottom: 8px;
                }}
                label {{
                    cursor: pointer;
                    font-size: 13px;
                    display: block;
                    margin: 6px 0;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📝 Interactive Feedback</h1>
                
                <div class="prompt" id="promptContainer">
                    <div id="promptContent"></div>
                </div>
                
                <form method="post" action="/submit">
                    {options_html}
                    
                    <h3>您的反馈：</h3>
                    <textarea name="feedback_text" placeholder="请在此输入您的详细反馈...&#10;&#10;💡 提示：按 Ctrl+Enter 快速提交"></textarea>
                    
                    <div>
                        <button type="submit">✅ 提交反馈</button>
                        <button type="button" class="cancel-btn" onclick="submitEmpty()">❌ 取消</button>
                    </div>
                </form>
            </div>
            
            <script>
                // 渲染 Markdown 内容
                function renderMarkdown() {{
                    const promptText = {prompt_escaped};
                    const promptContainer = document.getElementById('promptContent');
                    
                    // 先显示原始内容作为备用
                    promptContainer.innerHTML = '<strong>提示：</strong> ' + promptText.replace(/\\n/g, '<br>');
                    
                    // 检查marked库是否可用
                    if (typeof marked !== 'undefined') {{
                        try {{
                            // 使用 marked 库解析 Markdown
                            const htmlContent = marked.parse(promptText);
                            promptContainer.innerHTML = '<strong>提示：</strong><br>' + htmlContent;
                            console.log('Markdown渲染成功');
                        }} catch (error) {{
                            console.warn('Markdown parsing failed:', error);
                            // 保持原始文本显示
                        }}
                    }} else {{
                        console.warn('marked库未加载，使用原始文本显示');
                    }}
                }}
                
                function submitEmpty() {{
                    if (confirm('确定要取消吗？这将提交空反馈。')) {{
                        var form = document.querySelector('form');
                        var textarea = document.querySelector('textarea');
                        var checkboxes = document.querySelectorAll('input[type="checkbox"]');
                        
                        // 清空所有输入
                        textarea.value = '';
                        checkboxes.forEach(cb => cb.checked = false);
                        
                        form.submit();
                    }}
                }}
                
                // 页面加载完成后初始化
                document.addEventListener('DOMContentLoaded', function() {{
                    renderMarkdown();
                    
                    // 添加Ctrl+Enter快捷键提交反馈
                    const textarea = document.querySelector('textarea');
                    textarea.addEventListener('keydown', function(e) {{
                        if (e.ctrlKey && e.key === 'Enter') {{
                            e.preventDefault();
                            document.querySelector('form').submit();
                        }}
                    }});
                    
                    // 暂时移除自动聚焦，避免干扰中文输入法
                    // textarea.focus();
                }});
            </script>
        </body>
        </html>
        """
        return html

    def log_message(self, format, *args):
        # 禁用日志输出
        pass

def create_handler(prompt, predefined_options, result_container):
    def handler(*args, **kwargs):
        return FeedbackHandler(prompt, predefined_options, result_container, *args, **kwargs)
    return handler

def get_user_input_web(prompt: str, predefined_options: Optional[List[str]] = None) -> Dict[str, str]:
    """通过 Web 界面获取用户输入"""
    result_container = {'feedback': '', 'completed': False}
    
    # 创建 HTTP 服务器
    handler = create_handler(prompt, predefined_options, result_container)
    server = HTTPServer(('localhost', 0), handler)  # 使用随机端口
    port = server.server_address[1]
    
    # 在后台启动服务器
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    url = f"http://localhost:{port}"
    print(f"🌐 请在浏览器中打开以下链接提供反馈：", flush=True)
    print(f"   {url}", flush=True)
    print(f"📱 或者扫描二维码（如果支持）", flush=True)
    
    # 尝试自动打开浏览器
    try:
        webbrowser.open(url)
        print("✅ 已尝试自动打开浏览器", flush=True)
    except:
        print("⚠️  无法自动打开浏览器，请手动复制链接", flush=True)
    
    # 等待用户完成
    print("⏳ 等待用户反馈...", flush=True)
    timeout = 300  # 5分钟超时
    start_time = time.time()
    
    while not result_container['completed']:
        if time.time() - start_time > timeout:
            print("⏰ 超时，返回空反馈", flush=True)
            break
        time.sleep(1)
    
    server.shutdown()
    server.server_close()
    
    return {"interactive_feedback": result_container['feedback']}

def main():
    parser = argparse.ArgumentParser(description="Interactive Feedback Web Tool")
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
        result = get_user_input_web(args.prompt, predefined_options)
        
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