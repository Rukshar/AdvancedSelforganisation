from __future__ import division
import numpy as np
import random
import time
import matplotlib.pyplot as plt

w_cohere = 0.3
w_avoid = 0.3
w_align = 0.3
visible_distance = 30.0
minimum_distance = 15.0
max_velocity = 1.0
weight = 0.8



# TODO: BEE OBJECTS, with possibilities to "leave" pheromones
# TODO: BEE FOLLOWING RULES for pheromones

class World(object):
    """
    The model exists within this world. World controls the elapsing of time etc en checks the state of everything.
    """
    def __init__(self,x,y,z=0):
        #Als z = 0 dan is het niet 3d.
        #TODO: needs some registration of time, to make graphs later?
        self.x=x
        self.y=y
        self.z=z
        self.time = 0
        self.pheromones = []
        self.bees = []
        self.areas = self.get_positions() #lijst van lijsten met [pos,concentratie]
        # lijst met posities die taken
        # lijst met alle hokjes, en hun concentratie.
    
    def get_positions(self):
        # alle bestaande posities berekenen en die in de lijst zetten met concentratie 0
        # return a list [[pos,concentratie],[pos,concentratie],....,[pos,concentratie]]
        pass

    def add_pheromone(self,pheromone):
        self.pheromones.append(pheromone)
        pass

    def check_next_state(self):
        #TODO: bee, check neigbors and decides on action
        #TODO: Pheromone, diffuses
        #TODO: if bee if all actions are possible (no collision) everything can be processed
        pass
    def do_next_state(self):
        # TODO: after all states are checked and decided on, the world will change to the next world state
        # This means time +1 and new pheromone concentrations, new bee positions etc.
        pass
    def save_world_state(self):
        #TODO: this is so states are registered for later use, data analysis, graphs etc?
        pass
    

class Pheromone(object):
    """
    Scout bees can leave pheromones through their Naslav gland. The substance diffuses through the air.
    The concentration decreases when the substance diffuses.
    """
    def __init__(self,initial_pos,diff_rate=0.5,existence_threshold=0.02):
        # A pheromone has a position in space diffusion rate (how fast does the concentration decrease) and
        # a level of concentration
        self.position = initial_pos #numpy array
        self.diff_rate=diff_rate
        self.concentration = 1.0 # start at 100% concentration
        self.existence_threshold = existence_threshold
        self.diff_age = diff_age = 0
        self.color = "1.0" #some shade of grey 0.0 - 1.0

    def diffuse(self):
        self.disappear() # first check if the particle has to disappear
        
        # for all #ga alle hokjes in de wereld langs
        #     for all #ga alle pheromonen centra langs
        #         if (#de afstand van het hokje tot de pheromonen < diff_age)
        #             # concentratie van dit hokje wordt concentratie van de pheromoon * diff_rate ^ afstand)
        #             # change color naar lichter
        pass

    def disappear(self):
        if (self.concentration < self.existence_treshold):
         pass# check if present concentration is too low to keep existing.
        #self.delete??? # if so then pheromones should be removed from the world and free memory
        pass

def visualize():
    # Some kind of visiualisation, can use plot and graphs. Or something else.
    pass

# def magnitude(x):
#     return np.sqrt(x.dot(x))
# class Bee(object):
#     """
#     A bee has a starting position and a starting velocity, the swarm exists
#     of uninformed bees and scouts
#     """
#
#     def __init__(self, initial_position, initial_velocity):
#         self.position = initial_position
#         self.velocity = initial_velocity
#
# class UninformedBee(Bee):
#     """
#     Uninformed bees behave as a swarm (i.e. follow each other) therefore they
#     have a cohere function, align function, avoid function and also a random
#     function to determine their new velocity and position. The formulas are
#     from (Janson et al., 2004).
#     """
#
#     def _cohere(self, visible_neighbours):
#
#         if len(visible_neighbours) == 0:
#             return 0
#
#         total = 0.0
#
#         for neighbour in visible_neighbours:
#             total += (neighbour.position - self.position)
#
#         return (1/visible_distance) * (1/len(visible_neighbours)) * total
#
#     def _align(self, visible_neighbours):
#         if len(visible_neighbours) == 0:
#             return 0
#
#         total = 0.0
#
#         for neighbour in visible_neighbours:
#             total += neighbour.velocity
#
#         return (1/max_velocity) * (1/len(visible_neighbours)) * total
#
#     def _avoid(self, min_neighbours):
#         if len(min_neighbours) == 0:
#             return 0
#
#         total = 0.0
#         for neighbour in min_neighbours:
#             total += ((self.position - neighbour.position) *
#                       (minimum_distance/magnitude(self.position - neighbour.position) -1))
#
#         return (1/minimum_distance) * (1/len(min_neighbours)) * total
#
#     def _random(self):
#         pass
#
#     def determine_new_position(self, all_bees, tstep):
#         visible_neighbours = []
#         min_neighbours = []
#
#         for bee in all_bees:
#             if bee is self:
#                 continue
#
#             if magnitude(self.position - bee.position) < visible_distance:
#                 visible_neighbours.append(bee)
#
#                 if magnitude(self.position - bee.position) < minimum_distance:
#                     min_neighbours.append(bee)
#
#         cohere = self._cohere(visible_neighbours)
#         align = self._align(visible_neighbours)
#         avoid = self._avoid(min_neighbours)
#         new_velocity = w_cohere * cohere + w_avoid * avoid + w_align * align
#         self.velocity = weight * self.velocity + new_velocity
#         self.position = self.position + self.velocity * tstep
#
#         return self.position
#
#     def get_color(self):
#         color = 'blue'
#         return color
#
# class Scout(Bee):
#     """
#     Scout bees only have a new position, because they have the same velocity and
#     starting position, and goal position. They are not concerned with following
#     other bees.
#     """
#
#     def determine_new_position(self, all_bees, tstep):
#         self.position = self.position + self.velocity * tstep
#         return self.position
#
#     def get_color(self):
#         color = 'red'
#         return color
#
# def initialize_new_hives(numhives):
#     new_hive_positions = []
#     color_new_hive = []
#     color = 'orange'
#     for i in range(numhives):
#         # new_hive_x = random.random() * 100
#         # new_hive_y = random.random() * 100
#         new_hive_x = 200
#         new_hive_y = 50
#         new_hive_positions.append(np.array([new_hive_x, new_hive_y]))
#         color_new_hive.append(color)
#     return new_hive_positions, color_new_hive
#
# def get_bees(numbees, scouts_position):
#     all_bees = []
#     amount_uninformed_bees = numbees
#     #amount_scouts = int(amount_uninformed_bees * 0.05)
#     #amount_scouts = len(scouts_position)
#
#     for i in range(amount_uninformed_bees):
#         x = random.uniform(0.0, 0.2) * 100
#         y = random.uniform(0.0, 0.2) * 100
#         # z = random.random() * 100
#         all_bees.append(UninformedBee(np.array([x,y]), np.zeros(2)))
#
#     for position in scouts_position:
#         x = position[0]
#         y = position[1]
#         xvel = -20.0
#         yvel = 0.0
#         # z = random.random() * 100
#         all_bees.append(Scout(np.array([x,y]), np.array([xvel,yvel])))
#
#     return all_bees
#
# def simulate(n):
#     number_of_bees = 40
#     number_of_scouts = 2
#     new_hives, hives_colors = initialize_new_hives(1)
#     all_bees = get_bees(number_of_bees, new_hives)
#     data = []
#     colors = []
#     for i in range(n):
#         positions = []
#         for bee in all_bees:
#             positions.append(bee.determine_new_position(all_bees, 0.1))
#             colors.append(bee.get_color())
#         data.append(positions)
#     return data, colors, new_hives, hives_colors
#
# def plot(data, color, new_hives, hives_colors):
#
#     plt.ion()
#     plt.show()
#
#     for positions in data:
#         plt.axis([-100, 300, -100, 300])
#
#         for count, position in enumerate(positions):
#             plt.scatter(position[0], position[1], color=color[count])
#             plt.draw()
#
#         for count, position in enumerate(new_hives):
#             plt.scatter(position[0], position[1], color=hives_colors[count])
#             plt.draw()
#
#         plt.pause(0.1)
#         plt.clf()
#
# if __name__ == '__main__':
#
#     data, color, new_hives, hives_colors = simulate(100)
#     plot(data, color, new_hives, hives_colors)

