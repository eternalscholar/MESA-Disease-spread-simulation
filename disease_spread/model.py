from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import MultiGrid
from mesa.time import RandomActivation

from .agent import Species1TreeCell, Species2TreeCell, MovingAgent


class ForestDisease(Model):
    """
    Simple Forest Fire model.
    """
    def __init__(self, height=100, width=100, species1_tree_density=0.25, species2_tree_density=0.25, mortality=1, wind='N', distance='1'):
        """
        Create a new forest fire model.
        Args:
            height, width: The size of the grid to model
            density: What fraction of grid cells have a tree in them.
        """
        # Initialize model parameters
        self.height = height
        self.width = width
        self.species1_tree_density = species1_tree_density
        self.species2_tree_density = species2_tree_density
        self.mortality = mortality
        self.wind = wind
        self.distance = distance

        # Set up model objects
        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(height, width, torus=False)

        self.datacollector = DataCollector(
            {"Species1_Fine": lambda m: self.count_type(m, "Fine"),
             "Species1_Infected": lambda m: self.count_type(m, "Infected"),
             "Species1_Dead": lambda m: self.count_type(m, "Dead"),
             "Species2_Fine": lambda m: self.count_type(m, "Fine"),
             "Species2_Infected": lambda m: self.count_type(m, "Infected"),
             "Species2_Dead": lambda m: self.count_type(m, "Dead")})

        # Place a tree in each cell with Prob = density
        for (contents, x, y) in self.grid.coord_iter():
            if self.random.random() < self.species1_tree_density:
                # Create a tree
                new_species1_tree = Species1TreeCell((x, y), self)
                self.grid._place_agent((x, y), new_species1_tree)
                self.schedule.add(new_species1_tree)

        for (contents, x, y) in self.grid.coord_iter():
            if self.random.random() < self.species2_tree_density:
                # Create a tree
                new_species2_tree = Species2TreeCell((x, y), self)
                self.grid._place_agent((x, y), new_species2_tree)
                self.schedule.add(new_species2_tree)                
                
        center = (int(width / 2), int(height / 2))
        movingAgent = MovingAgent(center, self)
        self.grid._place_agent(center, movingAgent)
        new_species1_tree = Species1TreeCell(center, self)
        
        self.grid._place_agent(center, new_species1_tree)
        self.schedule.add(new_species1_tree)
        self.schedule.add(new_species2_tree)
        self.schedule.add(movingAgent)

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        """
        Advance the model by one step.
        """
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)

        # Halt if no more fire
        if (self.count_type(self, "Species1_Fine") == 0) and (self.count_type(self, "Species2_Fine")):
            self.running = False

    @staticmethod
    def count_type(model, tree_condition):
        """
        Helper method to count trees in a given condition in a given model.
        """
        count = 0
        for tree in model.schedule.agents:
            if tree.condition == tree_condition:
                count += 1
        return count
