using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Drawing;
using System.Windows.Forms;

namespace NeuralNetVisualizer
{
    class NeuralNet
    {
        NetNode[] inputNodes, outputNodes;
        NetNode[,] hiddenNodes;
        NetNode selectedNode;
        int[] baseCoords, canvasSize;
        int radius;

        public NeuralNet(Double[] inputValues, int hiddenLayers, int outputCount, int[] newCanvasSize)
        {
            int inputCount = inputValues.Length;
            baseCoords = new int[] { 120, 62 };
            canvasSize = newCanvasSize;
            selectedNode = null;

            //Create a neural network based on passed values
            Random random = new Random();
            //determine the radius of our nodes
            radius = 25;

            //create our input layer
            inputNodes = new NetNode[inputCount];
            for (int i = 0; i < inputCount; i++)
            {
                //create random weights for our node
                Double[] newWeights = new Double[inputCount + 1];
                for (int c = 0; c < inputCount + 1; c++)
                {
                    newWeights[c] = random.NextDouble();
                }
                //assign a position for the node to occupy
                Point newPosition = new Point(
                    baseCoords[0] + radius,
                    canvasSize[1] / newWeights.Length * (i + 1)
                );
                //create the new node
                inputNodes[i] = new NetNode(newWeights, inputValues[i], newPosition, radius);
            }

            //create our hidden layers
            hiddenNodes = new NetNode[hiddenLayers, inputCount + 1];
            for (int i = 0; i < hiddenLayers; i++)
            {
                for (int c = 0; c <= inputCount; c++)
                {
                    //create random weights for our node
                    Double[] newWeights = new Double[inputCount + 1];
                    for (int x = 0; x < inputCount + 1; x++)
                    {
                        newWeights[x] = random.NextDouble();
                    }
                    //assign a position for the node to occupy
                    Point newPosition = new Point(
                        baseCoords[0] + (canvasSize[0] - radius * 4) / (hiddenLayers + 1) * (i + 1),
                        canvasSize[1] / (newWeights.Length + 1) * (c + 1)
                    );

                    //create the new node
                    hiddenNodes[i, c] = new NetNode(newWeights, newPosition, radius);
                }
            }

            //create our output layer
            outputNodes = new NetNode[outputCount];
            for (int i = 0; i < outputCount; i++)
            {
                //assign a position for the node to occupy
                Point newPosition = new Point(
                    canvasSize[0] - radius,
                    canvasSize[1] / (outputCount + 1) * (i + 1)
                );
                //create the new node
                outputNodes[i] = new NetNode(newPosition, radius);
            }
        }

        public void DrawSelf(Graphics myScreen) 
        {
            Double maxValue = 0, minValue = 100, maxWeightValue = 0, minWeightValue = 100;
            myScreen.FillRectangle(
                new SolidBrush(Color.White),
                new Rectangle(baseCoords[0], baseCoords[1], canvasSize[0], canvasSize[1])
            );
            //draw the weights
            //input layer
            foreach (NetNode node in inputNodes)
            {
                Double currValue = node.Value;
                if (maxValue < currValue) { maxValue = currValue; }
                if (minValue > currValue) { minValue = currValue; }
                foreach (Double weight in node.Weights)
                {
                    if (maxWeightValue < weight) { maxWeightValue = weight; }
                    if (minWeightValue > weight) { minWeightValue = weight; }
                }
            }
            foreach (NetNode node in inputNodes)
            {                
                Double[] currWeights = node.Weights;
                for (int i = 0; i < currWeights.Length; i++) 
                {
                    this.drawLine(
                        myScreen, 
                        currWeights[i],
                        new Point[] { node.Position, hiddenNodes[0, i].Position }, 
                        maxWeightValue, 
                        minWeightValue);
                }
            }
            //hidden layers
            for (int c = 0; c < hiddenNodes.GetLength(0); c++)
            {
                maxWeightValue = 0; minWeightValue = 100;
                for (int x = 0; x < hiddenNodes.GetLength(1); x++)
                {
                    foreach (Double weight in hiddenNodes[c, x].Weights)
                    {
                        if (maxWeightValue < weight) { maxWeightValue = weight; }
                        if (minWeightValue > weight) { minWeightValue = weight; }
                    }
                }
                NetNode[] weightTarget;
                if (c >= hiddenNodes.GetLength(0) - 1)
                {
                    //we are in the last layer of the hidden layers
                    weightTarget = outputNodes; //made the output layer our target
                }
                else
                {
                    //create a copy of the next hidden layer
                    weightTarget = new NetNode[hiddenNodes.GetLength(1)];
                    for (int x = 0; x < hiddenNodes.GetLength(1); x++)
                    {
                        weightTarget[x] = hiddenNodes[c + 1, x];
                    }
                }
                for (int x = 0; x < hiddenNodes.GetLength(1); x++)
                {
                    Double[] currWeights = hiddenNodes[c,x].Weights;
                    for (int i = 0; i < weightTarget.Length; i++)
                    {
                        this.drawLine(
                            myScreen, 
                            currWeights[i],
                            new Point[] { hiddenNodes[c, x].Position, weightTarget[i].Position },
                            maxWeightValue,
                            minWeightValue
                        );
                    }
                }
            }
            
            //draw the nodes
            //input nodes
            foreach (NetNode node in inputNodes)
            {
                node.drawSelf(myScreen, maxValue, minValue);
            }

            //hidden layers
            NetNode[] targetLayer;
            Double value = 0;
            NetNode[] lastHiddenLayer;
            for (int c = 0; c < hiddenNodes.GetLength(0); c++)
            {
                maxValue = 0; minValue = 100;
                for (int x = 0; x < hiddenNodes.GetLength(1); x++)
                {
                    if (c == 0)
                    {
                        //we need to pass the input layer
                        hiddenNodes[c, x].judge(inputNodes, x);
                    }
                    else
                    {
                        targetLayer = new NetNode[hiddenNodes.GetLength(1)];
                        for (int i = 0; i < hiddenNodes.GetLength(1); i++)
                        {
                            targetLayer[i] = hiddenNodes[c - 1, i];
                        }
                        hiddenNodes[c, x].judge(targetLayer, x);
                    }
                    value = hiddenNodes[c, x].Value;
                    if (maxValue < value) { maxValue = value; }
                    if (minValue > value) { minValue = value; }
                }
                for (int x = 0; x < hiddenNodes.GetLength(1); x++)
                {
                    hiddenNodes[c, x].drawSelf(myScreen, maxValue, minValue);
                }
            }
            
            //output layer
            lastHiddenLayer = new NetNode[hiddenNodes.GetLength(1)];
            for (int i = 0; i < hiddenNodes.GetLength(1); i++)
            {
                lastHiddenLayer[i] = hiddenNodes[hiddenNodes.GetLength(0) - 1, i];
            }
            maxValue = 0; minValue = 100;
            for (int i = 0; i < outputNodes.Length; i++ )
            {
                outputNodes[i].judge(lastHiddenLayer, i);
                value = outputNodes[i].Value;
                if (maxValue < value) { maxValue = value; }
                if (minValue > value) { minValue = value; }
            }
            foreach (NetNode node in outputNodes)
            {
                node.drawSelf(myScreen, maxValue, minValue);
            }
        }

        public void drawLine(Graphics graphic, Double weightValue, Point[] coords, Double maxValue, Double minValue)
        {
            //colorcode our line's fill in relation to the max and min values
            if (weightValue == 0) { weightValue = 0.0001; } //div0 safety
            Color color = Color.FromArgb(
                Convert.ToInt16(255 * (weightValue / maxValue)),
                Convert.ToInt16(255 * (minValue / weightValue)),
                0
            );
            Pen pen = new Pen(color, 3);
            Point coord1 = new Point(this.radius + coords[0].X, this.radius + coords[0].Y);
            Point coord2 = new Point(this.radius + coords[1].X, this.radius + coords[1].Y);
            graphic.DrawLine(pen, coord1, coord2);
            pen.Dispose();
        }

        public void randomizeInputs()
        {
            Random random = new Random();
            foreach (NetNode node in inputNodes)
            {
                node.Value = random.NextDouble();
            }
        }

        public void randomizeWeights()
        {
            foreach (NetNode node in inputNodes)
            {
                node.randomizeWeights();
            }

            for (int i = 0; i < hiddenNodes.GetLength(0); i++)
            {
                for (int c = 0; c < hiddenNodes.GetLength(0); c++)
                {
                    hiddenNodes[i, c].randomizeWeights();
                }
            }
        }

        public NetNode[] getInputNodes()
        {
            return inputNodes;
        }
    }
}
