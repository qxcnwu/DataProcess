# -*- coding: utf-8 -*-
# @Time    : 2023/10/11 10:43
# @Author  : qxcnwu
# @FileName: Process.py
# @Software: PyCharm
import logging
import os
import struct
from abc import abstractmethod
from struct import pack

import numpy as np
from ModisDownload.Visited import GetHtml
from PIL import Image
from matplotlib import pyplot as plt
from pyhdf.SD import SD
from tqdm import tqdm

import framework.RedisTools as rd
from framework.TaskState import TaskState

logging.basicConfig(level=logging.INFO)


def get_line_data():
    """
    获取国境线表示
    :return:
    """
    return np.array(Image.open("extend/test.png"))


def get_mask_array():
    """
    返回
    :return:
    """
    return np.load("extend/china_line.npy")


def convert_to_rgb(datas: np.array, mask_array: np.array, line_data: np.array, save_path: str,
                   remove_zeros: bool = True):
    """

    :param data:
    :param mask_array:
    :param line_data:
    :param save_path:
    :param remove_zeros:
    :return:
    """
    data = datas.copy()
    max_v = np.max(data)
    min_v = np.min(data)
    if remove_zeros:
        data[data <= 0] = np.nan
    # 创建画布
    fig, ax = plt.subplots()
    # 绘制底图
    pic = ax.imshow(data, interpolation='none', cmap='rainbow', vmax=max_v, vmin=min_v)
    position = fig.add_axes([0.15, 0.15, 0.7, 0.03])
    # 位置[左,下,右,上]
    plt.colorbar(pic, cax=position, orientation='horizontal', fraction=0.035, pad=0.04, shrink=0)
    ax.set_xticks([])
    ax.set_yticks([])
    # 插入国界线
    axin = ax.inset_axes(
        [0, 0, 631, 361], transform=ax.transData)
    axin.imshow(mask_array * 0, alpha=mask_array)
    axin.axis('off')
    # 插入九段线
    axins = ax.inset_axes(
        [631 - int(68 * 1.5), 361 - int(84 * 1.5), int(68 * 1.5), int(84 * 1.5)], transform=ax.transData)
    axins.set_xticks([])
    axins.set_yticks([])
    axins.imshow(line_data)
    plt.savefig(save_path, bbox_inches='tight', dpi=600, pad_inches=0.0)
    plt.close(fig)
    return


def make_fill_bin(save_name: str, datas: np.array):
    """
    将fill结果写入bin文件
    :return:
    """
    data = datas.copy()
    x, y = data.shape
    data[data > 0] = 1
    dat = np.zeros((x + 1, y + 1))
    for i in range(x):
        for j in range(y):
            dat[i + 1, j + 1] = data[i][j] + dat[i][j + 1] + dat[i + 1][j] - dat[i][j]
    f = open(save_name, 'wb')
    x, y = dat.shape
    for i in range(x):
        for j in range(y):
            f.write(struct.pack('>d', dat[i][j]))
    f.close()
    return


def make_fill_sum_bin(save_name: str, datas: np.array):
    """
    将fill结果写入bin文件
    :return:
    """
    data = datas.copy()
    x, y = data.shape
    dat = np.zeros((x + 1, y + 1))
    for i in range(x):
        for j in range(y):
            dat[i + 1, j + 1] = data[i][j] + dat[i][j + 1] + dat[i + 1][j] - dat[i][j]
    f = open(save_name, 'wb')
    x, y = dat.shape
    for i in range(x):
        for j in range(y):
            f.write(struct.pack('>d', dat[i][j]))
    f.close()
    return


class ProcessFather:
    def __init__(self, taskName: str, save_dir: str):
        """
        初始化
        :param taskName:
        :param save_dir:
        """
        self.task_name = taskName
        self.save_dir_path = save_dir
        self.token = "cXhjMTIzOmNYaGpibmQxUUdkdFlXbHNMbU52YlE9PToxNjUwMTEwOTMyOjU4N2U5ZjEwYjhiODA5NTUyODdmMjU3NDMxYTYxMjNmZDIzMTViN2Q"
        self.work_space = ""
        self.array = np.load("extend/China.npy").astype(np.float32)
        self.attr = None

    def _change_state(self, state: str):
        """
        改变任务的状态
        :param state:
        :return:
        """
        rd.updateTaskState(self.task_name, state)
        return

    def run_task(self):
        """
        执行任务
        :return:
        """
        try:
            self._change_state(TaskState.RUNNING)
            # 执行处理
            self.process()
            # 更改状态
            self._change_state(TaskState.OK)
        except Exception as ex:
            # 需要将状态更改为错误
            self._change_state(TaskState.ERROR)
            # 打印错误日志
            logging.error(ex)
        return

    def _downloadMain(self, date: str, product: str):
        """
        下载文件的主函数
        :param name:
        :param date:
        :param product:
        :return:
        """
        logging.info("Start download files!!")
        g = GetHtml(self.token)
        g.download_main(product, date, "china", self.work_space, thread_num=1, max_try=5)
        return

    def _concatMain(self):
        """
        拼接下载完成的对象
        :return:
        """

        def __copy_array(path: str, temp_array, sum_array):
            """
            拷贝对应的参数
            :param path:
            :param temp_array:
            :param sum_array:
            :return:
            """
            temp = SD(path)
            data_dic = temp.datasets()
            if not data_dic.__contains__(self.attr) and data_dic.__contains__("Longitude") and data_dic.__contains__(
                    "Latitude"):
                return False, temp_array, sum_array
            lat = np.array(temp.select("Latitude")[:])
            lon = np.array(temp.select("Longitude")[:])
            prop = np.array(temp.select(self.attr)[:]).astype(np.float32)
            lon = np.round((lon - 73) * 10).astype(np.int32)
            lat = np.round((lat - 18) * 10).astype(np.int32)
            for i in range(prop.shape[0]):
                for j in range(prop.shape[1]):
                    if 0 <= lat[i, j] < self.array.shape[0] and 0 <= lon[i, j] < self.array.shape[1] and prop[i, j] > 0:
                        temp_array[lat[i, j], lon[i, j]] += prop[i, j]
                        sum_array[lat[i, j], lon[i, j]] += 1
            return True, temp_array, sum_array

        def __save_bin(array, path):
            """
            保存bin文件
            :param array:
            :param path:
            :return:
            """
            f = open(path, 'wb')
            x, y = array.shape
            for i in range(x):
                for j in range(y):
                    f.write(pack('>d', array[i][j]))
            f.close()
            return

        def __save_pic(data, path):
            """
            保存图像文件
            :param data:
            :param path:
            :return:
            """
            data = data + 1
            im = Image.fromarray(np.array(data * 256 / np.max(data)).astype(np.uint8))
            im.save(path)
            return

        def __save_other(data, png_rgb_name, fill_bin, fill_bin_mean):
            """
            保存其他文件
            :param data:
            :param pic:
            :return:
            """
            mask_array = get_mask_array()
            line_array = get_line_data()
            # 转换为彩色
            convert_to_rgb(data, mask_array=mask_array, line_data=line_array, save_path=png_rgb_name)
            # 保存新的bin文件
            make_fill_bin(fill_bin, data)
            # 保存求和文件
            make_fill_sum_bin(fill_bin_mean, data)
            return

        logging.info("Start init array")
        # 初始化
        temp_array = np.zeros(self.array.shape)
        sum_array = np.zeros(self.array.shape)
        files = os.listdir(self.work_space)

        # 如果下载的文件数量为0那么我们将任务标记为写回任务队列
        if len(files) == 0:
            logging.error("Download file error!!" + self.task_name)
            rd.send_task(self.task_name)
            return

        logging.info("Start copy array")
        # 拷贝文件
        for file in tqdm(files):
            bo, temp_array, sum_array = __copy_array(os.path.join(self.work_space, file), temp_array, sum_array)
            if not bo:
                return
        # 翻转文件
        temp_array = np.flipud(temp_array)
        sum_array = np.flipud(sum_array)
        # 取消对中国边界的限制
        # temp_array[self.array == -1] = -1
        temp_array[temp_array > 0] = temp_array[temp_array > 0] / sum_array[temp_array > 0] / 1000

        logging.info("Start save array")
        # 保存文件
        save_path = os.path.join(self.save_dir_path, self.task_name + ".bin")
        save_pic = os.path.join(self.save_dir_path, self.task_name + ".png")
        png_rgb_name = os.path.join(self.save_dir_path, self.task_name + "_rgb.png")
        fill_bin = os.path.join(self.save_dir_path, self.task_name + "_fill.bin")
        fill_bin_mean = os.path.join(self.save_dir_path, self.task_name + "_fille_mean.bin")
        __save_bin(temp_array, save_path)
        __save_pic(temp_array, save_pic)
        __save_other(temp_array, png_rgb_name, fill_bin, fill_bin_mean)
        logging.info("Save successfully!!")
        return

    @abstractmethod
    def process(self):
        """
        保存结果
        :return:
        """
        return
