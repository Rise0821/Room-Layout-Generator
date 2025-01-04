# chat.py
import json
from langchain_community.chat_models import ChatCoze
from langchain_core.messages import HumanMessage

def get_chat_response(description, config):
    chat = ChatCoze(
        coze_api_base=config.COZE_API_BASE,
        coze_api_key=config.COZE_API_KEY,
        bot_id=config.BOT_ID,
        user=config.USER_ID,
        conversation_id=config.CONVERSATION_ID,
        streaming=config.STREAMING,
    )
    
    # 构造消息
    prompt = f"""请帮我提取描述中的家具数量：{description}。并按照{{"length":10, "width":8, "door_position":2, "num_beds":1, "num_wardrobes":2, "num_table_chairs":2, "num_bookshelves":1}}的格式返回给我json串，除了这个json串什么都不要返回给我。"""
    
    # 发送消息并接收回复
    response = chat.invoke([HumanMessage(content=prompt)])
    
    # 解析返回的 JSON
    if isinstance(response, list) and len(response) > 0:
        message = response[0]
        json_str = message.content.strip()
    else:
        json_str = response.content.strip()
    
    return json_str
