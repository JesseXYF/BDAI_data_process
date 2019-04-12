# -*- coding: utf-8 -*-
"""
Created on Thu May 17 14:46:05 2018

@author: wulj
"""
'''
此文件用于提取原始txt文本数据，并存储为嵌套型列表，生成pickle文件，方便后续再处理
'''
import pickle

'''====对demo数据进行处理===='''


def demo_process(data):
    '''
    输入数据格式：'value0_value1_...' 
    无时序信息，只有一级分割“_", 因此只需要存储为一维列表
    输出数据格式：[value0,value1],数据类型为一维list,元素类型为int
    '''
    temp = data.split('_')
    result = list(temp)
    return result


# 测试上述代码
# print(demo_process(data_split_category[0][0]))

'''====对vital数据进行处理===='''


def vitals_process(data):
    '''
    输入数据格式：'{[(),(),...];[];...}_{}_...'
    一级分割'_', 二级分割';', 三级分割','
    输出数据格式：[[[value,value,...],[],...],[],...],数据类型为3维list,元素类型为int
    '''
    first_split = data.split('_')
    second_split = [first_split[i].split(';') for i in range(len(first_split))]
    third_split = [[second_split[i][j].split(',') for j in range(len(second_split[i]))] for i in
                   range(len(second_split))]

    '''是否需要将-str变成float形式-'''
    result = [[[float(third_split[i][j][k]) for k in range(len(third_split[i][j]))] for j in range(len(third_split[i]))]
              for i in range(len(third_split))]
    return result
    # return third_split


# 测试上述代码
# print( vitals_process(data_split_category[0][1]))

'''====对comorbidity、procedure数据进行处理===='''


def css_px_process(data):
    '''
    输入数据格式：'{xxx:[(),()...]}_{xxx:[(),()...]}' eg：ccs10:-80,-51_ccs55:-113
    一级分割'_'，二级分割':'，三级分割','
    输出数据格式[[[xxx], [value, value]]...]
    '''
    first_split = data.split('_')
    second_split = [first_split[i].split(':') for i in range(len(first_split))]
    third_split = [[second_split[i][j].split(',') for j in range(len(second_split[i]))] for i in
                   range(len(second_split))]
    return third_split


# 测试上述代码
# print( css_px_process(data_split_category[0][3]))

'''====lab、med数据进行处理===='''


def lab_med_process(data):
    '''
    输入数据格式:'{xxx:[[(),(),...];[];...]}_{xxx:[[(),()];[]]}' eg: lab106:9.3,PERCENT,1_lab108:9.6,MG/DL,1;8.5,MG/DL,2;8.4,MG/DL,3;8.6,MG/DL,4
    一级分割'_'，二级分割':'，三级分割';'，四级分割','
    输出数据格式[[[[xxx]], [[value, value]]]...]  eg:[[[['lab106']], [['9.3', 'PERCENT', '1']]]...]
    '''
    first_split = data.split('_')
    second_split = [first_split[i].split(':') for i in range(len(first_split))]
    third_split = [[second_split[i][j].split(';') for j in range(len(second_split[i]))] for i in
                   range(len(second_split))]
    fourth_split = [
        [[third_split[i][j][k].split(',') for k in range(len(third_split[i][j]))] for j in range(len(third_split[i]))]
        for i in range(len(third_split))]
    return fourth_split


# 测试上述代码
# print( lab_med_process(data_split_category[0][2]))

'''=====对label 数据进行提取整理========'''


def label_process(data):
    '''
    输入数据格式：'label,date_label,date_label,date\n'
    输出数据格式：[[label,date],[]],数据类型为2维list,元素类型为int
    '''
    first_split = data.split('_')
    second_split = [first_split[i].split(',') for i in range(len(first_split))]

    for i in range(len(second_split)):
        second_split[i][0] = int(second_split[i][0])
        second_split[i][1] = int(second_split[i][1])
    return second_split


# 测试上述代码
# print(label_process(data_split_category[0][-1]))


# 主程序
cd = 'D:/Pydataproject/xyf_data_algorithm/Raw_Data/'
allFileName = ['AKI_newdata', 'AKI_newdata1', 'AKI_newdata4']
# cd='/home/xzhang_sta/xyf/AKI_CDM_byYear/'
# allFileName = ['ft_zip2010', 'ft_zip2011', 'ft_zip2012', 'ft_zip2013', 'ft_zip2014', 'ft_zip2015',
#                'ft_zip2016', 'ft_zip2017', 'ft_zip2018']
for m in range(len(allFileName)):
    fileName = allFileName[m]  # AKI
    '''====读取文件===（AKI 与nonAKI 单独处理生成各自文件）'''
    f = open(cd + fileName + '.txt', 'r')
    lines = f.readlines()  # 读取全部内容
    f.close()

    '''对原始数据集lines按不同feature category 即‘|’分割成list'''
    data_split_category = []
    lines__split_category = []
    temp = [lines__split_category.append(lines[i].split('"')) for i in range(len(lines))]

    temp = [data_split_category.append(lines__split_category[i][3].split('|')) for i in range(len(lines))]

    '''====对demo,vitals, lab, drg, com, imed, omed, ccs, label 类别进行分割======'''

    Data = []
    for n in range(len(data_split_category)):
        demo = demo_process(data_split_category[n][0])

        vital = vitals_process(data_split_category[n][1])

        lab = lab_med_process(data_split_category[n][2])
        med = lab_med_process(data_split_category[n][5])

        ccs = css_px_process(data_split_category[n][3])
        px = css_px_process(data_split_category[n][4])

        label = label_process(data_split_category[n][6])

        Data.append([demo, vital, lab, ccs, px, med, label])

    '''==========整合数据=============='''
    # save data into a pickle file
    cdd = 'D:/Pydataproject/xyf_data_algorithm/result/'
    # cdd = '/home/xzhang_sta/xyf/result/'
    file = open(cdd + fileName + '.pkl', 'wb')
    pickle.dump(Data, file)
    file.close()
