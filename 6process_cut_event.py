### 完成数据预处理后，拆分每个event
### Ye Wang, 20231023
### Huihong Lin, 20231027
###每个eeg数据需要读取evt，通过表格实现

import numpy as np
import mne
import os
import matplotlib
matplotlib.use('TkAgg')

#指定eeg文件所在文件夹
eeg_folder = '/Volumes/H U I H U N G/InternationalComm/EEGprocessing/videos'

#统一存储路径
save_path = '/Volumes/H U I H U N G/InternationalComm/EEGprocessing/DataForBatch'

#指定最小被试编号
sub_range = 3
######

# 获取文件夹中的所有文件
eeg_files = [file for file in os.listdir(eeg_folder) if file.endswith('.fif')]

# 遍历打开每个 EEG 文件
for eeg_file in eeg_files:
    eeg_file_path = os.path.join(eeg_folder, eeg_file)
    sub = eeg_file[:3]
    if int(sub) > sub_range-1:
        raw = mne.io.read_raw_fif(eeg_file_path, preload=True)

        ### read events
        event_path = '/Volumes/H U I H U N G/InternationalComm/raw/' + sub + '/evt.bdf'
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
            raw.save(os.path.join(save_path, sub + '_' + str(video_list[i]) + '.fif'),
                     tmin=np.sum(this_time_list[0:i]), tmax=np.sum(this_time_list[0:i + 1]), overwrite=True)
        print('DONE!!!')
