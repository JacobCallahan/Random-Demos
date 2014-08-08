namespace AVL_Tool
{
    partial class frmAVL
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.cmdAdd = new System.Windows.Forms.Button();
            this.cmdBalance = new System.Windows.Forms.Button();
            this.txtNum = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.lblDepth = new System.Windows.Forms.Label();
            this.lblList = new System.Windows.Forms.Label();
            this.label3 = new System.Windows.Forms.Label();
            this.DrawingSurface = new System.Windows.Forms.Panel();
            this.SuspendLayout();
            // 
            // cmdAdd
            // 
            this.cmdAdd.Location = new System.Drawing.Point(13, -1);
            this.cmdAdd.Name = "cmdAdd";
            this.cmdAdd.Size = new System.Drawing.Size(80, 32);
            this.cmdAdd.TabIndex = 0;
            this.cmdAdd.Text = "Add Number";
            this.cmdAdd.UseVisualStyleBackColor = true;
            this.cmdAdd.Click += new System.EventHandler(this.cmdAdd_Click);
            // 
            // cmdBalance
            // 
            this.cmdBalance.Location = new System.Drawing.Point(12, 37);
            this.cmdBalance.Name = "cmdBalance";
            this.cmdBalance.Size = new System.Drawing.Size(80, 32);
            this.cmdBalance.TabIndex = 1;
            this.cmdBalance.Text = "Balance Tree";
            this.cmdBalance.UseVisualStyleBackColor = true;
            this.cmdBalance.Click += new System.EventHandler(this.cmdBalance_Click);
            // 
            // txtNum
            // 
            this.txtNum.Location = new System.Drawing.Point(99, 6);
            this.txtNum.Name = "txtNum";
            this.txtNum.Size = new System.Drawing.Size(69, 20);
            this.txtNum.TabIndex = 2;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(235, 9);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(39, 13);
            this.label1.TabIndex = 3;
            this.label1.Text = "Depth:";
            // 
            // lblDepth
            // 
            this.lblDepth.AutoSize = true;
            this.lblDepth.Location = new System.Drawing.Point(269, 9);
            this.lblDepth.Name = "lblDepth";
            this.lblDepth.Size = new System.Drawing.Size(13, 13);
            this.lblDepth.TabIndex = 4;
            this.lblDepth.Text = "0";
            // 
            // lblList
            // 
            this.lblList.AutoSize = true;
            this.lblList.Location = new System.Drawing.Point(347, 9);
            this.lblList.Name = "lblList";
            this.lblList.Size = new System.Drawing.Size(36, 13);
            this.lblList.TabIndex = 6;
            this.lblList.Text = "Empty";
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(308, 9);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(42, 13);
            this.label3.TabIndex = 5;
            this.label3.Text = "Values:";
            // 
            // DrawingSurface
            // 
            this.DrawingSurface.Location = new System.Drawing.Point(101, 35);
            this.DrawingSurface.Name = "DrawingSurface";
            this.DrawingSurface.Size = new System.Drawing.Size(803, 440);
            this.DrawingSurface.TabIndex = 7;
            this.DrawingSurface.Paint += new System.Windows.Forms.PaintEventHandler(this.DrawingSurface_Paint);
            // 
            // frmAVL
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(916, 483);
            this.Controls.Add(this.DrawingSurface);
            this.Controls.Add(this.lblList);
            this.Controls.Add(this.label3);
            this.Controls.Add(this.lblDepth);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.txtNum);
            this.Controls.Add(this.cmdBalance);
            this.Controls.Add(this.cmdAdd);
            this.Name = "frmAVL";
            this.Text = "AVL Tree Demo";
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Button cmdAdd;
        private System.Windows.Forms.Button cmdBalance;
        private System.Windows.Forms.TextBox txtNum;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.Label lblDepth;
        private System.Windows.Forms.Label lblList;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Panel DrawingSurface;
    }
}

