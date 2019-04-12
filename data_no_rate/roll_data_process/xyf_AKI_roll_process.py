# -*- coding: utf-8 -*-
"""
@author: xueyunfei use python3.6
"""
import pickle
import numpy as np
import time
import os


# == demo
def get_demo(input_data):
    Demo = np.array(input_data)
    # 将 demo类中数据对应到整个矩阵对应的位置 ，注意:【位置需要查映射表获取】
    for m in range(len(Demo)):
        demo_index = "demo"
        indexNum = 0
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
                # 判断 'vital1_HT'/'vital1'在映射表中的位置。
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
    try:
        day_index = list(map_data).index("days")  # 获取特征值对应下标索引
        value_index = list(map_data).index("AKI_label")  # 获取特征值对应下标索引
        valueAll[0, day_index] = input_time
        # valueAll[0, value_index] = input_value
        # 获取出院时间。（最后一个元素值）
        a = np.array(input_value)
        y_value = a[:, 0]
        t_time = a[:, 1]
        out_time = np.max(t_time)
        if input_time > out_time:  # 说明该病人已经出院，将该样本舍弃。
            return 0
        # 找出病人第一次发病时间
        first_disease_day = 0
        first_disease_value = 0
        if np.max(y_value) == 0:  # 说明该病人一直未患病
            valueAll[0, value_index] = 0
            return 1
        else:  # 说明该病人患病,找出病人第一次发病时间
            for s in range(len(y_value)):
                if y_value[s] > 0:
                    first_disease_day = t_time[s]
                    first_disease_value = y_value[s]
                    break
        if input_time >= first_disease_day:  # 说明在t_time 之前该病人已经发病，将该样本舍弃
            return 0
        elif input_time == first_disease_day - 1:  # 说明在 t_time 的下一天该样本将要发病，将该样本设置成有病样本。eg:[x0,y1]
            valueAll[0, value_index] = first_disease_value
            return 1
        elif input_time < first_disease_day - 1:  # 说明该样本在t_time 之前还没有发病，将该样本设置成无病样本。
            valueAll[0, value_index] = 0
            return 1
    except:
        return 0


def find_max_day(input_data):
    max = -1
    for j in range(len(input_data)):
        a = np.array(input_data[j][-1])
        y_value = a[:, 0]
        t_time = a[:, 1]
        for s in range(len(y_value)):
            if y_value[s] > 0:
                if max < t_time[s]:
                    max = t_time[s]
                break
        # if max < np.max(t_time) and y_value[list(t_time).index(np.max(t_time))] > 0:
        #     max = np.max(t_time)
    return max


# ====== input data
# cd='F:/2018_research_python/AKI_Python_rawData_process_20180517/result/'
startime = time.time()
print("======process star time========")
print(startime)
# allFileName = ['ft_zip2010', 'ft_zip2011', 'ft_zip2012', 'ft_zip2013', 'ft_zip2014', 'ft_zip2015',
#                'ft_zip2016', 'ft_zip2017', 'ft_zip2018']
cd = '../result/'
allFileName = ['ft_zip2018']


for k in range(len(allFileName)):
    fileName = allFileName[k]  # AKI
    f = open(cd + fileName + '.pkl', 'rb')
    data = pickle.load(f)

    map_f = open(cd + 'feature_dict_BDAI_map.pkl', 'rb')
    map_data = pickle.load(map_f)

    # ====input parameter
    # pre_day = 1

    # 找出需要处理的最大天数
    max_day = find_max_day(data)
    print(max_day)
    # 相比从后往前的预处理数据，只需修改处理各个特征值时候的入参时间，即传入所需要测试的时间
    for day in range(max_day):  # 舍弃掉最后一天
        # day = 1
        Data = np.zeros([1, len(map_data)])
        # 遍历每一个样本
        for i in range(len(data)):

            #  feature category
            demo, vital, lab, ccs, px, med, label = data[i]
            valueAll = np.zeros([1, len(map_data)])  # all feature number is 28298

            # ==label  判断样本是否舍弃，以及将label进行预处理。
            result = get_label(label, day)
            if result <= 0:  # 说明该样本要舍弃
                continue

            # demo
            get_demo(demo)

            # vital
            get_vital(vital, day)

            # lab && med
            get_lab_med(lab, day)
            get_lab_med(med, day)

            # ccs && px
            get_ccs_px(ccs, day)
            get_ccs_px(px, day)

            Data = np.row_stack((Data, valueAll))

        # '==========整合数据=============='
        # 删除数组中的第一行：
        final_Data = Data[1:, :]
        # print(final_Data)
        cdd = 'rollresult/' + fileName + '/'
        isExists = os.path.exists(cdd)
        if not isExists:
            os.mkdir(cdd)
        file = open(cdd + 'roll_test_day' + str(day) + '.pkl', 'wb')
        pickle.dump(final_Data, file)
        file.close()
print("======process use time========")
print(time.time() - startime)
