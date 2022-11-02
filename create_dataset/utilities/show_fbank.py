import librosa
import numpy as np
import torchaudio
import librosa.display as display
import matplotlib.pyplot as plt
import matplotlib
import torchaudio
import torch

fig = plt.figure(dpi=100)
file_path = rf"D:\workspace\audio_relay\8.19\train\error_NG\7_14_9_18_97_0.0.wav"
# file_path = rf"D:\workspace\audio_relay\8.19\train\error_OK\7_13_17_7_220_0.97.wav"  #

s_show, sr_show = librosa.load(file_path,
                               mono=False)
name = ['zuo', 'you']
for idx, one in enumerate(s_show):
    s_show = one
    fbk = torchaudio.compliance.kaldi.fbank(torch.from_numpy(s_show[None, :]), htk_compat=True,
                                            sample_frequency=sr_show, use_energy=False,
                                            window_type='hanning', num_mel_bins=384, dither=0.0,
                                            frame_shift=10,
                                            # low_freq=200,
                                            # high_freq=0
                                            )

    fig.add_subplot(1, 2, 1 + idx)
    plt.imshow(fbk.t().numpy())
plt.savefig(f"./fbank_easy_wrong_classfiy2OK.png")
plt.show()
