#!/bin/bash

.venv/bin/python src/main.py

# 检查上一条命令是否成功
if [ $? -eq 0 ]; then
    git push -u origin main
else
    echo "Python 程序执行失败，取消 Git push"
    exit 1
fi