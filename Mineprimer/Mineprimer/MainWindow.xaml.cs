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
using System.ComponentModel;

namespace Mineprimer
{

    public class Column
    {
        public List<Cell> Cells { get; set; }
        public Column()
        {
            Cells = new List<Cell>();
        }
    }
    public class Cell : INotifyPropertyChanged
    {
        // http://blog.livedoor.jp/morituri/archives/54652766.html
        public event PropertyChangedEventHandler PropertyChanged;

        public int ColumnID { get; set; }
        public int RowID { get; set; }
        public string ID { get; set; }
        public Boolean HasBomb { get; set; }
        public Boolean Opened { get; set; }
        public string View { get; set; }
        public Cell(int column_id, int row_id, Boolean has_bomb)
        {
            ColumnID = column_id;
            RowID = row_id;
            HasBomb = has_bomb;
            ID = ColumnID + "/" + RowID;
            Opened = false;

            View = "";
        }

        public void Open(int around_bombs)
        {
            Opened = true;
            if (HasBomb)
            {
                View = "★";

                var window = new BombMessageWindow();
                window.Show();
            }
            else
            {
                View = around_bombs.ToString();
            }
            OnPropertyChanged("View");
        }

        protected void OnPropertyChanged(string name)
        {
            PropertyChangedEventHandler handler = PropertyChanged;
            if (handler != null)
            {
                handler(this, new PropertyChangedEventArgs(name));
            }
        }
    }


    public partial class MainWindow : Window
    {
        public List<Column> columns;
        public int RowNum;
        public int ColumnNum;
        public int BombNum;

        public MainWindow()
        {
            InitializeComponent();

            RowNum = 20;
            ColumnNum = 15;
            BombNum = 30;

            var size = RowNum * ColumnNum;
            int[] nums = new int[size];
            for (var i = 0; i < size; i++)
            {
                nums[i] = i;
            }
            int[] shuffled = nums.OrderBy(i => Guid.NewGuid()).ToArray();
            int[] bombIds = new int[BombNum];
            for (var j=0; j < BombNum; j++)
            {
                bombIds[j] = shuffled[j];
            }

            columns = new List<Column>();
            for (int column_id = 0; column_id < ColumnNum; column_id++)
            {
                var column = new Column();

                for (int row_id = 0; row_id < RowNum; row_id++)
                {
                    Boolean has_bomb = bombIds.Contains(column_id * RowNum + row_id);
                    column.Cells.Add(new Cell(column_id, row_id, has_bomb));
                }
                columns.Add(column);
            }
            datalistitems.DataContext = columns;
        }

        public Cell GetCell(int column_id, int row_id)
        {
            return columns[column_id].Cells[row_id];
        }
        public void SetCell(int column_id, int row_id, string view)
        {
            var cell = new Cell(column_id, row_id, true);

            cell.View = view;
            columns[column_id].Cells[row_id] = cell;
        }
        public int GetAroundBombs(int column_id, int row_id)
        {
            int num = 0;
            for (int c = column_id - 1; c <= column_id + 1; c++)
            {
                if (c < 0 || c >= ColumnNum)
                {
                    continue;
                }
                for (int r = row_id - 1; r <= row_id + 1; r++)
                {
                    if (c == column_id && r == row_id)
                    {
                        continue;
                    }
                    if (r < 0 || r >= RowNum)
                    {
                        continue;
                    }
                    if (GetCell(c, r).HasBomb)
                    {
                        num++;
                    }
                }
            }
            return num;
        }
        private void Button_Click(object sender, RoutedEventArgs e)
        {

            var button = (Button)sender;
            var tag = button.Tag;
            var columnid_rowid = tag.ToString().Split('/').Select(numstr => int.Parse(numstr)).ToArray();

            var column_id = columnid_rowid[0];
            var row_id = columnid_rowid[1];
            var cell = GetCell(column_id, row_id);
            var around_bombs = GetAroundBombs(column_id, row_id);
            cell.Open(around_bombs);
        }
    }
}
