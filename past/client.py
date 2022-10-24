import sounddevice as sd
import numpy as np
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import socket


# デバイス設定 ####################################################################################
#device_list = sd.query_devices() # デバイス一覧
#print(device_list)
sd.default.device = [1, 6] # Input, Outputデバイス指定


# クライアント操作(WIFI通信) #######################################################################################
def operation(select):

    if(select == 0):
        print("Process : No Operation")
    elif(select == 1):
        print("Process : 1")
        HOST_NAME = "127.0.0.1"
        PORT = 8080
    elif(select == 2):
        print("Process : 2")
        HOST_NAME = "127.0.0.2"
        PORT = 8080
    elif(select == 3):
        print("Process : 3")
        HOST_NAME = "127.0.0.3"
        PORT = 8080
    elif(select == 4):
        print("Process : 4")
        HOST_NAME = "127.0.0.4"
        PORT = 8080

    if(select != 0):
            sk_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   #ソケット作成
            try:
                sk_client.connect((HOST_NAME, PORT))
                sk_client.send("TEST".encode("utf-8"))
                sk_client.close()
                print("Connection Successful ( IP :",HOST_NAME,")")
            except socket.error:
                sk_client.close() 
                print("Connection Faild ( IP :",HOST_NAME,")")

    return None


# リアルタイム収音 ################################################################################
def callback(indata, frames, time, status):         #indataには0.026秒分のデータが格納される
    global plotdata
    data = indata[::downsample, 0]                  #[::N] indataの要素をN(downsample)個ずつ飛ばして取り出す。　0はチャンネル。
    shift = len(data)                               #dataの要素数を取得
    plotdata = np.roll(plotdata, -shift, axis=0)    #plotdataの要素をdata(shift)の要素数分マイナスシフトする。axis=0は行方向のシフト。
    plotdata[-shift:] = data                        #後ろからshift番目までにdataを代入(plotを右から流れるようにするため)

"""
# フーリエ変換(1秒間) ###################################################################################
def fourier1():
    global plotdata, fsample,  window1
    F = np.fft.fft(plotdata * window1)
    F = F / (fsample / 2)                               # フーリエ変換の結果を正規化
    F = F * (fsample / sum(window1))                    # 窓関数による振幅補正
    FFT_result = 20 * np.log10(np.abs(F) + 1e-18)       # 振幅スペクトル

    return FFT_result, F
"""

# フーリエ変換(短時間) ###################################################################################
def fourier2():
    global plotdata, Framesize, window2
    Frame = plotdata[-Framesize:] * window2
    F = np.fft.fft(Frame)
    F = F / (Framesize / 2)                             # フーリエ変換の結果を正規化
    F = F * (Framesize / sum(window2))                  # 窓関数による振幅補正
    FFT_result = 20 * np.log10(np.abs(F) + 1e-18)       # 振幅スペクトル

    return FFT_result, F


# 回数判定関数 #####################################################################################
def count(data):
    count = 0
    time = 5
    for i in range(39) :
        if (data[i] > 0.07 and time >= 5) :
            count += 1
            time = 0
        time += 1
    print("Detection Count :", count)

    return count


# 更新関数 ######################################################################################
def update_plot(frame):
    global plotdata, Framesize, fsample, window1, pre_data, Time, wait, detect, record, recording_data
    #plotdata2, ditection2 = fourier1()              #フーリエ変換(1秒間)
    plotdata3, ditection3 = fourier2()              #フーリエ変換(短時間)
    line1.set_ydata(plotdata)                       #データの更新(時間信号)
    #line2.set_ydata(plotdata2[0:fsample // 2:21])   #データの更新(スペクトル)
    line3.set_ydata(plotdata3[:Framesize // 2])     #データの更新(スペクトル)

    #ditection_data = (ditection3[:Framesize // 2] + ditection2[0:fsample // 2:21]) * 10
    ditection_data = ditection3[:Framesize // 2] * 10

    dt = ditection_data - pre_data
    pre_data = ditection_data
    line4.set_ydata(dt.real)

    ave = sum(np.abs(dt[336:504])) / (504 - 336)

    #時間経過
    Time += 1
    if (Time >= 3 and ave < 0.05 and record == False):
        wait = False

    #録音
    if (Time < 39 and record == True):
        recording_data[Time] = ave
    if (Time >= 39 and record == True):
        Time = 0
        record = False
        result = recording_data
        print("-recorded-----------------------------------")
        select = count(result)   #回数判定関数
        operation(select)

    #録音開始合図
    if (ave < 0.05 and wait == False and record == False and detect == True):
        Time = 0
        record = True
        detect = False
        print("-recording---------------------------------")

    #音検出
    if (ave > 0.12 and wait == False and record == False):
        print("-detected----------------------------------")
        wait = True
        detect = True
        Time = 0

    print("{0:>5d}  {1:>}  {2:>}  {3:>}  {4:>6.3f}".format(Time, wait, record, detect, round(ave, 3)))

    #return line1, line2, line3, line4,
    return line1, line3, line4,


# パラメータ #####################################################################################
downsample = 1
Framesize = 2100
fsample = 44100
length = int(1000 * 44100 / (1000 * downsample))

plotdata = np.zeros((length))
pre_data = np.zeros(int(Framesize / 2))
recording_data = np.zeros((39))

window1 = np.hamming(fsample)
window2 = np.hamming(Framesize)
freq = np.fft.fftfreq(Framesize, d = 1 / length)

Time = 0
detect = False
wait = False
record = False


# グラフレイアウト設定 ##############################################################################
#fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(16, 9), dpi=72)
fig, (ax1, ax3, ax4) = plt.subplots(3, 1, figsize=(16, 9), dpi=72)

line1, = ax1.plot(plotdata)
ax1.set_ylim([-1.2, 1.2])
ax1.set_xlim([0, length])
ax1.set_xlabel("Time [Hz^-1]")
ax1.set_ylabel("Gain")
ax1.yaxis.grid(True)

#line2, = ax2.plot(freq[:Framesize // 2], np.zeros(Framesize // 2))
#ax2.set_ylim([-100, 10])
#ax2.set_xlim([0, 20000])
#ax2.set_xlabel("Freqency [Hz]")
#ax2.set_ylabel("Amplitude[dB]")
#ax2.yaxis.grid(True)

line3, = ax3.plot(freq[:Framesize // 2], np.zeros(Framesize // 2))
ax3.set_ylim([-100, 10])
ax3.set_xlim([0, 20000])
ax3.set_xlabel("Freqency [Hz]")
ax3.set_ylabel("Amplitude")
ax3.yaxis.grid(True)

line4, = ax4.plot(freq[:Framesize // 2], np.zeros(Framesize // 2))
ax4.set_ylim([-1.0, 1.0])
ax4.set_xlim([0, 20000])
ax4.set_xlabel("Freqency [Hz]")
ax4.set_ylabel("Ditection")
ax4.yaxis.grid(True)

fig.tight_layout()


# 収音クラス ######################################################################################
stream = sd.InputStream(channels=1,     
                        dtype='float32',
                        callback=callback   #callbackにデータを送る
                        )


# アニメーションクラス ##############################################################################
ani = FuncAnimation(fig,                
                    update_plot,     #プロット更新関数
                    interval = 1,    #更新間隔(ms)
                    blit=True
                    )


with stream:
    plt.show()