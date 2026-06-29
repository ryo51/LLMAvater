import asyncio
import os
import time
from colorama import init, Fore, Style
import config
from WebUI import launch_webui

# 各モジュールの読み込み
from modules.avatar import FaceClient
from modules.hearing import Ear
from modules.thinking import Brain
from modules.speaking import Voice

async def chat_mode(ear, brain, voice):
    """いつもの会話モード"""
    print(f"{Fore.GREEN}=== Chat Mode Started ==={Style.RESET_ALL}")
    while True:
        # 聞く
        audio = await ear.listen()
        text = await ear.transcribe(audio)
        
        if not text: continue
        print(f"You: {text}")
        
        # 考える
        response = await brain.think(text)
        print(f"Novise: {response}")
        
        # 話す
        await voice.speak_with_lipsync(response)

async def script_mode(voice):
    """台本読み上げモード"""
    script_path = "script.txt"
    
    if not os.path.exists(script_path):
        print(f"{Fore.RED}エラー: {script_path} が見つかりません。{Style.RESET_ALL}")
        return

    print(f"{Fore.YELLOW}=== Script Mode Started ==={Style.RESET_ALL}")
    print(f"Reading from: {script_path}")

    with open(script_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    total_lines = len(lines)
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line: continue  # 空行はスキップ

        print(f"\n{Fore.CYAN}[Line {i+1}/{total_lines}] {line}{Style.RESET_ALL}")
        
        # 話す (生成→再生が終わるまで待機するので、順次再生される)
        await voice.speak_with_lipsync(line)
        
        # 行間の自然な間 (設定値に基づく)
        await asyncio.sleep(config.SILENCE_DURATION)

    print(f"{Fore.GREEN}=== Script Finished ==={Style.RESET_ALL}")

async def generation_mode(brain, voice):
    """
    モード3: コンテンツ生成モード (詳細設定版)
    """
    print(f"{Fore.YELLOW}=== Content Generation Mode (Detail Ver.) ==={Style.RESET_ALL}")
    
    # --- 詳細ヒアリング（就活向けにクリーンな例に変更） ---
    print("台本生成のための設定を入力してください。")
    
    print(f"\n{Fore.CYAN}[1/4] キャラクター・役割{Style.RESET_ALL}")
    print("例: 優秀な秘書、親しみやすい案内役、冷静なオペレーター")
    char_inp = input(">> ").strip() or "指定なし"

    print(f"\n{Fore.CYAN}[2/4] シチュエーションの傾向{Style.RESET_ALL}")
    print("例: スケジュール確認、観光ガイド、システムトラブル対応")
    sit_inp = input(">> ").strip() or "指定なし"
    
    print(f"\n{Fore.CYAN}[3/4] 外見・特徴{Style.RESET_ALL}")
    print("例: スーツ姿、メガネ着用、落ち着いた声")
    look_inp = input(">> ").strip() or "指定なし"

    print(f"\n{Fore.CYAN}[4/4] 会話のトーン (任意){Style.RESET_ALL}")
    print("例: 丁寧、フレンドリー、論理的")
    play_inp = input(">> ").strip() or "特になし"

    # 設定辞書を作成
    settings = {
        "char": char_inp,
        "sit": sit_inp,
        "look": look_inp,
        "play": play_inp
    }
    
    # フォルダ名用にシチュエーションを使用
    safe_name = sit_inp.replace("/", "_").replace("\\", "_")[:15]

    # --- 台本生成 ---
    script_text = await brain.generate_scenario(settings)
    
    # 台本保存
    with open(config.SCRIPT_FILENAME, "w", encoding="utf-8") as f:
        f.write(script_text)
    
    print(f"\n{Fore.GREEN}--- 生成された台本 ---{Style.RESET_ALL}")
    print(script_text)
    print(f"{Fore.GREEN}----------------------{Style.RESET_ALL}")
    print(f"台本を '{config.SCRIPT_FILENAME}' に保存しました。")
    print("内容を修正する場合は、今テキストエディタで編集して保存してください。")
    
    confirm = input("音声生成を開始しますか？ (y/n): ").strip().lower()
    if confirm != 'y':
        print("キャンセルしました。")
        return

    # --- 音声生成ループ ---
    save_dir = os.path.join(config.OUTPUT_DIR, f"{safe_name}_{int(time.time())}")
    os.makedirs(save_dir, exist_ok=True)
    
    # 修正後のファイルを再読み込み
    with open(config.SCRIPT_FILENAME, "r", encoding="utf-8") as f:
        lines = f.readlines()

    count = 1
    print(f"{Fore.CYAN}Saving wav files to: {save_dir}{Style.RESET_ALL}")

    for line in lines:
        text = line.strip()
        if not text: continue
        if text.startswith("(") or text.startswith("（"): continue
        if text.startswith("【") or text.startswith("["): continue 

        filename = f"{count:03d}_voice.wav"
        output_path = os.path.join(save_dir, filename)

        success = await voice.save_audio_file(text, output_path)
        
        if success:
            count += 1
            await asyncio.sleep(0.5)

    print(f"{Fore.GREEN}=== All Recordings Finished! ({count-1} files saved) ==={Style.RESET_ALL}")

async def main():
    init(autoreset=True)
    config.check_dependencies()
    
    print(f"{Fore.CYAN}=== Project Novise (Creator Ver.) ==={Style.RESET_ALL}")

    avatar = FaceClient(config.VTS_IP, config.VTS_PORT)
    voice = Voice(avatar_client=avatar)
    brain = Brain()
    
    print("Select Mode:")
    print("1: Chat Mode (Whisper + LLM)")
    print("2: Script Mode (Read script.txt & Speak)")
    print("3: Generation Mode (Create Script & Save WAVs)")
    print("4: WebUI Mode (Browser Chat)")
    mode = input(">> ").strip()

    try:
        if mode == "1":
            ear = Ear()
            await chat_mode(ear, brain, voice)
        elif mode == "2":
            await script_mode(voice)
        elif mode == "3":
            await generation_mode(brain, voice)
        elif mode == "4":
            launch_webui()
        else:
            print("Invalid selection.")
    except KeyboardInterrupt:
        print("\n停止しました。")

if __name__ == "__main__":
    asyncio.run(main())