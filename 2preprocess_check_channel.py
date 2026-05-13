### Huihong Lin 231205 version 1.0
### 功能：从滤波后的统一存储位置中读取数据，批量打开数据并绘制脑电信号图，手动检查并选择坏导，坏导将输出至excel中。

import os.path
import mne
import pandas as pd
import matplotlib.pyplot as plt

# 设置滤波文件位置
path = '/Volumes/H U I H U N G/InternationalComm/Data/02处理中数据/rest/rest_filter'

# 设置excel保存位置
excel_save_path = '/Volumes/H U I H U N G/InternationalComm/Data/02处理中数据/rest'

# 设置需要处理的被试编号范围
sub_min = 3 # 最小编号被试
sub_max = 4 # 最大编号被试
jump_data = [] # 跳过编号，如['001','002']

#####################################
sub_num = []
bad_channel = []

for i in range(sub_min, sub_max + 1):
    sub = str(i).zfill(3)
    if sub not in jump_data:
        data_path = path + '/' + sub + '_videos_filter.fif'
        raw = mne.io.read_raw_fif(data_path, preload=True)
        raw.plot(n_channels=59, duration=30, scalings={'eeg': 200e-6})
        plt.show()

        sub_num.append(str(i).zfill(3))
        bad_channel.append(raw.info['bads'])

data = {'sub': sub_num, 'bad_channel': bad_channel}
df = pd.DataFrame(data)
df.to_excel(os.path.join(excel_save_path, 'bad_channel_240112.xlsx'), index=False)
print('DONE!!!')