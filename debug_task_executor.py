#!/usr/bin/env python3
"""
RAGFlow Task Executor Debug Launcher for PyCharm
用于在PyCharm中调试RAGFlow任务执行器的启动脚本
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_environment():
    """设置必要的环境变量"""
    project_root = Path(__file__).parent.absolute()
    
    # 设置Python路径
    os.environ['PYTHONPATH'] = str(project_root)
    
    # 设置库路径（如果在Linux环境下）
    if sys.platform.startswith('linux'):
        os.environ['LD_LIBRARY_PATH'] = '/usr/lib/x86_64-linux-gnu/'
    
    # 清除代理设置
    proxy_vars = ['http_proxy', 'https_proxy', 'no_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'NO_PROXY']
    for var in proxy_vars:
        os.environ[var] = ''
    
    # 设置NLTK数据目录
    os.environ['NLTK_DATA'] = str(project_root / 'nltk_data')
    
    # 设置任务执行器相关环境变量
    os.environ.setdefault('MAX_CONCURRENT_TASKS', '5')
    os.environ.setdefault('MAX_CONCURRENT_CHUNK_BUILDERS', '1')
    os.environ.setdefault('MAX_CONCURRENT_MINIO', '10')
    os.environ.setdefault('WORKER_HEARTBEAT_TIMEOUT', '120')
    
    # 检查虚拟环境
    venv_python = project_root / '.venv' / 'bin' / 'python'
    if not venv_python.exists():
        print(f"错误: Python虚拟环境不存在: {venv_python}")
        print("请先运行: uv sync --python 3.10")
        sys.exit(1)
    
    print(f"项目根目录: {project_root}")
    print(f"PYTHONPATH: {os.environ['PYTHONPATH']}")
    print(f"NLTK_DATA: {os.environ['NLTK_DATA']}")

def check_dependencies():
    """检查必要的依赖服务"""
    services = [
        ('MySQL', 'localhost', 5455),
        ('Redis', 'localhost', 6379),
        ('Elasticsearch', 'localhost', 1200),
        ('MinIO', 'localhost', 9000)
    ]
    
    print("检查依赖服务...")
    for service_name, host, port in services:
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((host, port))
            sock.close()
            
            if result == 0:
                print(f"✓ {service_name} ({host}:{port}) - 运行中")
            else:
                print(f"✗ {service_name} ({host}:{port}) - 未运行")
                print(f"  请先启动: docker compose -f docker/docker-compose-base.yml up -d")
        except Exception as e:
            print(f"✗ {service_name} - 检查失败: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("RAGFlow Task Executor Debug Launcher")
    print("=" * 60)
    
    # 设置环境
    setup_environment()
    
    # 检查依赖
    check_dependencies()
    
    # 设置任务执行器ID（默认为0）
    task_id = sys.argv[1] if len(sys.argv) > 1 else "0"
    print(f"\n启动任务执行器 ID: {task_id}")
    print("在PyCharm中设置断点，然后运行此脚本进行调试")
    print("=" * 60)
    
    # 导入并启动任务执行器
    try:
        # 切换到项目根目录
        os.chdir(Path(__file__).parent)
        
        # 设置命令行参数
        sys.argv = ['task_executor.py', task_id]
        
        # 启动任务执行器 - 直接执行task_executor.py的主逻辑
        import runpy
        runpy.run_path('rag/svr/task_executor.py', run_name='__main__')
        
    except KeyboardInterrupt:
        print("\n任务执行器已停止")
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main() 