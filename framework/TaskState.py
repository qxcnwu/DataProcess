# -*- coding: utf-8 -*-
# @Time    : 2023/9/11 14:14
# @Author  : qxcnwu
# @FileName: TaskState.py
# @Software: PyCharm

# 当前任务的枚举状态
class TaskState:
    NEW = "0"
    RUNABLE = "1"
    RUNNING = "2"
    ERROR = "3"
    OK = "4"
    LOSS = "5"