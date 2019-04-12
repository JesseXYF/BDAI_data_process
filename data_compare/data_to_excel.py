import pickle
import pandas as pd

file = open("D:\\homework\\study_obj\\stu_excel\\new_AKI_newdata1.pkl","rb")
data =pickle.load(file)
# print(data)
file.close()

finaldata = pd.DataFrame(data[5:])
finaldata.to_csv("D:\\homework\\study_obj\\stu_excel\\result\\mycsv.csv")
finaldata.to_excel("D:\\homework\\study_obj\\stu_excel\\result\\myexcel.xlsx")