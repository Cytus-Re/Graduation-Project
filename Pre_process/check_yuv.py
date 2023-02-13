# 该脚本用ffplay播放某一个文件夹下的所有yuv，通过肉眼观察看是否有问题
# 需要界面，不能终端播放
import os

ffplay_path = 'ffplay'
width, height = 1280, 720
yuv_folder = '/home/wyn/HEVC/Pre_process/Output'

for yuv_name in os.listdir(yuv_folder):
    yuv_path = f'{yuv_folder}/{yuv_name}'
    print(f'正在播放 {yuv_path}...')
    command = f'{ffplay_path} -f rawvideo -video_size {width}x{height} -pixel_format yuv420p -autoexit -framerate 60 {yuv_path}' # -autoexit表示播放结束自动退出,-framerate 60表示以60的fps进行播放,这样比较快
    os.system(command)
