# -*- coding: utf-8 -*-
"""
该代码用于生成发病前1天的数据集
"""

import pickle
import numpy as np


# == demo
def get_demo(input_data):
    Demo = np.array(input_data)
    # 将 demo类中数据对应到整个矩阵对应的位置 ，注意:【位置需要查映射表获取】
    for m in range(len(Demo)):
        demo_index = "demo"
        if m == 0:
            demo_index = demo_index + str(1)
        else:
            demo_index = demo_index + str(m + 1) + str(Demo[m])
            Demo[m] = 1

        indexNum = list(map_data).index(demo_index)
        valueAll[0, indexNum] = Demo[m]


# == vital
def get_vital(input_data, input_t_time):
    for m in range(len(input_data)):
        try:
            temp = input_data[m]
            temp1 = np.asarray(temp)
            temp2 = temp1[:, -1]
            temp3 = [x for x in temp2 if x <= input_t_time]
            temp4 = np.max(temp3)
            temp5 = list(temp2).index(temp4)

            if m == 3 or m == 4 or m == 5:
                # vital4,vital5,vital6为定性变量
                vitalIndex = 'vital' + str((m + 1) * 10) + str(int(temp[temp5][0]))
                indexNum = list(map_data).index(vitalIndex)  # 获取特征值对应下标索引
                valueAll[0, indexNum] = 1
                continue
            else:
                # 判断特征值在映射表中的位置。
                vitalIndex = 'vital' + str(m + 1)
                indexNum = list(map_data).index(vitalIndex)  # 获取特征值对应下标索引
                valueAll[0, indexNum] = temp[temp5][0]
        except:
            continue


# == lab
def get_lab_med(input_data, input_t_time):
    # value = np.zeros([1, len(input_data)], dtype=np.int)  # lab is 817
    for m in range(len(input_data)):
        try:
            labIndex = input_data[m][0][0][0]
            # 通过labIndex找到映射表中对应的位置
            indexNum = list(map_data).index(labIndex)  # 获取特征值对应下标索引
            temp = input_data[m][1]
            temp1 = np.asarray(temp)
            temp2 = temp1[:, -1]
            temp3 = [int(x) for x in temp2 if int(x) <= input_t_time]
            temp4 = np.max(temp3)
            temp5 = list(temp2).index(str(temp4))
            valueAll[0, indexNum] = temp[temp5][0]
        except:
            continue
    pass


# ==ccs
def get_ccs_px(input_data, input_t_time):
    for m in range(len(input_data)):
        try:
            ccsTime = int(input_data[m][1][-1])
            if ccsTime <= input_t_time:
                # 根据ccsIndex 确定映射位置
                ccsIndex = input_data[m][0][0]
                indexNum = list(map_data).index(ccsIndex)  # 获取特征值对应下标索引
                valueAll[0][indexNum] = 1
        except:
            continue
    pass


# ==label
def get_label(input_value, input_time):
    day_index = list(map_data).index("days")  # 获取特征值对应下标索引
    value_index = list(map_data).index("AKI_label")  # 获取特征值对应下标索引
    valueAll[0, day_index] = input_time
    valueAll[0, value_index] = input_value


# ====== input data
# cd='F:/2018_research_python/AKI_Python_rawData_process_20180517/result/'
cd = '/home/xzhang_sta/xyf/result/'
allFileName = ['ft_zip2010', 'ft_zip2011', 'ft_zip2012', 'ft_zip2013', 'ft_zip2014', 'ft_zip2015',
               'ft_zip2016', 'ft_zip2017', 'ft_zip2018']
# cd = 'D:/Pydataproject/xyf_data_algorithm/result/'
# allFileName = ['AKI_newdata', 'AKI_newdata1', 'AKI_newdata4']

for x in range(len(allFileName)):
    fileName = allFileName[x]  # AKI
    f = open(cd + fileName + '.pkl', 'rb')
    data = pickle.load(f)

    map_f = open(cd + 'feature_dict_BDAI_map.pkl', 'rb')
    map_data = pickle.load(map_f)

    # ====input parameter
    pre_day = 1
    Data = np.zeros([1, len(map_data)])
    # 遍历每一个样本
    for i in range(len(data)):

        #  feature category
        demo, vital, lab, ccs, px, med, label = data[i]
        # =======================首先解决：每个样本的AKI爆发时间的提前n天的对应时间
        # ==label 应该如何对应矩阵位置
        a = np.array(label)
        y_value = a[:, 0]
        t_time = a[:, 1] - pre_day
        for j in range(len(t_time)):
            # 每一个样本定义一个整的零矩阵
            valueAll = np.zeros([1, len(map_data)])  # all feature number is 28298

            y_value_sub = y_value[j]
            t_time_sub = t_time[j]

            # 测试上述代码
            # label
            get_label(y_value_sub, t_time_sub)

            # demo
            get_demo(demo)

            # vital
            get_vital(vital, t_time_sub)

            # lab && med
            get_lab_med(lab, t_time_sub)
            get_lab_med(med, t_time_sub)

            # ccs && px
            get_ccs_px(ccs, t_time_sub)
            get_ccs_px(px, t_time_sub)

            Data = np.row_stack((Data, valueAll))

    # '==========整合数据=============='
    # 删除数组中的第一行：
    final_Data = Data[1:, :]
    # print(final_Data)
    file = open(cd + fileName + '_day' + str(pre_day) + '.pkl', 'wb')
    pickle.dump(final_Data, file)
    file.close()
