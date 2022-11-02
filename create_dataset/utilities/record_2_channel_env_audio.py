#-*-coding:utf-8-*-
import multiprocessing
import numpy as np
import pyaudio
import soundfile
import wave

CHUNK = int(1024)  # 每个缓冲区的帧数
FORMAT = pyaudio.paInt16  # 采样位数
CHANNELS = 1  # 单声道
RATE = 22050  # 采样频率
SEC = 600 # 采样时间，10分钟

def get_usb_mic():
    p = pyaudio.PyAudio()
    mic=[]
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    for i in range(0, numdevices):
        device=p.get_device_info_by_host_api_device_index(0, i)
        if device.get('maxInputChannels') > 0 and device.get('name').__contains__('USB'):
            print("USB mic id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'))
            mic.append(i)
    return mic


class Recorder:
    def __init__(self, mic_ids, queue, num_frames=1024):
        self.mic_ids = mic_ids
        self.queue = queue
        self.num_frames = num_frames

    def run(self):  # 把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        """
        Record an audio clip with 10 minutes length and play it simultaneously
        """
        p1 = pyaudio.PyAudio()
        stream1 = p1.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=self.num_frames,
                          input_device_index=self.mic_ids[0],
                          )  # 打开流，传入响应参数
        print("start...", 1)
        p2 = pyaudio.PyAudio()  # 实例化对象
        stream2 = p2.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=self.num_frames,
                          input_device_index=self.mic_ids[1],
                          )  # 打开流，传入响应参数
        print("start...", 2)

        wf = wave.open("2_channel_env2.wav", "wb")
        # Set parameters of the wav file, channels, sample width and rate, must be the same
        # with the streams
        wf.setnchannels(2)  # number of channels
        wf.setsampwidth(sampwidth=p1.get_sample_size(FORMAT))
        wf.setframerate(framerate=RATE)
        # 22050 * 600s / buffer size = how many chunks need to record
        for w in range(int(RATE * SEC / self.num_frames)):
            audio1 = stream1.read(self.num_frames)
            audio2 = stream2.read(self.num_frames)
            out_data1 = np.frombuffer(audio1, dtype=np.int16)[None, :]
            out_data2 = np.frombuffer(audio2, dtype=np.int16)[None, :]
            out_data = np.stack([out_data2[0], out_data1[0]], axis=-1)
            wf.writeframes(out_data)
            self.queue.put(out_data)
        print("stops recording")
        stream1.stop_stream()  # step 1. stop stream
        stream2.stop_stream()
        p1.close(stream1)  # step2. colse streams
        p2.close(stream2)
        p1.terminate()   # terminate pyaudio instance
        p2.terminate()
        wf.close()  # close the wav file, otherwise it cant be played

class Player:
    def __init__(self, queue, num_frames=1024):
        self.queue = queue
        self.num_frames = num_frames
        super(Player, self).__init__()

    def run(self):
        p = pyaudio.PyAudio()
        stream = p.open(channels=2,
                        rate=RATE,
                        output=True,
                        format=FORMAT,
                        )
        while True:
            ret = self.queue.get()
            stream.write(ret, num_frames=self.num_frames)
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == "__main__":
    mic_ids = get_usb_mic()
    q = multiprocessing.Queue(maxsize=1000)
    record = Recorder(mic_ids, q)
    play = Player(q, CHUNK)

    p1 = multiprocessing.Process(target=play.run)
    p1.daemon = True
    p1.start()

    p2 = multiprocessing.Process(target=record.run)
    p2.daemon = True
    p2.start()

    p1.join()
    p2.join()
