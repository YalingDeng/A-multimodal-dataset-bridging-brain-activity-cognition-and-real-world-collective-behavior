### Huihong Lin 231205 version 1.0
### 功能：（1）从添加肌电成分的的excel中读取伪迹，删除伪迹，（2）对视频进行分段

import mne
from mne.preprocessing import ICA
import os
import pandas as pd
import ast
import numpy as np
import matplotlib
matplotlib.use('TkAgg')

# 设置文件位置
path = '/Volumes/H U I H U N G/InternationalComm/Data/02处理中数据/rest/rest_filter'

# 设置伪迹excel储存位置
excel_path = '/Volumes/H U I H U N G/InternationalComm/Data/02处理中数据/rest/ica_artifacts_rest_240111.xlsx'

# 设置ica数据存储路径
save_ica_path = '/Volumes/H U I H U N G/InternationalComm/Data/02处理中数据/rest/rest_filter_ica'

# 设置分段数据存储路径
save_epoch_path = '/Volumes/H U I H U N G/InternationalComm/Data/02处理中数据/videos/videos_filter_ica_epoch'

#####################################
# 读取excel
df = pd.read_excel(excel_path)
artifacts_select = df.apply(
    lambda row: (row['sub'], ast.literal_eval(row['artifacts'])) if ast.literal_eval(row['artifacts']) and len(
        ast.literal_eval(row['artifacts'])) > 0 else None, axis=1)
# 去除空值
artifacts_select = list(filter(None, artifacts_select))

# 分离 sub 和 artifacts
subs, artifacts = zip(*artifacts_select)

for i in range(len(subs)):
    sub = str(subs[i]).zfill(3)
    print(sub)
    artifact = artifacts[i]

    raw = mne.io.read_raw_fif(os.path.join(path, sub + '_videos_filter.fif'),preload=True)

    #重参考（全脑平均）
    raw.set_channel_types({'ECG': 'ecg', 'HEOL': 'eog', 'HEOR': 'eog', 'VEOL': 'eog', 'VEOU': 'eog'})  # 标注眼电和心电的电极
    raw.set_eeg_reference(ref_channels='average')  # 没有把EOG, ECG算进去做平均

    # ICA
    mne.channels.get_builtin_montages(descriptions=True)
    montage = mne.channels.make_standard_montage('standard_1020')
    raw.set_montage(montage, on_missing='ignore')

    ica = ICA(n_components=40, random_state=0)
    ica.fit(raw.copy().filter(8, 35))
    #ica.plot_components(sphere=(0.0, 0.02, 0.03, 0.095))

    ica.exclude = artifact
    raw = ica.apply(raw.copy(), exclude=ica.exclude)

    # 储存ica后文件
    raw.save(os.path.join(save_ica_path,sub + '_videos_filter_ica.fif'),overwrite=True)

    # 分段
    # 读取evt
    event_path = '/Volumes/H U I H U N G/InternationalComm/Data/01原始数据/raw/' + sub + '/evt.bdf'
    fs = raw.info['sfreq']
    annotationData = mne.read_annotations(event_path)
    onset = annotationData.onset
    duration = annotationData.duration
    description = annotationData.description
    onset = np.array([i * fs for i in onset], dtype=np.int64)
    duration = np.array([int(i) for i in duration], dtype=np.int64)
    desc = np.array([int(i) for i in description], dtype=np.int64)
    events = np.vstack((onset, duration, desc)).T

    rest_event_n = 16
    video_time = [154, 156, 150, 129, 149, 155, 136, 111,
                  140, 142, 147, 149, 123, 134, 170, 120]  # 每段视频的时长

    video_list = []  # 这个被试看的视频顺序
    this_time_list = []  # 这个被试看的视频顺序对应的时间

    for i in range(rest_event_n, events.shape[0]):
        video_list.append(desc[i])
        this_time_list.append(video_time[int(desc[i]) - 1])

    # 保存看每段视频的数据
    for i in range(video_list.__len__()):
        raw.save(os.path.join(save_epoch_path, sub + '_' + str(video_list[i]) + '.fif'),
                 tmin=np.sum(this_time_list[0:i]), tmax=np.sum(this_time_list[0:i + 1]), overwrite=True)

print('DONE!!!')