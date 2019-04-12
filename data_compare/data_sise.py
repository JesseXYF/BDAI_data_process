import pickle
import pandas as pd
import numpy as np

allFileName = ['ft_zip2010', 'ft_zip2011', 'ft_zip2012', 'ft_zip2013', 'ft_zip2014', 'ft_zip2015',
               'ft_zip2016', 'ft_zip2017', 'ft_zip2018']
data_all = []
k = 0
for filename in allFileName:
    file = open("/panfs/pfs.local/work/liu/xzhang_sta/xyf/result/" + filename + ".pkl", "rb")
    data = list(pickle.load(file))
    # print(data)
    file.close()
    label = data[:-1]
    AKIstu = label[:-1]
    data_info = [filename, len(data), AKIstu.count(0), AKIstu.count(1), AKIstu.count(2), AKIstu.count(3)]
    if k == 0:
        data_all = data_info
    else:
        data_all = np.vstack((data_all, data_info))

finaldata = pd.DataFrame(data_all)

finaldata.to_excel("/panfs/pfs.local/work/liu/xzhang_sta/xyf/data_compare/result/data_size.xlsx")
