# -*- coding: utf-8 -*-
# @Time    : 2023/9/11 14:12
# @Author  : qxcnwu
# @FileName: RegisterCenter.py
# @Software: PyCharm

import threading

from tqdm import tqdm

from framework.TaskDispatcher import TaskDispatcher


def make_thread(save_dir: str):
    """
    制作单一的线程逻辑
    :return:
    """
    TaskDispatcher(save_dir).try_get()
    return


class RegisterCenter:
    def __init__(self, size: int, save_dir: str = "D:/temp"):
        """
        创建多个线程
        :param size:
        """
        self.save_dir = save_dir
        self.threads = []
        # 创建size个线程
        for _ in tqdm(range(size)):
            self.threads.append(self._create_thread())
        for th in self.threads:
            th.start()
        for th in self.threads:
            th.join()

    def _create_thread(self):
        """
        创建单一的线程
        :return:
        """
        # todo 2023/10/11
        t = threading.Thread(target=make_thread, args=(self.save_dir,))
        t.setDaemon(True)
        return t


if __name__ == '__main__':
    # size = int(sys.argv[1])
    size = 1
    RegisterCenter(size)