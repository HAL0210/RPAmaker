'''音声出力(s)
'''

import pyopenjtalk
import numpy as np
from scipy.io import wavfile
import winsound
from lib.paramSetting import getParam, loadParams
import time
from lib.decoratorSetting import *

import re

from lib.loggerSetting import getMyLogger

logger = getMyLogger(__name__)

loadParams('mod\sound.yaml')

# 日本語表記 → 半音番号
jp_notes = {
    'ド': 0, 'ド#': 1, 'レ♭': 1,
    'レ': 2, 'レ#': 3, 'ミ♭': 3,
    'ミ': 4,
    'ファ': 5, 'ファ#': 6, 'ソ♭': 6,
    'ソ': 7, 'ソ#': 8, 'ラ♭': 8,
    'ラ': 9, 'ラ#': 10, 'シ♭': 10,
    'シ': 11,
}

# 英語表記 → 半音番号
en_notes = {
    'C': 0, 'C#': 1, 'Db': 1,
    'D': 2, 'D#': 3, 'Eb': 3,
    'E': 4,
    'F': 5, 'F#': 6, 'Gb': 6,
    'G': 7, 'G#': 8, 'Ab': 8,
    'A': 9, 'A#': 10, 'Bb': 10,
    'B': 11,
}

# 休符として扱うキーワード
rest_keywords = {'休符', 'H', 'rest'}

# A4 = 440Hz、C4 = ド4
A4_freq = 440
C4_offset = -9  # ラ4よりド4は9半音下
C4_freq = A4_freq * 2 ** (C4_offset / 12)  # ≒ 261.63Hz

# 音名 → 周波数へ変換
def get_freq(note: str, default_octave=4) -> int | None:
    note = note.strip()

    # 休符なら None を返す
    if note in rest_keywords:
        return None
    
    # 音程,オクターブ分解
    match = re.match(r'^([^0-9]+[#b]?)(\d*)$', note)
    if match:
        name = match.group(1)
        octave = int(match.group(2)) if match.group(2) else default_octave

        if name in jp_notes:
            semitones = (octave - 4) * 12 + jp_notes[name]
            return round(C4_freq * (2 ** (semitones / 12)))
        if name in en_notes:
            semitones = (octave - 4) * 12 + en_notes[name]
            return round(C4_freq * (2 ** (semitones / 12)))

    raise ValueError(f"無効な音名です: {note}")

@instrumented(timer=True)
def playAction(text):
    """
    テキストを音声合成して再生する汎用アクション。

    説明:
        指定されたテキストを pyopenjtalk で音声合成し、
        wavファイルとして保存した後、即座に再生します。
        音声ファイルの出力先や音程(半音単位の調整)は設定ファイルから取得可能です。

    Args:
        text (str): 合成・再生する対象のテキスト文字列。

    Returns:
        None

    Raises:
        Exception: 合成処理、ファイル保存、再生時の各種エラー。

    Examples:
        >>> s.play: こんにちは。今日はいい天気ですね。
        テキストを音声合成して出力wavに保存後、すぐ再生する。

    Params:
        - s.sound_output_file (str): 出力wavファイルパス (デフォルト: "output.wav")
        - s.half_tone (float): 音程の上下調整。プラスで高く、マイナスで低くする (デフォルト: -3.0)
    """
    output_file = getParam('s.sound_output_file', 'output.wav')
    half_tone = float(getParam('s.half_tone', -3.0))
    x, sr = pyopenjtalk.tts(text, half_tone=half_tone)
    wavfile.write(output_file, sr, x.astype(np.int16))
    winsound.PlaySound(output_file, winsound.SND_FILENAME)


@instrumented(timer=True)
def beepAction(note_duration):
    try:
        note_str, dur_str = note_duration.split(',')
        ms = int(dur_str.strip())
        octave = int(getParam('s.default_octave', 4))

        freq = get_freq(note_str, octave)
        if freq == None:
            time.sleep(ms / 1000)
        elif 37 <= freq <= 32767:
            logger.info(f'freq:{freq}, ms:{ms}')
            winsound.Beep(freq, ms)
        else:
            time.sleep(ms / 1000)
    except Exception as e:
        raise ValueError(f"無効な入力です: {note_duration} ({e})")


# メッセージに対応する音を鳴らす関数
@instrumented()
def messageAction(msg):
    if msg in message_list:
        winsound.MessageBeep(message_list[msg])  # 対応する音を鳴らす
    else:
        raise ValueError(f"未対応のメッセージタイプ: {msg}")

# メッセージに対応する音のリスト
message_list = {
    'OK'         : winsound.MB_OK,
    'ASTERISK'   : winsound.MB_ICONASTERISK,
    'EXCLAMATION': winsound.MB_ICONEXCLAMATION,
    'HAND'       : winsound.MB_ICONHAND,
    'QUESTION'   : winsound.MB_ICONQUESTION
}

action_list = {
    'play'   : playAction,
    'beep'   : beepAction,
    'msg'    : messageAction,
}