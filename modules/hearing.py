import asyncio
import sounddevice as sd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from faster_whisper import WhisperModel
from colorama import Fore, Style
import config

class Ear:
    def __init__(self):
        print(f"{Fore.CYAN}[Ear] Initializing Whisper...{Style.RESET_ALL}")
        # モデルロード（重い処理）
        self.stt_model = WhisperModel("medium", device="cpu", compute_type="int8")
        self.executor = ThreadPoolExecutor(max_workers=1)

    async def listen(self):
        """マイク入力を監視し、音声データを返す"""
        loop = asyncio.get_running_loop()
        print(f"{Fore.CYAN}Listening...{Style.RESET_ALL}")
        audio_buffer = []
        is_speaking = False
        silence_start = None
        queue = asyncio.Queue()

        def callback(indata, frames, time, status):
            loop.call_soon_threadsafe(queue.put_nowait, indata.copy())

        with sd.InputStream(samplerate=config.SAMPLE_RATE, channels=1, callback=callback):
            while True:
                indata = await queue.get()
                vol = np.linalg.norm(indata) * 10
                
                if vol > config.VAD_THRESHOLD:
                    if not is_speaking:
                        print(f"{Fore.GREEN}●{Style.RESET_ALL}", end="\r")
                        is_speaking = True
                    silence_start = None
                    audio_buffer.append(indata)
                elif is_speaking:
                    audio_buffer.append(indata)
                    if silence_start is None: silence_start = loop.time()
                    elif loop.time() - silence_start > config.SILENCE_DURATION:
                        break
        
        return np.concatenate(audio_buffer, axis=0).flatten()

    async def transcribe(self, audio_data):
        """音声データをテキストに変換"""
        loop = asyncio.get_running_loop()
        def _run():
            segments, _ = self.stt_model.transcribe(audio_data, beam_size=5, language="ja")
            return "".join([s.text for s in segments])
        
        return await loop.run_in_executor(self.executor, _run)