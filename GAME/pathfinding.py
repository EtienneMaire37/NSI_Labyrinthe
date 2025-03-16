from GAME.file import File

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
    open_list = File()
    closed_set = set()
    
    start_node = Node(start)
    open_list.enfiler(start_node)
    
    best_g = {start: 0}
    max_iterations = (map_size[0] * map_size[1]) * 2
    
    iteration_count = 0
    
    while not open_list.est_vide() and iteration_count < max_iterations:
        iteration_count += 1
        current_node = open_list.defiler()
        
        if current_node.g > best_g.get(current_node.position, float('inf')):
            continue
            
        if current_node.position == end:
            path = []
            while current_node is not None:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]
        
        closed_set.add(current_node.position)
        
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            x = current_node.position[0] + dx
            y = current_node.position[1] + dy
            
            if 0 <= x < map_size[0] and 0 <= y < map_size[1]:
                if map_data[y * map_size[0] + x] != 0:
                    continue
                
                neighbor_pos = (x, y)
                tentative_g = current_node.g + 1
                
                if tentative_g >= best_g.get(neighbor_pos, float('inf')):
                    continue
                
                best_g[neighbor_pos] = tentative_g
                
                neighbor_node = Node(neighbor_pos, current_node)
                neighbor_node.g = tentative_g
                neighbor_node.h = abs(x - end[0]) + abs(y - end[1])
                neighbor_node.f = neighbor_node.g + neighbor_node.h
                
                in_open = False
                for n in open_list.contenu:
                    if n.position == neighbor_pos and n.f <= neighbor_node.f:
                        in_open = True
                        break
                
                if not in_open:
                    open_list.enfiler(neighbor_node)
    
    return []