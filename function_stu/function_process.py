import numpy as np

# item = [["1", "2"], ["1", "3"], ["2", "4"]]
# # 转换数据的类型 ：str -> int
# s1 = np.array(list(map(lambda x: [int(x[0]), int(x[1])], item)))
# s2 = s1[:, 0] -1
# print(s2)
# print(s2[0])
# print("#"*5)
# s3 = np.array(list(map(lambda x: [int(x[0]), int(x[1])], item))[::-1])
# print(s3)
# print(item[::-1])
# s1 = np.zeros((1, 5), dtype=np.int8)
# print(s1)
# s1[0, 2] = 1
# print(s1)
# s1[0, 3] = 2
# print(s1)
# s2 = np.zeros((1, 3), dtype=np.int8)
# print(s2)
#
# s3 = np.zeros((5,), dtype=np.int8)
# print(type(s3))
# print(s3)
# age = [[70]]
# print(age)
#
# s4 = np.hstack((s1, s2))
# print(s4)
# s5 = np.hstack((age, s4))
# print(s5)
# print(np.hstack([age, s4]))
# s6 = s5
# s7 = s5
# s8 = np.hstack((s5, s6, s7))
# print(s8)
# s9 = s8
# s10 = np.vstack((s8, s9))
# print("="*30)
# print(s10)

# item = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
#
# # 数组中从后往前数的话，最后一个位置是-1
# # [:-1] 表示从位置0到位置-1之前的数
# s1 = item[:-1]
# print(s1)  # [0, 1, 2, 3, 4, 5, 6, 7, 8]
# # [::-1] 从后向前将数据输出，即倒序
# s2 = item[::-1]
# print(s2)   # [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
# item = [[1, 2], [1, 3], [2, 4]]
#
# s1 =np.array(item)
# print(type(item))
# s2 = s1[:,-1]
# print(type(s2))
# print(s2)
# nearValue = item[np.argmax(s2)][0]
# print(nearValue)
# fillNA =-1000
# baseIN = list([fillNA, fillNA, fillNA, fillNA])
# baseIN2 = [fillNA, fillNA, fillNA, fillNA]
# rate = fillNA
# try:
#     # s = 1/0
#     baseIN2 = [0,0,0]
#     rate = 1/0
# except Exception as e:
#     print(e)
# s1 = np.hstack((baseIN2,rate))
# print(s1)
s1 =np.ones([1,5])* 10 , 10
print(type(s1))
print(s1)