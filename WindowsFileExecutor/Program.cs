using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO.Pipes;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Threading;

namespace CWDFE
{
    internal class Program
    {
        public static bool quit = false;
        public static string monitorfile;
        public static MemoryStream s = new MemoryStream();
        public static StreamReader sr = new StreamReader(s);
        public static StreamWriter sw = new StreamWriter(s);
        //Craft Server Setup Dynamic File Executor by Enderbyte Programs (c) 2024, no rights reserved.
        static void Monitor()
        {
            string lastdata;
            using (var fs = new FileStream(monitorfile, FileMode.Open, FileAccess.Read, FileShare.ReadWrite))
            using (var ssr = new StreamReader(fs, Encoding.Default))
            {
                while (true)
                {

                    lastdata = ssr.ReadToEnd();
                    if (!string.IsNullOrWhiteSpace(lastdata))
                    {
                        //Console.Write($"SENDING {lastdata}");

                        sw.Write(lastdata);
                        sw.Flush();
                        if (quit)
                        {
                            break;
                        }
                    }
                    Thread.Sleep(100);
                }
            }
        }
        static void Main(string[] args)
        {
            //s.ReadTimeout = 100;
            //s.WriteTimeout = 100;
            monitorfile = args[0];
            if (File.Exists(monitorfile))
            {
                File.Delete(monitorfile);
            }
            File.WriteAllText(monitorfile,"");
            string filename = args[1];
            List<string> ar = new List<string>(args);
            ar.RemoveAt(0);//Remove filename
            ar.RemoveAt(0);
            string arguments = string.Join(" ", ar);

            Process p = new Process
            {
                StartInfo =
                {
                    FileName = filename,
                    Arguments = arguments,
                    RedirectStandardInput = true,
                    UseShellExecute = false
              
                }
            };
            p.Start();
            var t = new Thread(new ThreadStart(Monitor));
            t.Start();
            s.Seek(0, SeekOrigin.Begin);
            int osf = 0;
            while (true)
            {
                if (p.HasExited)
                {
                    break;
                }
                s.Seek(osf, SeekOrigin.Begin);
                string d = sr.ReadToEnd();
                osf += d.Length;
                //Console.WriteLine($"LEN {s.Length}");
                if (!string.IsNullOrWhiteSpace(d))
                {
                    //Console.WriteLine($"RECV {d}");
                    foreach (string line in d.Split('\n'))
                    {
                        string rl = line.Trim();
                        if (string.IsNullOrWhiteSpace(rl))
                        {
                            continue;
                        }
                        //Console.WriteLine($"SENDING {rl}");
                        p.StandardInput.WriteLine(rl);
                    }
                    
                }
                
                Thread.Sleep(1000);
            }
            quit = true;
            Environment.Exit(p.ExitCode);
        }
    }
}
