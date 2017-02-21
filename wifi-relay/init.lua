local AP_SSID = "EPD"
local AP_PASSWORD = "AP_PASSWORD"

local SSID = "<YOUR_WIFI_SSID>"
local PASSWORD = "ROUTER_PASSWORD"

local PORT = 3333

wifi.setmode(wifi.STATIONAP)
wifi.ap.config({ssid=AP_SSID, pwd=AP_PASSWORD})
wifi.ap.setip({ip="192.168.1.1", netmask="255.255.255.0", gateway="192.168.1.1"})
wifi.sta.config(SSID, PASSWORD)
wifi.sta.autoconnect(1)

tmr.alarm(0,1000,0,function() -- run after a delay
    uart.setup(0, 115200, 8, 0, 1, 1)
    srv=net.createServer(net.TCP, 28800) 
    srv:listen(PORT,function(conn)
        uart.on("data", 0, function(data)
            conn:send(data)
        end, 0)
        conn:on("receive",function(conn,payload) 
            uart.write(0, payload)
        end)  
        conn:on("disconnection",function(c) 
            uart.on("data")
        end)
    end)
end)

