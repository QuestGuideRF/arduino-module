import requests
import sys
import serial
import time
def get_data (token ):
    try :
        base_url ='https://fitodomik.online/api'
        headers ={'X-Auth-Token':token }if token else {}
        t =requests .get (f"{base_url }/get-thresholds.php",headers =headers ).json ()
        d =requests .get (f"{base_url }/get-sensor-data.php",headers =headers ).json ()
        s =requests .get (f"{base_url }/get-schedule.php",headers =headers ).json ()
        order =['temperature','humidity_air','humidity_soil','co2']
        thresholds =";".join (f"{t [k ]['min_limit']}-{t [k ]['max_limit']}"
        for k in order if k in t )or "0-0;0-0;0-0;0-0"
        data =d .get ('data',{})
        devices =f"{int (data .get ('lamp_state',0 ))},{int (data .get ('curtains_state',0 ))}"
        sched =s .get ('data',{}).get ('schedule',[])
        lamp_hours =[h for h in range (24 )for item in sched
        if item .get ('time_interval','').startswith (f'{h }:')and item .get ('lighting_active')]
        curtain_hours =[h for h in range (24 )for item in sched
        if item .get ('time_interval','').startswith (f'{h }:')and item .get ('curtains_active')]
        def group (hours ):
            if not hours :return "0"
            hours =sorted (set (hours ))
            result =[]
            start =end =hours [0 ]
            for h in hours [1 :]:
                if h ==end +1 :
                    end =h
                else :
                    result .append (f"{start }-{end }"if start !=end else str (start ))
                    start =end =h
            result .append (f"{start }-{end }"if start !=end else str (start ))
            return ",".join (result )
        schedule =f"{group (lamp_hours )};{group (curtain_hours )}"
        return f"{thresholds }|{devices }|{schedule }"
    except :
        return "0-0;0-0;0-0;0-0|0,0|0;0"
def send_to_arduino (data ):
    try :
        ser =serial .Serial ('COM4',9600 ,timeout =2 )
        time .sleep (5 )
        ser .write ((data +'\n').encode ())
        ser .flush ()
        time .sleep (2 )
        ser .close ()
        return True
    except :
        return False
def main ():
    token =sys .argv [1 ]if len (sys .argv )>1 else input ("Token: ")
    data =get_data (token )
    print (data )
    if send_to_arduino (data ):
        print ("OK")
    else :
        print ("Error")
if __name__ =="__main__":
    main ()