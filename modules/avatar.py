from pythonosc import udp_client

class FaceClient:
    """
    VSeeFace/VMMを制御するクライアント (OSCプロトコル)
    """
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.client = udp_client.SimpleUDPClient(self.ip, self.port)
        print(f"✅ VMM Connected: {ip}:{port}")

    async def connect(self):
        # 将来的な拡張用
        return True

    async def send_mouth_value(self, ratio):
        """
        口の開き具合を送信
        ratio: 0.0 (閉) 〜 1.0 (開)
        """
        # VMCプロトコル: /VMC/Ext/Blend/Val (Name, Value)
        # 適用コマンド(/Apply)も送る必要がある
        self.client.send_message("/VMC/Ext/Blend/Val", ["A", float(ratio)])
        self.client.send_message("/VMC/Ext/Blend/Apply", [])