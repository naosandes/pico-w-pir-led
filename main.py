import time
import machine
time.sleep(0.1) # Wait for USB to become ready

print("Hello, Pi Pico W!")

pin_sensor = machine.Pin(13, machine.Pin.IN)
led = machine.Pin(10, machine.Pin.OUT)

print('センサー作動中')

while True:
    if pin_sensor.value() == 1:
        led.value(1)
        print('動きを検知しました')
        time.sleep(3.0) #動きを検知したら、LEDをつけたまま3秒間停止するため

        led.value(0) #3秒の待機がすべて終わった直後にLEDを消してメッセージを出す
        print('正常に反応しました')
    else:
        led.value(0)
    time.sleep(0.1) #動体検知がない場合は装置の負荷を抑えるため
