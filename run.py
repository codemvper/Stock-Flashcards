#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动脚本
"""
import os
import sys

# 添加backend目录到Python路径
backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_dir)

from backend.app import app

if __name__ == '__main__':
    # 获取环境变量
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    print(f"""
    ╔══════════════════════════════════════════════╗
    ║   A股上市公司闪卡 - 后端服务启动中...        ║
    ╠══════════════════════════════════════════════╣
    ║   地址: http://{host}:{port}              ║
    ║   模式: {'开发模式' if debug else '生产模式'}                            ║
    ╚══════════════════════════════════════════════╝
    """)
    
    app.run(host=host, port=port, debug=debug)

