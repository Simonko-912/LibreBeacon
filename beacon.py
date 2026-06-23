import subprocess
import datetime
import time
import board
import adafruit_dht
import numpy as np
from scipy.io import wavfile

# Temp sensor setup 
dht = adafruit_dht.DHT11(board.D17)

# CW and audio stuff
SAMPLE_RATE = 48000
TONE_FREQ = 700
WPM = 12
DOT_DURATION = 1.2 / WPM

# Beacon settings
BEACON_FREQ = 433800 // Change me to a ISM band or Ham radio freq
BEACON_NAME = "RPiTX" // On ISM bands, no need to include callsing, but for non ISM do something like 'RPiTX OM3ABC'
BEACON_LOC = "JN" // Recommend like max 6 letters of mainhead locator
BEACON_EMAIL = "EXAMPLE AT EXAMPLE DOT COM" // Include your email, or contact, or callsign or leave empty
PAUSE_LENGTH = 30 // seconds to wait between transmissions 
CUSTOM_TEXT = "" // a full line after the beacon name is transmitted, added here for faster access 

# Recommended to not touch MORSE and PROSIGNS

MORSE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
    'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
    'Z': '--..', '0': '-----', '1': '.----', '2': '..---',
    '3': '...--', '4': '....-', '5': '.....', '6': '-....',
    '7': '--...', '8': '---..', '9': '----.',
    '.': '.-.-.-', '/': '-..-.', ' ': ' ',
    '-': '-....-', '#': '.-.-.', '@': '.--.-.'
}

PROSIGNS = {
    'BT': '-...-',
    'AR': '.-.-.',
    'SK': '...-.-',
    'KN': '-.--.'}

def make_tone(duration):
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration), False)
    return np.sin(2 * np.pi * TONE_FREQ * t) * 0.8

def make_silence(duration):
    return np.zeros(int(SAMPLE_RATE * duration))

def encode_symbol_seq(symbol_seq, audio):
    for symbol in symbol_seq:
        if symbol == '.':
            audio.append(make_tone(DOT_DURATION))
        elif symbol == '-':
            audio.append(make_tone(DOT_DURATION * 3))
        audio.append(make_silence(DOT_DURATION))
    audio.append(make_silence(DOT_DURATION * 2))

def text_to_cw_wav(text, filename):
    audio = []

    # 4 second lead-in carrier for decoder lock
    audio.append(make_tone(4.0))
    audio.append(make_silence(0.5))

    tokens = text.upper().split(' ')
    i = 0
    while i < len(tokens):
        token = tokens[i]

        # Check for prosigns
        if token in PROSIGNS:
            encode_symbol_seq(PROSIGNS[token], audio)
            audio.append(make_silence(DOT_DURATION * 4))
            i += 1
            continue

        # Empty token = word space
        if token == '':
            audio.append(make_silence(DOT_DURATION * 7))
            i += 1
            continue

        # Process character by character
        for char in token:
            if char not in MORSE:
                continue
            encode_symbol_seq(MORSE[char], audio)

        # Word gap
        audio.append(make_silence(DOT_DURATION * 4))
        i += 1

    # End of message silence
    audio.append(make_silence(1.0))

    combined = np.concatenate(audio)
    combined = (combined * 32767).astype(np.int16)
    wavfile.write(filename, SAMPLE_RATE, combined)

def get_cpu_temp():
    try:
        result = subprocess.run(
            ['vcgencmd', 'measure_temp'],
            capture_output=True, text=True
        )
        return result.stdout.strip().replace("temp=","").replace("'C","C")
    except Exception:
        return "ERR"

def get_uptime_minutes():
    try:
        with open("/proc/uptime", "r") as f:
            seconds = float(f.readline().split()[0])
        return int(seconds // 60)
    except:
        return -1

# If you dont have a dht11 sensor make it return Null and in build_beacon remove the temp and humidity stuff

def get_dht():
    try:
        temp = dht.temperature
        hum = dht.humidity
        if temp is None or hum is None:
            return "ERR", "ERR"
        return f"{temp:.1f}C", f"{hum:.1f}PCT"
    except RuntimeError:
        return "ERR", "ERR"

def get_ram_mb():
    with open("/proc/meminfo") as f:
        mem = f.read().splitlines()

    total = int(mem[0].split()[1]) // 1024
    free = int(mem[1].split()[1]) // 1024
    buffers = int(mem[3].split()[1]) // 1024
    cached = int(mem[4].split()[1]) // 1024

    used = total - free - buffers - cached
    return used, total

def build_beacon():
    now = datetime.datetime.now(datetime.UTC)
    cpu = get_cpu_temp()
    temp, hum = get_dht()
    uptime = get_uptime_minutes()
    used, total = get_ram_mb()

    return (
        f"VVV DE {BEACON_NAME} "
        f"{CUSTOM_TEXT} "
        f"LOC {BEACON_LOC} "
        f"CPU {cpu} "
        f"RAM {used}/{total}MB PEAK {peak_ram}MB "
        f"UP {uptime}MIN "
        f"TEMP {temp} "
        f"HUM {hum} "
        f"TIME {now.strftime('%H%M%S')}UTC "
        f"QSL {BEACON_EMAIL} "
        f"BT #"
    )

def transmit(beacon_text):
    print(f"TX: {beacon_text}")
    text_to_cw_wav(beacon_text, '/tmp/beacon.wav')
    subprocess.run([
        'rpitx', '-m', 'USB',
        '-i', '/tmp/beacon.wav',
        '-f', str(BEACON_FREQ)
    ])

def main():
    print(f"LibreBeacon b1.0.0 starting")
    print(f"Frequency: {BEACON_FREQ} kHz")
    print(f"WPM: {WPM}")
    print(f"Location: {BEACON_LOC}")
    threading.Thread(target=ram_monitor, daemon=True).start()
    while True:
        try:
            beacon_text = build_beacon()
            transmit(beacon_text)
        except Exception as e:
            print(f"Error: {e}")
        print(f"Waiting " + PAUSE_LENGTH + "s...")
        time.sleep(PAUSE_LENGTH)

import threading
import time

peak_ram = 0
running = True

def ram_monitor():
    global peak_ram, running

    while running:
        used, _ = get_ram_mb()
        if used > peak_ram:
            peak_ram = used

        time.sleep(1)

if __name__ == "__main__":
    main()
