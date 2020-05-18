/*
 Navicat Premium Data Transfer

 Source Server         : test01
 Source Server Type    : MySQL
 Source Server Version : 50642
 Source Host           : localhost:3306
 Source Schema         : demo01

 Target Server Type    : MySQL
 Target Server Version : 50642
 File Encoding         : 65001

 Date: 23/04/2020 17:50:17
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for userinfos
-- ----------------------------
DROP TABLE IF EXISTS `userinfos`;
CREATE TABLE `userinfos`  (
  `user` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `pwd` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `email` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `home_path` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `limit_size` double NULL DEFAULT NULL,
  PRIMARY KEY (`user`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = latin1 COLLATE = latin1_swedish_ci ROW_FORMAT = Compact;

-- ----------------------------
-- Records of userinfos
-- ----------------------------
INSERT INTO `userinfos` VALUES ('ben', '777', '999@126.com', 'D:\\networkproject\\project1516\\server\\home\\ben', 10240000000);
INSERT INTO `userinfos` VALUES ('kevin', '123123', 'zhukai1412@163.com', 'D:\\networkproject\\project1516\\server\\home\\kevin', 10240000000);
INSERT INTO `userinfos` VALUES ('lily', '888', 'sasdsadadsa@qq.com', 'D:\\networkproject\\project1516\\server\\home\\lily', 10240000000);
INSERT INTO `userinfos` VALUES ('mike', '123123', '123456@qq.com', 'D:\\networkproject\\project1516\\server\\home\\mike', 10240000000);

SET FOREIGN_KEY_CHECKS = 1;
