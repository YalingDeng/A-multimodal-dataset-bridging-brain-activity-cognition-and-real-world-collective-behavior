### author Huihong Lin
import numpy as np
import os
import pandas as pd

data_paths = '/Volumes/H U I H U N G/InternationalComm/Data/02处理中数据/rest/rest_event/power'

#创建channel
channel_name = ['Fpz', 'Fp1', 'Fp2', 'AF3', 'AF4', 'AF7', 'AF8', 'Fz', 'F1', 'F2',
                'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'FCz', 'FC1', 'FC2', 'FC3',
                'FC4', 'FC5', 'FC6', 'FT7', 'FT8', 'Cz', 'C1', 'C2', 'C3', 'C4',
                'C5', 'C6', 'T7', 'T8','CP1', 'CP2', 'CP3', 'CP4', 'CP5', 'CP6',
                'TP7', 'TP8', 'Pz', 'P3', 'P4', 'P5', 'P6', 'P7', 'P8','POz',
                'PO3', 'PO4', 'PO5', 'PO6', 'PO7', 'PO8', 'Oz', 'O1', 'O2']

#设置脑区对应电极点
fp_ch = ['Fpz','Fp1','Fp2', 'AF3', 'AF4', 'AF7', 'AF8', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8']
f_ch = ['Fz', 'FCz', 'FC1', 'FC2', 'FC3', 'FC4', 'FC5', 'FC6','Cz', ]
p_ch = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'CP1', 'CP2', 'CP3', 'CP4', 'CP5', 'CP6', 'Pz', 'P3', 'P4', 'P5', 'P6']
t_ch = ['FT7', 'FT8','T7', 'T8', 'TP7', 'TP8','P7', 'P8']
o_ch = ['POz', 'PO3', 'PO4', 'PO5', 'PO6', 'PO7', 'PO8', 'Oz', 'O1', 'O2']

# 创建一个列表，包含每个元素在 channel_name 中的索引
fp_num = [channel_name.index(channel) for channel in fp_ch]
f_num = [channel_name.index(channel) for channel in f_ch]
p_num = [channel_name.index(channel) for channel in p_ch]
t_num = [channel_name.index(channel) for channel in t_ch]
o_num = [channel_name.index(channel) for channel in o_ch]

#region of instrest
brain_area = [fp_num,f_num,p_num,t_num,o_num]

freq = 9
frequency_band_names = ['Delta', 'Theta', 'Alpha1', 'Alpha2','Alpha', 'Beta', 'Gamma1', 'Gamma2','Gamma']

# 读取文件夹中的 CSV 文件
csv_files_list = [file for file in os.listdir(data_paths) if file.endswith('.csv')]

band_psd = []
area_list = []
file_list = []

# 遍历打开每个 EEG 文件
for csv_file in csv_files_list:
    print(csv_file)
    csv_data = pd.read_csv(os.path.join(data_paths, csv_file))
    # 遍历每个脑区
    for i in brain_area:
        file_psd = []
        # 计算每个频率的平均 psd
        for j in range(int(freq)):
            psd_value = np.mean(csv_data.iloc[i, j + 2]) # 根据你的 CSV 文件格式调整列索引
            file_psd.append(psd_value)
            area_name = [channel_name[idx].split('_')[0] for idx in i]
        file_list.append(csv_file)
        area_list.append(area_name)
        band_psd.append(file_psd)

# 输出 excel
output_file_path = os.path.join('/Volumes/H U I H U N G/InternationalComm/Data/02处理中数据/rest/rest_event/power', 'rest_event_power.xlsx')
data = {'File Name': file_list, 'Area': area_list}
for i in range(int(freq)):
    data[frequency_band_names[i]] = [file_psd[i] for file_psd in band_psd]

df = pd.DataFrame(data)
df.to_excel(output_file_path, index=False)

print("PSD file saved.")