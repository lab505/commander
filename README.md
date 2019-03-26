# commander

# 依赖环境(windows)
## QGIS
http://qgis.org/downloads/QGIS-OSGeo4W-3.6.0-1-Setup-x86_64.exe (建议安装到默认路径)  
```qt_desinger : C:\Program Files\QGIS 3.6\apps\Qt5\bin\designer.exe```  
## conda with py37
https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Windows-x86_64.exe  

## mysql.connector
conda install -c anaconda mysql-connector-python

## mysql后端服务
linux/mac: conda install mysql
windows: https://www.mysql.com/cn/downloads/

# 程序入口
主窗口&后端服务
```python main_window.py```  
输入数据demo:
```python data_client_demo.py```  

# references
- https://qgis.org/pyqgis/master/
- http://pyqt.sourceforge.net/Docs/PyQt5/class_reference.html
- http://www.resdc.cn/data.aspx?DATAID=200 地图数据下载(省)
- http://mapclub.cn/archives/1814/comment-page-23#comment-3130 地图数据下载(各种)
