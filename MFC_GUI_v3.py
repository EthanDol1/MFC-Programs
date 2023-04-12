# This is the most recent version of the MFC GUI
import pyfirmata as pf              # Arduino Communication & Control
from tkinter import *               # GUI
from tkinter import messagebox
from decimal import *               # Decimal / Floating Point
import time                         # Time & Clocking operations
import threading                    # Multithreading Arduino and GUI
from datetime import datetime       # Calendar Formatting
from pytz import timezone           # Timezone Formatting


tz = timezone('EST')

# Change this to the channel that the Arduino is connected to.
# Represents Arduino microcontroller
board = pf.Arduino('COM3')

# Starts control / event loop for Arduino 
it = pf.util.Iterator(board)
it.start()

# PWM channels are DC 3, 5, 6, 9, 10, 11.
# This pin will be the output voltage supply.
pinD3 = board.get_pin('d:3:p')
pinA5 = board.get_pin('a:5:i')

# GUI stuff.
# Creates the GUI Object
controlGui = Tk()
controlGui.title('Mass Flow GUI')

# Creates entry box and Label for it
manual_entry = Entry(controlGui, width = 30, borderwidth = 5)
manual_entry.grid(column=1,row=0)
manual_label = Label(controlGui, text = 'Manually set the output voltage:').grid(column=0,row=0)

v = 0
f = 0
kill_boolean = False

# Creates box to display current voltage on GUI
voltage_display = Label(controlGui, text = 'Current voltage: ' + str(v*5))
voltage_display.grid(column=2,row=4)

# Creates box to display the gas flow signal on GUI
flow_signal_display = Label(controlGui, text = 'Mass Flow Signal: ' + str(f*5))
flow_signal_display.grid(column=3,row=4)

# Updates the reading in voltage display in GUI
def vdisplay_update():
    voltage_display.config(text = 'Current voltage: ' + str(v*5) + 'V')
    controlGui.after(50, vdisplay_update)

# Updates the reading in flow signal display in GUI
def fsdisplay_update():
    global f
    f = pinA5.read()
    f = Decimal(f'{f:.2f}')
    flow_signal_display.config(text = 'Mass Flow Signal: ' + str(f*5) + 'V')

    controlGui.after(50, fsdisplay_update)
    
# IO output of current status : Writes flow signal to a file
def mfc_output():
    with open('mfc_output.txt', 'a') as file:
        file.write('Outflow signal is ' + str(f*5) + ' at time ' + str(datetime.now(tz)) + '\n')
    
    controlGui.after(3600000, mfc_output)

# Allows user to manually enter voltage to be written from Arduino
# Tethered to "Apply Manual Change" Button
def manual_update():
    global v
    global f
    if manual_entry.get() == '':
        messagebox.showerror('Mass Flow GUI','Manual Setting Input Error \nPlease enter a number between 0 and 5 (inclusive).')
    else:
        try:
            float(manual_entry.get())
            if 0 <= float(manual_entry.get()) <= 5:
                v = Decimal(manual_entry.get())/5
                manual_entry.delete(0,END)
                pinD3.write(v)
                f = pinA5.read()
            else:
                messagebox.showerror('Mass Flow GUI','Manual Setting Input Error \nPlease enter a number between 0 and 5 (inclusive).')
                manual_entry.delete(0,END)
        except:
            messagebox.showerror('Mass Flow GUI','Manual Setting Input Error \nPlease enter a number between 0 and 5 (inclusive).')
            manual_entry.delete(0,END)

# Creates button to apply user entered voltages sent from digital 
# pin 3 on Arduino
manual_button = Button(controlGui, text = 'Apply Manual Change', width=30, pady=20,\
    command = manual_update).\
    grid(column=1,row=1)

# Writes max / rail voltage (5V) to digital pin 3 on Arduino
# Tethered to "Apply Max Voltage" button
def max_voltage():
    global v
    v = 1
    pinD3.write(v)

# Creates button to apply rail voltage (5V)
max_button = Button(controlGui, text = 'Apply Max Voltage', width=30, pady=20, command = max_voltage).\
    grid(column=0,row=4)

# Writes floor voltage (0V) to digital pin 3 on Arduino
# Tethered to "Kill Voltage" Button
def floor_voltage():
    global v
    global kill_boolean
    kill_boolean = True
    v = 0
    pinD3.write(v)

# Closes / Destroys GUI
def close():
    with open('MFC.txt','w') as file:
        file.write(str(v))
    floor_voltage()
    controlGui.destroy()

# Creates killswitch button for voltage
floor_button = Button(controlGui, text = 'Kill Voltage', width=30, pady=20, command = floor_voltage).\
    grid(column=1,row=4)

# Creates killswitch button for GUI
close_button = Button(controlGui, text = 'Close GUI', width=30, pady=20, command = close).\
    grid(column=4,row=4)

# Code for creating a gradual linear change in the output voltage

# Start voltage entry
start_voltage = Entry(controlGui, width = 30, borderwidth=5)
start_voltage.grid(column=3,row=0)

sv_label = Label(controlGui, text = 'Set the start voltage:').grid(column=2,row=0)

# End voltage entry
end_voltage = Entry(controlGui, width=30, borderwidth=5)
end_voltage.grid(column=3,row=1)

ev_label = Label(controlGui, text = 'Set the end voltage:').grid(column=2, row=1)

# Step size entry
step_size = Entry(controlGui, width=30, borderwidth=5)
step_size.grid(column=3,row=2)

ss_label = Label(controlGui, text = 'Set the voltage step size:').grid(column=2, row=2)

# Time between steps entry
time_between = Entry(controlGui, width=30, borderwidth=5)
time_between.grid(column=3,row=3)

tb_label = Label(controlGui, text = 'Set the time (s) between steps:').grid(column=2,row=3)

def x1_get():
    global b1
    try:
        if 0 <= Decimal(start_voltage.get()) <= 5:
            b1 = True
            return Decimal(start_voltage.get())
        else:
            b1 = False
            messagebox.showerror('Mass Flow GUI','Start Voltage Input Error \nPlease enter a number between 0 and 5 (inclusive).')
    except:
        b1 = False
        messagebox.showerror('Mass Flow GUI','Start Voltage Input Error \nPlease enter a number between 0 and 5 (inclusive).')

def x2_get():
    global b2
    try:
        if 0 <= Decimal(end_voltage.get()) <= 5:
            b2 = True
            return Decimal(end_voltage.get())
        else:
            b2 = False
            messagebox.showerror('Mass Flow GUI','End Voltage Input Error \nPlease enter a number between 0 and 5 (inclusive).')
    except:
        b2 = False
        messagebox.showerror('Mass Flow GUI','End Voltage Input Error \nPlease enter a number between 0 and 5 (inclusive).')

def x3_get():
    global b3
    try:
        if 0 <= Decimal(step_size.get()) <= 5:
            b3 = True
            return Decimal(step_size.get())
        else:
            b3 = False
            messagebox.showerror('Mass Flow GUI','Step Size Input Error \nPlease enter a number between 0 and 5 (inclusive).')
    except:
        b3 = False
        messagebox.showerror('Mass Flow GUI','Step Size Input Error \nPlease enter a number between 0 and 5 (inclusive).')

def x4_get():
    global b4
    try:
        if 0 <= float(time_between.get()):
            b4 = True
            return float(time_between.get())
        else:
            b4 = False
            messagebox.showerror('Mass Flow GUI','Time Between Steps Input Error \nPlease enter a positive number.')
    except:
        b4 = False
        messagebox.showerror('Mass Flow GUI','Time Between Steps Input Error \nPlease enter a positive number.')

# Applies a voltage change given some parameters
# sv : Start Voltage
# ev : End Voltage
# ss : Step Size
# tb : Time Between 
def vChange(sv,ev,ss,tb):
    global v
    deltaV = ev - v
    if kill_boolean == False:
        if deltaV == 0:
            messagebox.showinfo('Mass Flow GUI','The end voltage has been reached')
            return
        if deltaV > 0:
            if v + ss > 1:
                messagebox.showinfo('Mass Flow GUI','The end voltage has been reached')
                return
            else:
                v += ss
                pinD3.write(v)
                time.sleep(tb)
        if deltaV < 0:
            if v - ss < 0:
                messagebox.showinfo('Mass Flow GUI','The end voltage has been reached')
                return
            else:
                v -= ss
                pinD3.write(v)
                time.sleep(tb)
        controlGui.after(20, vChange, sv, ev, ss, tb)
    else:
        return

# Applies a linear voltage increase or decrease
# given some parameters
def linear_voltage():
    global v
    global b1
    global kill_boolean

    kill_boolean = False

    if start_voltage.get() == '':
        if messagebox.askyesno('Mass Flow GUI',\
            """Are you sure you want to leave the start voltage as its default
            setting? \nThe default setting is whatever the current voltage is."""):
            sv = v
            b1 = True
        else:
            b1 = False
            return
    else:
        sv = x1_get()/5
        v = sv

    ev = x2_get()/5
    ss = x3_get()/5
    tb = x4_get()
    
    if b1 and b2 and b3 and b4:

        start_voltage.delete(0,END)
        end_voltage.delete(0,END)
        step_size.delete(0,END)
        time_between.delete(0,END)

        pinD3.write(v)

        vChange(sv,ev,ss,tb)
    else:
        return

linear_auto_button = Button(controlGui, text = 'Apply Automatic Change \n(linear increase/decrease)', width=30, pady=20,\
    command = linear_voltage).grid(column=4,row=1)

# Displays useful information about how to use the GUI
def help():
    messagebox.showinfo('Mass Flow GUI',
        """Here is some info on how the GUI works.\nThe output voltage from the Arduino
        Uno varies from 0 - 5V.\n1) The Apply Max Voltage button instructs the Arduino 
        to output 5V.\n2) The Kill Voltage button instructs the Arduino to output 0V.\n3) 
        The Apply Manual Change button takes the value enterred into the entry slot above 
        the button and instructs the Arduino to output that specific voltage.\n4) The Apply 
        Linear Change button takes in 4 entries as parameters: the start voltage, the end 
        voltage, the step size, and the time between steps. This button has the effect of 
        an automated gradual change in voltage depending upon the parameters you enter in.\n
        a) The start voltage entry and end voltage entry instruct the Arduino on what 
        voltages you would like to start and end at. The start voltage does not have to 
        be lower than the end voltage, i.e. you may use this button to go up or down in 
        voltage. Because of discrepancies between the voltages written to the Arduino 
        and the voltages that it actually outputs, there is an error in the display voltage 
        of approximately +/- 1 step.\n    b) The step size entry instructs the Arduino on 
        how big of steps to take to get from the start voltage to the end voltage, e.g. 
        with a start voltage of 0, an end voltage of 1, and a step size of 0.1, the 
        Arduino would take 10 steps incrementing like 0.1 .. 0.2 .. 0.3 .. and so on. 
        Additionally, if you wish to go down in voltage from a higher start voltage to 
        a lower end voltage, you should still enter in a positive-valued step size.\n   
        c) The time between entry instructs the Arduino on how many seconds you would 
        like it to wait after performing one step before it performs the next step. 
        20 milliseconds is added on to this time between in order for the GUI to run smoothly.""")

# Help Button in GUI 
# Displays relevant opeartion information when clicked
help_button = Button(controlGui, text = 'Help', width = 30, pady=20,\
    command = help).grid(column=0,row=3)

# Starts loop for voltage display 
# This method is a multithread target
def vdUpdate_initial():
    controlGui.after(100, fsdisplay_update)

# Starts loop for flow signal display
# This method is a multithread target
def fdUpdate_initial():
    controlGui.after(100, vdisplay_update)

def mfcOutput_initial():
    controlGui.after(100, mfc_output)

t2 = threading.Thread(target=vdUpdate_initial)
t3 = threading.Thread(target=fdUpdate_initial)
#t4 = threading.Thread(target=mfcOutput_initial)

t2.start()
t3.start()
#t4.start()

controlGui.mainloop()

#The End :)