using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;

namespace Mineprimer
{
    public class ARCLS
    {
        public List<CLS> clss { get; set; }
        public ARCLS()
        {
            clss = new List<CLS>();
        }
    }
    public class CLS
    {
        public string Name { get; set; }
    }
    /// <summary>
    /// MainWindow.xaml の相互作用ロジック
    /// </summary>
    /// 

    public partial class MainWindow : Window
    {
        public List<ARCLS> datalist;

        public MainWindow()
        {
            InitializeComponent();
            datalist = new List<ARCLS>();
            for (int i = 0; i < 3; i++)
            {
                var arcls = new ARCLS();

                for (int j = 0; j < 3; j++)
                {
                    arcls.clss.Add( new CLS { Name = i.ToString() + "/"+ j.ToString(), });
                }
                datalist.Add(arcls);
            }
            datalistitems.DataContext = datalist;
        }
    }


}
