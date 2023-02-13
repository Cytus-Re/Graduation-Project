from PIL import Image
import numpy as np
import os
import math

# 注意！！！此处定义是列 * 行(w * h)，和后面不一致
SIZE_2Nx2N           = 0,           # < symmetric motion partition,  2Nx2N
SIZE_2NxN            = 1,           # < symmetric motion partition,  2Nx N
SIZE_Nx2N            = 2,           # < symmetric motion partition,   Nx2N
SIZE_NxN             = 3,           # < symmetric motion partition,   Nx N
SIZE_2NxnU           = 4,           # < asymmetric motion partition, 2Nx( N/2) + 2Nx(3N/2)
SIZE_2NxnD           = 5,           # < asymmetric motion partition, 2Nx(3N/2) + 2Nx( N/2)
SIZE_nLx2N           = 6,           # < asymmetric motion partition, ( N/2)x2N + (3N/2)x2N
SIZE_nRx2N           = 7,           # < asymmetric motion partition, (3N/2)x2N + ( N/2)x2N
NUMBER_OF_PART_SIZES = 8

# 每一帧的长宽
# Width, Height = 176, 144
# Width, Height = 1280, 720
CTUSize = 64  
Length = 16 # 4*4存储


def save_png(Y, name):
    Y = Y.astype(float)
    max = float(np.max(Y))
    Y = Y / max * 255
    Y = Y.astype(np.uint8)
    # L:灰度图,彩色图为‘RGB’
    Image.fromarray(Y, mode='L').save('./Output/' + name + '.png')


# def load_data(path):
#     data = np.loadtxt(path, dtype = int)
#     # with open(path) as file:
#     #     data = file.read()
#     return data

# python切片前闭后开
def convert(stream, Width, Height):
    """一帧CU or PU信息的映射图 
    参数:
        stream - 编码器提取CU or PU流，16列矩阵
        Width - 帧宽度
        Height - 帧长度
    返回:
        CU or PU Map(原图分辨率1/16)
    """
    NumCTU_Col = math.ceil(Width / CTUSize);     # 列有多少CTU，不满64的也算一个
    NumCTU_Row = math.ceil(Height / CTUSize);     # 行有多少CTU，不满64的也算一个

    # 读数据, 将CTU放在正确位置，存入四维矩阵CTU
    h, w = stream.shape
    CTU = np.ones((NumCTU_Row, NumCTU_Col, 16, 16), dtype = 'int')
    zipped = zip(range(0, h, 16), range(0, NumCTU_Col * NumCTU_Row, 1))
    for cnt, idx in zipped:
        i = int(idx / NumCTU_Col) # 第i行
        j = int(idx % NumCTU_Col) # 第j列
        # print((i, j, idx, NumCTU_Col, NumCTU_Row))
        CTU[(i, j)] = stream[cnt : cnt + 16]
    # print("begin")
    # print(CTU[(17, 0)])
    # print(CTU[(18, 0)])
    # print("end")
    # print(CTU)

    # 按顺序拼成一张图，存入Map
    Map = np.ones((NumCTU_Row * 16, NumCTU_Col * 16), dtype = 'int')
    zipped = zip(range(0, NumCTU_Col), range(0, NumCTU_Row))
    for i in range(0, NumCTU_Row):
        for j in range(0, NumCTU_Col):
            # print((i, j, i * 16, i * 16 + 16, j * 16, j * 16 + 16))
            Map[i * 16 : i * 16 + 16, j * 16 : j * 16 + 16] = CTU[(i, j)]
    # np.set_printoptions(threshold=np.inf)
    # print(Map[0:16, 16:32])

    # # 裁剪超出图片边缘的部分
    # Map = Map[0 : int(Height / 4), 0 : int(Width / 4)]
    return Map


def get_partition(CU_Depth):
    """一帧的CU划分图  
    参数:
        CU_Map - convert后的CU_depth分布图
    返回:
        CU划分图, 分辨率不变, 其中'1'代表此处为边界
    """

def get_PU_Map(CU_Depth, PU_partition, Width, Height):
    """一帧的PU Map  
    参数:
        CU_Depth - convert后的CU_depth分布图
        PU_partition - convert后的PU划分图
    返回:
        PU Map
    """
    NULL = -999
    square_set = [255, 127, 63, 32, 0]
    rectangular_set = [224, 186, 164, 96, 72, 48, 40, 12]
    N_ = np.array([32, 16, 8, 4])
    N = N_ / 4 # 由于4*4为一个单位, 全部除以4
    N = N.astype(int)
    h, w = CU_Depth.shape
    rst = np.zeros((h, w), dtype = 'int')
    rst.fill(NULL)
    for i in range(h): # i是行
        for j in range(w): # j是列
            if rst[i, j] == NULL: # 仅针对还未填写值的部分
                depth = CU_Depth[i, j] # depth = 0, 1, 2, 3
                cur_N = N[depth] # N = 8, 4, 2, 1
                if PU_partition[i ,j] == SIZE_2Nx2N:
                    rst[i : i + cur_N * 2, j : j + cur_N * 2] = square_set[depth]
                elif PU_partition[i ,j] == SIZE_NxN:
                    rst[i : i + cur_N, j : j + cur_N] = square_set[depth + 1]
                elif PU_partition[i ,j] == SIZE_Nx2N: # 左右均分
                    rst[i : i + cur_N * 2, j : j + cur_N] = rectangular_set[2 * depth  + 1] # 左边长方形
                    rst[i : i + cur_N * 2, j + cur_N : j + cur_N * 2] = rectangular_set[2 * depth] # 右边长方形
                elif PU_partition[i ,j] == SIZE_2NxN:  # 上下均分
                    rst[i : i + cur_N, j : j + cur_N * 2] = rectangular_set[2 * depth + 1] # 上方长方形
                    rst[i + cur_N : i + cur_N * 2, j : j + cur_N *2] = rectangular_set[2 * depth] # 下方长方形
                elif PU_partition[i, j] == SIZE_2NxnU:  # 2Nx(N/2) + 2Nx(3N/2) 上窄下宽
                    # 上方小长方形i : i + N/2, 高N/2
                    rst[i : i + int(cur_N / 2), j : j + cur_N * 2] = rectangular_set[2 * depth + 1]
                    # 下方大长方形i + N/2: i + N/2 + 3*N/2, 高3N/2
                    rst[i + int(cur_N / 2) : i + int(cur_N / 2) * 4, j : j + cur_N * 2] = rectangular_set[2 * depth]
                elif PU_partition[i, j] == SIZE_2NxnD:  # 2Nx(3N/2) + 2Nx( N/2) 上宽下窄
                    # 上方大长方形 i : i + 3*N/2, 高3N/2
                    rst[i : i + int(cur_N / 2) * 3, j : j + cur_N * 2] = rectangular_set[2 * depth + 1]
                    # 下方小长方形 i + 3*N/2: i + 3*N/2 + N/2, 高N/2
                    rst[i + int(cur_N / 2) * 3 : i + int(cur_N / 2) * 4, j : j + cur_N * 2] = rectangular_set[2 * depth]
                elif PU_partition[i, j] == SIZE_nLx2N: # ( N/2)x2N + (3N/2)x2N 左窄右宽
                    # print(("左窄的值:",rectangular_set[2 * depth + 1], "宽度:", int(cur_N / 2)))
                    # 左边小长方形 j : j + N/2, 宽N/2
                    rst[i : i + cur_N * 2, j : j + int(cur_N / 2)] = rectangular_set[2 * depth + 1]
                    # 右边大长方形 j + N/2 : j + N/2 + 3*N/2, 宽3N/2
                    rst[i : i + cur_N * 2, j + int(cur_N / 2): j + int(cur_N / 2) * 4] = rectangular_set[2 * depth] 
                elif PU_partition[i, j] == SIZE_nRx2N: # (3N/2)x2N + ( N/2)x2N 左宽右窄
                    # 左边大长方形 j : j + 3*N/2, 宽3N/2
                    rst[i : i + cur_N * 2, j : j + int(cur_N / 2) * 3] = rectangular_set[2 * depth + 1]
                    # 右边小长方形 j + 3*N/2 : j + 3*N/2 + N/2, 宽N/2
                    rst[i : i + cur_N * 2, j + int(cur_N / 2) * 3 : j + int(cur_N / 2) * 4] = rectangular_set[2 * depth] 
                else:
                    continue
    # 裁剪超出图片边缘的部分
    rst = rst[0 : int(Height / 4), 0 : int(Width / 4)]     
    return rst
		

# if __name__=='__main__':
#     # os.path.dirname("文件名")
#     # pu = "./Input/720ppu(0).txt" 
#     # cu = "./Input/720pcu(0).txt"
#     # pu = "./Input/PU_test.txt"
#     # cu = "./Input/cU_test.txt"
#     pu = "./Input/DecoPU720pHM(0).txt"
#     cu = "./Input/DecoCU720pHM(0).txt"
#     data_pu = load_data(pu)
#     data_cu = load_data(cu)
#     CMap = convert(data_cu, Width, Height)
#     PMap = convert(data_pu, Width, Height)
#     save_png(PMap, 'PMap720p')
#     PU_Map = get_PU_Map(CMap, PMap)
#     np.set_printoptions(threshold=np.inf)
#     # print(PU_Map)
#     save_png(PU_Map, 'PU_Map(deco)')
#     # print(PU_Map)    