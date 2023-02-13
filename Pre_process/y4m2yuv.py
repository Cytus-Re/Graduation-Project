import os

width, height = 352, 288
ffmpeg_path = 'ffmpeg'
y4m_folder = './dataset/352x288_y4m'
yuv_folder = './dataset/352x288_yuv'

if not os.path.exists(y4m_folder):
    print(f'{y4m_folder} 文件夹不存在!')
    exit()

if not os.path.exists(yuv_folder):
    print(f'{y4m_folder} 文件夹不存在!')
    exit()

for y4m_name in os.listdir(y4m_folder):
    if not y4m_name.endswith('.y4m'):
        continue
    video_name = y4m_name[:y4m_name.find('.y4m')]
    # print(video_name)
    command = f'{ffmpeg_path} -i {y4m_folder}/{y4m_name} -pix_fmt yuv420p {yuv_folder}/{video_name}.yuv'
    os.system(command)
