# agent.py
import random 
#IT24610328---Lab03---Importing required libraries
from collections import deque
import heapq

#IT24610328---Lab04---Importing math library for equations.
import math

#IT24610328---Lab07---Part3---Importing the KnowledgeBase class from logic_engine.py
from logic_engine import KnowledgeBase

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

    #IT24610328---Lab04---Added manhattan_distance heuristic, calculates the sum of absolute coordinate differences.
    def manhattan_distance(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])

    #IT24610328---Lab04---Added euclidean_distance heuristic, calculates straight-line distance between two points.
    def euclidean_distance(self, pos, goal):
        return math.sqrt((pos[0] - goal[0]) ** 2 + (pos[1] - goal[1]) ** 2)

    def __init__(self):
        self.plan = []
        self.active_algo = 'AStar'  # switch to 'BFS', 'DFS' or 'UCS' to compare

        #IT24610328---Lab07---Part3---Creating the Knowledge Base for the agent.
        self.kb = KnowledgeBase()

        #IT24610328---Lab07---Part3---Adding Rule 1: TargetVisible AND HasDust => SafeToEngage
        self.kb.tell_rule(['TargetVisible', 'HasDust'], 'SafeToEngage')

        #IT24610328---Lab07---Part3---Adding Rule 2: SafeToEngage AND BloodseekerMissing => Retreat
        self.kb.tell_rule(['SafeToEngage', 'BloodseekerMissing'], 'Retreat')

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

    #IT24610328---Lab04---Added astar_search
    #IT24610328---Lab07---Part3---Adding a tile_facts parameter to pass the per-tile facts into A*.
    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan', tile_facts=None):

        #IT24610328---Lab07---Part3---Treating None as an empty dictionary.
        if tile_facts is None:
            tile_facts = {}

        #IT24610328---Lab04---Choose which heuristic function to use based on heuristic_type.
        if heuristic_type == 'euclidean':
            heuristic = self.euclidean_distance
        else :
            heuristic = self.manhattan_distance

        counter = 0
        h_start = heuristic(start_pos, goal_pos)

        #IT24610328---Lab04--Initializing an empty priority queue (frontier)
        #IT24610328---Lab04---Push the initial state into the priority queue with its f_cost, g_cost, and path.
        frontier = [(h_start, 0, counter, start_pos, [])]  # (f_cost, g_cost, tie_breaker, pos, path)

        #IT24610328---Lab04---Initializing an empty set
        reached_states = set()

        #IT24610328---Lab04---Create a while loop that continues until the frontier is empty. 
        while frontier:
            f_cost, g_cost, _, current_pos, path = heapq.heappop(frontier)

            #IT24610328---Lab04---Check if the current position is the goal position. If it is, return the path taken to reach the goal.
            if current_pos == goal_pos:
                return path

            #IT24610328---Lab04---Check if the current position has already been reached. If it has, skip to the next iteration of the loop. Otherwise, add the current position to the reached_states set.
            if current_pos in reached_states:
                continue
            reached_states.add(current_pos)

            #IT24610328---Lab04---For node expansion, checking all adjacent cells (neighbours/succesors)
            for action, next_pos, step_cost in self._successors(current_pos, walls, grid_size):
                if next_pos not in reached_states:

                    #IT24610328---Lab07---Part3---Clearing the KB facts before checking this neighbour.
                    self.kb.clear_facts()

                    #IT24610328---Lab07---Part3---Feeding this tile's facts into the KB.
                    for fact in tile_facts.get(next_pos, []):
                        self.kb.tell_fact(fact)

                    #IT24610328---Lab07---Part3---Running forward chaining to deduce new facts.
                    self.kb.forward_chain()

                    #IT24610328---Lab07---Part3---Marking the tile as Infeasible if Retreat is deduced and skipping it, even though it is physically reachable.
                    if 'Retreat' in self.kb.facts:
                        continue

                    #IT24610328---Lab04---For each valid neighbour, calculate the new g_cost, h_cost, and f_cost. Then push the neighbour into the priority queue with its f_cost, g_cost, and path.
                    g_new = g_cost + step_cost
                    h_new = heuristic(next_pos, goal_pos)
                    f_new = g_new + h_new
                    counter += 1
                    heapq.heappush(frontier, (f_new, g_new, counter, next_pos, path + [action]))

        return []

    #IT24610328---Lab03---Added sense_and_act method to determine the next action based on the current percept.
    def sense_and_act(self, percept):

        if not self.plan:

            #IT24610328---Lab04--Extracting the global state from the percept dictionary
            start = percept['agent_pos']
            walls = set(percept['walls'])
            grid_size = percept['grid_size']
            all_food = percept['all_food']

            if not all_food:
                return percept['facing']  # no food left

            #IT24610328---Lab03---Pick closest food by manhattan distance as the target.
            #IT24610328---Lab03---Manhattan distance only used to determine the closest food item, not for pathfinding.
            #IT24610328---Lab04---Finding the closest item to be the goal position
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

            #IT24610328---Lab04---Added AStar branch
            elif self.active_algo == 'AStar':

                #IT24610328---Lab07---Part3---Defining sample facts per tile. Placing the tiles next to the agent's start (6, 0) so the block is visible.
                tile_facts = {
                    (6, 1): ['TargetVisible', 'HasDust', 'BloodseekerMissing'],  # deduces Retreat: blocked
                    (7, 0): ['TargetVisible', 'HasDust'],                        # SafeToEngage only: allowed
                }

                #IT24610328---Lab07---Part3---Passing tile_facts into A*.
                self.plan = self.astar_search(start, goal, walls, grid_size, heuristic_type='manhattan', tile_facts=tile_facts)

            if not self.plan:
                return percept['facing']  # no path found,

        return self.plan.pop(0)