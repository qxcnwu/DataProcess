# -*- coding: utf-8 -*-
# @Time    : 2023/10/15 21:40
# @Author  : qxcnwu
# @FileName: testDownload.py
# @Software: PyCharm
# -*- coding=utf-8
import logging
import os
import sys

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
from tqdm import tqdm


def get_all():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    secret_id = 'AKIDT0Y2Rr9FGOUh6XZosoaKydIoiPwGWijZ'
    secret_key = 'ESXXSVakw6FJftz01udJyY4kMzU3ShHr'
    region = 'ap-beijing'
    token = None
    scheme = 'https'
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
    client = CosS3Client(config)
    ans = []
    marker = ""
    while True:
        response = client.list_objects(
            Bucket='water-1256388644',
            Marker=marker
        )
        if 'Contents' in response:
            ans.extend([q['Key'] for q in response['Contents']])
        if response['IsTruncated'] == 'false':
            break
        marker = response['NextMarker']
    marker = ""
    while True:
        response = client.list_objects(
            Bucket='aod-1256388644',
            Marker=marker
        )
        if 'Contents' in response:
            ans.extend([q['Key'] for q in response['Contents']])
        if response['IsTruncated'] == 'false':
            break
        marker = response['NextMarker']
    return ans


def upload():
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    secret_id = 'AKIDT0Y2Rr9FGOUh6XZosoaKydIoiPwGWijZ'
    secret_key = 'ESXXSVakw6FJftz01udJyY4kMzU3ShHr'
    region = 'ap-beijing'
    token = None
    scheme = 'https'
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
    client = CosS3Client(config)
    ans = get_all()
    for file in tqdm(os.listdir(path)):
        if '_rgb' in file and file.replace('_rgb', '') not in ans:
            if 'water' in file:
                with open(os.path.join(path, file), 'rb') as fp:
                    response = client.put_object(
                        Bucket='water-1256388644',
                        Body=fp,
                        Key=file.replace('_rgb', ''),
                        StorageClass='STANDARD',
                        EnableMD5=False
                    )
                fp.close()
            else:
                with open(os.path.join(path, file), 'rb') as fp:
                    response = client.put_object(
                        Bucket='aod-1256388644',
                        Body=fp,
                        Key=file.replace('_rgb', ''),
                        StorageClass='STANDARD',
                        EnableMD5=False
                    )
                fp.close()
    return


def upload_one(path: str, file: str):
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    secret_id = 'AKIDT0Y2Rr9FGOUh6XZosoaKydIoiPwGWijZ'
    secret_key = 'ESXXSVakw6FJftz01udJyY4kMzU3ShHr'
    region = 'ap-beijing'
    token = None
    scheme = 'https'
    config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key, Token=token, Scheme=scheme)
    client = CosS3Client(config)
    with open(path, 'rb') as fp:
        client.put_object(
            Bucket='water-1256388644',
            Body=fp,
            Key=file.replace('_rgb', ''),
            StorageClass='STANDARD',
            EnableMD5=False
        )
    fp.close()
    return


if __name__ == '__main__':
    path = ""
