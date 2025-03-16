from GAME.file import File
import heapq  # Add this import

class Node:
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f

def a_star(start, end, map_data, map_size):
    open_list = []
    closed_set = set()
    
    start_node = Node(start)
    heapq.heappush(open_list, start_node)
    
    best_g = {start: 0}
    
    while open_list:
        current_node = heapq.heappop(open_list)
        
        if current_node.position == end:
            path = []
            while current_node is not None:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]
        
        if current_node.position in closed_set:
            continue
            
        closed_set.add(current_node.position)
        
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            x = current_node.position[0] + dx
            y = current_node.position[1] + dy
            
            if 0 <= x < map_size[0] and 0 <= y < map_size[1]:
                if map_data[y * map_size[0] + x] != 0:
                    continue
                
                neighbor_pos = (x, y)
                tentative_g = current_node.g + 1
                
                if neighbor_pos in closed_set and tentative_g >= best_g.get(neighbor_pos, float('inf')):
                    continue

                if tentative_g < best_g.get(neighbor_pos, float('inf')):
                    best_g[neighbor_pos] = tentative_g
                    neighbor_node = Node(neighbor_pos, current_node)
                    neighbor_node.g = tentative_g
                    neighbor_node.h = abs(x - end[0]) + abs(y - end[1])
                    neighbor_node.f = neighbor_node.g + neighbor_node.h
                    heapq.heappush(open_list, neighbor_node)
    
    return []