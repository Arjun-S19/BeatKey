from endless_imports import *

# sampling rate
sr = 48000

# all window function types
window_type_list = ["hamming", 
                    "hann", 
                    "hannnsgcq", 
                    "triangular", 
                    "square", 
                    "blackmanharris62", 
                    "blackmanharris70", 
                    "blackmanharris74", 
                    "blackmanharris92"]

# Key method testing
print("----- Testing Key Method -----")
for window_type in window_type_list:
    loader = ess.MonoLoader(filename = test_filename, sampleRate = sr)

    framecutter = ess.FrameCutter(frameSize = 4096, 
                                  hopSize = 2048, 
                                  silentFrames = "noise")

    windowing = ess.Windowing(type = window_type)

    spectrum = ess.Spectrum(size = 2048)

    spectralpeaks = ess.SpectralPeaks(orderBy = "magnitude", 
                                      magnitudeThreshold = 0.00001, 
                                      maxPeaks = 60, 
                                      sampleRate=sr)

    hpcp = ess.HPCP(size = 36, 
                    sampleRate = sr, 
                    referenceFrequency = 440, 
                    bandPreset = False, 
                    weightType = "cosine")

    key = ess.Key(averageDetuningCorrection = True, 
                  profileType = "temperley", 
                  numHarmonics = 4, 
                  pcpSize = 36, 
                  pcpThreshold = 0.2, 
                  slope = 0.6, 
                  usePolyphony = True, 
                  useThreeChords = True)

    pool = essentia.Pool()

    loader.audio >> framecutter.signal
    framecutter.frame >> windowing.frame >> spectrum.frame
    spectrum.spectrum >> spectralpeaks.spectrum
    spectralpeaks.magnitudes >> hpcp.magnitudes
    spectralpeaks.frequencies >> hpcp.frequencies
    hpcp.hpcp >> key.pcp
    key.key >> (pool, "tonal.key_key")
    key.scale >> (pool, "tonal.key_scale")
    key.strength >> (pool, "tonal.key_strength")

    essentia.run(loader)

    final_key = pool["tonal.key_key"]
    final_scale = pool["tonal.key_scale"]
    final_keyStr = pool["tonal.key_strength"]

    if str(final_key + " " + final_scale) == test_keyscale:
        keyScaleStrength = f"Windowing WindowType: {window_type}\nEstimated key and scale: {final_key} {final_scale}\nKey Strength: {final_keyStr}\n"
        print(keyScaleStrength)


# KeyExtractor method testing
print("----- Testing KeyExtractor Method -----")
for window_type in window_type_list:

    loader = ess.MonoLoader(filename = test_filename, sampleRate = sr)

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
                                    windowType = window_type)

    pool = essentia.Pool()

    loader.audio >> key_extract.audio
    key_extract.key >> (pool, "tonal.key_key")
    key_extract.scale >> (pool, "tonal.key_scale")
    key_extract.strength >> (pool, "tonal.key_strength")

    essentia.run(loader)

    final_key = pool["tonal.key_key"]
    final_scale = pool["tonal.key_scale"]
    final_keyStr = pool["tonal.key_strength"]

    if str(final_key + " " + final_scale) == test_keyscale:
        keyScaleStrength = f"KeyExtractor WindowType = {window_type}\nEstimated key and scale: {final_key} {final_scale}\nKey Strength: {final_keyStr}\n"
        print(keyScaleStrength)