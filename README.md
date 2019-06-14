###运行代码的方式:
```
1. 首先创建好mysql数据库,
    如果连接的是宿主机上的mysql,那么要重新设置Config.py模块下的SQLALCHEMY_DATABASE_URI   格式为mysql+pymysql://<用户名>:<密码>@<ip地址>:<端口号>/<数据库名>

    如果连接的是容器内的mysql,需要 --link mysql容器。而且修改Config.py下的SQLALCHEMY_DATABASE_URI 的ip地址为mysql容器名.
2. 进入Dockerfile所在的目录(也就是项目根目录)执行以下命令:
docker build -t flask .                                             ##根据dockerfile创建一个叫flask的镜像。
docker run --name web -p 5000:5000 --link mysql:mysql -d flask      ##创建运行容器，命名为web,并与mysql容器link. 
如果不需要link,   执行 docker run --name web -p 5000:5000 -d flask。
> -p 5000:5000 端口映射 ：前是本地端口，后是容器端口。
> -d 后台运行
> --name 给容器命名
> --link mysql:mysql    :前面的是容器的名字，:后面的是容器在link下的别名。
```

<hr>

###依赖
```
[dev-packages]

[packages]
flask = "*"                   ##flask 核心包
flask-sqlalchemy = "*"        ##数据库orm
pymysql = "*"                 ##PyMySQL 是在 Python3.x 版本中用于连接 MySQL 服务器的一个库
flask-wtf = "*"               ##管理表单数据。    官方文档:https://flask-wtf.readthedocs.io/en/stable/
flask-bootstrap = "*"         ##html模板美化。    官方文档:https://pythonhosted.org/Flask-Bootstrap/basic-usage.html
pandas = "*"                  ##pandas是一个开源的，BSD许可的库，为Python语言提供高性能，易于使用的数据结构和数据分析工具。

[requires]
python_version = "3.6"
```
<hr>

###数据库
```
/*
 Navicat Premium Data Transfer

 Source Server         : mm
 Source Server Type    : MySQL
 Source Server Version : 80015
 Source Host           : localhost:3306
 Source Schema         : jxc

 Target Server Type    : MySQL
 Target Server Version : 80015
 File Encoding         : 65001

 Date: 13/06/2019 11:35:21
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for buy_order
-- ----------------------------
DROP TABLE IF EXISTS `buy_order`;
CREATE TABLE `buy_order` (
  `ids` int(11) NOT NULL AUTO_INCREMENT,
  `number` int(11) NOT NULL,
  `price` float NOT NULL,
  `date` datetime DEFAULT NULL,
  `name` varchar(64) DEFAULT NULL,
  `ID` int(11) DEFAULT NULL,
  PRIMARY KEY (`ids`),
  KEY `ID` (`ID`),
  CONSTRAINT `buy_order_ibfk_1` FOREIGN KEY (`ID`) REFERENCES `materials` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for inventory_flow
-- ----------------------------
DROP TABLE IF EXISTS `inventory_flow`;
CREATE TABLE `inventory_flow` (
  `ids` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) DEFAULT NULL,
  `ID` int(11) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `types` varchar(32) DEFAULT NULL,
  `occurred_amount` int(11) NOT NULL,
  `stock` int(11) NOT NULL,
  PRIMARY KEY (`ids`),
  KEY `ID` (`ID`),
  CONSTRAINT `inventory_flow_ibfk_1` FOREIGN KEY (`ID`) REFERENCES `materials` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=14 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for materials
-- ----------------------------
DROP TABLE IF EXISTS `materials`;
CREATE TABLE `materials` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(64) NOT NULL,
  `package` varchar(64) DEFAULT NULL,
  `types` varchar(64) DEFAULT NULL,
  `stock` int(11) DEFAULT NULL,
  `remark` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for sale_order
-- ----------------------------
DROP TABLE IF EXISTS `sale_order`;
CREATE TABLE `sale_order` (
  `ids` int(11) NOT NULL AUTO_INCREMENT,
  `number` int(11) NOT NULL,
  `price` float NOT NULL,
  `date` datetime DEFAULT NULL,
  `name` varchar(64) DEFAULT NULL,
  `ID` int(11) DEFAULT NULL,
  PRIMARY KEY (`ids`),
  KEY `ID` (`ID`),
  CONSTRAINT `sale_order_ibfk_1` FOREIGN KEY (`ID`) REFERENCES `materials` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for stock_in
-- ----------------------------
DROP TABLE IF EXISTS `stock_in`;
CREATE TABLE `stock_in` (
  `ids` int(11) NOT NULL AUTO_INCREMENT,
  `number` int(11) NOT NULL,
  `price` float NOT NULL,
  `date` datetime DEFAULT NULL,
  `name` varchar(64) DEFAULT NULL,
  `ID` int(11) DEFAULT NULL,
  PRIMARY KEY (`ids`),
  KEY `ID` (`ID`),
  CONSTRAINT `stock_in_ibfk_1` FOREIGN KEY (`ID`) REFERENCES `materials` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for stock_out
-- ----------------------------
DROP TABLE IF EXISTS `stock_out`;
CREATE TABLE `stock_out` (
  `ids` int(11) NOT NULL AUTO_INCREMENT,
  `number` int(11) NOT NULL,
  `price` float NOT NULL,
  `date` datetime DEFAULT NULL,
  `name` varchar(64) DEFAULT NULL,
  `ID` int(11) DEFAULT NULL,
  PRIMARY KEY (`ids`),
  KEY `ID` (`ID`),
  CONSTRAINT `stock_out_ibfk_1` FOREIGN KEY (`ID`) REFERENCES `materials` (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- ----------------------------
-- Table structure for type
-- ----------------------------
DROP TABLE IF EXISTS `type`;
CREATE TABLE `type` (
  `ID` int(11) NOT NULL AUTO_INCREMENT,
  `type_name` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`ID`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

SET FOREIGN_KEY_CHECKS = 1;

```
<hr>

###项目结构以及说明
```
    |——app
    |   |——api_1_0
    |   |——csv
    |   |——mnt
    |   |——static
    |   |——templates
    |   |——__init__.py
    |   |——forms.py
    |   |——models.py
    |——Config.py
    |——Dockerfile
    |——manage.py
    |——Pipfile
    |——Pipfile.lock
    |——README.md
    |——requirements.txt
    |——output.log

```