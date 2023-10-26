# -*- coding: utf-8 -*-
# @Time    : 2023/10/11 10:35
# @Author  : qxcnwu
# @FileName: AodProcess.py
# @Software: PyCharm

import os.path

from Process import ProcessFather


class Process(ProcessFather):
    def __init__(self, taskName: str, save_dir: str):
        super().__init__(taskName, save_dir)
        self.date = None
        self.product_name = "MOD05_L2"
        self.attr = "Water_Vapor_Near_Infrared"

    def _parse_date(self):
        """
        解析日期
        :return:
        """
        dt = self.task_name.split('_')[1]
        self.date = dt[0:4] + "-" + dt[4:6] + "-" + dt[6:]
        return

    def _make_dir(self):
        """
        创建文件的工作目录
        :return:
        """
        self.work_space = os.path.join("../temp", self.task_name)
        if not os.path.exists(self.work_space):
            os.mkdir(self.work_space)
        return

    def process(self):
        """
        处理
        :return:
        """
        # 首先创建工作目录
        self._make_dir()
        # 解析日期
        self._parse_date()
        # 下载文件
        self._downloadMain(self.date, self.product_name)
        # 下载完成进行处理
        self._concatMain()
        return
