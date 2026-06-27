import time
import machine
import network #Pico WからデータWi-Fiチップを動かすための標準ライブラリ
import urequests #インターネット上のホームページやサーバーに対して、データを取得(get)したり送信(post)したりする役割
import os
import ujson

print("Hello, Pi Pico W!")

# --- AWSの送信先設定 ---
#Wokwiのシミュレーター用Wi-Fi設定
SSID = 'Wokwi-GUEST'
PASSWORD = ''

#AWS(EC2)へデータを送信するWebサーバーのURL　※後に実際のWebサーバーURLに変更！
SERVER_URL = 'http://ec2-15-152-151-230.ap-northeast-3.compute.amazonaws.com:5000/sensor'

#ピンの設定
pin_sensor = machine.Pin(13, machine.Pin.IN)
led_red = machine.Pin(10, machine.Pin.OUT)
led_blue = machine.Pin(8, machine.Pin.OUT)

print('センサー作動中')

# --- ① Wi-Fiの接続処理 ---
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Wi-Fiに接続中...')
        wlan.connect(SSID, PASSWORD)
        #タイムアウトのカウンターを用意
        attempt = 0
        max_attempt = 15
        #接続完了まで待機
        while not wlan.isconnected():
            time.sleep(1)
            #1秒待つごとに、数字を1づつ増やす
            attempt += 1
            print(f'接続を待っています... ({attempt}秒経過)')
            #数字が15以上になるとループが終了し、接続中断
            if attempt>=max_attempt:
                print('15秒経過しても接続ができないため、中断します。')
                break
    
    if wlan.isconnected():
        print('Wi-Fi接続成功! IPアドレス:', wlan.ifconfig()[0])
        return True
    else:
        return False

#最初にWi-Fiに接続しておく  
time.sleep(0.1) #接続処理を行う前に待機時間を設定する  
connect_wifi() #関数の呼び出し
print('センサー作動中')

#センサーが反応した時に『実行したい処理』を関数で定義
def sensor_handler(pin):
    print('動きを検知しました')
    led_red.value(1)
    led_blue.value(1)
    
# --- ②サーバーへデータ送信
    try: #エラーをキャッチしながら実行するための構文　フリーズ防止機能
            #サーバーに送るデータ（Json形式）
            #『検知した』というステータスなどを送信
        data = {'device_name': 'pico_w_01', 
                'status': 'detected',
        }

        
        #AWS送信するデータの形式設定
        headers = {'Content-Type': 'application/json'}

        print('EC2へデータを送信中...')
        #HTTP POSTという方法でSERVER_URLにリクエストを送信
        response = urequests.post(SERVER_URL, data=ujson.dumps(data), headers=headers) #括弧内のデータは送信側のもつポケット（右側のjson, headers）に実際の変数を入力することにより機能する。

        print(response.status_code)
        #サーバーからの返事（200番なら成功）
        if  response.status_code == 201 or response.status_code == 200:                
            print('AWSへの送信成功')
            led_red(0)
            for i in range(4):
                led_blue.value(1)
                time.sleep(1)
                led_blue.value(0)
                time.sleep(0.5)
        else:
            print('送信エラー。ステータスコード:',response.status_code)
            led_blue(0)
            for i in range(4):
                led_red.value(1)
                time.sleep(1)
                led_red.value(0)
                time.sleep(1)
        response.close() #メモリ開放のために必ず閉じる。閉じなければメモリがいっぱいになってしまう。
        led_red.value(0)
        led_blue.value(0) 
        print('正常に反応しました')

    except Exception as e:
        print('送信失敗(ネットワークエラーなど）:', e)

        led_red.value(1)
        led_blue.value(0)

        wifi_success = connect_wifi() #Wi-Fiへ再接続

        if wifi_success:
            led_red.value(0) #再接続終了後、消灯
            print('再接続完了')
        else:
            #15秒経っても接続されない場合
            print('接続失敗のため待機モードへ入ります。')
            for i in range(5):
                led_red.value(1)
                time.sleep(0.1)
                led_red.value(0)
                time.sleep(0.1)

pin_sensor.irq(trigger=machine.Pin.IRQ_RISING, handler=sensor_handler)

# --- メインループ ---
while True:
    time.sleep(1)
