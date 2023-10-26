# -*- coding: utf-8 -*-
# @Time    : 2023/10/21 20:34
# @Author  : qxcnwu
# @FileName: AfterProcess.py
# @Software: PyCharm
import os
import struct
import threading
from io import BytesIO
from typing import List

import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from tqdm import tqdm


def make_9_seg():
    """
    压缩9段线
    :return:
    """
    img = np.array(Image.open("extend/9seg.png"))
    x, y, c = img.shape
    img[:, 0, :] = [0, 0, 0, 255]
    img[:, y - 1, :] = [0, 0, 0, 255]
    img[0, :, :] = [0, 0, 0, 255]
    img[x - 1, :, :] = [0, 0, 0, 255]
    Image.fromarray(img.astype(np.uint8)).save("extend/test.png")
    # Image.open("extend/9seg.png").resize((int(68 * 1.5), int(84 * 1.5))).save("extend/resize_9_seg.png")
    return


def read_bin(bin_path: str) -> np.array:
    """
    读取bin文件
    :param bin_path:
    :return:
    """
    f = open(bin_path, 'rb')
    data = []
    for _ in tqdm(range(631 * 361)):
        data.append(struct.unpack(">d", f.read(8))[0])
    data = np.array(data)
    data = data.reshape((361, 631))
    return data


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
    position = fig.add_axes([0.15, 0.15, 0.7, 0.03])  # 位置[左,下,右,上]
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


def make_file_name(path: str, name: str):
    """
    创建对应的名称
    :param path:
    :param name:
    :return:
    """
    # 依次返回没有插值的图像，彩色图像，插值后的图像，插值后的彩色图像，bin文件，平均文件
    name = name.replace(".png", "")
    return [os.path.join(path, name + ".png"), os.path.join(path, name + "_rgb.png"),
            os.path.join(path, name + "_fill.png"), os.path.join(path, name + "_fill_rgb.png"),
            os.path.join(path, name + "_fill.bin"), os.path.join(path, name + "_fill_mean.bin")]


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


def resize():
    def pic_compress(pic_path, out_path, target_size=100, quality=1000, step=5, pic_type='.jpg'):
        # 读取图片bytes
        with open(pic_path, 'rb') as f:
            pic_byte = f.read()
        img_np = np.frombuffer(pic_byte, np.uint8)
        img_cv = cv2.imdecode(img_np, cv2.IMREAD_ANYCOLOR)
        current_size = len(pic_byte) / 1024
        print("图片压缩前的大小为(KB)：", current_size)
        while current_size > target_size:
            pic_byte = cv2.imencode(pic_type, img_cv, [int(cv2.IMWRITE_JPEG_QUALITY), quality])[1]
            if quality - step < 0:
                break
            quality -= step
            current_size = len(pic_byte) / 1024
        # 保存图片
        with open(out_path, 'wb') as f:
            f.write(BytesIO(pic_byte).getvalue())
        return len(pic_byte) / 1024

    pic_compress("../temp/2.png", "../temp/cv.png")
    return


def main(bin_path: str, base_dir: str, name: str, mask_array: np.array, line_array: np.array):
    """

    :param bin_path:
    :param base_dir:
    :param name:
    :param mask_array:
    :param line_array:
    :return:
    """

    # 获取名称
    png_name, png_rgb_name, fill_name, fill_rgb_name, fill_bin, fill_bin_mean = make_file_name(base_dir, name)
    # 读取bin文件
    data = read_bin(bin_path)
    # 转换为彩色
    convert_to_rgb(data, mask_array=mask_array, line_data=line_array, save_path=png_rgb_name)
    # 保存新的bin文件
    make_fill_bin(fill_bin, data)
    # 保存求和文件
    make_fill_sum_bin(fill_bin_mean, data)
    return


def change_all_file(base_dir: str, save_dir: str, bin_name: List[str], mask_array: np.array, line_array: np.array):
    """
    更改所有的对象
    :return:
    """
    for file in tqdm(bin_name):
        bin_path = os.path.join(base_dir, file)
        name = file.replace("bin", "png")
        main(bin_path, save_dir, name, mask_array, line_array)
    return


def Main(base_dir: str, save_dir: str, number: int):
    files = os.listdir(base_dir)
    bin = []
    for file in files:
        if file.endswith("bin"):
            bin.append(files)

    # 特定值
    mask_array = get_mask_array()
    line_array = get_line_data()

    sum = len(bin)
    pre_num = sum // number
    thread = []
    for i in range(number):
        thread.append(threading.Thread(target=change_all_file, args=(
            base_dir, save_dir, bin[i * pre_num: min(len(bin), (i + 1) * pre_num)], mask_array, line_array)))
        thread[-1].setDaemon(True)
    for th in thread:
        th.start()
    for th in thread:
        th.join()
    return


if __name__ == '__main__':
    # 原始文件
    base_dir = ""
    save_dir = ""
    # 特定值
    # Main(base_dir, save_dir, 8)

    resize()
