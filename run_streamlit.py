#!/usr/bin/env python3
"""
启动 Streamlit 应用的便捷脚本
"""

import subprocess
import sys
import os

def main():
    """启动 Streamlit 应用"""
    # 确保在正确的目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # 检查 web_app.py 是否存在
    if not os.path.exists("web_app.py"):
        print("❌ 错误: web_app.py 文件不存在")
        sys.exit(1)

    print("🚀 启动 Streamlit 应用...")
    print("📍 应用地址: http://localhost:8501")
    print("⏹️  按 Ctrl+C 停止应用")
    print("-" * 50)

    try:
        # 启动 Streamlit 应用
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "web_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.headless", "false"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except subprocess.CalledProcessError as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print("❌ 错误: 未找到 streamlit。请先安装依赖: uv sync")
        sys.exit(1)

if __name__ == "__main__":
    main()