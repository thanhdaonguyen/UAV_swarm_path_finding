from Parameters import Parameters
class Point:
    """
        Point class to represent a point in the map
        Attributes:
            x: x-coordinate of the point in pixel
            y: y-coordinate of the point in pixel
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Vector:
    """
        Vector class to represent a vector in the map
        Attributes:
            x: x-coordinate of the vector in pixel
            y: y-coordinate of the vector in pixel
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def normalize(self):
        """
            Normalize the vector
            Returns:
                Vector object representing the normalized vector
        """
        magnitude = (self.x ** 2 + self.y ** 2) ** 0.5
        if magnitude == 0:
            return Vector(0, 0)
        return Vector(self.x / magnitude, self.y / magnitude)

def get_sign(x):
    """
        Get the sign of a number
        Args:
            x: Number to get the sign
        Returns:
            1 if x >= 0, -1 otherwise
    """
    return -1 if x < 0 else 1

def is_point_in_polygon(x, y, polygon):
    """
        Check if a point (x, y) is inside a polygon.
        Args:
            x: x-coordinate of the point
            y: y-coordinate of the point
            polygon: List of points representing the polygon
        Returns:
            True if the point is inside the polygon, False otherwise    
    """
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

### Tsunami algo ###

def wavefront(goal, map):
    temp = (goal[0] // Parameters.cell_size, goal[1] // Parameters.cell_size)
    goal = temp;
    map_width = int(Parameters.map_width // Parameters.cell_size) + 1
    map_height = int(Parameters.map_height // Parameters.cell_size) + 1
    wavefront_matrix = [[-1 for j in range(map_height)] for i in range(map_width)];
    state_table = [[-1 for j in range(map_height)] for i in range(map_width)]
    value_table = [[-1 for j in range(map_height)] for i in range(map_width)]
    horizontal = 0;
    for x in range(0, Parameters.map_width, Parameters.cell_size):
        vertical = 0;
        for y in range(0, Parameters.map_height, Parameters.cell_size):                
            center_x = x + Parameters.cell_size // 2;
            center_y = y + Parameters.cell_size // 2;
            state_table[horizontal][vertical] = map.cells[(center_x, center_y)].state;
            value_table[horizontal][vertical] = map.cells[(center_x, center_y)].value;
            vertical += 1;
        horizontal += 1;

    def bfs_condition(state_table, result, position):
        if (state_table[position[0]][position[1]] != Map.CellState.UNREACHABLE and state_table[position[0]][position[1]] != Map.CellState.NO_INTEREST) and result[position[0]][position[1]] == -1:
            return True;
        return False

    rows, cols = len(state_table), len(state_table[0])
    
    # Initialize the result matrix with -1 (unreachable) values
    result = [[-1 for _ in range(cols)] for _ in range(rows)]
    
    # Directions for moving in the grid (up, down, left, right)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    # Priority queue initialization: (distance, x, y)
    pq = []
    heapq.heappush(pq, (0, goal[0], goal[1]))  # Start from the goal with distance 0
    result[goal[0]][goal[1]] = 0  # Distance from goal to goal is 0

    while pq:
        dist, x, y = heapq.heappop(pq)  # Pop the node with the smallest distance
        
        # Explore all possible neighbors
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            
            # Check if the neighbor is within bounds, not an obstacle, and not visited
            if 0 <= nx < rows and 0 <= ny < cols and bfs_condition(state_table, result, (nx, ny)):
                # Set the distance to the neighbor
                result[nx][ny] = dist + 1
                # Push the neighbor into the priority queue with updated distance
                heapq.heappush(pq, (dist + 1, nx, ny))
    
    return result

def find_circle_centers(map):
    radius=Parameters.radius
    centers = []
    step_x = int(radius)
    step_y = int(radius * 3) 

    # Xác định phạm vi chứa số 1
    xmin, xmax, ymin, ymax = Parameters.map_height, 0, Parameters.map_width, 0
    for i in range(len(map)):  
        for j in range(len(map[0])):  
            if map[i][j] == 1:
                xmin, xmax = min(xmin, i), max(xmax, i)
                ymin, ymax = min(ymin, j), max(ymax, j)

    if xmax < xmin or ymax < ymin:
        print("No cell with value 1")
        return []
    # Duyệt theo dạng lưới lục giác
    for x in range(xmin, xmax + 1, step_x):
        offset = (x // step_x) % 2 * (step_y // 2)  # Xen kẽ các hàng
        for y in range(ymin + offset, ymax + 1, step_y):
                centers.append((x, y))

    return centers

# def build_list_cell_1(map0):
#     step = Parameters.cell_size

#     # Tạo ma trận đúng kích thước
#     list_cell_1 = [[0] * Parameters.map_height for _ in range(Parameters.map_width)]

#     for x in range(0, Parameters.map_width):
#         for y in range(0, Parameters.map_height):
#             center_x = x
#             center_y = y

#             if (center_x, center_y) in map0.priority:
#                 cell = str(map0.priority[(center_x, center_y)])
#                 if 0 <= x< Parameters.map_width and 0 <= y < Parameters.map_height:  # Kiểm tra chỉ số hợp lệ
#                     list_cell_1[x][y] = 1 if cell[-1] == '1' else 0

#     return list_cell_1
#def tsunami_next_position((recent_uav.cell_x, recent_uav.cell_y), map0, wavefront_map):
    
    
def centroid_priority(map, cen_circles, time_to_scan, time_to_move):
    '''
    map: array with 0,1 value
    cen_circles: array store center, center is a tuple (x, y)
    time_to_scan: time that swarms have to scan the area that has centroid
    time_to_move: time that swarms have to move to the centroid
    return: array of centroid based on priority
    Tổng độ ưu tiên bằng tổng các ô trong vùng quét của centroid
    Ưu tiên tính bằng công thức: tổng ưu tiên/tổng thời gian di chuyển
    Thời gian di chuyển: time_to_move + time_to_scan
    '''
    priority_list = []

    for center in cen_circles:
        x, y = center
        total_priority = 0
        for i in range(int(x - Parameters.radius), int(x + Parameters.radius) + 1):
            for j in range(int(y - Parameters.radius), int(y + Parameters.radius) + 1):
                if 0 <= i < len(map) and 0 <= j < len(map[0]):
                    total_priority += map[i][j]
        total_time = time_to_move + time_to_scan
        priority = total_priority / total_time if total_time > 0 else 0
        priority_list.append((center, priority))

    priority_list.sort(key=lambda x: x[1], reverse=True)
    print(priority_list)
    return [center for center, _ in priority_list]
