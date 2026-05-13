### Huihong Lin 231205 version 1.0
### 功能：从统一文件中读取原始数据，执行（1）滤波（0.5-49 Hz），（2）切分静息数据和视频数据，（3）将处理后数据储存到统一位置。

import numpy as np
import mne
import os
import matplotlib
matplotlib.use('TkAgg')

# 设置原始文件路径
path = '/Volumes/H U I H U N G/InternationalComm/Data/01原始数据/静息态数据'

# 设置统一储存位置
save_rest_path = '/Volumes/H U I H U N G/InternationalComm/Data/02处理中数据/预处理脑电数据/rest/rest_filter'
save_videos_path = '/Volumes/H U I H U N G/InternationalComm/Data/02处理中数据/预处理脑电数据/videos/videos_filter'

# 设置需要处理的被试编号范围
sub_min = 3 # 最小编号被试
sub_max = 71 # 最大编号被试
jump_data = ['009','019','027','031'] # 跳过编号，如['001','002']

##################################
for i in range(sub_min,sub_max+1):
    sub = str(i).zfill(3)
    if sub not in jump_data:
        data_path = path + '/' + sub + '/data.bdf'
        event_path = path + '/' + sub + '/evt.bdf'

        raw = mne.io.read_raw_bdf(data_path, preload=True)
        raw.apply_function(lambda x: x * 1e-6, picks="eeg")

        # 滤波
        raw.filter(l_freq=0.5, h_freq=49)

        # 读取events
        fs = raw.info['sfreq']
        annotationData = mne.read_annotations(event_path)
        onset = annotationData.onset
        duration = annotationData.duration
        description = annotationData.description
        onset = np.array([i * fs for i in onset], dtype=np.int64)
        duration = np.array([int(i) for i in duration], dtype=np.int64)
        desc = np.array([int(i) for i in description], dtype=np.int64)
        events = np.vstack((onset, duration, desc)).T

        # 设置时长
        video_time = [154, 156, 150, 129, 149, 155, 136, 111,
                      140, 142, 147, 149, 123, 134, 170, 120]

        rest_event_n = 16
        rest_event_time = 15

        #储存静息数据
        raw.save(os.path.join(save_rest_path, sub + '_rest_filter.fif'), tmin=onset[0] / 1000,
                 tmax=onset[0] / 1000 + rest_event_n * rest_event_time, overwrite=True)
        #储存视频数据
        video_duration_1 = video_time[events[rest_event_n, 2] - 1]
        video = raw.copy().crop(tmin=onset[rest_event_n] / 1000, tmax=onset[rest_event_n] / 1000 + video_duration_1)
        for j in range(rest_event_n + 1, events.shape[0]):
            video_duration = video_time[events[j, 2] - 1]
            video.append(raw.copy().crop(tmin=onset[j] / 1000, tmax=onset[j] / 1000 + video_duration))
        video.save(os.path.join(save_videos_path, sub + '_videos_filter.fif'), overwrite=True)
print('DONE!!!')