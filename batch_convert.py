import asyncio
import os
import time
from colorama import init, Fore, Style
import config

from modules.speaking import Voice

async def batch_process(input_file):
    """テキストファイルを読み込み、音声ファイルとして一括保存する"""
    
    if not os.path.exists(input_file):
        print(f"{Fore.RED}Error: File '{input_file}' not found.{Style.RESET_ALL}")
        return

    voice = Voice(avatar_client=None)

    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_dir = os.path.join(config.OUTPUT_DIR, f"{base_name}_{int(time.time())}")
    os.makedirs(output_dir, exist_ok=True)

    print(f"{Fore.CYAN}=== Batch Conversion Started ==={Style.RESET_ALL}")
    print(f"Reading from: {input_file}")
    print(f"Saving to:    {output_dir}")

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    count = 1
    total_lines = len([l for l in lines if l.strip()])

    for i, line in enumerate(lines):
        text = line.strip()

        if not text: continue
        if text.startswith("#") or text.startswith("//"): continue
        if text.startswith("(") or text.startswith("（"): continue

        filename = f"{count:03d}_voice.wav"
        output_path = os.path.join(output_dir, filename)

        print(f"[{count}/{total_lines}] Processing: {text[:20]}...")

        success = await voice.save_audio_file(text, output_path)

        if success:
            count += 1
            await asyncio.sleep(0.5)
        else:
            print(f"{Fore.RED}Failed to process line {i+1}{Style.RESET_ALL}")

    print(f"\n{Fore.GREEN}=== Conversion Complete! ==={Style.RESET_ALL}")
    print(f"Saved {count-1} files in: {output_dir}")

if __name__ == "__main__":
    init(autoreset=True)
    config.check_dependencies()
    
    # 誰の環境でも動くように相対パスに修正
    TARGET_FILE = "./test_script.txt" 
    
    try:
        asyncio.run(batch_process(TARGET_FILE))
    except KeyboardInterrupt:
        print("\nAborted.")