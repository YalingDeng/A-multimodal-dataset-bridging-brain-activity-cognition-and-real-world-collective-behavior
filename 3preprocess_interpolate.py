### Huihong Lin 231205 version 1.0
### 功能：根据code2生成的坏导excel，（1）对有问题的数据进行批量插值，（2）单独储存未插值的数据，（3）用插值数据覆盖滤波后数据。

import os
import mne
import pandas as pd
import ast
import matplotlib
matplotlib.use('TkAgg')

# 设置滤波文件位置
path = '/Volumes/H U I H U N G/InternationalComm/Data/02处理中数据/rest/rest_filter'

#设置滤波前文件备份位置
backup_path = '/Volumes/H U I H U N G/InternationalComm/Data/02处理中数据/rest/rest_pre_interpolate'

# 设置excel位置
excel_path = '/Volumes/H U I H U N G/InternationalComm/Data/02处理中数据/rest/bad_channel_rest_2.xlsx'

#####################################
# 读取excel
df = pd.read_excel(excel_path)
bad_subs = df.apply(
    lambda row: (row['sub'], ast.literal_eval(row['bad_channel'])) if ast.literal_eval(row['bad_channel']) and len(
        ast.literal_eval(row['bad_channel'])) > 0 else None, axis=1)
# 去除空值
bad_subs = list(filter(None, bad_subs))
# 分离 sub 和 bad_channel
subs, bad_channels = zip(*bad_subs)

for i in range(len(subs)):
    sub = str(subs[i]).zfill(3)
    bad_channel = bad_channels[i]

    # 备份插值前文件
    raw = mne.io.read_raw_fif(os.path.join(path,sub + '_rest_filter.fif'),preload=True)
    raw.save(os.path.join(backup_path, sub + '_rest_pre_interpolate.fif'),overwrite=True)

    # 设置电极位置
    mne.channels.get_builtin_montages(descriptions=True)
    montage = mne.channels.make_standard_montage('standard_1020')
    raw.set_montage(montage, on_missing='ignore')
    raw.set_channel_types({'ECG': 'ecg', 'HEOL': 'eog', 'HEOR': 'eog', 'VEOL': 'eog', 'VEOU': 'eog'})  # 标注眼电和心电的电极

    # 插值坏导
    raw.info["bads"].extend(bad_channel)
    interp_data = raw.copy().interpolate_bads(reset_bads=True)

    # 储存插值后文件
    interp_data.save(os.path.join(path, sub + '_rest_filter.fif'),overwrite=True)
print('DONE!!!')
