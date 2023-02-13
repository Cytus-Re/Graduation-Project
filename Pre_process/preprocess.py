import os
import time
import numpy as np
import path

# frame_count = 500\
input_dir = '/home/wyn/HEVC/Pre_process/Input/'
# input_file = '/home/wyn/HEVC/Data/in_to_tree_420_720p50_500.yuv'
output_dir = '/home/wyn/HEVC/Pre_process/Output/'
# input_dir, name = os.path.split(input_file)
# frame_count = int(os.path.splitext(name)[0].split('_')[-1]) # 取出帧总数
width = 1280
height = 720


def parse(file_name):
    """从yuv文件名中解析参数
    参数:
        file_name - yuv文件名
    返回:
        视频名称, 分辨率, fps, 该文件总帧数
    """
    # input_dir, name = os.path.split(file)
    name = os.path.splitext(file_name)[0]
    contents = name.split('_')
    print(contents)
    video_name = contents[0]
    res = contents[1]
    fps = int(contents[2])
    frame_count = int(contents[-1]) # 取出帧总数
    return video_name, res, fps, frame_count

def dir_split(input_dir, output_dir):
    """遍历文件夹，对每一个yuv文件调用gen_cmd()
    参数:
        input_dir - 输入目录
        output_dir - 输出目录
    返回:
        空
    """
    files = os.listdir(input_dir)
    # 不可直接排序！！python默认遍历文件夹不是按名称大小

    for file in files:
        if not file.endswith('.yuv'):
            continue
        video_name, res, fps, frame_count = parse(file)
        path = os.path.join(input_dir, file)
        gen_split_cmd(res, path, output_dir, frame_count)
        # print("正在分割：" + file)
        # print("视频：" + video_name + " 分辨率：" + res + " fps：" + str(fps) + " 总帧数：" + str(frame_count))


def gen_split_cmd(res, input_file, output_dir, frame_count):
    """生成并执行ffmpeg命令  
    参数:
        res - 分辨率
        input_file - yuv文件的【全】路径
        output_dir - 输出目录
        frame_count - yuv文件的总帧数
    返回:
        空
    """
    # 注意空格
    cmd_prefix = 'ffmpeg '
    res = '-s ' + res + ' '
    input = '-i ' + input_file + ' '
    # 提取不包含后缀的文件名
    _, name = os.path.split(input_file)
    name = os.path.splitext(name)[0]
    # 30帧一段
    cnt = int(frame_count / 30)
    # range前闭后开！！
    for i in range(0, cnt):
        begin = i * 30
        end = 29 + i * 30
        para = '-c:v rawvideo -filter:v select=' + '"between(n\, {0}\, {1})"'.format(begin, end) + ' '
        output = output_dir + name + '_' + str(i + 1).zfill(2) + '.yuv' # 从1开始，且两位数显示
        cmd = cmd_prefix + res + input + para + output
        os.system(cmd)
        time.sleep(0.3) # 避免太频繁
        # print(cmd)

# def concate():
#     return 


def merge_yuv_sequence(yuv_files, output_file, width, height):
    frame_size = int(width * height * 3 / 2) # yuv420p下一个像素使用1.5个字节
    with open(output_file, 'wb') as output_yuv:
        for yuv_file in yuv_files:
            print(f'正在合并{yuv_files}')
            with open(yuv_file, 'rb') as input_yuv:
                    # buf = input_yuv.read(frame_size * 30)
                while True:
                    frame = input_yuv.read(frame_size)
                    if not frame:
                        break
                    output_yuv.write(frame)



if __name__=='__main__':
    
   dir_split(input_dir, output_dir)