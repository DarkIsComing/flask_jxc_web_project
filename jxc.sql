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
