### Huihong Lin, 20231027
### 从文件夹中读取eeg文件，批量计算psd

import os
import mne
import numpy as np

#指定eeg文件所在文件夹
eeg_folder = '/Volumes/H U I H U N G/InternationalComm/EEGprocessing/DataForBatch'

# 指定存储 EEG 文件的文件夹路径
save_event_path = '/Volumes/H U I H U N G/InternationalComm/EEGprocessing/psd/event'

#指定最小被试编号以避免重复计算
sub_range = 3

#set frequency
iter_freqs = [{'name':'Delta','fmin':0.5,'fmax':4},
              {'name': 'Theta', 'fmin': 4, 'fmax': 8},
              {'name': 'Alpha1', 'fmin': 8, 'fmax': 10.5},
              {'name': 'Alpha2', 'fmin': 10.5, 'fmax': 13},
              {'name': 'Alpha', 'fmin': 8, 'fmax': 13},
              {'name':'Beta','fmin': 13,'fmax':25},
              {'name':'Gamma1','fmin': 25,'fmax':40},
              {'name':'Gamma2','fmin': 40,'fmax':49},
              {'name': 'Gamma', 'fmin': 25, 'fmax': 49}]

# 获取文件夹中的所有文件
eeg_files = [file for file in os.listdir(eeg_folder) if file.endswith('.fif')]

# 遍历打开每个 EEG 文件
for eeg_file in eeg_files:
    eeg_file_path = os.path.join(eeg_folder, eeg_file)
    sub = os.path.splitext(eeg_file)[0]  # 提取文件名的前缀部分
    sub_num = eeg_file[:3]
    if int(sub_num) > sub_range - 1:
        raw = mne.io.read_raw_fif(eeg_file_path, preload=True)
        channel_name = raw.info['ch_names'][:-5]
        print(channel_name)

        # set for PSD
        stim_time = (raw.n_times - 1) / 1000  # set full time
        channel_num = 59
        freq_num = 7

        # calculate total psd
        psds_sum = 0
        for t in range(int(stim_time / 2)):
            spectrum = raw.compute_psd(fmin=0.5, fmax=49.0, tmin=2 * t, tmax=2 * (t + 1), n_jobs=None)
            psds, freqs = spectrum.get_data(return_freqs=True)  # psds?
            print(psds)
            psds_sum = psds + psds_sum
            print(psds_sum)

        mean_psds = psds_sum / int(stim_time / 2)  # ?

        # calculate event psd
        eventEnergy = np.zeros([channel_num, freq_num])
        for i in range(channel_num):
            for j in range(freq_num):
                iter_freq = iter_freqs[j]
                eventEnergy[i, j] = np.mean(mean_psds[i, (iter_freq['fmin'] < freqs) & (freqs < iter_freq['fmax'])])
        # save event psd
        np.save(os.path.join(save_event_path, sub + '_event_psd.npy'), eventEnergy)

print('DONE!!!')
