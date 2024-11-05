from endless_imports import *

#--------------------------------------------------------------------------------------------------
'''
Extracting Duration

Notes: 
    y is the audio time series, what is an audio time series you ask?
        - an audio time series is a way of representing audio as a series of numbers over time, 
        where each number represents the amplitude at a specific time step

    sr is sampling rate aka samples per second
'''


y, sr = librosa.load(test_filename, sr = 48000)
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
Extracting BPM

Notes:
    Tempo via beats per minute (BPM)
'''

bpm, beats = librosa.beat.beat_track(y = y, sr = sr)

bpm_int = round(bpm[0] if type(bpm) == np.ndarray else bpm)
bpm_float = bpm[0] if type(bpm) == np.ndarray else bpm

#--------------------------------------------------------------------------------------------------
'''
Extracting Key and Scale

Notes:
    - Key Algorithm Workflow: Loading Audio File - Loading audio file and sampling rate
                              ↓
                              FrameCutter - Cuts audio signal into framed for processing
                              ↓
                              Windowing -  Applying "window function" to each frame to reduce spectral leakage
                              ↓
                              Spectrum -  Converts the time-domain signal (frames) into the frequency domain (spectrum)
                              ↓
                              Spectral Peaks - Identifies peaks in the spectrum
                              ↓ 
                              HPCP -  Computes Harmonic Pitch Class Profile (harmonic content via pitch classes) from spectral peaks
                              ↓
                              Key -  Estimates key and scale from HPCP (Key Strength is the confidence of the key estimation)
                              ↓
                              Pool -  Stores data
                              ↓
                              Connecting Streaming Network -  Connects the algorithms to form a processing pipeline
                              ↓
                              Running Streaming Network -  Runs streaming network to process audio file
                              ↓
                              Output - Outputting Key/Scale/Key Strength

    - Key Strength: Confidence of the key estimation 
        - 12 keys and 2 scales -> 24 possible combinations
        - decimal probability between 0 and 1 assigned to each combination based on chance the key/scale is that combination, all together adding to 1

'''
def key():
    # loading audio file
    loader = ess.MonoLoader(filename = test_filename, sampleRate = sr)

    # framecutter
    framecutter = ess.FrameCutter(frameSize = 4096, 
                                  hopSize = 2048, 
                                  silentFrames = "noise")

    # windowing
    windowing = ess.Windowing(type = "hann")

    # spectrum
    spectrum = ess.Spectrum(size = 2048)

    # spectral peaks
    spectralpeaks = ess.SpectralPeaks(orderBy = "magnitude", 
                                      magnitudeThreshold = 0.00001, 
                                      maxPeaks = 60, 
                                      sampleRate = sr)

    # hpcp
    hpcp = ess.HPCP(size = 36, 
                    sampleRate = sr, 
                    referenceFrequency = 440, 
                    bandPreset = False, 
                    weightType = "cosine")

    # Key algorithm
    key = ess.Key(averageDetuningCorrection = True, 
                  profileType = "temperley", 
                  numHarmonics = 4, 
                  pcpSize = 36, 
                  pcpThreshold = 0.2, 
                  slope = 0.6, 
                  usePolyphony = True, 
                  useThreeChords = True)

    # pooling data
    pool = essentia.Pool()

    # connecting algorithms to create streaming network
    loader.audio >> framecutter.signal
    framecutter.frame >> windowing.frame >> spectrum.frame
    spectrum.spectrum >> spectralpeaks.spectrum
    spectralpeaks.magnitudes >> hpcp.magnitudes
    spectralpeaks.frequencies >> hpcp.frequencies
    hpcp.hpcp >> key.pcp
    key.key >> (pool, "tonal.key_key")
    key.scale >> (pool, "tonal.key_scale")
    key.strength >> (pool, "tonal.key_strength")

    # running streaming network
    essentia.run(loader)

    keyScaleStrength = "Estimated key and scale: " + str(pool["tonal.key_key"]) + " " + str(pool["tonal.key_scale"]) + "\nKey Strength: " + str(pool["tonal.key_strength"])

    print("Key Algorithm - ")
    print(keyScaleStrength)

def key_extractor():
    # loading audio file
    loader = ess.MonoLoader(filename = test_filename, sampleRate = sr)

    # KeyExtractor algorithm
    key_extract = ess.KeyExtractor(averageDetuningCorrection = True, 
                                    frameSize = 4096, 
                                    hopSize = 2048,
                                    hpcpSize = 36, 
                                    maxFrequency = 2000, 
                                    maximumSpectralPeaks = 100,
                                    minFrequency = 25, 
                                    pcpThreshold = 0.2, 
                                    profileType = "temperley",
                                    sampleRate = sr, 
                                    spectralPeaksThreshold = 0.00005, 
                                    tuningFrequency = 440,
                                    weightType = "cosine", 
                                    windowType = "hannnsgcq")

    # pooling data
    pool = essentia.Pool()

    # connecting algorithms to create streaming network
    loader.audio >> key_extract.audio
    key_extract.key >> (pool, "tonal.key_key")
    key_extract.scale >> (pool, "tonal.key_scale")
    key_extract.strength >> (pool, "tonal.key_strength")

    # running streaming network
    essentia.run(loader)

    keyScaleStrength = "Estimated key and scale: " + str(pool["tonal.key_key"]) + " " + str(pool["tonal.key_scale"]) + "\nKey Strength: " + str(pool["tonal.key_strength"])

    print("Key Extractor Algorithm - ")
    print(keyScaleStrength)

# uncomment below lines to extract key and scale via Key and KeyExtractor algorithms
#key()
#key_extractor()

#--------------------------------------------------------------------------------------------------
'''
Adjusting Tempo and Pitch

Notes:
    - PCM_24 refers to output file bitrate (24 bits)
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

# uncomment below line to adjust tempo and pitch
#tempo_pitch_adjust()
