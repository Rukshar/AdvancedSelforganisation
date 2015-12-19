from __future__ import division
import numpy as np
import random
import time
import csv
import matplotlib.pyplot as plt
import os

w_cohere = 0.3  # 0.3 volgens paper het beste
w_avoid = 0.3  # 0.3 volgens paper het beste
w_align = 0.3  # 0.3 volgens paper het beste
w_random = 0.3  # 0.3 volgens paper het beste
max_acceleration = 0.3
visible_distance = 30.0  # 30.0
minimum_distance = 15.0  # 15.0
max_velocity = 1.0
weight = 0.8

# pheromone model
w_excretion_freq = 0.5  # per hoeveel tijd er wordt uitgescheiden, moet een float zijn
w_attract = 0.3
pheromone_decay = 0.1

scout_velocity = -2.5
scout_velocity_decay = 0.8
scout_near = 5 #distance to destination to decrease velocity
scout_min_neighbours = 10
scout_minimum_distance = 10

hive_pos = np.array([-20.0, 0.0])
constant_names = ["w_cohere","w_avoid","w_align","w_random","max_acceleration","visible_distance","minimum_distance",\
                  "max_velocity", "weight","w_excretion_freq", "w_attract", "pheromone_decay", "scout_velocity","scout_velocity_decay",\
                  "scout_near", "scout_min_neighbours","scout_minimum_distance","hive_pos"]

constant_values = [w_cohere,w_avoid,w_align,w_random,max_acceleration,visible_distance,minimum_distance,max_velocity,\
                   weight,w_excretion_freq,w_attract, pheromone_decay,scout_velocity,scout_velocity_decay,scout_near,scout_min_neighbours,\
                   scout_minimum_distance,hive_pos]

def magnitude(pos):
    return np.sqrt(pos.dot(pos))

def get_xy_velocity(posa,posb,v):
    """
    Pos is a np.array (vector)
    v is the wished velocity
    this method will calculate the velocity for x and y given two positions and a velocity
    """
    rest = posa-posb
    m = magnitude(rest)
    vx = (v * rest[0])/m
    vy = (v * rest[1])/m
    if m < scout_near:
        return vx * scout_velocity_decay*m/scout_near,vy * scout_velocity_decay*m/scout_near
    return vx,vy


class Bee(object):
    """
    A bee has a starting position and a starting velocity, the swarm exists
    of uninformed bees and scouts
    """

    def __init__(self, initial_position, initial_velocity):
        self.position = initial_position
        self.velocity = initial_velocity

class UninformedBee(Bee):
    """
    Uninformed bees behave as a swarm (i.e. follow each other) therefore they
    have a cohere function, align function, avoid function and also a random
    function to determine their new velocity and position. The formulas are
    from (Janson et al., 2004).
    """

    def _cohere(self, visible_neighbours):

        if len(visible_neighbours) == 0:
            return 0

        total = 0.0

        for neighbour in visible_neighbours:
            total += (neighbour.position - self.position)

        return (1 / visible_distance) * (1 / len(visible_neighbours)) * total

    def _align(self, visible_neighbours):
        if len(visible_neighbours) == 0:
            return 0

        total = 0.0

        for neighbour in visible_neighbours:
            total += neighbour.velocity

        return (1 / max_velocity) * (1 / len(visible_neighbours)) * total

    def _avoid(self, min_neighbours):
        if len(min_neighbours) == 0:
            return 0

        total = 0.0
        for neighbour in min_neighbours:
            total += ((self.position - neighbour.position) *
                      (minimum_distance / magnitude(self.position - neighbour.position) - 1))

        return (1 / minimum_distance) * (1 / len(min_neighbours)) * total

    def _random(self):
        random_vector = np.random.uniform(low=-1.0, high=1.0, size=2)
        mag_random_vector = magnitude(random_vector)

        # In the paper they use a random point from the cdf but I don't think that's neceassary/useful
        beta = random.random()

        # _random = size of velocity * direction size
        return beta * (random_vector / mag_random_vector)

    def _attract(self, visible_pheromones):

        if len(visible_pheromones) == 0:
            return 0

        total = 0.0

        for pheromone in visible_pheromones:
            total += (pheromone.position - self.position) * pheromone.intensity

        return (1 / visible_distance) * total


    def determine_new_position(self, all_bees, pheromones, tstep):
        visible_neighbours = []
        visible_pheromones = []
        min_neighbours = []

        for bee in all_bees:
            if bee is self:
                continue

            if magnitude(self.position - bee.position) < visible_distance:
                visible_neighbours.append(bee)

                if magnitude(self.position - bee.position) < minimum_distance:
                    min_neighbours.append(bee)

        for pheromone in pheromones:
            if magnitude(self.position - pheromone.position) < visible_distance:
                visible_pheromones.append(pheromone)

        cohere = self._cohere(visible_neighbours)
        align = self._align(visible_neighbours)
        avoid = self._avoid(min_neighbours)
        random = self._random()
        attract = self._attract(visible_pheromones)

        new_velocity = w_cohere * cohere + w_avoid * avoid + w_align * align + w_random * random + w_attract * attract

        if magnitude(new_velocity) <= max_acceleration:
            self.velocity = weight * self.velocity + new_velocity
        else:
            new_velocity = max_acceleration * (new_velocity / magnitude(new_velocity))
            self.velocity = weight * self.velocity + new_velocity

        # self.velocity = weight * self.velocity + new_velocity
        self.position = self.position + self.velocity * tstep

        return self.position

class Scout(Bee):
    """
    Scout bees only have a new position, because they have the same velocity and
    starting position, and goal position. They are not concerned with following
    other bees.
    """

    def __init__(self, initial_position, initial_velocity):
        Bee.__init__(self, initial_position, initial_velocity)

        self.initial_position = initial_position

        self.timer = 0.0

    def excrete_pheromone(self, tstep):
        if (self.timer < w_excretion_freq):
            # print 'yes'
            self.timer += tstep
            return None
        else:
            self.timer = 0.0
            # print 'excrete!'
            return Pheromone(self.position)


    def determine_new_position(self, all_bees, pheromones, tstep):
        front_of_swarm, back_of_swarm = get_ends_of_swarm(all_bees)
        min_neighbours = []

        for bee in all_bees:
            if bee is self:
                continue

            if magnitude(self.position - bee.position) < scout_minimum_distance:
                min_neighbours.append(bee)

        if len(min_neighbours) < scout_min_neighbours:
            self.position = np.array([back_of_swarm, self.initial_position[1] + random.uniform(-0.5,0.5)])

        else:
            vx,vy = get_xy_velocity(self.position,hive_pos,scout_velocity)
            self.set_velocity(vx,vy)
            self.position = self.position + self.velocity * tstep

        return self.position

    def set_velocity(self,vx,vy):
        self.velocity = np.array([vx,vy])

class Pheromone:
    def __init__(self, position):
        self.position = position
        self.intensity = 1.0

    def update(self, tstep):
        self.intensity *= pheromone_decay ** tstep

def get_bees(numbees):
    uninformed_bees = []
    scout_bees = []

    amount_uninformed_bees = numbees
    amount_scouts = int(amount_uninformed_bees * 0.05)
    # amount_scouts = 10

    for i in range(amount_uninformed_bees):
        x = random.uniform(-5.0,5.0)
        y = random.uniform(-5.0,5.0)
        # z = random.random() * 100
        uninformed_bees.append(UninformedBee(np.array([x, y]), np.zeros(2)))

    front_of_swarm, back_of_swarm = get_ends_of_swarm(uninformed_bees)

    for i in range(amount_scouts):
        x = back_of_swarm + random.uniform(-2.5, 0.2)
        y = random.uniform(-5.0,5.0)
        spos = np.array([x, y])
        xvel,yvel = get_xy_velocity(hive_pos,spos,scout_velocity)
        # z = random.random() * 100
        scout_bees.append(Scout(spos, np.array([xvel, yvel])))

    return uninformed_bees, scout_bees

def get_ends_of_swarm(uninformed_bees):
    back_of_swarm = uninformed_bees[0].position[0]
    front_of_swarm = uninformed_bees[0].position[0]
    for bees in uninformed_bees[1:]:
        if bees.position[0] > back_of_swarm:
            back_of_swarm = bees.position[0]
        if bees.position[0] < front_of_swarm:
            front_of_swarm = bees.position[0]
    return front_of_swarm, back_of_swarm

def calculate_distance(pos_hive, pos_swarm):
    return round(magnitude(pos_hive - pos_swarm),3)

def save_file(listname):

    name = raw_input("Give file name: ")

    path = "sim_files/" +name +"/"
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    with open(path + name +".csv", "wb") as f:
        writer = csv.writer(f)
        writer.writerows(listname)
    save_image(path,name)

def save_file_auto(listname,path,filename):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))

    with open(path + filename +".csv", "wb") as f:
        writer = csv.writer(f)
        writer.writerows(listname)
    save_image(path,filename)

def save_image(path,name):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
    plt.savefig(path + name +".png")

def combine_list(lista,listb):
    new_list =[["TIME","DISTANCE"]]
    new_list[0].extend(constant_names)
    for i in range(len(lista)):
        l= [lista[i],round(listb[i],4)]
        l.extend(constant_values)
        new_list.append(l)
    return new_list


def simulate(n):

    time_list = []
    time_cummulative = 0.0
    number_of_bees = 100
    timestep = 0.1
    uninformed_bees, scout_bees = get_bees(number_of_bees)
    all_bees = uninformed_bees + scout_bees
    pheromones = []
    plt.subplot(1, 2, 1)
    # plt.ion()
    # plt.show()
    distances_list = []
    length = range(n)
    run = True

    while(run):
        for i in length:
            plt.clf()

            #manager = plt.get_current_fig_manager()
            #manager.window.showMaximized()

            swarm_centre = np.array([0.0, 0.0])
            plt.subplot(2, 1, 1)
            # COMPUTATION
            for bee in all_bees:
                bee.determine_new_position(all_bees, pheromones, timestep)

            for scout in scout_bees:
                pheromone = scout.excrete_pheromone(timestep)
                if pheromone:
                    pheromones.append(pheromone)

            for pheromone in pheromones:
                pheromone.update(timestep)
                if pheromone.intensity < 0.01:
                    pheromones.remove(pheromone)

            # VISUALIZE BEES
            for uninformed_bee in uninformed_bees:
                position = uninformed_bee.position
                swarm_centre += position / len(uninformed_bees)
                plt.scatter(position[0], position[1], color='blue')

            for scout in scout_bees:
                position = scout.position
                plt.scatter(position[0], position[1], color='red')

            for pheromone in pheromones:
                position = pheromone.position
                plt.scatter(position[0], position[1], color='black', alpha=pheromone.intensity)

            plt.scatter(swarm_centre[0], swarm_centre[1], color='orange')
            plt.scatter(hive_pos[0],hive_pos[1],color='green')
            plt.ylim(-5,20)
            plt.xlim(-50,20)
            plt.draw()

            plt.subplot(2, 1, 2)
            d = calculate_distance(hive_pos, swarm_centre)
            # print d
            distances_list.append(d)
            time_cummulative = round(time_cummulative +timestep,1)
            time_list.append(time_cummulative)

            plt.plot(time_list, distances_list)
            plt.ylim(0,45)
            plt.xlabel('TIME')
            plt.ylabel('DISTANCE TO DESTINATION')
            plt.draw()
            plt.pause(timestep)
            # plt.clf()
            print i
            if (i==length[-1]):

                user_input = raw_input("Want to continue sim? y/n ")
                if user_input == 'n':
                    run=False
                else:
                    length = range(int(raw_input("n = ")))

                user_input = raw_input("Want to export? y/n ")
                if user_input == 'y':
                    save_file( combine_list(time_list,distances_list) )
        print run
    plt.show()
    return time_list,distances_list

def simulate_auto(n,number_samples):
    dirname = filename = raw_input("Enter the name of this simulation (directory name): ")
    path = "sim_files/" +dirname +"/"
    filecount = 1

    for j in range(1,number_samples+1):
        time_list = []
        time_cummulative = 0.0
        number_of_bees = 100
        timestep = 0.1
        uninformed_bees, scout_bees = get_bees(number_of_bees)
        all_bees = uninformed_bees + scout_bees
        pheromones = []
        plt.subplot(1, 2, 1)
        # plt.ion()
        # plt.show()
        distances_list = []

        imagecount = 1
        for i in range(n):
            plt.clf()

            manager = plt.get_current_fig_manager()
            manager.window.showMaximized()

            front_of_swarm, back_of_swarm = get_ends_of_swarm(uninformed_bees)

            swarm_centre = np.array([0.0, 0.0])
            plt.subplot(1, 2, 1)
            # COMPUTATION
            for bee in all_bees:
                bee.determine_new_position(all_bees, pheromones, timestep)

            for scout in scout_bees:
                # print np.floor(scout.position[0]), np.floor(front_of_swarm)
                if np.floor(scout.position[0]) <= np.floor(front_of_swarm + random.uniform(-1.0,5 )):
                    pheromone = scout.excrete_pheromone(timestep)
                    if pheromone:
                        pheromones.append(pheromone)
                if scout.position[0] == hive_pos[0]:
                    pheromone = scout.excrete_pheromone(timestep)
                    if pheromone:
                        pheromones.append(pheromone)

            for pheromone in pheromones:
                pheromone.update(timestep)
                if pheromone.intensity < 0.01:
                    pheromones.remove(pheromone)

            # VISUALIZE BEES
            for uninformed_bee in uninformed_bees:
                position = uninformed_bee.position
                swarm_centre += position / len(uninformed_bees)
                plt.scatter(position[0], position[1], color='blue')

            for scout in scout_bees:
                position = scout.position
                plt.scatter(position[0], position[1], color='red')

            for pheromone in pheromones:
                position = pheromone.position
                plt.scatter(position[0], position[1], color='black', alpha=pheromone.intensity)

            plt.scatter(swarm_centre[0], swarm_centre[1], color='orange')
            plt.scatter(hive_pos[0],hive_pos[1],color='green')
            plt.ylim(-20,20)
            plt.xlim(-30,10)
            plt.draw()
            plt.xlabel('X coordinate',size=16)
            plt.ylabel('Y coordinate',size=16)

            plt.subplot(1, 2, 2)
            d = calculate_distance(hive_pos, swarm_centre)
            # print d
            distances_list.append(d)
            time_cummulative = round(time_cummulative +timestep,1)
            time_list.append(time_cummulative)

            plt.plot(time_list, distances_list)
            plt.ylim(0,45)
            plt.xlabel('Time',size=16)
            plt.ylabel('Distance to hive',size=16)
            plt.draw()
            plt.pause(timestep)

            if i%(n/5.0)==0:
                save_image(path,filename +"_"+ str(filecount) +"_"+str(imagecount))
                imagecount+=1
        l = combine_list(time_list,distances_list)
        save_file_auto(l,path,filename+str(filecount))
        filecount+=1
        print "finished sample nr: " + str(j)
    plt.show()


if __name__ == '__main__':
    simulate_auto(300,3)




