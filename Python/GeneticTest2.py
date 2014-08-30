#!/usr/bin/env python
#This file will create some classes and modules to do some 
#genetic algorithms stuff
import random
import math
import pygame

class Bug():
	#this class will help us create our little critters!!
	posx = 0
	posy = 0
	points = 0
	dirangle = 0
	genelist = []

	def __init__(self, newgene):
		self.genelist = newgene
		self.posx = random.randrange(20, 780)
		self.posy = random.randrange(20, 580)
		self.dirangle = random.randrange(0,359)
		print(self.genelist) #retaining python 3 print syntax

	def addPoint(self):
		self.points += 1

	def drawSelf(self, screen):
		#pygame.draw.circle(screen, color, (x,y), radius, thickness)
		pygame.draw.circle(screen, self.genelist[3], (self.posx, self.posy), 10, 4) #self
		pygame.draw.circle(screen, (0,0,0), (self.posx, self.posy), self.genelist[5], 1) #sight


	def move(self, pack, others, foodlist):
		#this function will choose where our bug will move to next

		#initiate our clustering/avoiding behavior (if need be)
		if self.genelist[4] == 1:
			self.cluster(pack)
		elif self.genelist[4] == 2:
			self.avoid(others)

		#food seaking overrides all!!!
		self.seekFood(foodlist)

		#keep our bug in bounds
		if self.posx <= 10 or self.posx >= 790 or self.posy <= 10 or self.posy >= 590:
			self.dirangle += 180
			self.dirangle %= 360

		if random.randrange(0,self.genelist[0]) == 1: #if we are going to change direction
			self.dirangle += random.randrange(0,self.genelist[2]) #choose a random change value
			self.dirangle %= 360		

		#there are much better ways of doing this, but i am just knocking it out now
		angle = self.dirangle
		dirmult = 1 
		if angle > 180:
			angle -= 180
			dirmult = -1 #make us move left
		self.posx += int(((90 - abs(90 - angle)) / 90 * dirmult) * self.genelist[1])

		angle = self.dirangle + 90 #adjust it by 90
		angle %= 360
		dirmult = -1 
		if angle > 180:
			angle -= 180
			dirmult = 1 #make us move up
		self.posy += int(((90 - abs(90 - angle)) / 90 * dirmult) * self.genelist[1])

	def cluster(self, pack):
		#this module will alter the trajectory of the current bug to move closer to others in its pack
		for mate in pack:
			#if they are close, but not too close
			if (abs(mate.posx - self.posx) > 15) and (abs(mate.posx - self.posx) < self.genelist[5]):
				 if (abs(mate.posy - self.posy) > 15) and (abs(mate.posy - self.posy) < self.genelist[5]):
				 	#make our new angle of travel equal to the split between the two
				 	if mate.dirangle > self.dirangle:
				 		self.dirangle += int((mate.dirangle - self.dirangle))
				 	elif mate.dirangle < self.dirangle:				 		
				 		self.dirangle -= int((self.dirangle - mate.dirangle))

	def avoid(self, others):
		#this module will alter the trajectory of the current bug to further from those around it
		for uglies in others:
			#if they are close, but not too close
			if abs(uglies.posx - self.posx) < self.genelist[5]:
				 if abs(uglies.posy - self.posy) < self.genelist[5]:
				 	#make our new angle of travel equal to the split between the two
				 	if uglies.dirangle > self.dirangle:
				 		self.dirangle += int((uglies.dirangle - self.dirangle) * .5)
				 	elif uglies.dirangle < self.dirangle:				 		
				 		self.dirangle -= int((self.dirangle - uglies.dirangle) * .5)

	def seekFood(self, foodlist):
		#this module will determine if there is any food within sight
		#if so, it will seek out the food!!!
		for food in foodlist:
			if abs(food.posx - self.posx) < self.genelist[5]:
				 if abs(food.posy - self.posy) < self.genelist[5]:
				 	#the food is within sight!
				 	#let's get it!!
				 	self.dirangle = 90 + math.degrees(math.atan2((food.posy - self.posy),(food.posx - self.posx + 0.001)))


	def combineWithGene(self, secondgene):
		#this function will combine two genes together
		splitpoint = random.randrange(0, len(self.genelist))
		secondgenelist = secondgene.getgenelist()
		return self.genelist[:splitpoint] + secondgenelist[splitpoint:]

	def calcFitness(self):
		return self.points

	def getgenelist(self):
		#this will return our genelist so it can be drawn
		return self.genelist

	def mutate(self, limdwell, limspeed, limagility, limsight):
		#change up to two parts of the gene
		for i in range(random.randrange(0,2)):
			randNum = random.randrange(0,6)
			if randNum == 0:
				self.genelist[0] = random.randrange(0,limdwell)	
			elif randNum == 1:
				self.genelist[1] = random.randrange(0,limspeed)
			elif randNum == 2:
				self.genelist[2] = random.randrange(0,limagility)
			elif randNum == 3:
				self.genelist[4] = random.randrange(0,3) #clustering
			else:
				self.genelist[5] = random.randrange(1,limsight)

			self.genelist[3] = (random.randrange(200),random.randrange(200),random.randrange(200))		

class Population():
	#This class will hold all the active bugs and perform the reproductions
	population = []
	limdwell = 1000
	limspeed = 8
	limagility = 350
	limsight = 75

	def __init__(self, populationcount):
		self.population = self.genPopulation(populationcount)

	def getPopulation(self):
		return self.population

	def genRandGene(self):
		newgene = []
		newgene.append(random.randrange(0,self.limdwell))		
		newgene.append(random.randrange(0,self.limspeed))
		newgene.append(random.randrange(0,self.limagility))
		color = (random.randrange(200),random.randrange(200),random.randrange(200))
		newgene.append(color)
		newgene.append(random.randrange(0,3)) #clustering/avoiding
		newgene.append(random.randrange(1,self.limsight))
		return newgene

	def genPopulation(self,populationcount):
		newpopulation = []
		for i in range(0, populationcount):
			newpopulation.append(Bug(self.genRandGene()))
		return newpopulation

	def sortPopulation(self):
		#this function will arrange the population from most to least fit
		populationlist = []
		for i in range(0, len(self.population)):  #go through each member in the population
			populationlist.append((self.population[i],self.population[i].calcFitness()))  #and add the member and its fitness

		newpopulationlist = sorted(populationlist, key=lambda x: x[1], reverse=True)
		self.population = [i[0] for i in newpopulationlist] #just get the genes

	def createNextGeneration(self):
		#this function will do the breeding for our next createNextGeneration
		self.sortPopulation()
		newpopulation = []
		print(self.population[0].calcFitness())
		self.population[0].points = 0 #set the top bug's points to 0 so there is no carry-over
		newpopulation.append(self.population[0])  #keep the top dog!
		newpopulation.append(Bug(self.population[0].combineWithGene(self.population[1])))
		newpopulation.append(Bug(self.population[0].combineWithGene(self.population[2])))
		newpopulation.append(Bug(self.population[0].combineWithGene(self.population[3])))
		newpopulation.append(Bug(self.population[0].combineWithGene(self.population[4])))
		newpopulation.append(Bug(self.population[1].combineWithGene(self.population[2])))
		newpopulation.append(Bug(self.population[1].combineWithGene(self.population[3])))
		newpopulation.append(Bug(self.population[1].combineWithGene(self.population[4])))
		newpopulation.append(Bug(self.population[2].combineWithGene(self.population[3])))
		newpopulation.append(Bug(self.population[0].combineWithGene(self.population[1])))
		self.population = newpopulation  #now we kill off the old generation and bring in the new!

	def mutatePopulation(self):
		#mutate anywhere from 0 to 4 members of the population
		self.sortPopulation() #sort the population beforehand to protect the top candidates
		for i in range(random.randrange(0,4)):
			self.population[random.randrange(2,9)].mutate(self.limdwell, self.limspeed, self.limagility, self.limsight)

	def maxFitness(self):
		#return the max fitness of the population
		self.sortPopulation()
		return self.population[0].calcFitness()

	def drawPopulation(self, screen):
		for creature in self.population:
			creature.drawSelf(screen)

	def getCreatures(self):
		return self.population

	def move(self, foodlist):
		pack = []
		#create our pack
		for creature in self.population:
			if creature.genelist[4] == 1: #only add them if they want to cluster
				pack.append(creature)

		for creature in self.population:
			creature.move(pack, self.population, foodlist)

	
class Food():
	#this will be a simple class to create our randomly placed food
	posx = 0
	posy = 0

	def __init__(self):
		self.posx = random.randrange(10, 790)
		self.posy = random.randrange(10, 590)

	def drawSelf(self, screen, color):
		#pygame.draw.rect(screen, color, (x,y,width,height), thickness)
		pygame.draw.rect(screen, color, (self.posx, self.posy,11,11), 5)

class FoodContainer():
	#this will be a class that controls and maintains the food supply	
	foodlist = []

	def __init__(self, foodlimit):
		for i in range(foodlimit):
			self.foodlist.append(Food())

	def drawFood(self, screen, color):
		for food in self.foodlist:
			food.drawSelf(screen, color)

	def handleCollisions(self, target):
		i = 0
		for food in self.foodlist:
			#simple circle collision detection
			if abs(food.posx + 5 - target.posx) < 15: 
				if abs(food.posy + 5 - target.posy) < 15: 
					target.addPoint()    #add a point to the target's total
					self.foodlist[i] = Food() #kill the old food and make a new piece
			i += 1


def runSimulation():
	#This will run the simulaiton and perform the majority of the logic
	pygame.init()
	screen = pygame.display.set_mode((800,600))

	green = (0,255,0)
	white = (255,255,255)

	availablefood = FoodContainer(15)
	creatures = Population(15)

	findingsolution = True
	count = 0
	longcount = 0
	while findingsolution:
		screen.fill(white)
		if longcount == 10000:
			creatures.createNextGeneration()
			creatures.mutatePopulation()
			longcount = 0
		else:
			longcount += 1
			
		if count == 0:
			creatures.move(availablefood.foodlist)
			count += 1
		elif count == 10:
			count = 0
		else:
			count += 1

		for creature in creatures.getCreatures():
			availablefood.handleCollisions(creature)

		availablefood.drawFood(screen, green)
		creatures.drawPopulation(screen)

		pygame.display.update()

	pygame.quit()


runSimulation()
