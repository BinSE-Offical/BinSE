#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
Main entrance for call graph generation
"""
from settings import IDA_PATH, IDA64_PATH, IS_LINUX
import subprocess
from pathlib import Path
import shutil
import os
from tqdm import tqdm
from multiprocessing import Pool

def execute_cmd(cmd, timeout=900):
    """
    execute system command
    :param cmd:
    :param f:
    :param timeout:
    :return:
    """
    try:
        p = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                           timeout=timeout)

    except subprocess.TimeoutExpired as e:
        return {
            'errcode': 401,
            'errmsg': 'timeout'
        }
    return {
        'errcode': p.returncode,
        'errmsg': p.stdout.decode()
    }

def get_bin_info(bin_path):
    """
    :param bin_path:
    :return:  cmd = f"file -b {bin_path}"
    """
    # file only works on linux
    cmd = "file -b %s"%(bin_path)
    execute_res = execute_cmd(cmd)
    if execute_res['errcode'] == 0:
        bin_info = {
            'arch': '',
            'mode': '',
        }
        msg = execute_res['errmsg']
        if 'ARM' in msg:
            bin_info['arch'] = "ARM"
        elif 'PowerPC' in msg:
            bin_info['arch'] = "PPC"
        elif '386' in msg:
            bin_info['arch'] = "386"
        elif 'MIPS' in msg:
            bin_info['arch'] = 'MIPS'
        elif 'x86-64' in msg:
            bin_info['arch'] = "AMD64"
        if '64-bit' in msg:
            bin_info['mode'] = '64'
        elif '32-bit' in msg:
            bin_info['mode'] = '32'

        if bin_info['arch'] and bin_info['mode']:
            return {
                'errcode': 0,
                'bin_info': bin_info
            }
        else:
            return {
                'errcode': 402,
                'errmsg': "can not get bin_info:%s"%(bin_info)
            }
    return {
        'errcode': 401,
        'errmsg': "Command execute failed:%s"%(execute_res['errmsg'])
    }

def gen_cg_ie_table(input_list):
    bin_path = input_list[0]
    feat_path = input_list[1]

    bin_path = Path(bin_path)

    bin_info_res = get_bin_info(bin_path)
    if bin_info_res['errcode'] != 0:
        return bin_info_res
    mode = bin_info_res['bin_info']['mode']

    if os.path.exists(feat_path):
        print('Exists!!! %s'%(feat_path))
        return {
            'errcode': 1,
            'feat_path': str(feat_path)
        }
    if '32' in mode:
       cmd = f'{IDA_PATH} -L/log/FeatureExtraction.log -c -A -S"/FeatureExtraction/cg_ida.py {feat_path}" {bin_path}'

    elif '64' in mode:
       cmd = f'{IDA64_PATH} -L/log/FeatureExtraction.log -c -A -S"/FeatureExtraction/cg_ida.py {feat_path}" {bin_path}'

    else:
        raise ValueError('mode is not supported.')
    if IS_LINUX:
        cmd = f"TVHEADLESS=1 {cmd}"

    # print("cmd:" + cmd)
    exe_res = execute_cmd(cmd, timeout=1200)
    exe_res['feat_path'] = str(feat_path)
    return exe_res


def main():

    arguments_list = []

    bin_path = ""
    feat_path = ""
    arguments_list.append([bin_path, feat_path])








    p = Pool(12)
    with tqdm(total=len(arguments_list)) as pbar:
        for i, res in tqdm(enumerate(p.imap_unordered(gen_cg_ie_table, arguments_list))):
            pbar.update()
    p.close()
    p.join()

#
# def move_genFile():
#     bin_Folder = "/data1/xx_1/Dataset/Library/bin/openjpeg/"
#     des_Folder = "/data1/xx_1/binFeature/cg/openjpeg/"
#
#
#     bin_Folder = "/data1/xx_1/Dataset_Android/Dataset/x86_64/"
#     des_Folder = "/data1/xx_1/Dataset_Android/cg/"
#
#     if not os.path.exists(des_Folder):
#         os.mkdir(des_Folder)
#
#     Files = os.listdir(bin_Folder)
#
#
#     for file in Files:
#         if file.endswith("_cg_ie_str.json"):
#             sourceFile = "%s/%s"%(bin_Folder, file)
#             desFile = "%s/%s"%(des_Folder, file)
#             shutil.copyfile(sourceFile, desFile)
#
#         # src_bin_path = "%s/%s" % (bin_Folder, file)
#         # bin_path = Path(src_bin_path)
#         # # print(bin_path)
#         #
#         # exe_res = gen_cg_ie_table(bin_path=bin_path)
#         #
#         # if exe_res['errcode'] == 0:
#         #     print('Call graph successfully generated')

if __name__ == '__main__':
    main()

