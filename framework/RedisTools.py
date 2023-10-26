# -*- coding: utf-8 -*-
# @Time    : 2023/10/10 22:37
# @Author  : qxcnwu
# @FileName: RedisTools.py
# @Software: PyCharm

import redis

# redis数据库连接
pool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True)
r = redis.Redis(connection_pool=pool)


def get_task():
    """
    需要以一定的速率获取任务
    :return:
    """
    p = r.blpop(["REDIS_TASK_LIST"])
    return p[1]


def send_task(task_name: str):
    """
    错误任务写回操作
    :return:
    """
    r.lpush("REDIS_TASK_LIST", task_name)
    return


def updateTaskState(task: str, state: str):
    """
    更新任务状态
    :param task:
    :param state:
    :return:
    """
    r.hset("TASK_LIST_MAP", task, state)
    return
