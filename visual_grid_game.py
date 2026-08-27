# visual_grid_game.py
import random
import tkinter as tk
#IT24610328---Lab03---Importing the SearchAgent class from agent.py to be used in the VisualGridHuntGame environment.
from agent import SearchAgent

class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""


    # IT24610328---Lab01---Adding num_traps input value in addition to the existing values for width, height, num_food, num_opponents, and custom_walls.
    def __init__(self, width=10, height=10, facing='Up', num_food=10, num_opponents=2, num_traps=3, custom_walls=None):
        self.width = width
        self.height = height

        #IT24610328---Lab02---Adding a facing attribute to the environment to track the agent's current facing direction
        self.facing = facing

        #IT24610328---Lab02---Adding a facing_before attribute to the environment to track the agent's previous facing direction
        self.facing_before = self.facing

        #IT24610328---Lab01---Setting the agent's starting position to (6, 0) to be directly under u pocket shaped walls.
        self.agent_pos = [6, 0]  # Starting position (x, y)

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            # Generate some default scattered walls for a larger grid
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        # Dynamically generate random food positions avoiding walls and agent start
        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple)

        # Generate adversarial opponents
        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]
            if tuple(op_pos) != (0, 0) and tuple(op_pos) not in self.walls and tuple(op_pos) not in self.food_positions:
                self.opponents.append(op_pos)

        # IT24610328---Lab01---Generate toxic traps, avoiding agent start, walls, food, and opponents
        self.toxic_traps = set()
        while len(self.toxic_traps) < num_traps:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            pos_tuple = (tx, ty)
            if (pos_tuple != (0, 0)
                    and pos_tuple not in self.walls
                    and pos_tuple not in self.food_positions
                    and pos_tuple not in [tuple(op) for op in self.opponents]):
                self.toxic_traps.add(pos_tuple)

        self.score = 0
        self.steps = 0
        self.collision = False

    #IT24610328---Lab02---Adding a method to get the position of the cell directly in front of the agent in the direction it is currently facing.
    #IT24610328---Lab02---Returning None if the position ahead is out of bounds, otherwise returning the valid position.
    def _get_ahead_position(self):
        ax, ay = self.agent_pos
        if self.facing == 'Up':
            nx, ny = ax, ay + 1
        elif self.facing == 'Down':
            nx, ny = ax, ay - 1
        elif self.facing == 'Left':
            nx, ny = ax - 1, ay
        elif self.facing == 'Right':
            nx, ny = ax + 1, ay
        else:
            nx, ny = ax, ay

        if 0 <= nx < self.width and 0 <= ny < self.height:
            return (nx, ny)
        return None  

    #IT24610328---Lab02---Adding a method to get the position of the cell directly to the left of the agent based on its current facing direction.
    def _get_left_position(self):
        ax, ay = self.agent_pos

        if self.facing == 'Up':
            nx, ny = ax - 1, ay
        elif self.facing == 'Down':
            nx, ny = ax + 1, ay
        elif self.facing == 'Left':
            nx, ny = ax, ay - 1
        elif self.facing == 'Right':
            nx, ny = ax, ay + 1
        else:
            nx, ny = ax, ay

        if 0 <= nx < self.width and 0 <= ny < self.height:
            return (nx, ny)
        return None

    #IT24610328---Lab02---Adding a method to get the position of the cell directly to the right of the agent based on its current facing direction.
    def _get_right_position(self):
        ax, ay = self.agent_pos

        if self.facing == 'Up':
            nx, ny = ax + 1, ay
        elif self.facing == 'Down':
            nx, ny = ax - 1, ay
        elif self.facing == 'Left':
            nx, ny = ax, ay + 1
        elif self.facing == 'Right':
            nx, ny = ax, ay - 1
        else:
            nx, ny = ax, ay

        if 0 <= nx < self.width and 0 <= ny < self.height:
            return (nx, ny)
        return None

    # IT24610328---Lab01---Added smells_toxin to the percept dictionary to inform the agent about the presence of toxic traps.  
    
    #IT24610328---Lab02---Added wall_ahead, food_ahead, toxin_ahead, and opponent_ahead to the percept dictionary to inform the agent about the presence of walls, food, toxic traps, and opponents in the cell directly in front of it based on its current facing direction.
    #IT24610328---Lab02---Added facing to the percept dictionary to inform the agent about its current facing direction.
    #IT24610328---Lab02---Removed remaining_food from the percept dictionary as it classifies as global information and is not directly perceivable by the agent in its immediate environment.
    #IT24610328---Lab02---Added wall_left and wall_right to the percept dictionary to inform the model agent about the presence of walls in the cells directly to its left and right based on its current facing direction.
    def get_percept(self) -> dict:
        ahead_pos = self._get_ahead_position()
        left_pos = self._get_left_position()
        right_pos = self._get_right_position()

        opponent_positions_set = {tuple(op) for op in self.opponents}

        return {
            'facing': self.facing,

            'wall_ahead': ahead_pos is None or ahead_pos in self.walls,
            'wall_left': left_pos is None or left_pos in self.walls,
            'wall_right': right_pos is None or right_pos in self.walls,

            'food_here': tuple(self.agent_pos) in self.food_positions,
            'food_ahead': ahead_pos is not None and ahead_pos in self.food_positions,

            'toxin_here': tuple(self.agent_pos) in self.toxic_traps,
            'toxin_ahead': ahead_pos is not None and ahead_pos in self.toxic_traps,

            'opponent_here': tuple(self.agent_pos) in opponent_positions_set,
            'opponent_ahead': ahead_pos is not None and ahead_pos in opponent_positions_set,

            'collision': self.collision,

            # IT24610328---Lab03---Added the agent's current position, grid size, walls, and all food positions to the percept dictionary to provide the agent with the global state.
            'agent_pos': tuple(self.agent_pos),
            'grid_size': (self.width, self.height),
            'walls': list(self.walls),
            'all_food': list(self.food_positions),

    }

    def execute_action(self, action: str):
        self.steps += 1

        #IT24610328---Lab02---Update the facing attribute based on the action taken by the agent.
        self.facing_before = self.facing
        self.facing = action

        #IT24610328---Lab02---If the action is a different direction than we were already facing, treat it as a pure turn, no movement
        #IT24610328---Lab03---Removed the early return here. The SearchAgent's bfs_search/dfs_search/ucs_search treat every action as a direct 1-step move with no separate turning cost, so keeping the turn-only behavior caused the agent to get stuck alternating directions without ever moving. Every action now moves the agent immediately, matching the cost model used in _successors.

        new_pos = list(self.agent_pos)

        if action == 'Up':
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right':
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)

        if tuple(new_pos) in self.walls:
            self.score -= 5
        else:
            self.agent_pos = new_pos

        tuple_pos = tuple(self.agent_pos)
        if tuple_pos in self.food_positions:
            self.food_positions.remove(tuple_pos)
            self.score += 20

        # IT24610328---Lab01---Check for toxic traps and apply penalty if the agent steps on one.
        if tuple_pos in self.toxic_traps:
            self.score -= 15

        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1
            elif move == 'Down' and op[1] > 0:
                op[1] -= 1
            elif move == 'Left' and op[0] > 0:
                op[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision

#IT24610328---Lab02---Implementing a simple reflex agent that makes decisions based on the current percept from the environment.   
class SimpleReflexAgent:
    def sense_and_act(self, percept: dict) -> str:
        turn_left = {'Up': 'Left', 'Left': 'Down', 'Down': 'Right', 'Right': 'Up'}

        # Rule 1: avoid immediate danger
        if percept['wall_ahead'] or percept['toxin_ahead'] or percept['opponent_ahead']:
            return turn_left[percept['facing']]

        # Rule 2: food ahead, keep moving forward into it
        if percept['food_ahead']:
            return percept['facing']

        # Rule 3: nothing interesting, just keep going forward
        return percept['facing']

#IT24610328---Lab02---Implementing a model-based agent that remembers previously encountered states.
class ModelBasedAgent:
    def __init__(self):

        #IT24610328---Lab02---Track the agent's estimated relative position.
        self.rel_pos = (0, 0)

        #IT24610328---Lab02---Store how many times each state has been visited.
        self.visits = {}

        #IT24610328---Lab02---Store the previous facing direction and action.
        self.last_facing = None
        self.last_action = None

    def sense_and_act(self, percept: dict) -> str:

        turn_left = {
            'Up': 'Left',
            'Left': 'Down',
            'Down': 'Right',
            'Right': 'Up'
        }

        turn_right = {
            'Up': 'Right',
            'Right': 'Down',
            'Down': 'Left',
            'Left': 'Up'
        }

        dir_vectors = {
            'Up': (0, 1),
            'Down': (0, -1),
            'Left': (-1, 0),
            'Right': (1, 0)
        }

        facing = percept['facing']

        #IT24610328---Lab02---Update the estimated relative position after moving forward.
        if (
            self.last_action is not None
            and self.last_facing is not None
            and self.last_action == self.last_facing
        ):
            dx, dy = dir_vectors[self.last_facing]
            self.rel_pos = (
                self.rel_pos[0] + dx,
                self.rel_pos[1] + dy
            )

        #IT24610328---Lab02---Represent the current internal state using the estimated position and facing direction.
        state = (self.rel_pos, facing)

        #IT24610328---Lab02---Count how many times this state has been encountered.
        self.visits[state] = self.visits.get(state, 0) + 1

        #IT24610328---Lab02---Avoid immediate dangers.
        if percept['toxin_ahead'] or percept['opponent_ahead']:
            action = turn_left[facing]
            self.last_facing = facing
            self.last_action = action
            return action

        #IT24610328---Lab02---Use the stored state history to choose an alternative turn when the same wall situation is encountered again.
        if percept['wall_ahead']:

            if self.visits[state] >= 2:
                action = turn_right[facing]
            else:
                action = turn_left[facing]

            self.last_facing = facing
            self.last_action = action
            return action

        #IT24610328---Lab02---Move forward when there is no immediate danger.
        self.last_facing = facing
        self.last_action = facing
        return facing
    
class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    # IT24610328---Lab01---Adding num_traps input value in addition to the existing values for width, height, num_food, num_opponents, and walls for the GUI.
    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, num_traps=3, walls=None):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

        #IT24610328---Lab01---Pass num_traps to the VisualGridHuntGame constructor to ensure traps are included in the environment.
        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_opponents=num_opponents, num_traps=num_traps,
                                      custom_walls=walls)

        #IT24610328---Lab02---Instantiate the SimpleReflexAgent to be used in the GUI for decision-making based on percepts.
        #IT24610328---Lab02---Uncomment the following line to use the SimpleReflexAgent instead of the ModelBasedAgent.

        #self.agent = SimpleReflexAgent()

        #IT24610328---Lab02---Instantiate the ModelBasedAgent to be used in the GUI for decision-making based on percepts and internal state.
        #Comment the following line to use the SimpleReflexAgent instead of the ModelBasedAgent.
        #self.agent = ModelBasedAgent()  

        #IT24610328---Lab03---Instantiate the SearchAgent to be used in the GUI for decision-making based on percepts and internal state.
        #Uncomment the following line to use the SearchAgent.
        #IT24610328---Lab04---The SearchAgent can now use A* to plan a path to the nearest food while avoiding walls, traps, and opponents.
        self.agent = SearchAgent()  

        # Dynamically calculate cell size so the total canvas fits nicely within a 600x600 window ceiling
        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066",
                             fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                # Only draw text if cell is large enough
                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white",
                                            font=("Arial", 8, "bold"))

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b",
                                    outline="#d97706")

        # IT24610328---Lab01---Draw toxic traps as purple triangles by iterating through each trap position
        for tx, ty in self.env.toxic_traps:
            offset = self.cell_size * 0.2
            x1 = tx * self.cell_size + offset
            y1 = (self.env.height - 1 - ty) * self.cell_size + offset
            self.canvas.create_polygon(x1 + self.cell_size * 0.3, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6,
                                    x1, y1 + self.cell_size * 0.6, fill="#7c3aed", outline="#5b21b6")

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000",
                                         outline="#7a0000")

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066",
                                outline="#1e3a8a")

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():
                
                #IT24610328---Lab02---Use the simple reflex agent to determine the next action based on the current percept.
                #IT24610328---Lab03---Use the search agent to determine the next action based on the current percept.
                percept = self.env.get_percept()
                action = self.agent.sense_and_act(percept)
                
                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
                self.root.after(250, step)
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()

if __name__ == "__main__":
    root = tk.Tk()
    #IT24610328---Lab02---Added walls for demonstration of agent getting stuck in a u shaped corner.
    #IT24610328---Lab03---Maze-style walls with multiple corridors and dead ends to clearly demonstrate the difference in path quality between BFS, DFS, and UCS.
    walls = [
        (1,9), (2,9), (3,9), (3,8), (3,7), (1,7),

        (5,1), (5,2), (5,3), (5,4), (5,5), (5,6), (5,7), (5,8),
        (6,8), (7,8), (8,8), (9,8),

        (7,1), (7,2), (7,3), (7,4), (7,5),
        (8,5), (9,5),

        (9,1), (9,2), (10,1), (10,2), (10,3),

        (3,3), (3,4), (4,4),
    ]
    app = GridGameGUI(root, width=12, height=12, num_food=1, num_opponents=2, walls=walls)
    root.mainloop()