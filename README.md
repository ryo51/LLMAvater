# Project Novise: Local AI Virtual Assistant

[cite_start]完全ローカル環境で動作する、音声対話およびシチュエーションボイス生成が可能なパーソナルAIアシスタントシステムです [cite: 1]。

## 🚀 プロジェクト概要 (Overview)
[cite_start]映画『アイアンマン』のJ.A.R.V.I.S.のような、高度な対話能力と実在感を持つパーソナルAIアシスタントの構築を目指したプロジェクトです [cite: 1]。
[cite_start]マイク音声入力、LLMによるテキスト生成、音声合成、そして3D/Live2Dモデルの視覚的な同期（リップシンク）までの一連のパイプライン（The Loop）をPythonで統合制御しています [cite: 1, 3]。

[cite_start]外部のAPI課金を行わず、プライバシー保護とランニングコストゼロを実現するため、すべての処理をローカル環境のOSSのみで完結させている点が特徴です [cite: 1, 2]。

## 🛠 技術スタック (Technology Stack)
[cite_start]単一のコンシューマー向けGPU（NVIDIA GeForce RTX 4060 Ti）のリソース制約内で動作するよう、各AIモデルを最適化して組み合わせています [cite: 2, 4]。

| 機能 | 役割 | 採用技術・ツール | 選定理由・設定方針 |
| :--- | :--- | :--- | :--- |
| **メイン制御** | パイプライン統合 | Python (`asyncio`) | 非同期処理による全体制御とモジュール化 |
| **耳 (Input)** | 音声認識 | `faster-whisper` | [cite_start]VRAM消費を抑えるため、CPU実行/int8量子化モデルを採用 [cite: 3, 4] |
| **脳 (Process)** | 思考エンジン | `Ollama` + `Llama3` / `Qwen 2.5` | [cite_start]日本語性能が高く軽量な4bit量子化モデルをローカルAPI化 [cite: 3] |
| **口 (Output)** | 音声合成 | `So-VITS-SVC` (GPT-SoVITS) | [cite_start]WebUIのAPI機能を利用し、PythonからHTTPリクエストでWAV生成 [cite: 3] |
| **顔 (Visual)** | アバター表示 | `VTube Studio` | [cite_start]WebSocket(UDP)通信を用いたリアルタイムなリップシンク制御 [cite: 3] |
| **UI** | ユーザーインターフェース | `Gradio` | ブラウザベースでの再帰的思考チャット用WebUIの構築 |

## 💡 主な機能 (Key Features)
1. **Chat Mode (対話モード)**
   [cite_start]マイクからの音声入力をトリガーに、LLMが文脈を判断して応答し、アバターが音声に合わせて口を動かします [cite: 3, 5]。WebUI上ではシステムプロンプトによる「再帰的思考（理解・回答の分離）」プロトコルを実装しています。
2. **Script Mode (台本読み上げモード)**
   事前に用意されたテキストファイル（台本）を順次読み上げ、自然な行間の「間」を取りながら音声を連続再生します。
3. **Generation Mode (コンテンツ生成・一括変換モード)**
   キャラクター設定やシチュエーションのヒアリングを元に、LLMが長尺の台本を自動生成し、各セリフを自動で音声ファイル（WAV）として一括保存します。

## 🔥 技術的挑戦と工夫 (Technical Challenges)
- **VRAMリソース管理の最適化**
  [cite_start]RTX 4060 TiのVRAM容量内で「音声認識・LLM・音声合成」を同時に稼働させるため、ロード時間の長いLLMを常駐（5-6GB消費）させつつ、音声認識（Whisper）をCPUへ逃がすなど、ハードウェア制約を意識した動的制御を設計しました [cite: 4]。
- **モジュール指向設計と非同期処理**
  [cite_start]`Ear`(入力)、`Brain`(思考)、`Voice`(出力)、`Face`(視覚)のように機能ごとにクラスを独立させ、メンテナンス性を向上させました [cite: 3]。また、`asyncio` による非同期通信を活用し、音声合成やAPIの通信待ち時間によってメインループがブロックされないように構築しています。

## 📅 ロードマップ (Roadmap)
- [x] [cite_start]Phase 1: コア・ループの実装（マイク入力〜音声認識〜LLM〜音声合成の自動パイプライン化） [cite: 5]
- [x] [cite_start]Phase 2: VTube Studio連携によるリアルタイムな視覚同期・リップシンクの実装 [cite: 5]
- [x] Phase 3: GradioによるWebUIの構築および詳細なコンテンツ生成モードの実装
- [ ] [cite_start]Phase 4: ローカルドキュメントを参照するRAG (Retrieval-Augmented Generation) の導入 [cite: 5]
- [ ] [cite_start]Phase 5: Blender等と連携した感情パラメータに基づくモーション自動生成 [cite: 5]