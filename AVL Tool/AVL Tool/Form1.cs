using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;

namespace AVL_Tool {
    public partial class frmAVL : Form {
        AVLTree myTree;

        public frmAVL() {
            InitializeComponent();
            this.myTree = new AVLTree();
        }

        private void cmdAdd_Click(object sender, EventArgs e) {
            try {
                int newValue = Convert.ToInt16(txtNum.Text); //get the value from the text box
                this.myTree.addValue(newValue);
                lblDepth.Text = Convert.ToString(this.myTree.getDepth());
                lblList.Text = this.myTree.getTreeString();
                txtNum.Text = "";
            } 
            catch (Exception ex) { //this is the single point of user input so we will be careful
                Console.WriteLine("Please choose am integer number less than 100");
                Console.WriteLine("Error message: " + ex.Message);
                throw;
            }
        }

        private void cmdBalance_Click(object sender, EventArgs e) {
            //balance the tree and update the depth value
            this.myTree.balance(); 
            lblDepth.Text = Convert.ToString(this.myTree.getDepth());
        }

        private void DrawingSurface_Paint(object sender, PaintEventArgs e) {
            Graphics mySurface = DrawingSurface.CreateGraphics();

        }

    }

}
