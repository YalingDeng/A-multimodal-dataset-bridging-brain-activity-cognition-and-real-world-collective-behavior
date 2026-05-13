### Huihong Lin 231205 version 1.0
### 功能：（1）对脑电文件进行重参考（全脑平均），（2）运行ICA算法，（3），用ICALABLE计算伪迹成分和可能性，输出ic图片为png。（4）将自动识别的伪迹储存为excel方便添加新成分
### ！！！注意！这份代码没有储存自动去除伪迹的数据！！！

import mne
from mne.preprocessing import ICA
import os
import pandas as pd
from mne_icalabel import label_components
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')

# 设置文件位置
path = '/Volumes/H U I H U N G/InternationalComm/Data/02处理中数据/rest/rest_filter'

# 设置独立成分png储存位置
save_png_path = '/Volumes/H U I H U N G/InternationalComm/Data/02处理中数据/rest/rest_ica_fig'

# 设置伪迹excel储存位置
excel_path = '/Volumes/H U I H U N G/InternationalComm/Data/02处理中数据/rest/ica_artifacts_rest_2.xlsx'

# 设置需要处理的被试编号范围
sub_min = 3 # 最小编号被试
sub_max = 71 # 最大编号被试
jump_data = ['009','019','027','031'] # 跳过编号，如['001','002']

#####################################
sub_num = []
artifacts_num = []

for i in range(sub_min, sub_max + 1):
    sub = str(i).zfill(3)
    if sub not in jump_data:
        raw = mne.io.read_raw_fif(os.path.join(path, sub + '_rest_filter.fif'),preload=True)

        # 重参考（全脑平均）
        raw.set_channel_types({'ECG': 'ecg', 'HEOL': 'eog', 'HEOR': 'eog', 'VEOL': 'eog', 'VEOU': 'eog'})  # 标注眼电和心电的电极
        raw.set_eeg_reference(ref_channels='average')  # 没有把EOG, ECG算进去做平均

        # ICA
        mne.channels.get_builtin_montages(descriptions=True)
        montage = mne.channels.make_standard_montage('standard_1020')
        raw.set_montage(montage, on_missing='ignore')

        ica = ICA(n_components=40, random_state=0)
        ica.fit(raw.copy().filter(8, 35))
        #ica.plot_components(sphere=(0.0, 0.02, 0.03, 0.095))
        bad_idx, scores = ica.find_bads_eog(raw)
        print(bad_idx)

        # 把被试和伪迹储存至列表
        sub_num.append(sub)
        artifacts_num.append(bad_idx)

        # icalable
        component_dict = label_components(raw, ica, method='iclabel')
        # icalabel画图
        fig, axes = plt.subplots(5, 8, figsize=(15, 10))
        for j, ax in enumerate(axes.flat):
            if j < len(component_dict['labels']):
                # 生成单个成分图像
                ica.plot_components(picks=j, axes=ax, show=False)
                # 添加标识和概率值
                label_text = f'{component_dict["labels"][j]}: {component_dict["y_pred_proba"][j]:.2%}'
                ax.text(0, -0.15, label_text, ha='center', va='center', fontsize=10)  # 调整文本位置
                ax.axis('off')  # 关闭图像坐标轴
            else:
                ax.axis('off')  # 关闭多余的子图

        # 调整图的外观
        plt.subplots_adjust(wspace=0.3, hspace=0.6)  # 调整行和列的间距
        #plt.show()
        plt.savefig(os.path.join(save_png_path, f"{sub}_{str(bad_idx)}.png"))
data = {'sub':sub_num, 'artifacts':artifacts_num}
df = pd.DataFrame(data)
df.to_excel(excel_path,index=False)
print('DONE!!!')