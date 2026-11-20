import os
import math
import numpy as np
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import *
from moviepy.audio.AudioClip import AudioClip

WIDTH, HEIGHT = 1920, 1080
FPS = 30

def kreiraj_pozadinu(putanja="pozadina_hd.png"):
    img = Image.new("RGB", (WIDTH, HEIGHT), (115, 205, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse((1550, 80, 1780, 310), fill=(255, 225, 50), outline=(255, 190, 0), width=8)
    for cx, cy in [(250, 180), (850, 140), (1250, 230)]:
        draw.ellipse((cx, cy, cx+220, cy+110), fill=(255, 255, 255))
        draw.ellipse((cx+60, cy-40, cx+260, cy+100), fill=(255, 255, 255))
        draw.ellipse((cx+130, cy+10, cx+320, cy+110), fill=(255, 255, 255))
    draw.ellipse((-200, 680, 1100, 1200), fill=(76, 187, 23))
    draw.ellipse((700, 650, 2200, 1200), fill=(60, 165, 20))
    draw.rectangle((0, 820, WIDTH, HEIGHT), fill=(50, 155, 25))
    img.save(putanja)

def kreiraj_lika(putanja="lik_hd.png"):
    img = Image.new("RGBA", (320, 320), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((20, 20, 300, 300), fill=(255, 200, 0), outline=(40, 40, 40), width=8)
    draw.ellipse((95, 100, 145, 150), fill=(255, 255, 255), outline=(0, 0, 0), width=4)
    draw.ellipse((175, 100, 225, 150), fill=(255, 255, 255), outline=(0, 0, 0), width=4)
    draw.ellipse((112, 115, 132, 135), fill=(0, 0, 0))
    draw.ellipse((192, 115, 212, 135), fill=(0, 0, 0))
    draw.arc((100, 140, 220, 240), start=15, end=165, fill=(0, 0, 0), width=8)
    draw.ellipse((65, 165, 105, 195), fill=(255, 120, 120, 180))
    draw.ellipse((215, 165, 255, 195), fill=(255, 120, 120, 180))
    img.save(putanja)

def kreiraj_titl(tekst, trajanje, indeks):
    img = Image.new("RGBA", (WIDTH, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("/system/fonts/Roboto-Bold.ttf", 54)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), tekst, font=font)
    tw = bbox[2] - bbox[0]
    x = (WIDTH - tw) // 2
    y = 50
    
    for dx in [-3, 0, 3]:
        for dy in [-3, 0, 3]:
            draw.text((x+dx, y+dy), tekst, font=font, fill=(0, 0, 0, 255))
    draw.text((x, y), tekst, font=font, fill=(255, 255, 255, 255))
    
    titl_path = f"temp_titl_{indeks}.png"
    img.save(titl_path)
    return ImageClip(titl_path).set_duration(trajanje).set_position(("center", HEIGHT - 220))

def generisi_muziku(trajanje):
    note = np.array([261.63, 329.63, 392.00, 523.25, 392.00, 329.63])
    def make_frame(t):
        t_arr = np.asarray(t)
        idx = np.floor(t_arr * 2.5).astype(int) % len(note)
        freq = note[idx]
        val = 0.04 * np.sin(2 * np.pi * freq * t_arr) * np.exp(-3 * (t_arr % 0.4))
        if t_arr.ndim == 0:
            return np.array([val, val])
        return np.column_stack([val, val])
    return AudioClip(make_frame, duration=trajanje, fps=44100)

scenario = [
    {"tekst": "Zdravo drugari! Dobrodošli u našu čarobnu šumu učenja.", "start_x": 150, "end_x": 450},
    {"tekst": "Danas ćemo naučiti kako sunce pomaže cvijeću i drveću da rastu.", "start_x": 450, "end_x": 950},
    {"tekst": "Kada sija toplo sunce i padne malo kiše, priroda postaje zelena!", "start_x": 950, "end_x": 1350},
    {"tekst": "Hvala što ste gledali! Vidimo se u sljedećoj avanturi!", "start_x": 1350, "end_x": 1500}
]

kreiraj_pozadinu()
kreiraj_lika()

klipovi = []
for i, scena in enumerate(scenario):
    glas_fajl = f"glas_{i}.mp3"
    gTTS(text=scena["tekst"], lang="hr").save(glas_fajl)
    
    glas = AudioFileClip(glas_fajl)
    trajanje = glas.duration + 0.6
    
    pozadina = ImageClip("pozadina_hd.png").set_duration(trajanje)
    lik = ImageClip("lik_hd.png").set_duration(trajanje)
    titl = kreiraj_titl(scena["tekst"], trajanje, i)
    
    sx, ex = scena["start_x"], scena["end_x"]
    def kretanje(t, sx=sx, ex=ex, d=trajanje):
        napredak = t / d
        x = int(sx + (ex - sx) * napredak)
        y = int(580 - abs(math.sin(t * 6)) * 45)
        return (x, y)
        
    animirani_lik = lik.set_position(kretanje)
    kompozicija = CompositeVideoClip([pozadina, animirani_lik, titl]).set_audio(glas)
    klipovi.append(kompozicija)

finalni_video = concatenate_videoclips(klipovi, method="compose")
muzika = generisi_muziku(finalni_video.duration)
finalni_zvuk = CompositeAudioClip([finalni_video.audio, muzika])
finalni_video = finalni_video.set_audio(finalni_zvuk)

izlazni_fajl = "Epizoda_01_FullHD.mp4"
finalni_video.write_videofile(izlazni_fajl, fps=FPS, codec="libx264", audio_codec="aac", threads=4)

for i in range(len(scenario)):
    if os.path.exists(f"glas_{i}.mp3"): os.remove(f"glas_{i}.mp3")
    if os.path.exists(f"temp_titl_{i}.png"): os.remove(f"temp_titl_{i}.png")
