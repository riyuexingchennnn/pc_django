[TOC]

# 影云后端django项目

![](./docs/piccloud.jpg)

---

## 一、项目简介

### 1. 项目结构(持续更新)

```bash
.
├── apps
│   ├── accounts
│   ├── admin
│   ├── ai
│   ├── images
│   ├── pay
│   ├── search
│   └── utils
├── docs
├── LICENSE
├── manage.py
├── log
├── media
│   └── avatar
├── pc_django
│   ├── asgi.py
│   ├── __init__.py
│   ├── __pycache__
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── README.md
└── requirements.txt
```
- apps: 存放后端应用模块
  - accounts: 用户管理模块
  - admin: 后台管理模块
  - ai: 人工智能模块
  - images: 图片管理模块
  - pay: 支付模块
  - search: 搜索模块
  - utils: 工具模块, 存放一些公共函数
- docs: 存放项目文档图片
- log: 存放日志文件
- media: 存放上传的用户头像
- pc_django: 项目的Django本体代码

### 2. 项目环境

- Python 3.10.12
- mysql 8.0.35
- django 5.1.4

环境具体部署参照[pc_docker仓库](http://vlab.csu.edu.cn/gitlab/piccloud/pc_docker)

### 3. 数据库可视化工具

#### 3.1 phpMyAdmin

基于web和php的数据库管理工具，可以方便地管理mysql数据库。

```
sudo apt update
sudo apt install apache2 mysql-server php libapache2-mod-php php-mysql unzip
sudo apt install phpmyadmin
```

安装phpMyAdmin数据库可视化工具，安装时注意用户名用`root`，密码用`123`。

因为这个要用apache2，如果你有装其他的web服务器比如nginx，会造成80端口冲突，要修改apache2的监听端口。

```
sudo nano /etc/apache2/ports.conf
```

修改`Listen 80`为`Listen 8080`，保存退出。

```
sudo systemctl restart apache2
```

然后登录本地phpMyAdmin：http://localhost:8080/phpmyadmin

![](./docs/phpmyAdmin.png)

#### 3.2 DBeaver

基于Java的数据库管理工具，可以方便地管理mysql数据库。

官网下载安装包：https://dbeaver.io/download/

![](./docs/DBeaver.png)

### 4. 配置宝塔面板(可配可不配)

1. ubuntu2204安装宝塔面板(这个在docker外面)

    ```
    wget -O install.sh https://download.bt.cn/install/install_lts.sh && sudo bash install.sh ed8484bec
    ```

    安装openssh-server，不然无法在宝塔面板中无法使用ssh：

    ```
    sudo apt-get install openssh-server
    ```

2. 登录宝塔面板
   
    蔡明辰的电脑宝塔面下信息：

    ```
    ==================================================================
    Congratulations! Installed successfully!
    =============注意：首次打开面板浏览器将提示不安全=================

    请选择以下其中一种方式解决不安全提醒
    1、下载证书，地址：https://dg2.bt.cn/ssl/baota_root.pfx，双击安装,密码【www.bt.cn】
    2、点击【高级】-【继续访问】或【接受风险并继续】访问
    教程：https://www.bt.cn/bbs/thread-11不然无法再宝塔面板中无法使用ssh7246-1-1.html
    mac用户请下载使用此证书：https://dg2.bt.cn/ssl/mac.crt

    ====================目====面板账户登录信息==========================

    【云服务器】请在安全组放行 16447 端口
    外网面板地址: https://119.39.65.155:16447/36553b08
    内网面板地址: https://100.67.77.5:16447/36553b08
    username: eu60wgit
    password: d3990e16

    浏览器访问以下链接，添加宝塔客服
    https://www.bt.cn/new/wechat_customer
    ==================================================================
    Time consumed: 2 Minute!
    ```

### 5. mySQL配置

遇到一个问题

```
root@e7e23fbad5e7:~/pc_django# mysql -u root -p
Enter password: 
ERROR 2002 (HY000): Can't connect to local MySQL server through socket '/var/run/mysqld/mysqld.sock' (111)
```

> 关于mySQL一个自己给自己挖坑，然后填坑的经历。

1. 大二下学期的数据库课程，我在ubuntu2204上安装了mysql，但是用的是源码安装。
2. 后来因为不想要mysql，所以把源文件删除了，但是不代表卸载了mysql。
3. 后来我又安装了mysql，但是用的是apt安装，安装报错，查看journalctl -u mysql.service，发现一个错误。
4. `Can't open file: 'mysql.ibd' (errno: 0)`，询问GPT得到答案是“这是一个与 InnoDB 存储引擎相关的错误，通常是由于数据库的 mysql.ibd 文件丢失或损坏导致的。”
5. 然后重新初始化数据库系统就好了。

```
sudo rm -rf /var/lib/mysql/*
sudo mysqld --initialize --user=mysql
sudo systemctl start mysql
```

> （每个人都不一样）在这里可以查看临时密码：uc0i>F:;i.WH

使用tcp协议连接mysql：

```
sudo mysql -u root -p --protocol=tcp
```

输入临时密码后，就可以进入mysql命令行了。修改root密码，不修改不让执行别的操作。

```
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '123';
FLUSH PRIVILEGES;
```

密码123

## 二、代码基建

### 1. 代码规范纠查

严格按照PEP8规范编写代码。提交GitLab前，请使用black自动格式化代码。

```
sudo apt install black

black .
```

![](./docs/black.png)

也可以用flake8来检查代码规范。然后手动纠正不规范代码。

```
flake8 .
```
![](./docs/flake8.png)

---

### 2. 日志记录

自己平时有些小调试可以使用print，但是确定下来的时候，还是要用log输出。

```
# views.py
import logging

# 获取日志记录器
logger = logging.getLogger('django')  # settings.py中配置日志记录器叫django

logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")
```

### 3. 规范画图

统一使用[plantuml](https://www.plantuml.com/)画图，然后导出png格式图片。

![](./docs/plantUML.png)

> 推荐和chatGPT一起使用，描述UML图需求，然后让chatGPT生成对应的UML代码，复制到plantuml中画图。

## 三、项目运行

### 1. 修改settings配置文件

找到settings.py文件，修改ALLOWED_HOSTS，添加你的外部域名为小米球内网穿透的域名，例如：

```python
ALLOWED_HOSTS = [    
    'rcsvnfd47bsc.ngrok.xiaomiqiu123.top',  # 你的外部域名
    'http://rcsvnfd47bsc.ngrok.xiaomiqiu123.top',  # 如果是 HTTP 协议也需要添加
    'https://rcsvnfd47bsc.ngrok.xiaomiqiu123.top',
    '127.0.0.1',                           # 本地地址
    'localhost',                           # 本地地址
]
```

### 2. 数据库迁移

使用 `python3 manage.py makemigrations` 和 `python3 manage.py migrate` 来创建和应用数据库迁移文件。

```
python3 manage.py makemigrations
python3 manage.py migrate
```

因为使用的是mySQL，所以不会像sqlite3那样自动生成db文件。

如果出现了，数据库中某个表找不到，字段找不到等问题，可以删除有问题的migrations文件夹，然后重新运行上面的命令。

如果发现没有产生migrations文件夹，可以单个为某个Django应用创建migrations：

> 如果还是没有数据库表，可以采用极端方法，直接删除整个数据库，然后重新迁移。

```
python3 manage.py makemigrations
python3 manage.py migrate
```

或

```
python manage.py makemigrations
python manage.py migrate
```

### 3. 项目整体运行

```
python3 manage.py runserver
```

或

```
python manage.py runserver 0.0.0.0:8000
```

如果出现了`Error: That port is already in use.`，说明端口被占用，查看占用端口的进程并杀死之。

```
sudo lsof -i :8000
```

> 用户登录

```
127.0.0.1:8000/user/login                       # 内网地址
rcsvnfd47bsc.ngrok.xiaomiqiu123.top/user/login  # 小米球外网地址
```

## 四、管理员终端

1. 创建超级管理员账号

    ```
    python3 manage.py createsuperuser
    ```

2. 登录管理员终端界面

    访问后端管理页面：http://localhost:8000/admin/ 在此界面可以方遍管理员直接管理数据库。

    ![](./docs/admin.png)

3. 查看系统占用

    点击右上角的`系统当前性能`。出现当前后端系统 的CPU和内存可视化占用情况。

    ![](./docs/system-monitor.png)
    
## 五、项目接口测试

### 1. Django REST framework

直接访问接口地址。例如登录接口：127.0.0.1:8000/user/login

Django的REST framework提供了一系列的工具，可以方便的直接的输入json的内容调试

![](./docs/api_login.png)

### 2. Apifox

前后端统一使用apifox进行接口测试，后端人员编写好接口保存到apifox项目组中，方便前端人员查看。

- 后端调试更改服务器地址，可以更改开发环境，测试环境，正式环境。

    ![](./docs/apifox_1.png)

- 新建接口进行调试，选择POST请求，输入json内容，调试完毕记得保存接口，给前端人员查看。

    ![](./docs/apifox_2.png)

## 六、OSS对象存储

### 1. 方法一：本地OSS存储（不推荐）

使用MinIO作为OSS存储，安装MinIO客户端，并配置django-storages。

```
docker run -p 9000:9000 -p 9001:9001 \
  --name minio \
  -e "MINIO_ROOT_USER=admin" \
  -e "MINIO_ROOT_PASSWORD=admin123" \
  minio/minio server /data --console-address ":9001"
```

![](./docs/MinIO.png)

需要第二台电脑，配置内网穿透9000端口。但是内网穿透流量有限制，1MB/s。

### 2. 方法二：腾讯云COS存储（推荐，但是要花钱）

> 腾讯云开始给你50G180天的COS。测试流量88MB 花费4分钱，还算便宜？ 

![](./docs/COS.png)

不用担心带宽问题，测试4MB图片也能在一秒钟内快速下载。

如果不使用docker环境，可以直接安装cos-python-sdk-v5。
```
pip install -U cos-python-sdk-v5
```

## 七、后端部署

### 1. 方法一：内网穿透

使用自己的笔记本电脑，配置小米球内网穿透，然后运行项目。

网穿地址：rcsvnfd47bsc.ngrok.xiaomiqiu123.top

- 优点：免费、简单、方便、不用担心性能。
- 缺点：带宽小最大只有1MB/s，网速不稳定，需要24小时开电脑。

### 2. 方法二：云服务

这里我使用`华为云`(~~因为阿里腾讯云的免费云服务器我都用了~~)

公网IP：113.45.3.117

ssh后台运行指令

```
nohup python3 manage.py runserver 0.0.0.0:8000 &
```

- 优点：带宽大，有2MB/s。部署好后不用管他。
- 缺点：可能要花钱。