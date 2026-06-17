import time
import machine
import network #Pico WからデータWi-Fiチップを動かすための標準ライブラリ
import urequests #インターネット上のホームページやサーバーに対して、データを取得(get)したり送信(post)したりする役割

print("Hello, Pi Pico W!")

# --- Supabaseの設定項目 ---
#Wokwiのシミュレーター用Wi-Fi設定
SSID = 'Wokwi-GUEST'
PASSWORD = ''

#データを送信するWebサーバーのURL　※後に実際のWebサーバーURLに変更！
SERVER_URL = 'https://ogcbgknuysyfoskqbihc.supabase.co/rest/v1/sensor_logs'

SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9nY2Jna251eXN5Zm9za3FiaWhjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODE2NTAwMTIsImV4cCI6MjA5NzIyNjAxMn0.oRkmSJ5vPh2RKRDegK9zsy1fNccP8ryZBcMByNg85jQ'

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
time.sleep(0.1) #接続処理を行う前に待機時間を設定する  
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
            data = {'device_name': 'pico_w_01'}

            #Supabaseの認証用ヘッダー
            headers = {
                'apikey': SUPABASE_KEY,
                'Authorization': 'Bearer '+ SUPABASE_KEY,
                'Content-Type': 'application/json'
            }

            print('Supabaseへデータを送信中...')
            #HTTP POSTという方法でサーバーにデータを送信
            response = urequests.post(SERVER_URL, json=data, headers=headers)

            #サーバーからの返事（200番なら成功）
            if  response.status_code == 201 or response.status_code == 200:
                print('SQLへの保存成功')
            else:
                print('送信エラー。ステータスコード:',response.status_code)
            response.close() #メモリ開放のために必ず閉じる

        except Exception as e:
            print('送信失敗(ネットワークエラーなど）:', e)
        time.sleep(3.0) #3秒間待機
        led.value(0) 
        print('正常に反応しました')
    else:
        led.value(0)
        time.sleep(0.1) #動体検知がない場合は装置の負荷を抑えるため
