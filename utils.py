from collections import deque

def is_point_in_polygon(x, y, polygon):
    """Check if a point (x, y) is inside a polygon."""
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def bfs(valid_cells, start):
    # Tạo dictionary lưu trạng thái bản đồ
    map_dict = {(x, y): v for x, y, v in valid_cells}
    
    if start not in map_dict or map_dict[start] == -1:
        return None  # Điểm bắt đầu không hợp lệ

    # Khởi tạo ma trận khoảng cách (bắt đầu từ điểm start)
    distances = {pos: float('inf') for pos in map_dict if map_dict[pos] == 1}
    distances[start] = 0  # Khoảng cách đến chính nó là 0

    # Hàng đợi BFS, bắt đầu từ điểm start
    queue = deque([start])
    directions = [(0, 30), (0, -30), (30, 0), (-30, 0)]  # Lên, xuống, phải, trái
    
    while queue:
        x, y = queue.popleft()

        for dx, dy in directions:
            next_pos = (x + dx, y + dy)
            if next_pos in distances and distances[next_pos] == float('inf'):  # Chưa đi qua
                distances[next_pos] = distances[(x, y)] + 1
                queue.append(next_pos)
    return distances  # Trả về toàn bộ khoảng cách
