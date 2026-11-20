import os
import re
import math
import shutil
import numpy as np
from gtts import gTTS
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import *
from moviepy.audio.AudioClip import AudioClip

WIDTH, HEIGHT = 1920, 1080
FPS = 30
IZLAZNI_FAJL = "Epizoda_04_Rekviziti_SFX.mp4"

def ucitaj_font(velicina):
    for putanja in ["/system/fonts/Roboto-Bold.ttf", "/system/fonts/DroidSans-Bold.ttf"]:
        if os.path.exists(putanja):
            return ImageFont.truetype(putanja, velicina)
    return ImageFont.load_default()

# --- 1. POZADINA, OBLACI I DRVO S JABUKAMA ---
def pripremi_grafiku():
    # Pozadina + Drvo na sredini (X=960)
    img = Image.new("RGB", (WIDTH, HEIGHT), (115, 205, 255))
    draw = ImageDraw.Draw(img)
    draw.ellipse((1550, 80, 1780, 310), fill=(255, 225, 50), outline=(255, 190, 0), width=8)
    draw.ellipse((-200, 680, 1100, 1200), fill=(76, 187, 23))
    draw.ellipse((700, 650, 2200, 1200), fill=(60, 165, 20))
    draw.rectangle((0, 820, WIDTH, HEIGHT), fill=(50, 155, 25))
    
    # Deblo drveta
    draw.rectangle((915, 520, 1005, 840), fill=(120, 72, 30), outline=(70, 40, 15), width=6)
    # Krošnja drveta
    for kx, ky, r in [(960, 420, 170), (830, 470, 130), (1090, 470, 130), (880, 340, 120), (1040, 340, 120)]:
        draw.ellipse((kx-r, ky-r, kx+r, ky+r), fill=(34, 139, 34), outline=(20, 95, 20), width=5)
    img.save("pozadina_baza.png")

    # Oblaci
    oblaci = Image.new("RGBA", (WIDTH, 400), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(oblaci)
    for cx, cy in [(150, 100), (750, 60), (1350, 130)]:
        odraw.ellipse((cx, cy, cx+220, cy+110), fill=(255, 255, 255, 230))
        odraw.ellipse((cx+60, cy-40, cx+260, cy+100), fill=(255, 255, 255, 230))
        odraw.ellipse((cx+130, cy+10, cx+320, cy+110), fill=(255, 255, 255, 230))
    oblaci.save("oblaci_sloj.png")

    # Rekviziti: Jabuke (0, 1, 2, 3 jabuke na krošnji)
    pozicije_jabuka = [(860, 440), (960, 360), (1060, 440)]
    for broj in range(4):
        j_img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        j_draw = ImageDraw.Draw(j_img)
        for idx in range(broj):
            jx, jy = pozicije_jabuka[idx]
            j_draw.ellipse((jx-32, jy-32, jx+32, jy+32), fill=(235, 30, 30), outline=(120, 0, 0), width=4)
            j_draw.rectangle((jx-4, jy-45, jx+4, jy-30), fill=(90, 50, 15))
            j_draw.ellipse((jx+2, jy-46, jx+22, jy-34), fill=(50, 200, 50))
        j_img.save(f"jabuke_{broj}.png")

def nacrtaj_stanje_lika(boja_tijela, otvorena_usta, zatvorene_oci, smjer_desno, fajl):
    img = Image.new("RGBA", (340, 340), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((20, 20, 320, 320), fill=boja_tijela, outline=(35, 35, 35), width=8)
    if zatvorene_oci:
        draw.line((95, 130, 145, 130), fill=(0, 0, 0), width=6)
        draw.line((195, 130, 245, 130), fill=(0, 0, 0), width=6)
    else:
        draw.ellipse((95, 100, 145, 150), fill=(255, 255, 255), outline=(0, 0, 0), width=4)
        draw.ellipse((195, 100, 245, 150), fill=(255, 255, 255), outline=(0, 0, 0), width=4)
        pomak = 8 if smjer_desno else -8
        draw.ellipse((112+pomak, 115, 132+pomak, 135), fill=(0, 0, 0))
        draw.ellipse((212+pomak, 115, 232+pomak, 135), fill=(0, 0, 0))
    if otvorena_usta:
        draw.ellipse((135, 175, 205, 235), fill=(180, 20, 40), outline=(0, 0, 0), width=5)
        draw.chord((145, 195, 195, 230), start=0, end=180, fill=(255, 120, 140))
    else:
        draw.arc((120, 155, 220, 230), start=15, end=165, fill=(0, 0, 0), width=7)
    img.save(fajl)

def pripremi_likove():
    nacrtaj_stanje_lika((255, 205, 0), False, False, True, "zuco_idle.png")
    nacrtaj_stanje_lika((255, 205, 0), True, False, True, "zuco_talk.png")
    nacrtaj_stanje_lika((255, 205, 0), False, True, True, "zuco_blink.png")
    nacrtaj_stanje_lika((70, 160, 255), False, False, False, "plavko_idle.png")
    nacrtaj_stanje_lika((70, 160, 255), True, False, False, "plavko_talk.png")
    nacrtaj_stanje_lika((70, 160, 255), False, True, False, "plavko_blink.png")

def animiraj_lika_klip(prefiks, prica, trajanje, baza_x, baza_y):
    img_idle = np.array(Image.open(f"{prefiks}_idle.png"))
    img_talk = np.array(Image.open(f"{prefiks}_talk.png"))
    img_blink = np.array(Image.open(f"{prefiks}_blink.png"))

    def make_frame(t):
        if (t % 3.0) > 2.85: return img_blink[:, :, :3]
        if prica and (int(t * 10) % 2 == 0): return img_talk[:, :, :3]
        return img_idle[:, :, :3]

    def make_mask(t):
        if (t % 3.0) > 2.85: return img_blink[:, :, 3] / 255.0
        if prica and (int(t * 10) % 2 == 0): return img_talk[:, :, 3] / 255.0
        return img_idle[:, :, 3] / 255.0

    klip = VideoClip(make_frame, duration=trajanje).set_mask(VideoClip(make_mask, ismask=True, duration=trajanje))
    def pozicija(t):
        dy = abs(math.sin(t * 8)) * 40 if prica else math.sin(t * 2) * 6
        return (baza_x, int(baza_y - dy))
    return klip.set_position(pozicija)

def kreiraj_titl(ime_lika, tekst, trajanje, indeks):
    img = Image.new("RGBA", (WIDTH, 200), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    font = ucitaj_font(48)
    puni_tekst = f"{ime_lika}: {tekst}"
    bbox = draw.textbbox((0, 0), puni_tekst, font=font)
    x = (WIDTH - (bbox[2] - bbox[0])) // 2
    y = 50
    for dx in [-3, 0, 3]:
        for dy in [-3, 0, 3]:
            draw.text((x+dx, y+dy), puni_tekst, font=font, fill=(0, 0, 0, 255))
    boja = (255, 235, 100, 255) if ime_lika == "ŽUĆO" else (150, 220, 255, 255)
    draw.text((x, y), puni_tekst, font=font, fill=boja)
    titl_path = f"temp_titl_{indeks}.png"
    img.save(titl_path)
    return ImageClip(titl_path).set_duration(trajanje).set_position(("center", HEIGHT - 160))

# --- 2. ZVUČNI EFEKTI (POP SFX) I MUZIKA ---
def generisi_pop_sfx():
    trajanje = 0.25
    def make_frame(t):
        t_arr = np.asarray(t)
        freq = 350 + 900 * t_arr
        val = 0.25 * np.sin(2 * np.pi * freq * t_arr) * np.exp(-15 * t_arr)
        if t_arr.ndim == 0: return np.array([val, val])
        return np.column_stack([val, val])
    return AudioClip(make_frame, duration=trajanje, fps=44100)

def generisi_muziku(trajanje):
    note = np.array([261.63, 329.63, 392.00, 523.25, 392.00, 329.63])
    def make_frame(t):
        t_arr = np.asarray(t)
        idx = np.floor(t_arr * 2.5).astype(int) % len(note)
        freq = note[idx]
        val = 0.03 * np.sin(2 * np.pi * freq * t_arr) * np.exp(-3 * (t_arr % 0.4))
        if t_arr.ndim == 0: return np.array([val, val])
        return np.column_stack([val, val])
    return AudioClip(make_frame, duration=trajanje, fps=44100)

pripremi_grafiku()
pripremi_likove()

with open("prica.txt", "r", encoding="utf-8") as f:
    linije = [l.strip() for l in f if l.strip()]

klipovi = []
ukupno_vrijeme = 0
prethodne_jabuke = 0

for i, linija in enumerate(linije):
    if linija.startswith("PLAVKO:"):
        govornik = "PLAVKO"
        ostatak = linija.replace("PLAVKO:", "").strip()
        tld = "com.au"
    else:
        govornik = "ŽUĆO"
        ostatak = linija.replace("ZUCO:", "").strip()
        tld = "hr"

    match = re.search(r"\[JABUKE:(\d+)\]", ostatak)
    broj_jabuka = int(match.group(1)) if match else prethodne_jabuke
    broj_jabuka = max(0, min(3, broj_jabuka))
    tekst = re.sub(r"\[JABUKE:\d+\]", "", ostatak).strip()

    glas_fajl = f"glas_{i}.mp3"
    gTTS(text=tekst, lang="hr", tld=tld).save(glas_fajl)
    
    glas = AudioFileClip(glas_fajl)
    trajanje = glas.duration + 0.5
    
    pozadina = ImageClip("pozadina_baza.png").set_duration(trajanje)
    oblaci = ImageClip("oblaci_sloj.png").set_duration(trajanje).set_position(
        lambda t, offset=ukupno_vrijeme: (int(((offset + t) * 35) % 600 - 200), 60)
    )
    rekvizit = ImageClip(f"jabuke_{broj_jabuka}.png").set_duration(trajanje)
    
    zuco_klip = animiraj_lika_klip("zuco", govornik == "ŽUĆO", trajanje, 240, 490)
    plavko_klip = animiraj_lika_klip("plavko", govornik == "PLAVKO", trajanje, 1340, 490)
    titl = kreiraj_titl(govornik, tekst, trajanje, i)
    
    zvuk_scene = [glas]
    if broj_jabuka > prethodne_jabuke:
        zvuk_scene.append(generisi_pop_sfx())
    prethodne_jabuke = broj_jabuka
    
    kompozicija = CompositeVideoClip([pozadina, oblaci, rekvizit, zuco_klip, plavko_klip, titl]).set_audio(CompositeAudioClip(zvuk_scene))
    klipovi.append(kompozicija)
    ukupno_vrijeme += trajanje

finalni_video = concatenate_videoclips(klipovi, method="compose")
muzika = generisi_muziku(finalni_video.duration)
finalni_video = finalni_video.set_audio(CompositeAudioClip([finalni_video.audio, muzika]))

finalni_video.write_videofile(IZLAZNI_FAJL, fps=FPS, codec="libx264", audio_codec="aac", threads=4)

for i in range(len(linije)):
    for f in [f"glas_{i}.mp3", f"temp_titl_{i}.png"]:
        if os.path.exists(f): os.remove(f)

download_dir = os.path.expanduser("~/storage/shared/Download")
if os.path.exists(download_dir):
    shutil.copy(IZLAZNI_FAJL, download_dir)
