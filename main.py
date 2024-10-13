from endless_imports import *

#--------------------------------------------------------------------------------------------------
'''
Extracting Duration

Notes: 
y is the audio time series, tf is an audio time series u ask? 
    - an audio time series is a way of representing audio as a series of numbers over time, 
    where each number represents the amplitude at a specific time step

sr is sampling rate aka samples per second
'''

y, sr = librosa.load("_K.K. Bossa (Orchestra).wav", sr = 48000)
duration = librosa.get_duration(y = y, sr = sr)

duration_min = int(duration / 60)
duration_sec = int(duration % 60)
duration_final = str(duration_min) + ":" + str(duration_sec)
#--------------------------------------------------------------------------------------------------
'''
Extracting Sampling Rate

Notes:
 - sampling rate is the number of samples per second that are taken from a waveform to create 
 a discete digital signal
'''

sampling_rate = sr

#--------------------------------------------------------------------------------------------------
'''
Extracting Tempo

Notes:
Tempo via beats per minute (BPM)
'''

tempo, beats = librosa.beat.beat_track(y = y, sr = sr)
tempo_int = int(tempo[0].round())
tempo_string = "BPM Estimation: " + str(tempo_int)

#--------------------------------------------------------------------------------------------------
'''
Extracting Key and Scale

Notes:
Being able to extract which of the following keys and scales the track is

'''

loader = ess.MonoLoader(filename="_K.K. Bossa (Orchestra).wav")
framecutter = ess.FrameCutter(frameSize=4096, 
                              hopSize=2048, 
                              silentFrames='drop')
windowing = ess.Windowing(type='hamming')
spectrum = ess.Spectrum()
spectralpeaks = ess.SpectralPeaks(orderBy='magnitude',
                                  magnitudeThreshold=0.00001,
                                  maxPeaks=60,
                                  sampleRate=44100)

# harmonic pitch class profile (HPCP)
hpcp = ess.HPCP()
hpcp_key = ess.HPCP(size=36,
                    sampleRate=44100,
                    referenceFrequency=440,
                    bandPreset=False,
                    weightType='cosine',
                    nonLinear=False,
                    windowSize=12)

# key
key = ess.Key(profileType='edma',
              numHarmonics=4,
              pcpSize=36,
              slope=0.6,
              usePolyphony=True,
              useThreeChords=True)

# pooling data
pool = essentia.Pool()

# connecting algorithms (data pipeline)
loader.audio >> framecutter.signal
framecutter.frame >> windowing.frame >> spectrum.frame
spectrum.spectrum >> spectralpeaks.spectrum
spectralpeaks.magnitudes >> hpcp.magnitudes
spectralpeaks.frequencies >> hpcp.frequencies
spectralpeaks.magnitudes >> hpcp_key.magnitudes
spectralpeaks.frequencies >> hpcp_key.frequencies
hpcp_key.hpcp >> key.pcp
hpcp.hpcp >> (pool, 'tonal.hpcp')
key.key >> (pool, 'tonal.key_key')
key.scale >> (pool, 'tonal.key_scale')
key.strength >> (pool, 'tonal.key_strength')

essentia.run(loader)

keyScaleStrength = "Estimated key and scale: " + str(pool['tonal.key_key']) + " " + str(pool['tonal.key_scale']) + "\nKey Strength: " + str(pool['tonal.key_strength'])

print(keyScaleStrength)

#--------------------------------------------------------------------------------------------------
'''
Adjusting Tempo and Pitch

Notes:
PCM_24 refers to output file bitrate (24 bits)
'''

user_file = y

def tempo_pitch_adjust():

    # tempo stretcher
    def tempo_stretch(inputStretch):
        global user_file
        y_stretched = pyrb.time_stretch(y = user_file, 
                                        sr = sr, 
                                        rate = float(inputStretch))
        user_file = y_stretched

    # pitch shifter
    def pitch_shift(inputShift):
        global user_file
        y_shifted = pyrb.pitch_shift(y = user_file, 
                                     sr = sr, 
                                     n_steps = int(inputShift))
        user_file = y_shifted

    def tempo_pitch_output():
        # create sliders and run tempo and pitch functions
        tempo_value = tempo_slider.get()
        pitch_value = pitch_slider.get()
        tempo_stretch(tempo_value)
        pitch_shift(pitch_value)
        
        # deleting the sliders and enter button
        tempo_label.pack_forget()
        tempo_slider.pack_forget()
        pitch_label.pack_forget()
        pitch_slider.pack_forget()
        next_button.pack_forget()
        
        # filename input and save button
        filename_label.pack(pady=10)
        filename_entry.pack(pady=10)
        save_button.pack(pady=10)

    def save_file():
        filename = filename_entry.get()
        if filename:
            sf.write(filename + ".wav", user_file, sr, "PCM_24")
            tp_gui.quit()

    # creates the window
    tp_gui = tk.Tk()
    tp_gui.title("")
    tp_gui.geometry("576x324")
    
    tempo_label = tk.Label(tp_gui, text = "Audio Manipulation")
    tempo_label.config(font = ("Ariel", 24))
    tempo_label.pack(pady = 18)

    # tempo slider
    tempo_label = tk.Label(tp_gui, text = "Tempo Stretch Factor:")
    tempo_label.config(font = ("Ariel", 16))
    tempo_label.pack(pady = 5)
    tempo_slider = tk.Scale(tp_gui, 
                            from_ = 0.1, 
                            to = 5.0, 
                            resolution = 0.1, 
                            orient = "horizontal", 
                            length = 300)
    tempo_slider.set(1.0)
    tempo_slider.pack(pady = 5)

    # pitch slider
    pitch_label = tk.Label(tp_gui, text = "Pitch Shift Factor:")
    pitch_label.config(font = ("Ariel", 16))
    pitch_label.pack(pady = 5)
    pitch_slider = tk.Scale(tp_gui, 
                            from_ = -12, 
                            to = 12, 
                            resolution = 1, 
                            orient = "horizontal", 
                            length = 300)
    pitch_slider.set(0)
    pitch_slider.pack(pady = 5)

    # next button
    next_button = tk.Button(tp_gui, text = "Next", command = tempo_pitch_output)
    next_button.pack(pady = 20)

    spacer = tk.Label(tp_gui, text = "")
    spacer.pack()

    # save button
    filename_label = tk.Label(tp_gui, text = "Enter a filename:")
    filename_label.config(font=("Ariel", 16))
    filename_entry = tk.Entry(tp_gui)
    save_button = tk.Button(tp_gui, text="Save", command=save_file)

    tp_gui.mainloop()

#tempo_pitch_adjust()
