import tkinter as tk
from tkinter import ttk ,messagebox
import serial
import threading
import time
import argparse
DEFAULT_PORT ='COM4'
DEFAULT_BAUDRATE =9600
ser =None
connected =False
running =True
COLORS ={
'background':'#263238',
'text':'#ECEFF1',
'button_bg':'#455A64',
'button_active':'#78909C',
'on':'#66BB6A',
'off':'#E53935',
'highlight':'#29B6F6',
'frame_bg':'#37474F'
}
class RelayControlApp :
    def __init__ (self ,root ,port ,baudrate ):
        self .root =root
        self .port =port
        self .baudrate =baudrate
        self .relay_states =[False ,False ,False ,False ]
        self .setup_ui ()
        self .start_serial_thread ()
    def setup_ui (self ):
        self .root .title ("Релейная система управления")
        self .root .geometry ("800x600")
        self .root .configure (bg =COLORS ['background'])
        style =ttk .Style ()
        style .theme_use ('clam')
        style .configure ("TFrame",background =COLORS ['background'])
        style .configure ("TLabel",background =COLORS ['background'],foreground =COLORS ['text'],font =("Arial",12 ))
        style .configure ("TButton",background =COLORS ['button_bg'],foreground =COLORS ['text'],font =("Arial",12 ))
        main_frame =ttk .Frame (self .root )
        main_frame .pack (fill =tk .BOTH ,expand =True ,padx =20 ,pady =20 )
        header_frame =ttk .Frame (main_frame )
        header_frame .pack (fill =tk .X ,pady =(0 ,20 ))
        title_label =ttk .Label (header_frame ,text ="Релейная система управления",font =("Arial",24 ,"bold"))
        title_label .pack (side =tk .LEFT )
        self .status_label =ttk .Label (header_frame ,text ="Статус: Отключено",font =("Arial",12 ))
        self .status_label .pack (side =tk .RIGHT )
        relay_frame =tk .Frame (main_frame ,bg =COLORS ['frame_bg'],bd =2 ,relief =tk .GROOVE )
        relay_frame .pack (fill =tk .BOTH ,expand =True ,pady =10 )
        relay_header =ttk .Label (relay_frame ,text ="Релейное управление",font =("Arial",16 ,"bold"))
        relay_header .pack (pady =10 )
        self .relay_controls =[]
        for i in range (4 ):
            relay_control_frame =tk .Frame (relay_frame ,bg =COLORS ['frame_bg'],pady =10 )
            relay_control_frame .pack (fill =tk .X ,padx =20 )
            relay_label =ttk .Label (relay_control_frame ,text =f"Relay {i +1 }",font =("Arial",14 ))
            relay_label .pack (side =tk .LEFT ,padx =10 )
            state_indicator =tk .Canvas (relay_control_frame ,width =30 ,height =30 ,bg =COLORS ['frame_bg'],
            highlightthickness =0 )
            state_indicator .pack (side =tk .LEFT ,padx =10 )
            indicator_circle =state_indicator .create_oval (5 ,5 ,25 ,25 ,fill =COLORS ['off'])
            button_frame =tk .Frame (relay_control_frame ,bg =COLORS ['frame_bg'])
            button_frame .pack (side =tk .RIGHT )
            toggle_button =tk .Button (button_frame ,text ="TOGGLE",bg =COLORS ['button_bg'],fg =COLORS ['text'],
            activebackground =COLORS ['button_active'],activeforeground =COLORS ['text'],
            command =lambda idx =i :self .toggle_relay (idx ))
            toggle_button .pack (side =tk .LEFT ,padx =5 )
            self .relay_controls .append ({
            'label':relay_label ,
            'indicator':state_indicator ,
            'circle':indicator_circle ,
            'toggle_button':toggle_button
            })
        all_control_frame =tk .Frame (relay_frame ,bg =COLORS ['frame_bg'],pady =20 )
        all_control_frame .pack (fill =tk .X ,padx =20 )
        all_on_button =tk .Button (all_control_frame ,text ="ВСЕ ВКЛЮЧЕНО",bg =COLORS ['button_bg'],fg =COLORS ['text'],
        activebackground =COLORS ['button_active'],activeforeground =COLORS ['text'],
        font =("Arial",12 ,"bold"),width =15 ,height =2 ,
        command =self .all_on )
        all_on_button .pack (side =tk .LEFT ,padx =10 ,expand =True )
        all_off_button =tk .Button (all_control_frame ,text ="ВСЕ ВЫКЛ.",bg =COLORS ['button_bg'],fg =COLORS ['text'],
        activebackground =COLORS ['button_active'],activeforeground =COLORS ['text'],
        font =("Arial",12 ,"bold"),width =15 ,height =2 ,
        command =self .all_off )
        all_off_button .pack (side =tk .RIGHT ,padx =10 ,expand =True )
        log_frame =tk .Frame (main_frame ,bg =COLORS ['frame_bg'],bd =2 ,relief =tk .GROOVE )
        log_frame .pack (fill =tk .BOTH ,expand =True ,pady =10 )
        log_header =ttk .Label (log_frame ,text ="Журнал команд",font =("Arial",14 ,"bold"))
        log_header .pack (pady =5 )
        self .log_text =tk .Text (log_frame ,bg =COLORS ['background'],fg =COLORS ['text'],
        font =("Consolas",10 ),height =6 )
        self .log_text .pack (fill =tk .BOTH ,expand =True ,padx =10 ,pady =5 )
        self .log_text .config (state =tk .DISABLED )
        scrollbar =ttk .Scrollbar (self .log_text ,command =self .log_text .yview )
        scrollbar .pack (side =tk .RIGHT ,fill =tk .Y )
        self .log_text .config (yscrollcommand =scrollbar .set )
        connection_frame =ttk .Frame (main_frame )
        connection_frame .pack (fill =tk .X ,pady =10 )
        port_label =ttk .Label (connection_frame ,text =f"Port: {self .port }",font =("Arial",10 ))
        port_label .pack (side =tk .LEFT )
        baud_label =ttk .Label (connection_frame ,text =f"Baud rate: {self .baudrate }",font =("Arial",10 ))
        baud_label .pack (side =tk .LEFT ,padx =20 )
        refresh_button =tk .Button (connection_frame ,text ="Обновить статус",bg =COLORS ['button_bg'],fg =COLORS ['text'],
        activebackground =COLORS ['button_active'],activeforeground =COLORS ['text'],
        command =self .request_status )
        refresh_button .pack (side =tk .RIGHT )
        self .root .protocol ("WM_DELETE_WINDOW",self .on_closing )
    def start_serial_thread (self ):
        self .serial_thread =threading .Thread (target =self .serial_worker )
        self .serial_thread .daemon =True
        self .serial_thread .start ()
    def serial_worker (self ):
        global ser ,connected ,running
        try :
            ser =serial .Serial (self .port ,self .baudrate ,timeout =1 )
            connected =True
            self .log_message (f"Connected to {self .port } at {self .baudrate } baud")
            self .update_status_label (f"Connected to {self .port }")
            time .sleep (2 )
            self .request_status ()
            while running :
                if ser and ser .is_open and ser .in_waiting >0 :
                    line =ser .readline ().decode ('utf-8').strip ()
                    if line :
                        self .process_response (line )
                time .sleep (0.1 )
        except serial .SerialException as e :
            self .log_message (f"Serial connection error: {e }")
            self .update_status_label ("Соединение не удалось")
            connected =False
        except Exception as e :
            self .log_message (f"Error: {e }")
        finally :
            if ser and ser .is_open :
                ser .close ()
            connected =False
    def send_command (self ,command ):
        global ser ,connected
        if not connected or not ser or not ser .is_open :
            self .log_message ("Ошибка: Не подключено к устройству")
            return False
        try :
            self .log_message (f"Sending: {command }")
            ser .write (f"{command }\n".encode ('utf-8'))
            return True
        except Exception as e :
            self .log_message (f"Error sending command: {e }")
            return False
    def process_response (self ,response ):
        self .log_message (f"Received: {response }")
        try :
            if response .startswith ("Status:"):
                parts =response .split ()
                for i in range (4 ):
                    if i +1 <len (parts ):
                        relay_part =parts [i +1 ]
                        if ":ON"in relay_part :
                            self .relay_states [i ]=True
                        elif ":OFF"in relay_part :
                            self .relay_states [i ]=False
                self .update_indicators ()
            elif response .startswith ("R")and (":ON"in response or ":OFF"in response ):
                relay_num =int (response [1 ])-1
                if 0 <=relay_num <4 :
                    self .relay_states [relay_num ]=":ON"in response
                    self .update_indicators ()
        except Exception as e :
            self .log_message (f"Error processing response: {e }")
    def update_indicators (self ):
        for i ,state in enumerate (self .relay_states ):
            color =COLORS ['on']if state else COLORS ['off']
            self .relay_controls [i ]['indicator'].itemconfig (self .relay_controls [i ]['circle'],fill =color )
    def toggle_relay (self ,relay_index ):
        self .send_command (f"{relay_index +1 }")
    def all_on (self ):
        self .send_command ("A+")
    def all_off (self ):
        self .send_command ("A-")
    def request_status (self ):
        self .send_command ("S")
    def log_message (self ,message ):
        timestamp =time .strftime ("%H:%M:%S")
        log_entry =f"[{timestamp }] {message }\n"
        self .root .after (0 ,self ._update_log ,log_entry )
    def _update_log (self ,message ):
        self .log_text .config (state =tk .NORMAL )
        self .log_text .insert (tk .END ,message )
        self .log_text .see (tk .END )
        self .log_text .config (state =tk .DISABLED )
    def update_status_label (self ,text ):
        self .root .after (0 ,lambda :self .status_label .config (text =f"Status: {text }"))
    def on_closing (self ):
        global running
        if messagebox .askokcancel ("Quit","Вы хотите бросить?"):
            running =False
            self .root .destroy ()
def main ():
    parser =argparse .ArgumentParser (description ='Релейная система управления')
    parser .add_argument ('-p','--port',help =f'Serial port (default: {DEFAULT_PORT })',default =DEFAULT_PORT )
    parser .add_argument ('-b','--baud',help =f'Baud rate (default: {DEFAULT_BAUDRATE })',
    type =int ,default =DEFAULT_BAUDRATE )
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
    root =tk .Tk ()
    app =RelayControlApp (root ,args .port ,args .baud )
    root .mainloop ()
if __name__ =="__main__":
    main ()