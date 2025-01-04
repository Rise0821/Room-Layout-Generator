# layout.py
import matplotlib.pyplot as plt
import io
import base64
import random

# 定义家具的尺寸
FURNITURE_SIZES = {
    '床': (2, 2),
    '单人床': (2, 1),
    '衣柜': (1, 1),       # 实际占位1x1，显示1x1
    '桌椅': (1, 2),
    '书架': (1, 1)        # 实际占位1x1，显示1x1
}

# 定义家具的颜色
FURNITURE_COLORS = {
    '床': 'lightgreen',
    '单人床': 'lightseagreen',
    '衣柜': 'lightcoral',
    '桌椅': 'lightblue',
    '书架': 'lightyellow',
    '门': 'brown'
}

# 定义家具的优先级
FURNITURE_PRIORITY = ['床', '衣柜', '桌椅', '书架']

def check_overlap(furniture, new_furniture):
    x_new, y_new, w_new, h_new = new_furniture['x'], new_furniture['y'], new_furniture['w'], new_furniture['h']
    for f in furniture:
        x, y, w, h = f['x'], f['y'], f['w'], f['h']
        if (x < x_new + w_new and x + w > x_new and
            y < y_new + h_new and y + h > y_new):
            return True
    return False

def generate_room_layout(length, width, door_position, num_beds, num_wardrobes, num_table_chairs, num_bookshelves):
    if length < 2 or width < 2:
        return None, "房间过小不宜居住。"

    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 绘制房间边界（长方形）
    ax.add_patch(plt.Rectangle((0, 0), width, length, fill=None, edgecolor='black', linewidth=2))
    
    # 绘制门作为墙壁上的一条线（假设门在底部墙壁）
    door_width = 1  # 门的宽度
    door_x_start = door_position
    door_x_end = door_position + door_width
    if door_x_end > width:
        door_x_end = width
    ax.plot([door_x_start, door_x_end], [0, 0], color=FURNITURE_COLORS['门'], linewidth=6, label='门')
    
    furniture = []
    unplaced_furniture = []
    
    # 定义门的缓冲区，避免家具靠近门
    buffer_zone = 1  # 缓冲区宽度

    # 定义门的缓冲区域
    door_buffer_area = [
        (door_x_start - buffer_zone, -buffer_zone, door_width + 2*buffer_zone, buffer_zone + 2)  # 底部缓冲区
    ]
    
    # 定义家具摆放函数
    def place_furniture(name, quantity, size, flush_to_wall=False):
        for _ in range(quantity):
            placed = False
            attempts = 0
            while not placed and attempts < 100:
                w, h = size
                if flush_to_wall:
                    # 随机选择一个墙壁：左、右、上
                    wall = random.choice(['left', 'right', 'top'])
                    if wall == 'left':
                        x = 0
                        y = round(random.uniform(buffer_zone, length - h), 2)
                        draw_w, draw_h = 1, 1
                    elif wall == 'right':
                        x = width - w
                        y = round(random.uniform(buffer_zone, length - h), 2)
                        draw_w, draw_h = 1, 1
                    elif wall == 'top':
                        x = round(random.uniform(0, width - w), 2)
                        y = length - h
                        draw_w, draw_h = 1, 1
                else:
                    x = round(random.uniform(0, width - w), 2)
                    y = round(random.uniform(buffer_zone, length - h), 2)
                    draw_w, draw_h = w, h
                
                new_furniture = {
                    'name': name,
                    'x': x,
                    'y': y,
                    'w': w,
                    'h': h,
                    'draw_w': draw_w,
                    'draw_h': draw_h
                }
                
                # 检查是否与门缓冲区重叠
                overlap_buffer = False
                for buf_x, buf_y, buf_w, buf_h in door_buffer_area:
                    if (new_furniture['x'] < buf_x + buf_w and new_furniture['x'] + new_furniture['w'] > buf_x and
                        new_furniture['y'] < buf_y + buf_h and new_furniture['y'] + new_furniture['h'] > buf_y):
                        overlap_buffer = True
                        break
                if overlap_buffer:
                    attempts += 1
                    continue
                
                # 检查是否与已放置家具重叠
                if not check_overlap(furniture, new_furniture):
                    furniture.append(new_furniture)
                    label = name if _ == 0 else ""
                    ax.add_patch(plt.Rectangle((x, y), new_furniture['draw_w'], new_furniture['draw_h'], 
                                               color=FURNITURE_COLORS[name], label=label))
                    placed = True
                else:
                    attempts += 1
            if not placed:
                unplaced_furniture.append(name)
    
    # 按照优先级摆放家具
    # 1. 床
    place_furniture('床', num_beds, FURNITURE_SIZES['床'])
    
    # 如果至少有一个床未能摆放，则尝试摆放单人床
    num_unplaced_beds = unplaced_furniture.count('床')
    if num_unplaced_beds > 0:
        for _ in range(num_unplaced_beds):
            place_furniture('单人床', 1, FURNITURE_SIZES['单人床'])
        # 移除无法摆放的床
        unplaced_furniture = [item for item in unplaced_furniture if item != '床']
    
    # 确保至少有一个床被摆放
    beds_placed = sum(1 for f in furniture if f['name'] in ['床', '单人床'])
    if beds_placed < 1:
        return None, "房间过小不宜居住。"
    
    # 2. 衣柜（必须贴墙）
    place_furniture('衣柜', num_wardrobes, FURNITURE_SIZES['衣柜'], flush_to_wall=True)
    
    # 3. 桌椅
    place_furniture('桌椅', num_table_chairs, FURNITURE_SIZES['桌椅'])
    
    # 4. 书架（必须贴墙）
    place_furniture('书架', num_bookshelves, FURNITURE_SIZES['书架'], flush_to_wall=True)
    
    # 设置图形的显示范围和样式
    ax.set_aspect('equal')
    ax.axis('off')  # 隐藏坐标轴
    
    # 保存图形为内存中的图像
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)  # 关闭图形，释放资源
    
    # 编码为 base64 字符串
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    
    return img_base64, unplaced_furniture
