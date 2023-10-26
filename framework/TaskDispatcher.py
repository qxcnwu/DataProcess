# -*- coding: utf-8 -*-
# @Time    : 2023/10/11 10:36
# @Author  : qxcnwu
# @FileName: TaskDispatcher.py
# @Software: PyCharm
import os
import logging
from RedisTools import *

logging.basicConfig(level=logging.INFO)


class TaskDispatcher:
    def __init__(self, save_dir: str):
        """
        首先加载对应的process
        """
        self.save_dir = save_dir
        self.start = True
        self.module_path = "."

    def try_get(self):
        """
        不断尝试获取新的任务
        :return:
        """
        while self.start:
            try:
                # 获取当前的任务
                task_name = get_task()
                logging.info("Get " + task_name + " from task list")
                # 处理的主要函数
                self._process_main(task_name)
            except:
                pass
        return

    def _process_main(self, name: str):
        """
        处理当前任务
        :param name:
        :return:
        """
        try:
            product_name = name.split("_")[0]
            # 首先需要加载当前的处理的类
            logging.info("Start get class object")
            c_name = self._find_process_class(product_name)
            # 加载对应的类并创建对象
            logging.info("Start create class object")
            c_object = self._insert_class(c_name, name)
            # 执行处理逻辑
            logging.info("Start run task")
            c_object.run_task()
        except Exception as ex:
            logging.error(ex)
        return

    def _find_process_class(self, name: str) -> str:
        """
        查找对应的处理类
        :return:
        """
        files = os.listdir(self.module_path)
        for file in files:
            if file.endswith("py") and file.lower() == name.lower() + "process.py":
                return file.split(".")[0]
        return ""

    def _insert_class(self, imp_module: str, task_name: str):
        """
        动态加载类
        :param imp_module:
        :return:
        """
        imp_class = 'Process'
        # 导入指定模块，导入时会执行全局方法。
        ip_module = __import__(imp_module)
        # 动态加载类test_class生成类对象
        cls_obj = getattr(ip_module, imp_class)(task_name, self.save_dir)
        return cls_obj
