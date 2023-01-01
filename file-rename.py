import os
path_name = r'./img/'  # 批量修改的文件夹路径
i = 414   # 起始数字
for item in os.listdir(path_name):
    original_name = os.path.join(path_name, item)
    new_name = os.path.join(path_name, (str(i)+'.png'))
    os.rename(original_name, new_name)  # 重命名
    i += 1
