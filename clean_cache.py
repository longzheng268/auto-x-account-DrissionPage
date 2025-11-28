#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
清理 Python 缓存文件
运行此脚本以确保使用最新代码
"""
import os
import shutil
from pathlib import Path

def clean_pycache(directory):
    """递归清理 __pycache__ 目录"""
    count = 0
    for root, dirs, files in os.walk(directory):
        # 删除 __pycache__ 目录
        if '__pycache__' in dirs:
            pycache_path = os.path.join(root, '__pycache__')
            print(f"删除: {pycache_path}")
            shutil.rmtree(pycache_path)
            count += 1
        
        # 删除 .pyc 文件
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                print(f"删除: {pyc_path}")
                os.remove(pyc_path)
                count += 1
    
    return count

if __name__ == '__main__':
    project_dir = Path(__file__).parent
    print("=" * 60)
    print("清理 Python 缓存文件")
    print("=" * 60)
    print(f"项目目录: {project_dir}")
    print()
    
    count = clean_pycache(project_dir)
    
    print()
    print("=" * 60)
    print(f"✅ 清理完成！共删除 {count} 个缓存文件/目录")
    print("=" * 60)
    print()
    print("现在可以运行: python .\\run_register.py")
