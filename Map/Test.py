import GenerateMap
import os
from PIL import Image
import numpy as np
from pathlib import Path
import time


os.chdir("/home/wyn/HEVC/Map") #进入指定的目录
start =time.perf_counter()
input_prefix = "./Input/"
output_prefix = "./Output"
Width = 1920 
Height = 1080
# Width = 176 
# Height = 144


def mkdir(path): 
    folder = os.path.exists(path) 
    if not folder:                   # 判断是否存在文件夹如果不存在则创建为文件夹
        os.makedirs(path)            # makedirs 创建文件时如果路径不存在会创建这个路径
        print ("成功创建目录")
    else:
        print ("目录存在")
        # os.removedirs(path)


def load_data(path):
    data = np.loadtxt(path, dtype = int)
    # with open(path) as file:
    #     data = file.read()
    return data

def process_single_frame(cu_path, pu_path, Width, Height):
    data_pu = load_data(pu_path)
    data_cu = load_data(cu_path)
    CMap = GenerateMap.convert(data_cu, Width, Height)
    PMap = GenerateMap.convert(data_pu, Width, Height)
    PU_Map = GenerateMap.get_PU_Map(CMap, PMap, Width, Height)
    return CMap, PMap, PU_Map
    

def traverse_dir(cu_dir, pu_dir, target_dir):
    cu_files = os.listdir(cu_dir)
    pu_files = os.listdir(pu_dir)
    # 不可直接排序！！python默认遍历文件夹不是按名称大小
    # idx = 0 
    for cu_file, pu_file in zip(cu_files, pu_files):
        cu_path = os.path.join(cu_dir, cu_file)
        pu_path = os.path.join(pu_dir, pu_file)
        _, _, PU_Map = process_single_frame(cu_path, pu_path, Width, Height)
        save_png(PU_Map, os.path.join(target_dir, str(Path(cu_path).stem))) # 用遍历到的cu,pu文件名来命名
        # print(Path(cu_path).stem)
        # idx += 1


def save_png(Y, name):
    Y = Y.astype(float)
    max = float(np.max(Y))
    Y = Y / max * 255
    Y = Y.astype(np.uint8)
    # L:灰度图,彩色图为‘RGB’
    Image.fromarray(Y, mode='L').save(name + '.png')

if __name__=='__main__':

    PUfolder = "PUamp/"
    CUfolder = "CUamp/"
    # PUfolder = "PUQcif/"
    # CUfolder = "CUQcif/"
    outfolder = "1080p_amp"
    mkdir(os.path.join(output_prefix, outfolder))
    traverse_dir(os.path.join(input_prefix, CUfolder), os.path.join(input_prefix, PUfolder), os.path.join(output_prefix, outfolder))

end= time.perf_counter()
print('运行时间: %s Seconds'%(end-start))