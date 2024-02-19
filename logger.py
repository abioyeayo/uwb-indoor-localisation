# ***************************************************************
# Author: Ayo Abioye (a.o.abioye@soton.ac.uk)
# Date: Thursday 1st February 2024
# Usage:
#    Program to fetch tag location, log to file, and plot
# ***************************************************************

import sys,tty,termios
import serial
from datetime import datetime
import requests
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Defining serial connection parameters
#port = "COM6"
# port = "/dev/ttyACM0"
port = "/dev/cu.usbmodem52870207291"
baud = 115200

ser = serial.Serial(port, baud, timeout=1)
filename = 't0_log_' + datetime.now().strftime("%Y%m%d%H%M%S") + '.txt'
f = open(filename,'a')
f.write(datetime.utcnow().isoformat() + '\n')
f.flush()

# open the serial port
if ser.isOpen():
     #print(ser.name + ' is open...')
     datastring = ser.name + ' is open...' + '\n'
     print (datastring)
     f.write(datastring)
     f.flush()

# while True:
#     while ser.in_waiting:
#         datastring = datetime.utcnow().isoformat() + '\t' + ser.readline().decode('ascii')
#         print (datastring)
#         f.write(datastring)
#         f.flush()							# Force system write to disk
#         #f.close()

x_data = [0.0]
y_data = [0.0] 
t_data = [0.0]    # time data
t_init = datetime.utcnow()                                                   
# fig = plt.figure()                                      # Create Matplotlib plots fig is the 'higher level' plot window
# ax = fig.add_subplot(111)                               # Add subplot to main fig window
# ax.plot(x_data,y_data,'o')

fig, axs = plt.subplots(2)
fig.suptitle("UWB tag tracking")                        # Set title of figure



def animate(i, f, ser, x_data, y_data, t_data, t_init):
    if ser.in_waiting:
        t0_string = ser.readline().decode('ascii') # Decode receive Arduino data as a formatted string
        #print(i)                                           # 'i' is a incrementing variable based upon frames = x argument

        datastring = datetime.utcnow().isoformat() + '\t' + t0_string
        print (datastring)
        f.write(datastring)
        f.flush()							# Force system write to disk
        #f.close()

        # time difference calculation
        t_diff = datetime.utcnow() - t_init
        t_diff_sec = int(t_diff.total_seconds() * 1000) # difference in milliseconds


        data_col = t0_string.split()
        if len(data_col) == 3:
            if data_col[0] == "(x,y)":
                if len(data_col[2]) < 14 and len(data_col[2]) > 10:
                    data_str = data_col[2].replace('(', '').replace(')', '')
                    data_str_array = data_str.split(',')
                    x_data.append(float(data_str_array[0]))
                    y_data.append(float(data_str_array[1]))
                    t_data.append(t_diff_sec)

        # if t0_string[0:5] == "(x,y)":
        #     data_str = t0_string[9:-3]
        #     print(data_str)
        #     data_str_array = data_str.split(',')
        #     x_data.append(float(data_str_array[0]))
        #     y_data.append(float(data_str_array[1]))
        #     t_data.append(t_diff_sec)

    axs[0].clear()                                          # Clear last data frame
    axs[0].plot(x_data,y_data,'o')                                   # Plot new data frame
    axs[0].set_xlim([-1, 3])
    axs[0].set_ylim([-1, 2])
    axs[0].set_xlabel("x-axis")                              # Set title of x axis 
    axs[0].set_ylabel("y-axis")                              # Set title of y axis 

    axs[1].clear()
    axs[1].plot(t_data,x_data)
    axs[1].plot(t_data,y_data)

    # ax.clear()                                          # Clear last data frame
    # # ax.plot(x_data,y_data,'o')                                   # Plot new data frame
    # ax.plot(t_data,x_data)
    # ax.plot(t_data,y_data)
    # # ax.set_xlim([-1, 3])
    # # ax.set_ylim([-1, 2])
    # ax.set_title("UWB tag tracking")                        # Set title of figure
    # # ax.set_xlabel("x-axis")                              # Set title of x axis 
    # # ax.set_ylabel("y-axis")                              # Set title of y axis 
    


ani = animation.FuncAnimation(fig, animate, frames=100, fargs=(f, ser, x_data, y_data, t_data, t_init), interval=100) 

plt.show()                                              # Keep Matplotlib plot persistent on screen until it is closed
ser.close()   


# # Strips the newline character
# for data_line in data_lines:
#     if data_line[0:5] == "(x,y)":
#         # print(data_line)
#         data_str = data_line[9:-2]
#         data_str_array = data_str.split(',')
#         x_data.append(float(data_str_array[0]))
#         y_data.append(float(data_str_array[1]))

# # # print(x_data)
# # # print(y_data)

# # plt.plot(x_data, y_data, 'o')
# # plt.xlim(-1, 3)
# # plt.ylim(-1, 2)
# # plt.title("UWB Tag tracking")
# # plt.xlabel("x-axis")
# # plt.ylabel("y-axis")
# # plt.show()

# # plt.scatter(2, 5)

# fig, ax = plt.subplots()
# point, = ax.plot(x_data, y_data, 'o')
# line, = ax.plot(x_data, y_data)

# def update(num, x_data, y_data, point, line):
#     point.set_data(x_data[num], y_data[num])
#     line.set_data(x_data[:num], y_data[:num])
#     # if num > 3 :
#     #     line.set_data(x_data[num-3:num], y_data[num-3:num])
#     # else:
#     #     line.set_data(x_data[:num], y_data[:num])
#     return line,

# ani = animation.FuncAnimation(fig, update, len(x_data), interval=100, 
#                               fargs=[x_data, y_data, point, line], blit=True)
# # ani.save('animation_drawing.gif', writer='imagemagick', fps=60)
# plt.show()