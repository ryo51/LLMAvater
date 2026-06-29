import aiohttp
from colorama import Fore, Style
import config

class Brain:
    def __init__(self):
        pass

    import aiohttp
from colorama import Fore, Style
import config

class Brain:
    def __init__(self):
        pass

    async def think(self, text):
        """(旧) 通常のChatモード用"""
        return await self.think_advanced(f"\nUser:{text}\nAI:")

    async def think_advanced(self, full_prompt):
        """
        (新) プロンプトを完全に制御できるメソッド
        WebUIや再帰的思考プロンプト用
        """
        print(f"{Fore.YELLOW}Thinking...{Style.RESET_ALL}")
        async with aiohttp.ClientSession() as session:
            payload = {
                "model": config.LLM_MODEL, 
                "prompt": full_prompt, 
                "stream": False,
                "options": {
                    "num_ctx": 4096, # コンテキスト長を確保
                    "temperature": 0.7
                }
            }
            
            try:
                async with session.post(config.OLLAMA_URL, json=payload) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        response = data.get("response", "")
                        return response
                    else:
                        print(f"{Fore.RED}LLM Error: {resp.status}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}Connection Error: {e}{Style.RESET_ALL}")
                return "エラーが発生しました。"
        return ""
    
    async def generate_scenario(self, settings):
            """詳細設定を受け取り、長尺の台本を生成する"""
            print(f"{Fore.YELLOW}[Brain] Writing detailed scenario...{Style.RESET_ALL}")
            
            # プロンプトエンジニアリング
            system_prompt = (
                "あなたはプロ脚本家です。\n"
                "以下の【設定資料】に基づき、リスナーを没入させる魅力的な台本を作成してください。\n"
                "\n"
                "【要件】\n"
                "1. **セリフのみ**を出力してください（ト書きや効果音の説明は不要）。\n"
                "2. **最低でも15行以上**のセリフを書いて、物語の「導入・展開・結末」を作ってください。\n"
                "3. キャラクターの口調や性格を徹底的に反映させてください。\n"
                "4. 1行1行は短めに、息遣いや「間」を感じさせるように。\n"
                "\n"
                "【設定資料】\n"
                f"1. キャラクター・衣装: {settings['char']}\n"
                f"2. シチュエーション: {settings['sit']}\n"
                f"3. 外見・特徴: {settings['look']}\n"
                "\n"
                "それでは、台本のみを出力してください。\n"
                "Start:"
            )

            async with aiohttp.ClientSession() as session:
                # 7bモデルだと長い出力が途中で切れることがあるため、必要ならnum_ctxなどを調整
                payload = {
                    "model": config.LLM_MODEL, 
                    "prompt": system_prompt, 
                    "stream": False,
                    "options": {
                        "num_predict": 1024, # 長文出力を許可
                        "temperature": 0.8   # 少し創造的に
                    }
                }
                
                try:
                    async with session.post(config.OLLAMA_URL, json=payload) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data.get("response", "")
                        else:
                            print(f"{Fore.RED}LLM Error: {resp.status}{Style.RESET_ALL}")
                except Exception as e:
                    print(f"{Fore.RED}Connection Error: {e}{Style.RESET_ALL}")
            return ""