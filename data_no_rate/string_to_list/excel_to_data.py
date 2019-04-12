import pandas as pd
data = pd.read_excel("D:\\Pydataproject\\BDAI_data_process\\data_no_rate\\string_to_list\\result\\AKI_newdata1\\part_0_list.xlsx").values
print(len(data))
print(type(data))
print(data)
dd=data[0][0][1]
print(dd)