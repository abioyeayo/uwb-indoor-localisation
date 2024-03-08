# ***************************************************************
# Author: Ayo Abioye (a.o.abioye@soton.ac.uk)
# Date: Friday 8th March 2024
# Usage:
#    Python script to plot uwb logged data
#    v2 - New algorithm for computing 3D plot
#    v3 - filtering input distances from anchors a0, a1, a2, and a3
# ***************************************************************

import sys,tty,termios
import serial
from datetime import datetime
# import requests
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import scipy.signal


def read_data(filename):
    r_data = []
    datalog = open(filename, 'r')
    data_lines = datalog.readlines()
    for data_line in data_lines:
        r_data.append(float(data_line)*100)
    return r_data



y_data1 = read_data("10cm.txt")
# print(y_data1)

x_data1 = np.full((500, 1), 10)
# print(x_data1)

y_data2 = read_data("20cm.txt")
x_data2 = np.full((500, 1), 20)

y_data3 = read_data("30cm.txt")
x_data3 = np.full((500, 1), 30)

y_data4 = read_data("40cm.txt")
x_data4 = np.full((500, 1), 40)

y_data5 = read_data("50cm.txt")
x_data5 = np.full((500, 1), 50)

y_data6 = read_data("60cm.txt")
x_data6 = np.full((500, 1), 60)

y_data7 = read_data("70cm.txt")
x_data7 = np.full((500, 1), 70)

y_data8 = read_data("80cm.txt")
x_data8 = np.full((500, 1), 80)

y_data9 = read_data("90cm.txt")
x_data9 = np.full((500, 1), 90)

y_data10 = read_data("100cm.txt")
x_data10 = np.full((500, 1), 100)

y_data11 = read_data("110cm.txt")
x_data11 = np.full((500, 1), 110)

y_data12 = read_data("120cm.txt")
x_data12 = np.full((500, 1), 120)

y_data13 = read_data("130cm.txt")
x_data13 = np.full((500, 1), 130)

y_data14 = read_data("140cm.txt")
x_data14 = np.full((500, 1), 140)

# Plotting data
plt.figure()
# plt.plot(nx_data_filtered, ny_data_filtered, 'o')
plt.plot(x_data1,y_data1, 'o')
plt.plot(x_data2,y_data2, 'o')
plt.plot(x_data3,y_data3, 'o')
plt.plot(x_data4,y_data4, 'o')
plt.plot(x_data5,y_data5, 'o')
plt.plot(x_data6,y_data6, 'o')
plt.plot(x_data7,y_data7, 'o')
plt.plot(x_data8,y_data8, 'o')
plt.plot(x_data9,y_data8, 'o')
plt.plot(x_data10,y_data10, 'o')
plt.plot(x_data11,y_data11, 'o')
plt.plot(x_data12,y_data12, 'o')
plt.plot(x_data13,y_data13, 'o')
plt.plot(x_data14,y_data14, 'o')
plt.plot([10,20,30,40,50,60,70,80,90,100,110,120,130,140],[10,20,30,40,50,60,70,80,90,100,110,120,130,140], 'xk')
plt.plot([10,20,30,40,50,60,70,80,90,100,110,120,130,140],[10,20,30,40,50,60,70,80,90,100,110,120,130,140], '-k')
plt.xlim(0, 150)
plt.ylim(-20, 200)
plt.title("Comparing UWB Tag actual vs measured values")
plt.xlabel("Actual value")
plt.ylabel("Measured value")

plt.show()