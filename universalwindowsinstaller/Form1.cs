using System;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Net;
using System.Threading;
using System.Windows.Forms;

namespace CRSSAutoInstall
{
    public partial class Form1 : Form
    {
        private bool downloaddone = false;
        private bool proceed = false;
        public Form1()
        {
            InitializeComponent();
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
        }

        private void button2_Click(object sender, EventArgs e)
        {
            proceed = false;
            startDownload();
        }

        private void button3_Click(object sender, EventArgs e)
        {
            Close();
        }
        private void startDownload()
        {
            downloaddone = false;
            label3.Text = "Resolving version (the installer may freeze for a second)";
            progressBar1.Value = 0;
            label3.Invalidate();
            label3.Refresh();
            this.Refresh();
            WebClient client = new WebClient();
            String downloadedString = client.DownloadString("https://github.com/Enderbyte-Programs/CraftServerSetup/raw/main/update.txt").Split('|')[0];
            Thread thread = new Thread(() => {
                client = new WebClient();
                client.DownloadProgressChanged += new DownloadProgressChangedEventHandler(client_DownloadProgressChanged);
                client.DownloadFileCompleted += new AsyncCompletedEventHandler(client_DownloadFileCompleted);
                client.DownloadFileAsync(new Uri(downloadedString),Environment.ExpandEnvironmentVariables("%USERPROFILE%\\Downloads\\CraftServerSetup-setup.exe"));
            });
            thread.Start();
        }
        void client_DownloadProgressChanged(object sender, DownloadProgressChangedEventArgs e)
        {
            this.BeginInvoke((MethodInvoker)delegate {
                double bytesIn = double.Parse(e.BytesReceived.ToString());
                double totalBytes = double.Parse(e.TotalBytesToReceive.ToString());
                double percentage = bytesIn / totalBytes * 100;
                label3.Text = "Downloaded " + e.BytesReceived + " of " + e.TotalBytesToReceive;
                progressBar1.Value = int.Parse(Math.Truncate(percentage).ToString());
            });
        }
        void client_DownloadFileCompleted(object sender, AsyncCompletedEventArgs e)
        {
            downloaddone = true;
            this.BeginInvoke((MethodInvoker)delegate {
                label3.Text = "Download Completed";
                if (proceed)
                {
                    label3.Text = "Running main installer";
                    Refresh();
                    Process p = new Process();
                    p.StartInfo.FileName = Environment.ExpandEnvironmentVariables("%USERPROFILE%\\Downloads\\CraftServerSetup-setup.exe");
                    p.Start();
                    Environment.Exit(0);
                }
            });
            
        }

        private void button1_Click(object sender, EventArgs e)
        {
            proceed = true;
            startDownload();
           
            
            
        }
    }
}
