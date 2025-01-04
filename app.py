# app.py
from flask import Flask, request, render_template
import json
from config import Config
from layout import generate_room_layout, FURNITURE_COLORS
from chat import get_chat_response

app = Flask(__name__)

# 验证环境变量
Config.validate()

@app.route('/', methods=['GET', 'POST'])
def home():
    img_data = None
    error_message = None
    if request.method == 'POST':
        form_type = request.form.get('form_type')
        try:
            if form_type == 'numeric':
                # 获取并验证表单数据
                length = float(request.form['length'])
                width = float(request.form['width'])
                door_position = float(request.form['door_position'])
                num_beds = int(request.form['num_beds'])
                num_wardrobes = int(request.form['num_wardrobes'])
                num_table_chairs = int(request.form['num_table_chairs'])
                num_bookshelves = int(request.form['num_bookshelves'])
                
                # 检查门位置是否合理
                if not (0 <= door_position <= width - 1):
                    error_message = f"门的位置必须在房间宽度范围内 (0 到 {width - 1} 米)。"
                else:
                    # 生成房间布局图
                    img_data, unplaced = generate_room_layout(
                        length=length,
                        width=width,
                        door_position=door_position,
                        num_beds=num_beds,
                        num_wardrobes=num_wardrobes,
                        num_table_chairs=num_table_chairs,
                        num_bookshelves=num_bookshelves
                    )
                    
                    # 如果有未摆放的家具，生成错误消息
                    if unplaced:
                        # 确保至少一个床被摆放
                        if '床' in unplaced or '单人床' in unplaced:
                            error_message = "房间过小，无法摆放至少一个床。"
                        else:
                            unplaced_set = set(unplaced)
                            error_message = f"面积太小，无法摆放：{', '.join(unplaced_set)}。"
            
            elif form_type == 'ai_chat':
                description = request.form['description'].strip()
                if not description:
                    error_message = "请输入房间描述。"
                else:
                    # 获取 AI 生成的 JSON 字符串
                    json_str = get_chat_response(description, Config)
                    
                    # 确保返回的是一个 JSON 字符串
                    try:
                        data = json.loads(json_str)
                    except json.JSONDecodeError:
                        raise ValueError("Coze API 返回的内容不是有效的 JSON。")
                    
                    # 提取必要的字段
                    required_fields = ["length", "width", "door_position", "num_beds", "num_wardrobes", "num_table_chairs", "num_bookshelves"]
                    if not all(field in data for field in required_fields):
                        raise ValueError("JSON 数据缺少必要的字段。")
                    
                    # 生成房间布局图
                    img_data, unplaced = generate_room_layout(
                        length=data["length"],
                        width=data["width"],
                        door_position=data["door_position"],
                        num_beds=data["num_beds"],
                        num_wardrobes=data["num_wardrobes"],
                        num_table_chairs=data["num_table_chairs"],
                        num_bookshelves=data["num_bookshelves"]
                    )
                    
                    # 如果有未摆放的家具，生成错误消息
                    if unplaced:
                        # 确保至少一个床被摆放
                        if '床' in unplaced or '单人床' in unplaced:
                            error_message = "房间过小，无法摆放至少一个床。"
                        else:
                            unplaced_set = set(unplaced)
                            error_message = f"面积太小，无法摆放：{', '.join(unplaced_set)}。"
            else:
                error_message = "未知的表单类型。"
        except ValueError as ve:
            error_message = f"处理失败: {ve}"
        except Exception as e:
            error_message = f"发生错误: {e}"
    
    # 渲染模板，包含输入表单和生成的图像（如果有）
    return render_template('index.html', img_data=img_data, error_message=error_message, FURNITURE_COLORS=FURNITURE_COLORS)

if __name__ == '__main__':
    app.run(debug=True)
