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
    track_names = [f"{i}: {t.name or 'Untitled'}" for i, t in enumerate(midi.tracks)]
    selected_index = st.selectbox("使用するMIDIトラックを選択", range(len(track_names)), format_func=lambda i: track_names[i])
    selected_track = midi.tracks[selected_index]

    # ノートのタイミング抽出
    note_times = []
    current_time = 0
    for msg in selected_track:
        current_time += msg.time
        if msg.type == 'note_on' and msg.velocity > 0:
            note_times.append(current_time)

    # 時間に変換
    ticks_per_beat = midi.ticks_per_beat
    tempo = 500000  # default 120BPM
    for msg in midi.tracks[0]:
        if msg.type == 'set_tempo':
            tempo = msg.tempo
            break

    def tick_to_sec(t): return t * tempo / ticks_per_beat / 1_000_000

    note_times_sec = [tick_to_sec(t) for t in note_times]

    # 出力クリップ作成
    output_clips = []

    if media_type == "video":
        clip = VideoFileClip(media_path)
        for i, t in enumerate(note_times_sec):
            if t + duration <= clip.duration:
                subclip = clip.subclip(t, t + duration)
                if use_flip and i % 2 == 1:
                    subclip = subclip.fx(vfx.mirror_x)
                output_clips.append(subclip)

    elif media_type == "image":
        for i, t in enumerate(note_times_sec):
            img_clip = ImageClip(media_path).set_duration(duration)
            if use_flip and i % 2 == 1:
                img_clip = img_clip.fx(vfx.mirror_x)
            output_clips.append(img_clip)

    # 動画書き出し
    if output_clips:
        final_clip = concatenate_videoclips(output_clips, method="compose")
        output_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
        final_clip.write_videofile(output_path, fps=24, audio=False)

        st.success("動画を生成しました！")
        st.video(output_path)
        with open(output_path, "rb") as f:
            st.download_button("動画をダウンロード", f.read(), file_name="output.mp4")
    else:
        st.warning("有効な音符タイミングが見つかりませんでした。")
