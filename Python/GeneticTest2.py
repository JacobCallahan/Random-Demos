#  This file will create some classes and modules to do some 
#  genetic algorithms stuff
import random
import math
import sys
import pygame

class Bug():
	#this class will help us create our little critters!!
	posX = 0
	posY = 0
	points = 0
	dirAngle = 0
	geneList = []

	def __init__(self, newGene):
		self.geneList = newGene
		self.posX = random.randrange(20, 780)
		self.posY = random.randrange(20, 580)
		self.dirAngle = random.randrange(0,359)
		print(self.geneList)

	def addPoint(self):
		self.points += 1

	def drawSelf(self, screen):
		#pygame.draw.circle(screen, color, (x,y), radius, thickness)
		pygame.draw.circle(screen, self.geneList[3], (self.posX, self.posY), 10, 4) #self
		pygame.draw.circle(screen, (0,0,0), (self.posX, self.posY), self.geneList[5], 1) #sight


	def move(self, pack, others, foodList):
		#this function will choose where our bug will move to next

		#initiate our clustering/avoiding behavior (if need be)
		if self.geneList[4] == 1:
			self.cluster(pack)
		elif self.geneList[4] == 2:
			self.avoid(others)

		#food seaking overrides all!!!
		self.seekFood(foodList)

		#keep our bug in bounds
		if self.posX <= 10 or self.posX >= 790 or self.posY <= 10 or self.posY >= 590:
			self.dirAngle += 180
			self.dirAngle %= 360

		if random.randrange(0,self.geneList[0]) == 1: #if we are going to change direction
			self.dirAngle += random.randrange(0,self.geneList[2]) #choose a random change value
			self.dirAngle %= 360		

		#there are much better ways of doing this, but i am just knocking it out now
		angle = self.dirAngle
		dirMult = 1 
		if angle > 180:
			angle -= 180
			dirMult = -1 #make us move left
		self.posX += int(((90 - abs(90 - angle)) / 90 * dirMult) * self.geneList[1])

		angle = self.dirAngle + 90 #adjust it by 90
		angle %= 360
		dirMult = -1 
		if angle > 180:
			angle -= 180
			dirMult = 1 #make us move up
		self.posY += int(((90 - abs(90 - angle)) / 90 * dirMult) * self.geneList[1])

	def cluster(self, pack):
		#this module will alter the trajectory of the current bug to move closer to others in its pack
		for mate in pack:
			#if they are close, but not too close
			if (abs(mate.posX - self.posX) > 15) and (abs(mate.posX - self.posX) < self.geneList[5]):
				 if (abs(mate.posY - self.posY) > 15) and (abs(mate.posY - self.posY) < self.geneList[5]):
				 	#make our new angle of travel equal to the split between the two
				 	if mate.dirAngle > self.dirAngle:
				 		self.dirAngle += int((mate.dirAngle - self.dirAngle))
				 	elif mate.dirAngle < self.dirAngle:				 		
				 		self.dirAngle -= int((self.dirAngle - mate.dirAngle))

	def avoid(self, others):
		#this module will alter the trajectory of the current bug to further from those around it
		for uglies in others:
			#if they are close, but not too close
			if (abs(uglies.posX - self.posX) < self.geneList[5]):
				 if (abs(uglies.posY - self.posY) < self.geneList[5]):
				 	#make our new angle of travel equal to the split between the two
				 	if uglies.dirAngle > self.dirAngle:
				 		self.dirAngle += int((uglies.dirAngle - self.dirAngle) * .5)
				 	elif uglies.dirAngle < self.dirAngle:				 		
				 		self.dirAngle -= int((self.dirAngle - uglies.dirAngle) * .5)

	def seekFood(self, foodList):
		#this module will determine if there is any food within sight
		#if so, it will seek out the food!!!
		for food in foodList:
			if (abs(food.posX - self.posX) < self.geneList[5]):
				 if (abs(food.posY - self.posY) < self.geneList[5]):
				 	#the food is within sight!
				 	#let's get it!!
				 	self.dirAngle = 90 + math.degrees(math.atan2((food.posY - self.posY),(food.posX - self.posX + 0.001)))


	def combineWithGene(self, secondGene):
		#this function will combine two genes together
		splitPoint = random.randrange(0, len(self.geneList))
		secondGeneList = secondGene.getGeneList()
		return self.geneList[:splitPoint] + secondGeneList[splitPoint:]

	def calcFitness(self):
		return self.points

	def getGeneList(self):
		#this will return our geneList so it can be drawn
		return self.geneList

	def mutate(self, limDwell, limSpeed, limAgility, limSight):
		#change up to two parts of the gene
		for i in range(random.randrange(0,2)):
			randNum = random.randrange(0,6)
			if randNum == 0:
				self.geneList[0] = random.randrange(0,limDwell)	
			elif randNum == 1:
				self.geneList[1] = random.randrange(0,limSpeed)
			elif randNum == 2:
				self.geneList[2] = random.randrange(0,limAgility)
			elif randNum == 3:
				self.geneList[4] = random.randrange(0,3) #clustering
			else:
				self.geneList[5] = random.randrange(1,limSight)

			self.geneList[3] = (random.randrange(200),random.randrange(200),random.randrange(200))		

class Population():
	#This class will hold all the active bugs and perform the reproductions
	population = []
	limDwell = 1000
	limSpeed = 8
	limAgility = 350
	limSight = 75

	def __init__(self, populationCount):
		self.population = self.genPopulation(populationCount)

	def getPopulation(self):
		return self.population

	def genRandGene(self):
		newGene = []
		newGene.append(random.randrange(0,self.limDwell))		
		newGene.append(random.randrange(0,self.limSpeed))
		newGene.append(random.randrange(0,self.limAgility))
		color = (random.randrange(200),random.randrange(200),random.randrange(200))
		newGene.append(color)
		newGene.append(random.randrange(0,3)) #clustering/avoiding
		newGene.append(random.randrange(1,self.limSight))
		return newGene

	def genPopulation(self,populationCount):
		newPopulation = []
		for i in range(0, populationCount):
			newPopulation.append(Bug(self.genRandGene()))
		return newPopulation

	def sortPopulation(self):
		#this function will arrange the population from most to least fit
		populationList = []
		for i in range(0, len(self.population)):  #go through each member in the population
			populationList.append((self.population[i],self.population[i].calcFitness()))  #and add the member and its fitness

		newPopulationList = sorted(populationList, key=lambda x: x[1], reverse=True)
		self.population = [i[0] for i in newPopulationList] #just get the genes

	def createNextGeneration(self):
		#this function will do the breeding for our next createNextGeneration
		self.sortPopulation()
		newPopulation = []
		print(self.population[0].calcFitness())
		self.population[0].points = 0 #set the top bug's points to 0 so there is no carry-over
		newPopulation.append(self.population[0])  #keep the top dog!
		newPopulation.append(Bug(self.population[0].combineWithGene(self.population[1])))
		newPopulation.append(Bug(self.population[0].combineWithGene(self.population[2])))
		newPopulation.append(Bug(self.population[0].combineWithGene(self.population[3])))
		newPopulation.append(Bug(self.population[0].combineWithGene(self.population[4])))
		newPopulation.append(Bug(self.population[1].combineWithGene(self.population[2])))
		newPopulation.append(Bug(self.population[1].combineWithGene(self.population[3])))
		newPopulation.append(Bug(self.population[1].combineWithGene(self.population[4])))
		newPopulation.append(Bug(self.population[2].combineWithGene(self.population[3])))
		newPopulation.append(Bug(self.population[0].combineWithGene(self.population[1])))
		self.population = newPopulation  #now we kill off the old generation and bring in the new!

	def mutatePopulation(self):
		#mutate anywhere from 0 to 4 members of the population
		self.sortPopulation() #sort the population beforehand to protect the top candidates
		for i in range(random.randrange(0,4)):
			self.population[random.randrange(2,9)].mutate(self.limDwell, self.limSpeed, self.limAgility, self.limSight)

	def maxFitness(self):
		#return the max fitness of the population
		self.sortPopulation()
		return self.population[0].calcFitness()

	def drawPopulation(self, screen):
		for creature in self.population:
			creature.drawSelf(screen)

	def getCreatures(self):
		return self.population

	def move(self, foodList):
		pack = []
		#create our pack
		for creature in self.population:
			if creature.geneList[4] == 1: #only add them if they want to cluster
				pack.append(creature)

		for creature in self.population:
			creature.move(pack, self.population, foodList)

	
class Food():
	#this will be a simple class to create our randomly placed food
	posX = 0
	posY = 0

	def __init__(self):
		self.posX = random.randrange(10, 790)
		self.posY = random.randrange(10, 590)

	def drawSelf(self, screen, color):
		#pygame.draw.rect(screen, color, (x,y,width,height), thickness)
		pygame.draw.rect(screen, color, (self.posX, self.posY,11,11), 5)

class FoodContainer():
	#this will be a class that controls and maintains the food supply	
	foodList = []

	def __init__(self, foodLimit):
		for i in range(foodLimit):
			self.foodList.append(Food())

	def drawFood(self, screen, color):
		for food in self.foodList:
			food.drawSelf(screen, color)

	def handleCollisions(self, target):
		i = 0
		for food in self.foodList:
			#simple circle collision detection
			if abs(food.posX + 5 - target.posX) < 15: 
				if abs(food.posY + 5 - target.posY) < 15: 
					target.addPoint()    #add a point to the target's total
					self.foodList[i] = Food() #kill the old food and make a new piece
			i += 1


def runSimulation():
	#This will run the simulaiton and perform the majority of the logic
	pygame.init()
	screen = pygame.display.set_mode((800,600))

	green = (0,255,0)
	white = (255,255,255)

	availableFood = FoodContainer(15)
	creatures = Population(15)

	findingSolution = True
	count = 0
	longCount = 0
	while findingSolution:
		screen.fill(white)
		if longCount == 10000:
			creatures.createNextGeneration()
			creatures.mutatePopulation()
			longCount = 0
		else:
			longCount += 1
			
		if count == 0:
			creatures.move(availableFood.foodList)
			count += 1
		elif count == 10:
			count = 0
		else:
			count += 1

		for creature in creatures.getCreatures():
			availableFood.handleCollisions(creature)

		availableFood.drawFood(screen, green)
		creatures.drawPopulation(screen)

		pygame.display.update()

	pygame.quit()


runSimulation()
