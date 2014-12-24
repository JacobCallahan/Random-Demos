using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace NeuralNetVisualizer
{
    public partial class frmVisualize : Form
    {
        NeuralNet myNeuralNet = null;
        NetNode[] inputNodes = null;

        public frmVisualize()
        {
            InitializeComponent();
        }

        private void button3_Click(object sender, EventArgs e)
        {
            int inputNodeCount, hiddenLayerCount, outputNodeCount;
            SimpleInput inputDialog = new SimpleInput();
            inputNodeCount = inputDialog.Prompt("Please enter the number of input nodes (1-4).", "Input Nodes", 4);
            hiddenLayerCount = inputDialog.Prompt("Please enter the number of hidden layers (1-3).", "Hidden Layers", 3);
            outputNodeCount = inputDialog.Prompt("Please enter the number of output nodes (1-4).", "Output Nodes", 4);

            Double[] inputValues = new Double[inputNodeCount];
            Random random = new Random();
            for (int i = 0; i < inputNodeCount; i++)
            {
                inputValues[i] = random.NextDouble();
            }
            myNeuralNet = new NeuralNet(inputValues, hiddenLayerCount, outputNodeCount, new int[] { 650, 480 });
            updateNN();
            lstNode.Items.Clear();
            for (int i = 1; i <= inputNodes.Length; i++)
            {
                lstNode.Items.Add("Node " + i.ToString());
            }
            Application.DoEvents();
        }

        private void button2_Click(object sender, EventArgs e)
        {
            if (myNeuralNet != null)
            {
                myNeuralNet.randomizeInputs();
                updateNN();
                lstNode.SelectedItem = 0;
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            if (myNeuralNet != null)
            {
                myNeuralNet.randomizeWeights();
                updateNN();
                lstNode.SelectedItem = 0;
            }
        }

        private void newToolStripMenuItem_Click(object sender, EventArgs e)
        {
            int inputNodeCount, hiddenLayerCount, outputNodeCount;
            SimpleInput inputDialog = new SimpleInput();
            inputNodeCount = inputDialog.Prompt("Please enter the number of input nodes (1-4).", "Input Nodes", 4);
            hiddenLayerCount = inputDialog.Prompt("Please enter the number of hidden layers (1-3).", "Hidden Layers", 3);
            outputNodeCount = inputDialog.Prompt("Please enter the number of output nodes (1-4).", "Output Nodes", 4);

            Double[] inputValues = new Double[inputNodeCount];
            Random random = new Random();
            for (int i = 0; i < inputNodeCount; i++)
            {
                inputValues[i] = random.NextDouble();
            }
            myNeuralNet = new NeuralNet(inputValues, hiddenLayerCount, outputNodeCount, new int[] { 650, 480 });
            updateNN();
            lstNode.Items.Clear();
            for (int i = 1; i <= inputNodes.Length; i++ )
            {
                lstNode.Items.Add("Node " + i.ToString());
            }
            Application.DoEvents();
        }

        private void exitToolStripMenuItem_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void updateNN()
        {
            Graphics myScreen = CreateGraphics();
            myNeuralNet.DrawSelf(myScreen);
            myScreen.Dispose();
            this.inputNodes = myNeuralNet.getInputNodes();
        }

        private void trackBar1_Scroll(object sender, EventArgs e)
        {
            if (this.inputNodes != null && lstNode.SelectedIndex > -1)
            {
                inputNodes[lstNode.SelectedIndex].Value = ((double)trackBar1.Value) / 100;
                textBox1.Text = inputNodes[lstNode.SelectedIndex].Value.ToString();
                updateNN();
            }
        }

        private void lstNode_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (lstNode.SelectedIndex > -1)
            {
                textBox1.Text = inputNodes[lstNode.SelectedIndex].Value.ToString();
                trackBar1.Value = (int)(inputNodes[lstNode.SelectedIndex].Value * 100);
                for (int i = 0; i < inputNodes.Length; i++)
                {
                    if (i == lstNode.SelectedIndex)
                    {
                        inputNodes[i].Selected = true;
                    }
                    else
                    {
                        inputNodes[i].Selected = false;
                    }
                }
            }
            updateNN();
        }
    }
}

public class SimpleInput
{
    public int Prompt(string dialogue, string title, int limit)
    {
        Form prompt = new Form();
        prompt.Width = 400;
        prompt.Height = 150;
        prompt.FormBorderStyle = FormBorderStyle.FixedDialog;
        prompt.Text = title;
        prompt.StartPosition = FormStartPosition.CenterScreen;
        Label lblDialogue = new Label() { Left = 50, Top=20, Width=300, Text=dialogue };
        TextBox inputBox = new TextBox() { Left = 50, Top=50, Width=300, Text="1" };
        Button submit = new Button() { Text = "Submit", Left=250, Width=100, Top=70 };
        submit.Click += (sender, e) => {
            if (Convert.ToInt16(inputBox.Text) <= limit && Convert.ToInt16(inputBox.Text) > 0)
            {
                prompt.Close();
            }
            else
            {
                MessageBox.Show("Please enter a value greater than 0, but not greater than " + limit.ToString());
            }
        };
        prompt.Controls.Add(inputBox);
        prompt.Controls.Add(submit);
        prompt.Controls.Add(lblDialogue);
        prompt.AcceptButton = submit;
        prompt.ShowDialog();
        return Convert.ToInt16(inputBox.Text);
    }
}