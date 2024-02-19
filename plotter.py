# ***************************************************************
# Author: Ayo Abioye (a.o.abioye@soton.ac.uk)
# Date: Tuesday 6th February 2024
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



x_data = []
y_data = []
t_data_xy = []
t_init_xy = ""

a0_data = []
a1_data = []
a2_data = []
a3_data = []
t_data = []
t_init = ""

# a0_xyz = [0.00,0.00,0.00]
# a1_xyz = [0.00,0.78,0.00]
# a2_xyz = [1.72,0.78,0.00]
# a3_xyz = [1.72,0.00,0.00]

# Lab setup with Lisa (Mon 12-Feb-2024)
# a0_xyz = [0.00,0.00,1.46]
# a1_xyz = [0.88,4.55,1.27]
# a2_xyz = [4.23,5.25,1.38]
# a3_xyz = [4.28,1.18,2.51]

# corrected lab measurements
a0_xyz = [0.00,0.00,1.46]
a1_xyz = [0.88,3.80,1.27]
a2_xyz = [4.23,4.50,1.38]
a3_xyz = [4.28,1.18,2.51]

# Using readlines()
# datalog = open('log/t0_log_20240212115833.txt', 'r')  # point test p(3.68, 1.04,0.50)
# datalog = open('log/t0_log_20240212121046.txt', 'r')    # square test
datalog = open('log/t0_log_20240212132303.txt', 'r')    # point test p(3.68, 3.40,1.05)
data_lines = datalog.readlines()

# Strips the newline character
for data_line in data_lines:
    data_col = data_line.split()
    if len(data_col) > 2 and len(data_col) < 5:
        if data_col[1] == "(x,y)":
            # print(data_line)
            data_str = data_col[3].replace('(', '').replace(')', '')
            # data_str = data_line[9:-2]
            data_str_array = data_str.split(',')
            x_data.append(float(data_str_array[0]))
            y_data.append(float(data_str_array[1]))

            if t_init_xy == "":
                t_init_xy = datetime.fromisoformat(data_col[0])
            # dt = datetime.fromisoformat('2023-04-01T05:00:30.001000')
            t_diff_xy = datetime.fromisoformat(data_col[0]) - t_init_xy
            t_data_xy.append(float(t_diff_xy.total_seconds()))

        if data_col[1] == "(a0,a1,a2,a3)":
            # print(data_line)
            data_str = data_col[3].replace('(', '').replace(')', '')
            # data_str = data_line[9:-2]
            data_str_array = data_str.split(',')
            a0_data.append(float(data_str_array[0]))
            a1_data.append(float(data_str_array[1]))
            a2_data.append(float(data_str_array[2]))
            a3_data.append(float(data_str_array[3]))

            if t_init == "":
                t_init = datetime.fromisoformat(data_col[0])
            # dt = datetime.fromisoformat('2023-04-01T05:00:30.001000')
            t_diff = datetime.fromisoformat(data_col[0]) - t_init
            t_data.append(float(t_diff.total_seconds()))
            

# print(x_data)
# print(y_data)
# print(t_data)

# ax_data_prev = 0
# for i in range(len(a0_data)):
#     if a0_data[i] == 12.30:
#         # print(x)
#         a0_data[i] = ax_data_prev
#     else:
#         ax_data_prev = a0_data[i]


def filter_function(ax_data):
    ax_data_prev = 0
    for i in range(len(ax_data)):
        if ax_data[i] == 12.30:
            ax_data[i] = ax_data_prev
        else:
            ax_data_prev = ax_data[i]
    return ax_data

#A function to apply trilateration formulas to return the (x,y,z) intersection point of three circles
def locate_tag(x1,y1,z1,r1,x2,y2,z2,r2,x3,y3,z3,r3):
    A = 2*(x1 - x2)
    B = 2*(y1 - y2)
    C = 2*(z1 - z2)
    D = x1**2 + y1**2 + z1**2 - x2**2 - y2**2 - z2**2 - r1**2 + r2**2
    E = 2*(x1 - x3)
    F = 2*(y1 - y3)
    G = 2*(z1 - z3)
    H = x1**2 + y1**2 + z1**2 - x3**2 - y3**2 - z3**2 - r1**2 + r3**2
    I = 2*(x2 - x3)
    J = 2*(y2 - y3)
    K = 2*(z2 - z3)
    L = x2**2 + y2**2 + z2**2 - x3**2 - y3**2 - z3**2 - r2**2 + r3**2

    try:
        z = (A*F*L - B*E*L - D*F*I + B*H*I - A*H*J + D*E*J) / (A*F*K - B*E*K - C*F*I + B*G*I + C*E*J - A*G*J)
    except ZeroDivisionError:
        z = 0.0
        # print('z = 0.0')
        # print(A, B, C, D, E, F, G, H, I, J, K, L, sep="\t")
        # print(A*F*K, B*E*K, C*F*I, B*G*I, C*E*J, A*G*J, sep="\t")
 
    y = (A*H - D*E + (C*E - A*G)*z) / (A*F - B*E)
    x = (D - B*y - C*z) / A

    return x,y,z

# Computing trilateration alternatively
def trilateration(P1, P2, P3, r1, r2, r3):

  p1 = np.array([0, 0, 0])
  p2 = np.array([P2[0] - P1[0], P2[1] - P1[1], P2[2] - P1[2]])
  p3 = np.array([P3[0] - P1[0], P3[1] - P1[1], P3[2] - P1[2]])
  v1 = p2 - p1
  v2 = p3 - p1

  Xn = (v1)/np.linalg.norm(v1)

  tmp = np.cross(v1, v2)

  Zn = (tmp)/np.linalg.norm(tmp)

  Yn = np.cross(Xn, Zn)

  i = np.dot(Xn, v2)
  d = np.dot(Xn, v1)
  j = np.dot(Yn, v2)

  X = ((r1**2)-(r2**2)+(d**2))/(2*d)
  Y = (((r1**2)-(r3**2)+(i**2)+(j**2))/(2*j))-((i/j)*(X))
  Z1 = np.sqrt(max(0, r1**2-X**2-Y**2))
  Z2 = -Z1

  K1 = P1 + X * Xn + Y * Yn + Z1 * Zn
  K2 = P1 + X * Xn + Y * Yn + Z2 * Zn
  return K1,K2


a0_data = filter_function(a0_data)
a1_data = filter_function(a1_data)
a2_data = filter_function(a2_data)
a3_data = filter_function(a3_data)

plt.plot(x_data, y_data, 'o')
plt.xlim(-1, 3)
plt.ylim(-1, 2)
plt.title("UWB Tag tracking")
plt.xlabel("x-axis")
plt.ylabel("y-axis")

plt.figure()
plt.plot(t_data_xy, x_data, label='x-data')
plt.plot(t_data_xy, y_data, label='y-data')
plt.legend()


## Applying low pass butterworth filter and apply filter forward and backward using filtfilt
fs = 30  # sampling rate, Hz
b, a = scipy.signal.iirfilter(4, Wn=2.5, fs=fs, btype="low", ftype="butter")
print(b, a, sep="\n")
a0_data_filtered = scipy.signal.filtfilt(b, a, a0_data)
a1_data_filtered = scipy.signal.filtfilt(b, a, a1_data)
a2_data_filtered = scipy.signal.filtfilt(b, a, a2_data)
a3_data_filtered = scipy.signal.filtfilt(b, a, a3_data)


plt.figure()
plt.plot(t_data, a0_data, label='A0')
plt.plot(t_data, a0_data_filtered, alpha=0.8, lw=3, label="A0 filtered")
plt.plot(t_data, a1_data, label='A1')
plt.plot(t_data, a1_data_filtered, alpha=0.8, lw=3, label="A1 filtered")
plt.plot(t_data, a2_data, label='A2')
plt.plot(t_data, a2_data_filtered, alpha=0.8, lw=3, label="A2 filtered")
plt.plot(t_data, a3_data, label='A3')
plt.plot(t_data, a3_data_filtered, alpha=0.8, lw=3, label="A3 filtered")
plt.title("UWB Anchor Distance Readings Over Time")
plt.xlabel("Time (s)")
plt.ylabel("Anchor distance (m)")
# plt.legend()
plt.legend(loc="lower center", bbox_to_anchor=[0.5, 1], ncol=4, fontsize="smaller")

nx_data = []
ny_data = []
nz_data = []

for i in range(len(a0_data)):
    # a0 a1 a2
    nx1,ny1,nz1 = locate_tag(a1_xyz[0],a1_xyz[1],a1_xyz[2],a1_data[i],a2_xyz[0],a2_xyz[1],a2_xyz[2],a2_data[i],a0_xyz[0],a0_xyz[1],a0_xyz[2],a0_data[i])
    # nx1,ny1,nz1 = locate_tag(P1, P2, P3, r1, r2, r3)
    # kn1,kn2 = trilateration([a0_xyz[0],a0_xyz[1],a0_xyz[2]], [a1_xyz[0],a1_xyz[1],a1_xyz[2]], [a2_xyz[0],a2_xyz[1],a2_xyz[2]], a0_data[i], a1_data[i], a2_data[i])
    kn1,kn2 = trilateration([a0_xyz[0],a0_xyz[1],a0_xyz[2]], [a1_xyz[0],a1_xyz[1],a1_xyz[2]], [a2_xyz[0],a2_xyz[1],a2_xyz[2]], a0_data_filtered[i], a1_data_filtered[i], a2_data_filtered[i])
    # print(kn1, kn2, sep="\t")
    # a1 a2 a3
    nx2,ny2,nz2 = locate_tag(a1_xyz[0],a1_xyz[1],a1_xyz[2],a1_data[i],a2_xyz[0],a2_xyz[1],a2_xyz[2],a2_data[i],a3_xyz[0],a3_xyz[1],a3_xyz[2],a3_data[i])
    # a2 a3 a0
    nx3,ny3,nz3 = locate_tag(a0_xyz[0],a0_xyz[1],a0_xyz[2],a0_data[i],a2_xyz[0],a2_xyz[1],a2_xyz[2],a2_data[i],a3_xyz[0],a3_xyz[1],a3_xyz[2],a3_data[i])
    # a3 a0 a1
    nx4,ny4,nz4 = locate_tag(a3_xyz[0],a3_xyz[1],a3_xyz[2],a3_data[i],a0_xyz[0],a0_xyz[1],a0_xyz[2],a0_data[i],a1_xyz[0],a1_xyz[1],a1_xyz[2],a1_data[i])

    nx = (nx1 + nx2 + nx3 + nx4) / 4
    ny = (ny1 + ny2 + ny3 + ny4) / 4
    nz = (nz1 + nz2 + nz3 + nz4) / 4
    # nx_data.append(nx1)
    # ny_data.append(ny1)
    # nz_data.append(nz1)
    nx_data.append(kn1[0])
    ny_data.append(kn1[1])
    nz_data.append(kn1[2])

# print(nx_data)
# print(ny_data)
# print(nz_data)

plt.figure()
plt.plot(nx_data, ny_data, 'o')
# plt.plot(ny_data, nz_data, 'o')
plt.xlim(-1, 6)
plt.ylim(-1, 6)
plt.title("UWB Tag tracking - filtered data")
plt.xlabel("x-axis")
plt.ylabel("y-axis")


# 3-D plot
plt.figure()
ax = plt.axes(projection ='3d')
ax.plot3D(nx_data, ny_data, nz_data, 'o')
ax.set_xlim([-1, 6])
ax.set_ylim([-1, 6])
ax.set_zlim([-1, 4])
ax.set_title("UWB 3D Tag tracking - filtered data")
ax.set_xlabel('x-axis', fontsize=12)
ax.set_ylabel('y-axis', fontsize=12)
ax.set_zlabel('z-axis', fontsize=12)


# ## Applying low pass butterworth filter and apply filter forward and backward using filtfilt
# fs = 30  # sampling rate, Hz
# b, a = scipy.signal.iirfilter(4, Wn=2.5, fs=fs, btype="low", ftype="butter")
# print(b, a, sep="\n")
# nx_data_filtered = scipy.signal.filtfilt(b, a, nx_data)
# ny_data_filtered = scipy.signal.filtfilt(b, a, ny_data)
# nz_data_filtered = scipy.signal.filtfilt(b, a, nz_data)

plt.figure()
plt.plot(t_data, nx_data, label="x-data")
# plt.plot(t_data, nx_data_filtered, alpha=0.8, lw=3, label="x-data filtered")
plt.plot(t_data, ny_data, label="y-data")
# plt.plot(t_data, ny_data_filtered, alpha=0.8, lw=3, label="y-data filtered")
plt.plot(t_data, nz_data, label="z-data")
# plt.plot(t_data, nz_data_filtered, alpha=0.8, lw=3, label="z-data filtered")
plt.xlabel("Time / s")
plt.ylabel("Amplitude")
plt.legend(loc="lower center", bbox_to_anchor=[0.5, 1], ncol=3, fontsize="smaller")


# # Plotting filtered data
# plt.figure()
# plt.plot(nx_data_filtered, ny_data_filtered, 'o')
# plt.xlim(-1, 6)
# plt.ylim(-1, 6)
# plt.title("UWB Tag tracking - filtered data")
# plt.xlabel("x-axis")
# plt.ylabel("y-axis")




plt.show()