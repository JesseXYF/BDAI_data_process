# -*- coding: utf-8 -*-
"""
Created on Sat Mar 23 15:59:13 2019

@author: molong
"""
import pickle
import numpy as np
import pandas as pd

import threading
import sys
import logging

# logging
logging.basicConfig(filename="D:\\Pydataproject\\xyf_data_algorithm\\pre_one_day\\loggings\\Print_logging.log",
                    level=logging.DEBUG,
                    format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %I:%M:%S %p')
# 缺失值用-1000填充
fillNA = -1000


def columnsNameMap(item, prefix):
    index = []
    for i in item:
        index.append(str(prefix + i))
    return index


###----------------demographic

###columns
HISPANIC = ["Y", "N", "R", "NI", "UN", "OT"]
RACE = ["01", "02", "03", "04", "05", "06", "07", "NI", "UN", "OT"]
SEX = ["A", "F", "M", "NI", "UN", "OT"]


def demoMap(demo):
    age = np.array([int(demo[0])], dtype=np.int8)
    hispanicIndex = HISPANIC.index(demo[1])
    raceIndex = RACE.index(demo[2])
    sexIndex = SEX.index(demo[3])

    hispanic = np.zeros((1, len(HISPANIC)), dtype=np.int8)
    hispanic[0, hispanicIndex] = 1

    race = np.zeros((1, len(RACE)), dtype=np.int8)
    race[0, raceIndex] = 1

    sex = np.zeros((1, len(SEX)), dtype=np.int8)
    sex[0, sexIndex] = 1
    baseINF = np.hstack((hispanic, race, sex))
    # baseINF.astype(categoryList)
    return np.hstack([[age], baseINF])


###----------------demographic ----------------end


###----------------vital
def sameDayVarbMap(item):
    return float(item[0]), float(item[-1])


# 筛选出以记录AKI状态的时间为时间节点的前一天的数据，即[statusDay-1,statusDay]，代码中day = statusDay-1
def getSameDayVariable(var, day):
    if len(var) == 0:
        return []

    index = np.array(var[:, -1] >= day)
    var = var[index]
    if len(var) == 0:
        return []

    index = np.array(var[:, -1] < day + 1)
    var = var[index]
    return var


# 计算平均值，最近值，比例值
def getVarientScaleMean(variable, day):
    if len(variable) == 0:
        return [fillNA, fillNA, fillNA]

    variable = np.array(list(map(sameDayVarbMap, variable))[::-1])  # 将数据倒序输出

    var = getSameDayVariable(variable, day)  # 筛选出第day天记录的数据

    if len(var) > 0:

        scale = np.max(var[:, 0]) - np.min(var[:, 0])  # 比例：最大值-最小值
        # 最近值；即选出当天的时长中，最大时间所对应的值
        nearValue = var[np.argmax(var[:, -1])][0]  # np.argmax()取出var中元素最大值所对应的索引。
        mean = np.mean(var[:, 0])  # 平均值
    else:
        # 如果该属性在提前一天到当天的时间段中没有记录数据，那么最近值就取提前一天(day)之前的数据
        nearValueIndex = variable[:, -1] <= day

        if np.sum(nearValueIndex) == 0:
            return [0, 0, 0]

        nearValue = variable[np.argmax(nearValueIndex)][0]
        mean = 0

        scale = 0

    return list([mean, nearValue, scale])


###----------------vital----------------


##--------------------vital 
# 计算变化率 (最大值 - 最小值)/(最大值对应的时间-最小值对应的时间)
def getVarientRate(variable, day):
    var = np.array(list(map(sameDayVarbMap, variable))[::-1])
    var = getSameDayVariable(var, day)
    rate = 0
    if len(var) > 0:
        maxIndex = np.argmax(var[:, 0])
        minIndex = np.argmin(var[:, 0])

        if maxIndex != minIndex and (var[maxIndex][-1] - var[minIndex][-1]) != 0:
            rate = (var[maxIndex][0] - var[minIndex][0]) / (var[maxIndex][-1] - var[minIndex][-1])

    return rate


##somke columns     “0”代表在数据处理的时候，数据中出现的数值有“0”的情况，但是excel中没有给出，在这里进行定义该情况
SMOKE = ["01", "07", "02", "08", "03", "04", "05", "06", "NI", "UN", "OT", "0"]
TOBACCO = ["0", "01", "02", "03", "04", "06", "NI", "UN", "OT"]
TOBACCO_TYPE = ["0", "01", "02", "03", "04", "05", "NI", "UN", "OT"]


##vital mean cale earVariable rate
def varibaleArrange(variable, day):
    baseIN = list([fillNA, fillNA, fillNA])
    rate = fillNA
    try:
        # 获取该属性的平均值，最近值，比例值
        baseIN = getVarientScaleMean(variable, day)

        rate = getVarientRate(variable, day)
    except Exception as e:
        logging.info("varibaleArrange erro")
        logging.error(e)

    return np.hstack((baseIN, rate))


def smokeElevation(smoke, day):
    if len(smoke) == 0:
        return np.ones((1, len(SMOKE)), dtype=np.int8) * fillNA, fillNA

    if len(smoke) == 1:
        smo = np.zeros((1, len(SMOKE)), dtype=np.int8)
        if len(smoke[0]) == 1 or float(smoke[0][1]) <= day:
            smokeIndex = SMOKE.index(smoke[0][0])
            smo[0, smokeIndex] = 1

        return smo, fillNA
    else:
        elva = 2  # elva是对吸烟趋势分析  -1：减轻了,0：没变,1：加重了，2：未知，-1000：缺失
        indexSet = set([])
        smo = np.zeros((1, len(SMOKE)), dtype=np.int8)
        for smokeItem in smoke:
            if float(smokeItem[1]) <= day:
                indexSet.add(smokeItem[0])
        indexSet = list(indexSet)

        if len(indexSet) == 0:
            return smo, elva

        if len(indexSet) == 1:
            smo[0, SMOKE.index(indexSet[0])] = np.int8(1)
            return smo, elva

        formerVar = SMOKE.index(indexSet[-2])
        lasetVar = SMOKE.index(indexSet[-1])
        smo[0, lasetVar] = 1

        if formerVar < 4 and lasetVar < 4:  # 4对应于SMOKE数组的下标，前四个是可以判断吸烟的趋势，而之后的吸烟趋势是未知的
            if formerVar == lasetVar:
                elva = 0
            elif formerVar > lasetVar:
                elva = -1
            else:
                elva = 1
        return smo, elva


def tobaccoNearVar(var, index, day):
    if len(var) == 0:
        return np.ones((1, len(index)), dtype=np.int8) * fillNA
    if len(var) == 1:
        toba = np.zeros((1, len(index)), dtype=np.int8)
        if len(var[0]) == 1 or float(var[0][1]) <= day:
            varIndex = index.index(var[0][0])
            toba[0, varIndex] = 1

        return toba

    else:
        toba = np.zeros((1, len(index)), dtype=np.int8)
        indexSet = set([])
        for varItem in var:
            if float(varItem[1]) <= day:
                indexSet.add(varItem[0])
        indexSet = list(indexSet)
        if len(indexSet) == 0:
            return np.ones((1, len(index)), dtype=np.int8) * fillNA
        varIndex = index.index(indexSet[-1])
        toba[0, varIndex] = 1
        return toba


def vitalMap(vital, day):
    try:

        height = np.array([varibaleArrange(vital[0], day)])
        weight = np.array([varibaleArrange(vital[1], day)])
        bmi = np.array([varibaleArrange(vital[2], day)])
        bpSys = np.array([varibaleArrange(vital[6], day)])
        bpDia = np.array([varibaleArrange(vital[7], day)])

        smoke, elev = smokeElevation(vital[3], day)

        tobacco = tobaccoNearVar(vital[4], TOBACCO, day)

        tobaccoType = tobaccoNearVar(vital[5], TOBACCO_TYPE, day)

    except Exception as e:
        logging.info("vitalMap erro: ")
        logging.error(e)
        logging.info(vital)

        smoke = np.ones((1, len(SMOKE)), dtype=np.int8) * fillNA
        elev = fillNA
        tobacco = np.ones((1, len(TOBACCO)), dtype=np.int8) * fillNA
        tobaccoType = np.ones((1, len(TOBACCO_TYPE)), dtype=np.int8) * fillNA

        height = [[fillNA] * 4]
        weight = [[fillNA] * 4]
        bmi = [[fillNA] * 4]
        bpSys = [[fillNA] * 4]
        bpDia = [[fillNA] * 4]

    elev = np.array([[elev]])
    baseIN = np.hstack((smoke, tobacco, tobaccoType))
    # baseIN.astype(categoryList)
    return np.hstack([height, elev, weight, bmi, baseIN, bpSys, bpDia])


##--------------------vital ----------------end


##--------------------lab
def labMap(lab, day, col):
    try:
        labDiscrt = np.zeros((1, len(col) * 3))
        for item in lab:
            index = col.index(item[0][0][0]) * 3
            # index = (int(str(item[0][0][0])[3:])-1)*3
            mean, lately, scale = getVarientScaleMean(item[1], day)
            labDiscrt[0, index] = mean
            labDiscrt[0, index + 1] = lately
            labDiscrt[0, index + 2] = scale
    except Exception as e:
        logging.info("labMap erro:")
        logging.error(e)
        logging.info(lab)
        labDiscrt = np.ones((1, len(col) * 3), dtype=np.float32) * fillNA
    return labDiscrt


##--------------------lab -----------end


###---------------------
def comorbidityMap(comorbidity, day, col):
    if len(comorbidity) == 1 and len(comorbidity[0]) == 1:
        comorbidityDiscrt = np.ones((1, len(col) * 2), dtype=np.int8) * fillNA
        return comorbidityDiscrt
    try:

        comorbidityDiscrt = np.zeros((1, len(col) * 2), dtype=np.int8)
        for item in comorbidity:
            index = col.index(item[0][0]) * 2
            value = item[1]
            value = np.array(list(map(int, value)))
            value = value[np.array(value <= day)]

            comorbidityDiscrt[0, index:index + 2] = len(value), np.max(value)
    except Exception as e:
        logging.info("comorbidityMap erro:")
        logging.error(e)
        logging.info(comorbidity)
        comorbidityDiscrt = np.ones((1, len(col) * 2), dtype=np.int8) * fillNA
    return comorbidityDiscrt


###------------------------------------


###---------------------
def procedureMap(procedure, day, column):
    try:
        procedureDiscrt = np.zeros((1, len(column)), dtype=np.int8)
        for item in procedure:
            curDay = int(item[1][0])
            if curDay <= day:
                index = column.index(item[0][0])

                # index = int(str(item[0][0])[2:])
                procedureDiscrt[0, index] = 1
    except Exception as e:
        logging.info("procedureMap erro:")
        logging.error(e)
        logging.info(procedure)
        procedureDiscrt = np.ones((1, len(column)), dtype=np.int8) * fillNA

    return procedureDiscrt


###---------------------------------end


###---------------------
def medValueMap(itemValue):
    return [int(itemValue[0]), int(itemValue[1])]


def medMap(med, day, col):
    try:
        medDiscrt = np.zeros((1, len(col) * 2), dtype=np.int8)
        for item in med:

            index = col.index(item[0][0][0]) * 2

            value = np.array(list(map(medValueMap, item[1]))[::-1])

            valueIndex = np.array(value[:, 1] <= day)
            if np.sum(valueIndex) > 0:
                value = value[valueIndex]

                medDiscrt[0, index] = np.sum(valueIndex)

                medDiscrt[0, index + 1] = value[np.argmax(value[:, 1]), 0]

    except Exception as e:
        logging.info("medMap erro:")
        logging.error(e)
        logging.info(med)
        medDiscrt = np.ones((1, len(col) * 2), dtype=np.int8) * fillNA
    return medDiscrt


###----------------------------------------end


##-----------------------AKI ab 
# AKICategoryList = CategoricalDtype(categories=[0,1,2,3,fillNA])

# AKIIndex = list(["AKI_0","AKI_1","AKI_2","AKI_3","AKI_former"])
def AKIStaueMap(sta, day):
    AKIMes = np.zeros([1, 5], dtype=np.int8)
    if len(sta) > 0:
        AKIMes = np.zeros([1, 5], dtype=np.int8)
        sta = np.array(list(map(lambda x: [int(x[0]), int(x[1])], sta)))
        former = np.array(sta[:, 1] <= day)

        if np.sum(former) != 0:
            AKIMes[0, -1] = sta[former][-1][0]

        AKIsta = np.array(sta[:, 1] == day + 1)

        if np.sum(AKIsta) != 0:
            AKIsta = sta[AKIsta]

            AKIMes[0, AKIsta[0][0]] = 1
        else:
            AKIMes[0, 0] = 1
    else:
        AKIMes = np.array([fillNA] * 5)

    # AKIMes.astype(AKICategoryList)
    return AKIMes


##-----------------------AKI lab -------------end


CCSIndex = pd.read_excel(
    "/panfs/pfs.local/work/liu/xzhang_sta/moshenglong/AKIData/CCS_index.xlsx").values.flatten().tolist()
LABIndex = pd.read_excel(
    "/panfs/pfs.local/work/liu/xzhang_sta/moshenglong/AKIData/LAB_index.xlsx").values.flatten().tolist()
PXIndex = pd.read_excel(
    "/panfs/pfs.local/work/liu/xzhang_sta/moshenglong/AKIData/PX_index.xlsx").values.flatten().tolist()
MEDIndex = pd.read_excel(
    "/panfs/pfs.local/work/liu/xzhang_sta/moshenglong/AKIData/MED_index.xlsx").values.flatten().tolist()

dayScale = 50
pre_day = 1


def reduceCompute(data, p, year):
    savePath = "/panfs/pfs.local/work/liu/xzhang_sta/moshenglong/AKIData/AKI_" + year
    # for i in range(dayScale):
    k = 0
    dalyData = []
    for item in data:
        lable = np.array(list(map(lambda x: [int(x[0]), int(x[1])], item[6])))  # 类型转换
        t_time = lable[:, 1] - pre_day
        for i in t_time:
            logging.info("------------------day-------------%d" % i, "----theard---%d" % p)
            if i < 0:
                logging.info("This is the time to begin hospitalization")
                continue
            demo = demoMap(item[0])
            vital = vitalMap(item[1], i)
            lab = labMap(item[2], i, LABIndex)
            ccs = comorbidityMap(item[3], i, CCSIndex)

            px = procedureMap(item[4], i, PXIndex)
            med = medMap(item[5], i, MEDIndex)
            AKI = AKIStaueMap(item[6], i)

            singleCol = np.hstack([demo, vital, lab, ccs, px, med, AKI])
            if k == 0:
                dalyData = singleCol
            else:
                dalyData = np.vstack((dalyData, singleCol))

            logging.info("----%5dperson done-----" % k, "----theard---%d" % p)
            k += 1

    dalyData = pd.DataFrame(dalyData)
    dalyData.to_excel(savePath + "/ExcelFile/part_" + str(p) + "/" + year + "pre_day_" + str(pre_day) + ".xlsx")
    dalyData.to_csv(savePath + "/CSVFile/part_" + str(p) + "/" + year + "pre_day_" + str(pre_day) + ".csv")


if __name__ == '__main__':

    year = str(sys.argv[1])

    file_path = "/panfs/pfs.local/work/liu/xzhang_sta/shaoyong/AKI_CDM_byYear/ku/list_data/ku_ft_zip" + year + "_list.pkl"

    f = open(file_path, 'rb')
    data = np.array(list(pickle.load(f))).T
    f.close()

    threadNumb = 5
    dataScale = np.floor(len(data) / threadNumb)

    threadList = []
    for i in range(threadNumb):
        star = i * dataScale
        end = star + dataScale

        logging.info(len(data[star:end]))
        logging.info(len(data[star:end].tolist()))

        thread = threading.Thread(target=reduceCompute, args=(data[star:end].tolist(), i, year))
        logging.info("thread %2d star" % i)
        thread.start()
        threadList.append(thread)

    thread = threading.Thread(target=reduceCompute, args=(data[dataScale * threadNumb:].tolist(), threadNumb, year))
    logging.info(len(data[dataScale * threadNumb:]))
    logging.info("thread %d star" % threadNumb)
    thread.start()
    thread.join()

    for i in range(threadNumb):
        threadList[i].join()

    logging.info("main thread run out")
