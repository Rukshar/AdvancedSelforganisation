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


def magnitude(x):
	return np.sqrt(x.dot(x))

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

		return (1/visible_distance) * (1/len(visible_neighbours)) * total

	def _align(self, visible_neighbours):
		if len(visible_neighbours) == 0:
			return 0
		
		total = 0.0

		for neighbour in visible_neighbours:
			total += neighbour.velocity
		
		return (1/max_velocity) * (1/len(visible_neighbours)) * total

	def _avoid(self, min_neighbours):
		if len(min_neighbours) == 0:
			return 0

		total = 0.0
		for neighbour in min_neighbours:
			total += ((self.position - neighbour.position) *
			 (minimum_distance/magnitude(self.position - neighbour.position) -1))

		return (1/minimum_distance) * (1/len(min_neighbours)) * total

	def _random(self):
		pass

	def determine_new_position(self, all_bees, tstep):
		visible_neighbours = []
		min_neighbours = []

		for bee in all_bees:
			if bee is self:
				continue

			if magnitude(self.position - bee.position) < visible_distance:
				visible_neighbours.append(bee)

				if magnitude(self.position - bee.position) < minimum_distance:
					min_neighbours.append(bee)

		cohere = self._cohere(visible_neighbours)
		align = self._align(visible_neighbours)
		avoid = self._avoid(min_neighbours)
		new_velocity = w_cohere * cohere + w_avoid * avoid + w_align * align
		self.velocity = weight * self.velocity + new_velocity
		self.position = self.position + self.velocity * tstep
		
		return self.position

	def get_color(self):
		color = 'blue'
		return color

class Scout(Bee):
	"""
	Scout bees only have a new position, because they have the same velocity and
	starting position, and goal position. They are not concerned with following
	other bees.
	"""

	def determine_new_position(self, all_bees, tstep):
		self.position = self.position + self.velocity * tstep
		return self.position

	def get_color(self):
		color = 'red'
		return color

def get_bees(numbees):
	all_bees = []
	amount_uninformed_bees = numbees
	amount_scouts = int(amount_uninformed_bees * 0.05)

	for i in range(amount_uninformed_bees):
		x = random.random() * 100
		y = random.random() * 100
		# z = random.random() * 100
		all_bees.append(UninformedBee(np.array([x,y]), np.zeros(2)))

	for i in range(amount_scouts):
		x = 100.
		y = 50.
		xvel = -20.0
		yvel = 0.0
		# z = random.random() * 100
		all_bees.append(Scout(np.array([x,y]), np.array([xvel,yvel])))

	return all_bees

def simulate(n):
	all_bees = get_bees(40)
	
	data = []
	colors = []
	for i in range(n):
		positions = []
		for bee in all_bees:
			positions.append(bee.determine_new_position(all_bees, 0.1))
			colors.append(bee.get_color())
		data.append(positions)
	return data, colors

def plot(data, color):
	
	plt.ion()
	plt.show()

	for positions in data:
		plt.axis([0, 100, 0, 100])
		
		for count, position in enumerate(positions):
			plt.scatter(position[0], position[1], color=color[count])
			plt.draw()

		plt.pause(0.1)
		plt.clf()

if __name__ == '__main__':
	data, color = simulate(100)
	plot(data, color)

