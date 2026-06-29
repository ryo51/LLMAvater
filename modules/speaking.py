import asyncio
import os
import soundfile as sf
import sounddevice as sd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from colorama import Fore, Style
import config
import shutil

# 安全装置付きインポート
try:
    from gradio_client import Client, handle_file as file_wrapper
except ImportError:
    from gradio_client import Client, file as file_wrapper

class Voice:
    def __init__(self, avatar_client):
        self.avatar = avatar_client
        self.executor = ThreadPoolExecutor(max_workers=1)
        try:
            self.tts_client = Client(config.SOVITS_URL)
            print(f"{Fore.GREEN}[TTS] GPT-SoVITS Connected.{Style.RESET_ALL}")
        except:
            print(f"{Fore.RED}[TTS] Connection Failed.{Style.RESET_ALL}")

    async def speak_with_lipsync(self, text):
        """音声を生成し、リップシンク付きで再生する"""
        print(f"{Fore.MAGENTA}[Generating Voice...]{Style.RESET_ALL}")
        
        if not os.path.exists(config.REF_WAV_PATH):
            print(f"{Fore.RED}Error: Reference wav not found.{Style.RESET_ALL}")
            return

        try:
            loop = asyncio.get_running_loop()
            
            # 1. 音声生成 (重い処理なのでExecutorで実行)
            def _call_tts():
                return self.tts_client.predict(
                    ref_wav_path=file_wrapper(config.REF_WAV_PATH),
                    prompt_text=config.REF_TEXT,
                    prompt_language=config.REF_LANG,
                    text=text,
                    text_language="日文",
                    how_to_cut="凑四句一切",
                    top_k=5, top_p=1, temperature=1, ref_free=False, speed=1,
                    if_freeze=False, inp_refs=None, sample_steps=32, if_sr=False, pause_second=0.3,
                    api_name="/get_tts_wav"
                )
            
            result_path = await loop.run_in_executor(self.executor, _call_tts)
            
            # 2. 音声読み込み
            data, fs = sf.read(result_path)
            
            # 3. リップシンク再生
            print(f"{Fore.MAGENTA}♪ Speaking...{Style.RESET_ALL}")
            await self._play_and_sync(data, fs)

        except Exception as e:
            print(f"{Fore.RED}TTS Error: {e}{Style.RESET_ALL}")
            import traceback
            traceback.print_exc()

    async def _play_and_sync(self, data, fs):
        """再生コールバック内で口の動きを計算して送信"""
        loop = asyncio.get_running_loop()
        block_size = 1024 
        current_pos = 0
        
        def callback(outdata, frames, time, status):
            nonlocal current_pos
            if status: print(status)
            
            chunk_size = len(outdata)
            remaining = len(data) - current_pos
            
            if remaining <= 0:
                outdata.fill(0)
                raise sd.CallbackStop
            
            valid_frames = min(chunk_size, remaining)
            chunk = data[current_pos : current_pos + valid_frames]
            
            # ステレオ/モノラル調整
            if len(chunk.shape) == 1:
                chunk = chunk.reshape(-1, 1)
            if chunk.shape[1] == 1 and outdata.shape[1] == 2:
                 chunk_to_write = np.tile(chunk, (1, 2))
            else:
                chunk_to_write = chunk

            outdata[:valid_frames] = chunk_to_write
            if valid_frames < chunk_size:
                outdata[valid_frames:] = 0
            
            # --- リップシンク計算 ---
            rms = np.sqrt(np.mean(chunk**2))
            mouth_open = min(rms * 5.0, 1.0)
            
            # アバターへ送信 (非同期実行)
            asyncio.run_coroutine_threadsafe(
                self.avatar.send_mouth_value(mouth_open), loop
            )
            
            current_pos += valid_frames

        # 再生開始
        with sd.OutputStream(samplerate=fs, channels=2, callback=callback):
            duration = len(data) / fs
            await asyncio.sleep(duration + 0.5)
            await self.avatar.send_mouth_value(0.0) # 最後に口を閉じる
    async def save_audio_file(self, text, output_filename):
            """音声を生成し、指定したパスにWAVとして保存する（再生はしない）"""
            print(f"{Fore.MAGENTA}[Recording] Generating: {text[:10]}...{Style.RESET_ALL}")
            
            if not os.path.exists(config.REF_WAV_PATH):
                print(f"{Fore.RED}Error: Reference wav not found.{Style.RESET_ALL}")
                return False

            try:
                loop = asyncio.get_running_loop()
                
                # 音声生成 (So-VITS)
                def _call_tts():
                    return self.tts_client.predict(
                        ref_wav_path=file_wrapper(config.REF_WAV_PATH),
                        prompt_text=config.REF_TEXT,
                        prompt_language=config.REF_LANG,
                        text=text,
                        text_language="日文",
                        how_to_cut="凑四句一切",
                        top_k=5, top_p=1, temperature=1, ref_free=False, speed=1,
                        if_freeze=False, inp_refs=None, sample_steps=32, if_sr=False, pause_second=0.3,
                        api_name="/get_tts_wav"
                    )
                
                # 一時ファイルのパスを取得
                temp_path = await loop.run_in_executor(self.executor, _call_tts)
                
                # 指定した場所にコピー保存
                shutil.copy(temp_path, output_filename)
                print(f"{Fore.CYAN}  -> Saved: {output_filename}{Style.RESET_ALL}")
                return True

            except Exception as e:
                print(f"{Fore.RED}Recording Error: {e}{Style.RESET_ALL}")
                return False