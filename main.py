import time
import machine
import network #Pico WからデータWi-Fiチップを動かすための標準ライブラリ
import urequests #インターネット上のホームページやサーバーに対して、データを取得(get)したり送信(post)したりする役割

time.sleep(0.1) # Wait for USB to become ready

print("Hello, Pi Pico W!")

# --- 設定項目 ---
#Wokwiのシミュレーター用Wi-Fi設定
SSID = 'Wokwi-GUEST'
PASSWORD = ""

#データを送信するWebサーバーのURL　※後に実際のWebサーバーURLに変更！
SERVER_URL = 'http://my-web-server.com/api/log_sensor'

#ピンの設定
pin_sensor = machine.Pin(13, machine.Pin.IN)
led = machine.Pin(10, machine.Pin.OUT)

print('センサー作動中')

# --- ① Wi-Fiの接続処理 ---
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Wi-Fiに接続中...')
        wlan.connect(SSID, PASSWORD)
        #接続完了まで待機
        while not wlan.isconnected():
            time.sleep(1)
    print('Wi-Fi接続成功! IPアドレス:', wlan.ifconfig()[0])

#最初にWi-Fiに接続しておく    
connect_wifi()    
print('センサー作動中')


# --- メインループ ---
while True:
    if pin_sensor.value() == 1:
        led.value(1)
        print('動きを検知しました')

        # --- ②サーバーへデータ送信
        try: #エラーをキャッチしながら実行するための構文　フリーズ防止機能
            #サーバーに送るデータ（Json形式）
            #『検知した』というステータスなどを送信
            data = {'device_id': 'pico_w_01', 'status': 'detected'}

            print('データを送信中...')
            #HTTP POSTという方法でサーバーにデータを送信
            response = urequests.post(SERVER_URL, json=data)

            #サーバーからの返事（200番なら成功）
            if response.status_code == 200:
                print('サーバーへの送信成功')
            else:
                print('サーバーエラー:',response.status_code)
            response.close() #メモリ開放のために必ず閉じる

        except Exception as e:
            print('送信失敗(ネットワークエラーなど）:', e)
        time.sleep(3.0) #3秒間待機
        led.value(0) 
        print('正常に反応しました')
    else:
        led.value(0)
        time.sleep(0.1) #動体検知がない場合は装置の負荷を抑えるため
