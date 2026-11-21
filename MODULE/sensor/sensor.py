import serial
import json
import time
import matplotlib .pyplot as plt
from matplotlib .animation import FuncAnimation
import matplotlib .dates as mdates
from datetime import datetime
import numpy as np
from collections import deque
import threading
import argparse
import os
import tkinter as tk
from tkinter import ttk
from matplotlib .backends .backend_tkagg import FigureCanvasTkAgg ,NavigationToolbar2Tk
import matplotlib .style as mplstyle
mplstyle .use ('dark_background')
DEFAULT_PORT ='COM4'
DEFAULT_BAUDRATE =9600
MAX_DATA_POINTS =100
data ={
'co2':deque (maxlen =MAX_DATA_POINTS ),
'temperature':deque (maxlen =MAX_DATA_POINTS ),
'humidity':deque (maxlen =MAX_DATA_POINTS ),
'pressure':deque (maxlen =MAX_DATA_POINTS ),
'soil_moisture':deque (maxlen =MAX_DATA_POINTS ),
'relay1':deque (maxlen =MAX_DATA_POINTS ),
'relay2':deque (maxlen =MAX_DATA_POINTS ),
'relay3':deque (maxlen =MAX_DATA_POINTS ),
'relay4':deque (maxlen =MAX_DATA_POINTS ),
'uptime':deque (maxlen =MAX_DATA_POINTS ),
'timestamps':deque (maxlen =MAX_DATA_POINTS )
}
running =True
connected =False
ser =None
COLORS ={
'co2':'#FF5252',
'temperature':'#42A5F5',
'humidity':'#66BB6A',
'pressure':'#AB47BC',
'soil_moisture':'#FFA726',
'relay1':'#E57373',
'relay2':'#81C784',
'relay3':'#64B5F6',
'relay4':'#FFD54F',
'background':'#263238',
'text':'#ECEFF1',
'grid':'#455A64'
}
def parse_sensor_data (line ,status_label ,co2_value ,temp_value ,humidity_value ,pressure_value ,soil_value ):
    try :
        sensor_data =json .loads (line )
        timestamp =datetime .now ()
        data ['co2'].append (sensor_data .get ('co2',0 ))
        data ['temperature'].append (sensor_data .get ('temp',0 ))
        data ['humidity'].append (sensor_data .get ('humidity',0 ))
        data ['pressure'].append (sensor_data .get ('pressure',0 ))
        data ['soil_moisture'].append (sensor_data .get ('soil',0 ))
        data ['relay1'].append (1 if sensor_data .get ('relay1')==True else 0 )
        data ['relay2'].append (1 if sensor_data .get ('relay2')==True else 0 )
        data ['relay3'].append (1 if sensor_data .get ('relay3')==True else 0 )
        data ['relay4'].append (1 if sensor_data .get ('relay4')==True else 0 )
        data ['uptime'].append (sensor_data .get ('uptime',0 ))
        data ['timestamps'].append (timestamp )
        status_text =f"Status: Connected | Last Update: {timestamp .strftime ('%H:%M:%S')}"
        status_label .config (text =status_text )
        co2_value .config (text =f"{sensor_data .get ('co2',0 )} ppm")
        temp_value .config (text =f"{sensor_data .get ('temp',0 ):.1f} °C")
        humidity_value .config (text =f"{sensor_data .get ('humidity',0 ):.1f} %")
        pressure_value .config (text =f"{sensor_data .get ('pressure',0 ):.1f} hPa")
        soil_value .config (text =f"{sensor_data .get ('soil',0 )} %")
        co2_level =sensor_data .get ('co2',0 )
        if co2_level <800 :
            co2_quality_color ="#66BB6A"
        elif co2_level <1200 :
            co2_quality_color ="#FFA726"
        elif co2_level <1500 :
            co2_quality_color ="#F57C00"
        else :
            co2_quality_color ="#D32F2F"
        co2_value .config (foreground =co2_quality_color )
        return True
    except json .JSONDecodeError :
        status_label .config (text =f"Error parsing JSON: {line }")
        return False
    except Exception as e :
        status_label .config (text =f"Error: {e }")
        return False
def read_serial_data (port ,baudrate ,status_label ,co2_value ,temp_value ,humidity_value ,pressure_value ,soil_value ,relay_indicators ):
    global connected ,ser ,running
    try :
        ser =serial .Serial (port ,baudrate ,timeout =1 )
        connected =True
        status_label .config (text =f"Connected to {port } at {baudrate } baud")
        while running :
            if ser .in_waiting >0 :
                line =ser .readline ().decode ('utf-8').strip ()
                if line :
                    parse_sensor_data (line ,status_label ,co2_value ,temp_value ,humidity_value ,pressure_value ,soil_value )
                    if data ['relay1']and len (data ['relay1'])>0 :
                        relay_indicators [0 ].config (background ="#66BB6A"if data ['relay1'][-1 ]else "#455A64")
                    if data ['relay2']and len (data ['relay2'])>0 :
                        relay_indicators [1 ].config (background ="#66BB6A"if data ['relay2'][-1 ]else "#455A64")
                    if data ['relay3']and len (data ['relay3'])>0 :
                        relay_indicators [2 ].config (background ="#66BB6A"if data ['relay3'][-1 ]else "#455A64")
                    if data ['relay4']and len (data ['relay4'])>0 :
                        relay_indicators [3 ].config (background ="#66BB6A"if data ['relay4'][-1 ]else "#455A64")
            time .sleep (0.1 )
    except serial .SerialException as e :
        status_label .config (text =f"Serial connection error: {e }")
        connected =False
    except Exception as e :
        status_label .config (text =f"Error: {e }")
    finally :
        if ser and ser .is_open :
            ser .close ()
        connected =False
        status_label .config (text ="Disconnected")
def toggle_relay (relay_num ):
    if ser and ser .is_open :
        cmd =str (relay_num )
        ser .write (cmd .encode ('utf-8'))
        return True
    return False
def update_plots (frame ,fig ,axes ):
    if not data ['timestamps']or len (data ['timestamps'])==0 :
        return
    ax_co2 ,ax_temp ,ax_humidity ,ax_pressure ,ax_soil ,ax_relay =axes
    timestamps =list (data ['timestamps'])
    for ax in axes :
        ax .clear ()
    ax_co2 .plot (timestamps ,data ['co2'],color =COLORS ['co2'],linewidth =2 )
    ax_co2 .set_title ('Уровень CO2',color =COLORS ['text'])
    ax_co2 .set_ylabel ('PPM',color =COLORS ['text'])
    ax_co2 .grid (True ,color =COLORS ['grid'],linestyle ='--',alpha =0.7 )
    ax_co2 .tick_params (colors =COLORS ['text'])
    ax_co2 .xaxis .set_major_formatter (mdates .DateFormatter ('%H:%M:%S'))
    ax_temp .plot (timestamps ,data ['temperature'],color =COLORS ['temperature'],linewidth =2 )
    ax_temp .set_title ('Temperature',color =COLORS ['text'])
    ax_temp .set_ylabel ('°C',color =COLORS ['text'])
    ax_temp .grid (True ,color =COLORS ['grid'],linestyle ='--',alpha =0.7 )
    ax_temp .tick_params (colors =COLORS ['text'])
    ax_temp .xaxis .set_major_formatter (mdates .DateFormatter ('%H:%M:%S'))
    ax_humidity .plot (timestamps ,data ['humidity'],color =COLORS ['humidity'],linewidth =2 )
    ax_humidity .set_title ('Humidity',color =COLORS ['text'])
    ax_humidity .set_ylabel ('%',color =COLORS ['text'])
    ax_humidity .grid (True ,color =COLORS ['grid'],linestyle ='--',alpha =0.7 )
    ax_humidity .tick_params (colors =COLORS ['text'])
    ax_humidity .xaxis .set_major_formatter (mdates .DateFormatter ('%H:%M:%S'))
    ax_pressure .plot (timestamps ,data ['pressure'],color =COLORS ['pressure'],linewidth =2 )
    ax_pressure .set_title ('Pressure',color =COLORS ['text'])
    ax_pressure .set_ylabel ('hPa',color =COLORS ['text'])
    ax_pressure .grid (True ,color =COLORS ['grid'],linestyle ='--',alpha =0.7 )
    ax_pressure .tick_params (colors =COLORS ['text'])
    ax_pressure .xaxis .set_major_formatter (mdates .DateFormatter ('%H:%M:%S'))
    ax_soil .plot (timestamps ,data ['soil_moisture'],color =COLORS ['soil_moisture'],linewidth =2 )
    ax_soil .set_title ('Влажность почвы',color =COLORS ['text'])
    ax_soil .set_ylabel ('%',color =COLORS ['text'])
    ax_soil .grid (True ,color =COLORS ['grid'],linestyle ='--',alpha =0.7 )
    ax_soil .tick_params (colors =COLORS ['text'])
    ax_soil .xaxis .set_major_formatter (mdates .DateFormatter ('%H:%M:%S'))
    ax_relay .plot (timestamps ,data ['relay1'],color =COLORS ['relay1'],linewidth =2 ,label ='Реле 1')
    ax_relay .plot (timestamps ,data ['relay2'],color =COLORS ['relay2'],linewidth =2 ,label ='Реле 2')
    ax_relay .plot (timestamps ,data ['relay3'],color =COLORS ['relay3'],linewidth =2 ,label ='Реле 3')
    ax_relay .plot (timestamps ,data ['relay4'],color =COLORS ['relay4'],linewidth =2 ,label ='Реле 4')
    ax_relay .set_title ('Состояния реле',color =COLORS ['text'])
    ax_relay .set_ylabel ('State',color =COLORS ['text'])
    ax_relay .set_ylim (-0.1 ,1.1 )
    ax_relay .legend (loc ='верхний левый')
    ax_relay .grid (True ,color =COLORS ['grid'],linestyle ='--',alpha =0.7 )
    ax_relay .tick_params (colors =COLORS ['text'])
    ax_relay .xaxis .set_major_formatter (mdates .DateFormatter ('%H:%M:%S'))
    for ax in axes :
        plt .setp (ax .get_xticklabels (),rotation =45 ,ha ='right')
    fig .tight_layout ()
def create_gui (port ,baud ):
    global running ,ser ,connected
    root =tk .Tk ()
    root .title ("Мультисенсорная система мониторинга")
    root .geometry ("1280x900")
    root .configure (bg =COLORS ['background'])
    style =ttk .Style ()
    style .theme_use ('clam')
    style .configure ("TFrame",background =COLORS ['background'])
    style .configure ("TLabel",background =COLORS ['background'],foreground =COLORS ['text'])
    style .configure ("TButton",background ="#455A64",foreground =COLORS ['text'])
    main_frame =ttk .Frame (root )
    main_frame .pack (fill =tk .BOTH ,expand =True ,padx =10 ,pady =10 )
    status_frame =ttk .Frame (main_frame )
    status_frame .pack (fill =tk .X ,pady =(0 ,10 ))
    status_label =ttk .Label (status_frame ,text ="Initializing...",font =("Arial",10 ))
    status_label .pack (side =tk .LEFT )
    plot_frame =ttk .Frame (main_frame )
    plot_frame .pack (fill =tk .BOTH ,expand =True )
    fig =plt .figure (figsize =(12 ,8 ))
    fig .patch .set_facecolor (COLORS ['background'])
    ax_co2 =fig .add_subplot (3 ,2 ,1 )
    ax_temp =fig .add_subplot (3 ,2 ,2 )
    ax_humidity =fig .add_subplot (3 ,2 ,3 )
    ax_pressure =fig .add_subplot (3 ,2 ,4 )
    ax_soil =fig .add_subplot (3 ,2 ,5 )
    ax_relay =fig .add_subplot (3 ,2 ,6 )
    for ax in [ax_co2 ,ax_temp ,ax_humidity ,ax_pressure ,ax_soil ,ax_relay ]:
        ax .set_facecolor (COLORS ['background'])
        ax .spines ['bottom'].set_color (COLORS ['text'])
        ax .spines ['top'].set_color (COLORS ['text'])
        ax .spines ['left'].set_color (COLORS ['text'])
        ax .spines ['right'].set_color (COLORS ['text'])
    canvas =FigureCanvasTkAgg (fig ,master =plot_frame )
    canvas .get_tk_widget ().pack (fill =tk .BOTH ,expand =True )
    toolbar =NavigationToolbar2Tk (canvas ,plot_frame )
    toolbar .update ()
    canvas .get_tk_widget ().pack (fill =tk .BOTH ,expand =True )
    control_frame =ttk .Frame (main_frame )
    control_frame .pack (fill =tk .X ,pady =(10 ,0 ))
    values_frame =ttk .Frame (control_frame )
    values_frame .pack (side =tk .LEFT ,fill =tk .Y )
    co2_frame =ttk .Frame (values_frame )
    co2_frame .pack (side =tk .LEFT ,padx =10 )
    ttk .Label (co2_frame ,text ="CO2:",font =("Arial",12 )).pack (side =tk .LEFT )
    co2_value =ttk .Label (co2_frame ,text ="--",font =("Arial",12 ,"bold"))
    co2_value .pack (side =tk .LEFT ,padx =(5 ,0 ))
    temp_frame =ttk .Frame (values_frame )
    temp_frame .pack (side =tk .LEFT ,padx =10 )
    ttk .Label (temp_frame ,text ="Temp:",font =("Arial",12 )).pack (side =tk .LEFT )
    temp_value =ttk .Label (temp_frame ,text ="--",font =("Arial",12 ,"bold"))
    temp_value .pack (side =tk .LEFT ,padx =(5 ,0 ))
    humidity_frame =ttk .Frame (values_frame )
    humidity_frame .pack (side =tk .LEFT ,padx =10 )
    ttk .Label (humidity_frame ,text ="Humidity:",font =("Arial",12 )).pack (side =tk .LEFT )
    humidity_value =ttk .Label (humidity_frame ,text ="--",font =("Arial",12 ,"bold"))
    humidity_value .pack (side =tk .LEFT ,padx =(5 ,0 ))
    pressure_frame =ttk .Frame (values_frame )
    pressure_frame .pack (side =tk .LEFT ,padx =10 )
    ttk .Label (pressure_frame ,text ="Pressure:",font =("Arial",12 )).pack (side =tk .LEFT )
    pressure_value =ttk .Label (pressure_frame ,text ="--",font =("Arial",12 ,"bold"))
    pressure_value .pack (side =tk .LEFT ,padx =(5 ,0 ))
    soil_frame =ttk .Frame (values_frame )
    soil_frame .pack (side =tk .LEFT ,padx =10 )
    ttk .Label (soil_frame ,text ="Soil:",font =("Arial",12 )).pack (side =tk .LEFT )
    soil_value =ttk .Label (soil_frame ,text ="--",font =("Arial",12 ,"bold"))
    soil_value .pack (side =tk .LEFT ,padx =(5 ,0 ))
    relay_frame =ttk .Frame (control_frame )
    relay_frame .pack (side =tk .RIGHT ,fill =tk .Y )
    relay_indicators =[]
    for i in range (1 ,5 ):
        relay_ctrl_frame =ttk .Frame (relay_frame )
        relay_ctrl_frame .pack (side =tk .LEFT ,padx =10 )
        indicator =tk .Label (relay_ctrl_frame ,width =2 ,bg ="#455A64")
        indicator .pack (side =tk .LEFT ,padx =(0 ,5 ))
        relay_indicators .append (indicator )
        relay_btn =tk .Button (
        relay_ctrl_frame ,
        text =f"Relay {i }",
        command =lambda r =i :toggle_relay (r ),
        bg ="#546E7A",
        fg =COLORS ['text'],
        activebackground ="#78909C",
        activeforeground =COLORS ['text'],
        padx =10
        )
        relay_btn .pack (side =tk .LEFT )
    serial_thread =threading .Thread (
    target =read_serial_data ,
    args =(port ,baud ,status_label ,co2_value ,temp_value ,humidity_value ,pressure_value ,soil_value ,relay_indicators )
    )
    serial_thread .daemon =True
    serial_thread .start ()
    ani =FuncAnimation (fig ,update_plots ,
    fargs =(fig ,(ax_co2 ,ax_temp ,ax_humidity ,ax_pressure ,ax_soil ,ax_relay )),
    interval =1000 )
    def on_closing ():
        global running
        running =False
        root .destroy ()
    root .protocol ("WM_DELETE_WINDOW",on_closing )
    root .mainloop ()
    running =False
    if ser and ser .is_open :
        ser .close ()
def main ():
    global running
    parser =argparse .ArgumentParser (description ='Мультисенсорная система мониторинга')
    parser .add_argument ('-p','--port',help =f'Serial port (default: {DEFAULT_PORT })',default =DEFAULT_PORT )
    parser .add_argument ('-b','--baud',help =f'Baud rate (default: {DEFAULT_BAUDRATE })',type =int ,default =DEFAULT_BAUDRATE )
    parser .add_argument ('-l','--list',help ='Список доступных последовательных портов',action ='store_true')
    args =parser .parse_args ()
    if args .list :
        import serial .tools .list_ports
        ports =list (serial .tools .list_ports .comports ())
        if ports :
            print ("Доступные последовательные порты:")
            for port in ports :
                print (f"  {port .device }: {port .description }")
        else :
            print ("Последовательные порты не найдены!")
        return
    print (f"Starting Multi-Sensor Monitoring System")
    print (f"Connecting to {args .port } at {args .baud } baud...")
    create_gui (args .port ,args .baud )
    print ("Программа прекращена.")
if __name__ =="__main__":
    main ()