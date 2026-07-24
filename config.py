import os
import sys
from colorama import Fore, Style

# --- Windows GPU設定 ---
try:
    import nvidia.cudnn
    import nvidia.cublas
    os.add_dll_directory(os.path.dirname(nvidia.cudnn.__file__) + "/bin")
    os.add_dll_directory(os.path.dirname(nvidia.cublas.__file__) + "/bin")
except:
    pass

# --- 接続先設定 ---
OLLAMA_URL = "http://localhost:11434/api/generate"
LLM_MODEL = "llama3"
SOVITS_URL = "http://127.0.0.1:9872/" 

VTS_IP = "127.0.0.1"
VTS_PORT = 33333

# --- ファイル設定 ---
REF_WAV_PATH = "sample.wav"
REF_TEXT = "音声ファイルの文字起こしを入力してください" 
REF_LANG = "日文"

# --- 音声設定 ---
SAMPLE_RATE = 16000
VAD_THRESHOLD = 2.0 
SILENCE_DURATION = 1.5

# --- エラーハンドリング ---
def check_dependencies():
    try:
        from gradio_client import Client
    except ImportError:
        print(f"{Fore.RED}Error: gradio_client not found.{Style.RESET_ALL}")
        sys.exit(1)

OUTPUT_DIR = "Audiofiles"
SCRIPT_FILENAME = "generated_script.txt"
