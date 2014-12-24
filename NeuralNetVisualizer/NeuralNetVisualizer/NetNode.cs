using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Drawing;
using System.Drawing.Drawing2D;
using System.Collections;

namespace NeuralNetVisualizer
{
    class NetNode
    {
        Double[] weights;
        Double node_value;
        Color color;
        Point position;
        int radius;
        bool selected;

        public NetNode()
        {
            weights = new Double[0];
            node_value = 0;
            color = Color.FromArgb(255, 255, 255, 255);
            position = new Point(0, 0);
            radius = 25;
            selected = false;
        }

        public NetNode(Point newPosition, int newRadius)
        {
            weights = new Double[0];
            node_value = 0;
            color = Color.FromArgb(255, 255, 255, 255);
            position = newPosition;
            radius = newRadius;
            selected = false;
        }

        public NetNode(Double[] newWeights, Point newPosition, int newRadius)
        {
            weights = newWeights;
            node_value = 0;
            color = Color.FromArgb(255, 255, 255, 255);
            position = newPosition;
            radius = newRadius;
            selected = false;
        }

        public NetNode(Double[] newWeights, Double newValue, Point newPosition, int newRadius)
        {
            weights = newWeights;
            node_value = newValue;
            color = Color.FromArgb(255, 255, 255, 255);
            position = newPosition;
            radius = newRadius;
            selected = false;
        }

        public double judge(NetNode[] inputNodes, int myPositon)
        {
            node_value = 0;
            for (int i = 0; i < inputNodes.Length; i++)
            {
                //multiply the input values by the associated weights and
                //add them all together
                node_value += inputNodes[i].Value * inputNodes[i].Weights[myPositon];
            }
            return node_value;
        }

        public void drawSelf(Graphics graphic, Double maxValue, Double minValue)
        {
            //colorcode our node's fill in relation to the max and min values
            if (this.node_value == 0) { this.node_value = 0.0001; } //div0 safety
            this.Color = Color.FromArgb(
                (int)(255 * (this.node_value / maxValue)),
                (int)(255 * (minValue / this.node_value)), 
                0
            );
            SolidBrush brush = new SolidBrush(this.Color);
            graphic.FillEllipse(brush, new Rectangle(this.Position, this.getSize()));
            brush.Dispose();
            Pen pen = new Pen(Color.Black, 5);
            if (Selected)
            {
                pen.Color = Color.Blue;
            }
            graphic.DrawEllipse(pen, new Rectangle(this.Position, this.getSize()));
            pen.Dispose();
        }

        public void randomizeWeights()
        {
            Random random = new Random();
            for (int i = 0; i < weights.Length; i++)
            {
                weights[i] = random.NextDouble();
            }
        }

        // all of our get/sets
        public Double[] Weights
        {
            get {return weights;}
            set {weights=value;}
        }
        public Double Value
        {
            get { return node_value; }
            set { node_value = value; }
        }
        public Color Color
        {
            get {return color;}
            set {color=value;}
        }
        public Point Position
        {
            get {return position;}
            set {position=value;}
        }
        public int Radius
        {
            get {return radius;}
            set {radius=value;}
        }
        public bool Selected
        {
            get {return selected;}
            set {selected=value;}
        }
        public Size getSize()
        {
            return new Size(radius * 2, radius * 2);
        }
    }
}
