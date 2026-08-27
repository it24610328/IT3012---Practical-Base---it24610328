# agent.py
import random 
#IT24610328---Lab03---Importing required libraries
from collections import deque
import heapq



class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)


#IT24610328---Lab03---Added a new SearchAgent class that implements BFS, DFS, and UCS search algorithms. The agent can switch between these algorithms by changing the active_algo attribute.
class SearchAgent:

    def __init__(self):
        self.plan = []
        self.active_algo = 'BFS'  # switch to 'DFS' or 'UCS' to compare

    #IT24610328---Lab03---Added _successors method to generate valid moves from the current state, considering walls and grid boundaries. 
    #IT24610328---Lab03---This method added as all three search algorithms (BFS, DFS, UCS) require the same logic to generate successors.
    def _successors(self, state, walls, grid_size):

        """Return list of (action, next_state, cost) for valid moves from state."""
        x, y = state
        width, height = grid_size
        moves = [
            ('Up', (x, y + 1)),
            ('Down', (x, y - 1)),
            ('Left', (x - 1, y)),
            ('Right', (x + 1, y)),
        ]
        result = []

        for action, (nx, ny) in moves:
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in walls:
                result.append((action, (nx, ny), 1))  
        return result

    #IT24610328---Lab03---Added bfs search 
    def bfs_search(self, start, goal, walls, grid_size):

        frontier = deque([(start, [])])
        #IT24610328---Lab03---Added reached set to keep track of visited states to avoid cycles and redundant searches.
        reached = {start}

        while frontier:
            state, path = frontier.popleft()
            if state == goal:
                return path
            for action, next_state, cost in self._successors(state, walls, grid_size):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, path + [action]))
        return []

    #IT24610328---Lab03---Added dfs search
    def dfs_search(self, start, goal, walls, grid_size):

        frontier = [(start, [])]
        #IT24610328---Lab03---Added reached set to keep track of visited states to avoid cycles and redundant searches.
        reached = {start}
        
        while frontier:
            state, path = frontier.pop()
            if state == goal:
                return path
            for action, next_state, cost in self._successors(state, walls, grid_size):
                if next_state not in reached:
                    reached.add(next_state)
                    frontier.append((next_state, path + [action]))
        return []

    #IT24610328---Lab03---Added ucs search
    def ucs_search(self, start, goal, walls, grid_size):

        counter = 0
        frontier = [(0, counter, start, [])]  # (g_cost, tie_breaker, state, path)
        #IT24610328---Lab03---Added reached set to keep track of visited states to avoid cycles and redundant searches.
        reached = {start: 0}

        while frontier:
            g_cost, _, state, path = heapq.heappop(frontier)
            if state == goal:
                return path
            for action, next_state, step_cost in self._successors(state, walls, grid_size):
                new_cost = g_cost + step_cost
                if next_state not in reached or new_cost < reached[next_state]:
                    reached[next_state] = new_cost
                    counter += 1
                    heapq.heappush(frontier, (new_cost, counter, next_state, path + [action]))
        return []

    #IT24610328---Lab03---Added sense_and_act method to determine the next action based on the current percept.
    def sense_and_act(self, percept):

        if not self.plan:
            start = percept['agent_pos']
            walls = set(percept['walls'])
            grid_size = percept['grid_size']
            all_food = percept['all_food']

            if not all_food:
                return percept['facing']  # no food left

            #IT24610328---Lab03---Pick closest food by manhattan distance as the target.
            #IT24610328---Lab03---Manhattan distance only used to determine the closest food item, not for pathfinding.
            goal = min(
                all_food,
                key=lambda f: abs(f[0] - start[0]) + abs(f[1] - start[1])
            )

            #IT24610328---Lab03---Select the search algorithm based on the active_algo attribute.
            if self.active_algo == 'BFS':
                self.plan = self.bfs_search(start, goal, walls, grid_size)
            elif self.active_algo == 'DFS':
                self.plan = self.dfs_search(start, goal, walls, grid_size)
            elif self.active_algo == 'UCS':
                self.plan = self.ucs_search(start, goal, walls, grid_size)

            if not self.plan:
                return percept['facing']  # no path found,

        return self.plan.pop(0)