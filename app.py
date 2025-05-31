# -*- coding: utf-8 -*-
import streamlit as st
from mido import MidiFile
from moviepy.editor import VideoFileClip, ImageClip, concatenate_videoclips, vfx
import tempfile
import os

st.set_page_config(page_title="MIDI × 動画・画像ツール", layout="centered")
st.title("MIDIに合わせて動画 or 画像をパッパッと出すツール")

# アップロードUI
midi_file = st.file_uploader("MIDIファイルをアップロード", type=["mid", "midi"])
video_file = st.file_uploader("動画ファイル（.mp4 / .mov など）", type=["mp4", "mov"])
image_file = st.file_uploader("画像ファイル（.png / .jpg）", type=["png", "jpg", "jpeg"])

use_flip = st.checkbox("音符ごとに左右反転を切り替える", value=False)
duration = st.slider("音符ごとの表示時間（秒）", 0.1, 1.0, 0.3, 0.1)

if midi_file and (video_file or image_file):
    # 一時保存
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as tmp_midi:
        tmp_midi.write(midi_file.read())
        midi_path = tmp_midi.name

    media_path = None
    if video_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_vid:
            tmp_vid.write(video_file.read())
            media_path = tmp_vid.name
        media_type = "video"
    elif image_file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
            tmp_img.write(image_file.read())
            media_path = tmp_img.name
        media_type = "image"
    else:
        media_type = None

    # MIDI処理
    midi = MidiFile(midi_path)
