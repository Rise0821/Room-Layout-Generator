# config.py
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    COZE_API_BASE = os.getenv("COZE_API_BASE", "https://api.coze.com")  # 替换为实际的 API 基础 URL
    COZE_API_KEY = os.getenv("COZE_API_KEY")
    BOT_ID = os.getenv("BOT_ID")
    USER_ID = os.getenv("USER_ID")
    CONVERSATION_ID = os.getenv("CONVERSATION_ID")
    STREAMING = os.getenv("STREAMING", "False").lower() in ("true", "1", "t")

    REQUIRED_VARS = ["COZE_API_KEY", "BOT_ID", "USER_ID", "CONVERSATION_ID"]

    @classmethod
    def validate(cls):
        missing_vars = [var for var in cls.REQUIRED_VARS if not getattr(cls, var)]
        if missing_vars:
            raise EnvironmentError(f"缺少环境变量: {', '.join(missing_vars)}")
