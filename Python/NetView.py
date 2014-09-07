import sys
import pygame
import random
import math

class BaseNode():
	#this class will mimick a NetNode, but keep an on or off value
	#and return that value for the judge function
	value = 0
	xPos = 0
	yPos = 0
	radius = 0

	def __init__(self, value,x,y, radius):
		#simply set the isOn value to the passed value
		self.value = value
		self.xPos = int(x)
		self.yPos = int(y)
		self.radius = int(radius)

	def judge(self):
		return self.value

	def draw(self, screen, color):
		#this module will draw the node 
		pygame.draw.circle(screen, (0,255 * self.value,0), (self.xPos, self.yPos), self.radius, 0)


class NetNode():
	#This class will be the simulated brain cells
	inputNodes = []
	inputWeights = []
	xPos = 0
	yPos = 0
	radius = 0
	value = 0

	def __init__(self, newInputNodes,x, y, radius):
		#this constructor will assign 
		self.xPos = int(x)
		self.yPos = int(y)
		self.radius = int(radius)
		random.seed()
		self.inputNodes = []
		self.inputWeights = []
		for node in newInputNodes:
			self.inputNodes.append(node)
			self.inputWeights.append(random.random())

	def judge(self):
		#this modle will determine whether the neuron will fire
		#it will also recursively call 
		total = 0
		i = 0
		for node in self.inputNodes:
			total += node.judge() * self.inputWeights[i]
			i += 1

		total = 1 / (1 + math.exp(-total)) #sigmoid value
		self.value = total
		return total

	def draw(self, screen, color):
		#this module will draw the node and its associated lines
		self.judge()
		pygame.draw.circle(screen, color, (self.xPos, self.yPos), self.radius, 0)
		for node in self.inputNodes:
			pygame.draw.lines(screen, black, False, [(self.xPos - self.radius, self.yPos),(node.xPos + node.radius, node.yPos)], 1)


class NeuralNet():
	#this class will hold the majority of the logic base 
	#in the neural net implementation
	hiddenLayer = []
	baseLayer = []
	outPutLayer = []
	outPutSize = 1

	def __init__(self, inputList, outPutSize, screenSize):
		self.baseLayer = inputList
		self.outPutSize = outPutSize

		hiddenCount = len(inputList) + 1
		xSize = screenSize[0] - 100 #50 pixel buffer
		ySize = screenSize[1] - 100 

		ySpacing = ySize / hiddenCount
		# realEstate = int((ySize - ySpacing) / hiddenCount - 1)

		for i in range(1,len(inputList)+2):
			self.hiddenLayer.append(NetNode(self.baseLayer, 360, 50 + (ySpacing * i) - (ySpacing / 2), 30))

		ySpacing = ySize / self.outPutSize

		for i in range(1,self.outPutSize+1):
			self.outPutLayer.append(NetNode(self.hiddenLayer, 660, 50 + (ySpacing * i) - (ySpacing / 2), 30))

	def draw(self, screen):
		for node in self.baseLayer:
			node.draw(screen, (0,255,0))

		for node in self.hiddenLayer:
			node.draw(screen, (255 * node.judge(),0,0))

		for node in self.outPutLayer:
			node.draw(screen, (0,0,255 * node.judge()))

		self.identifyWinner(screen)

	def identifyWinner(self, screen):
		maxNode = None
		maxVal = 0
		for node in self.outPutLayer:
			print(node.value)
			if (node.value >= maxVal):
				maxVal = node.value
				maxNode = node
		pygame.draw.circle(screen, black, (maxNode.xPos, maxNode.yPos), maxNode.radius + 10, 2)

pygame.init()
screen = pygame.display.set_mode((800,600))

green = (0,255,0)
red = (255,0,0)
blue = (0,0,255)
white = (255,255,255)
black = (0,0,0)

screen.fill(white)

inputList = []
inputList.append(BaseNode(random.random(),60, 130, 30))
inputList.append(BaseNode(random.random(),60, 290, 30))
inputList.append(BaseNode(random.random(),60, 450, 30))

myNet = NeuralNet(inputList, 3, [800,600])
myNet.draw(screen)
pygame.display.update()
