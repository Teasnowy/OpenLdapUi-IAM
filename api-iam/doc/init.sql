-- 需要库表字符集为utf8mb4
-- 请确定不会误删您已经存在的表

-- 用户表
DROP TABLE IF EXISTS `sw_user`;
CREATE TABLE `sw_user` (
  `user_id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `account` varchar(30) NOT NULL COMMENT '用户帐号',
  `displayname` varchar(100) NOT NULL COMMENT '用户显示名',
  `rank` varchar(200) NOT NULL DEFAULT '初学乍练' COMMENT '用户称号, 定义在表sw_rank',
  `email` varchar(100) DEFAULT '' COMMENT '邮箱地址',
  `tel` varchar(20) COMMENT '手机号码',
  `befrom` varchar(20) NOT NULL DEFAULT 'local' COMMENT '从何处创建, local:本地, ldap:ldap账号系统',
  `ldap_dn` varchar(200) COMMENT 'ldap用户对应的条目dn',
  `ldap_ou_name` varchar(20) COMMENT '如果是ldap用户, 对应哪个ou搜索表达式的ou_name, 在sw_ldap_ous表中',
  `status` varchar(20) NOT NULL COMMENT '账号状态, off:禁用 on:正常',
  `password` varchar(200) COMMENT '用户密码',
  `photo_id` varchar(100) COMMENT '图片id, 在sw_photo表',
  `date_create` datetime NOT NULL COMMENT '创建日期',
  `date_update` datetime NOT NULL COMMENT '更新日期',
  `date_latest_login` datetime NOT NULL COMMENT '最后登录日期',
  PRIMARY KEY (`user_id`),
  UNIQUE index account(`account`),
  UNIQUE index `account_befrom` (`account`, `befrom`, `ldap_ou_name`)
);

insert into `sw_user` (user_id, account, displayname, rank, email, tel, befrom, status, password, date_create, date_update, date_latest_login)
values
    (null, 'admin', '超级管理员', '举世无双', 'xxx@xxx.com', '123456789000', 'local', 'on', '123456', now(), now(), now());


-- 用户组表
DROP TABLE IF EXISTS `sw_group`;
create table `sw_group` (
  `group_id` varchar(100) NOT NULL COMMENT '组id',
  `group_desc` varchar(1000) COMMENT '此组的描述',
  `date_create` datetime NOT NULL COMMENT '创建日期',
  `date_update` datetime NOT NULL COMMENT '更新日期',
  PRIMARY KEY (`group_id`)
);
insert into sw_group (group_id, group_desc, date_create, date_update) values
    ('管理员组', '管理员组', now(), now());


-- 角色表
DROP TABLE IF EXISTS `sw_role`;
create table `sw_role` (
  `role_id` varchar(30) NOT NULL COMMENT '角色id',
--  `role_displayname` varchar(30) NOT NULL COMMENT '角色别名',
  `role_desc` varchar(1000) COMMENT '此角色的描述',
  `date_create` datetime NOT NULL COMMENT '创建日期',
  `date_update` datetime NOT NULL COMMENT '更新日期',
  PRIMARY KEY (`role_id`)
);

insert into sw_role (role_id, role_desc, date_create, date_update)
values
    ('管理员', '管理员权限, 拥有所有权限', now(), now()),
    ('访客', '访客权限, 仅查询部分非敏感数据页面', now(), now());

-- 组和角色中间表
DROP TABLE IF EXISTS `sw_rolegroup`;
create table `sw_rolegroup` (
  `group_id` varchar(30) NOT NULL COMMENT '组名',
  `role_id` varchar(30) NOT NULL COMMENT '角色id',
  unique index group_roleid(group_id, role_id)
);

insert into sw_rolegroup (group_id, role_id)
values
    ('管理员组', '管理员');


-- 用户和组中间表
DROP TABLE IF EXISTS `sw_usergroup`;
create table `sw_usergroup` (
  `account` varchar(30) NOT NULL COMMENT '用户账号',
  `group_id` varchar(30) NOT NULL COMMENT '组名',
  unique index account_groupid(account, group_id)
);

insert into sw_usergroup (account, group_id)
values
    ('admin', '管理员组');

-- 用户和角色中间表
DROP TABLE IF EXISTS `sw_roleuser`;
create table `sw_roleuser` (
  `account` varchar(30) NOT NULL COMMENT '用户账号',
  `role_id` varchar(30) NOT NULL COMMENT '角色id',
  unique index account_roleid(account, role_id)
);

insert into sw_roleuser (account, role_id)
values
    ('admin', '管理员');

-- 头像表, 存储图片的base64编码
DROP TABLE IF EXISTS `sw_photo`;
create table `sw_photo` (
  `photo_id` varchar(100) NOT NULL COMMENT '图片id, 为base64编码的md5值',
  `photo_base64` MEDIUMTEXT NOT NULL COMMENT 'base64编码格式的图片',
  PRIMARY KEY (`photo_id`)
);

-- 称号表
DROP TABLE IF EXISTS `sw_rank`;
create table `sw_rank` (
  `rank` varchar(100) NOT NULL COMMENT '称号名',
  PRIMARY KEY (`rank`)
);
insert into sw_rank
  (rank)
values
    ('不堪一击'),
    ('初学乍练'),
    ('初窥门径'),
    ('略有小成'),
    ('驾轻就熟'),
    ('融会贯通'),
    ('炉火纯青'),
    ('出类拔萃'),
    ('神乎其技'),
    ('出神入化'),
    ('傲视群雄'),
    ('登峰造极'),
    ('无与伦比'),
    ('所向披靡'),
    ('一代宗师'),
    ('神功盖世'),
    ('举世无双'),
    ('惊世骇俗'),
    ('撼天动地'),
    ('震古铄今'),
    ('超凡入圣'),
    ('威镇寰宇'),
    ('空前绝后');


-- 前端页面列表
DROP TABLE IF EXISTS `sw_web`;
create table `sw_web` (
  `web_id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `web_route` varchar(190) NOT NULL COMMENT '标签所属的前端route路径',
  `web_name` varchar(30) NOT NULL COMMENT '标签所属的前端route路径的显示名',
  `web_desc` varchar(300) NOT NULL COMMENT '详细描述',
  `date_create` datetime NOT NULL COMMENT '创建日期',
  `date_update` datetime NOT NULL COMMENT '更新日期',
  unique index web_route(web_route),
  PRIMARY KEY (`web_id`)
);
INSERT INTO `sw_web` VALUES
    (null,'/home/myInfo','我的信息','右上角点击我的信息进入的页面','2024-12-31 17:18:22','2024-12-31 17:18:22'),
    (null,'/home/setting/rbac_manage','系统设置-角色管理','','2024-12-31 17:22:39','2024-12-31 17:22:39'),
    (null,'/home/setting/user_manage','系统设置-用户管理','','2024-12-31 17:22:51','2024-12-31 17:22:51'),
    (null,'/home/setting/ldap_group','系统设置-LDAP组管理','','2024-12-31 17:23:03','2024-12-31 17:23:03'),
    (null,'/home/setting/group_manage','系统设置-用户组管理','','2024-12-31 17:25:07','2024-12-31 17:25:07'),
    (null,'/home/setting/menu_manage','系统设置-菜单块管理','','2024-12-31 17:34:32','2024-12-31 17:34:32'),
    (null,'/home/ldapServers','运维-LDAP远程管理','','2025-01-07 16:29:35','2025-01-07 16:29:35');


-- 前端页面与角色关联表
DROP TABLE IF EXISTS `sw_roleweb`;
create table `sw_roleweb` (
  `role_id` varchar(30) NOT NULL COMMENT '角色id',
  `web_route` varchar(190) NOT NULL COMMENT '标签所属的前端route路径',
  `date_create` datetime NOT NULL COMMENT '创建日期',
  unique index role_route(role_id,web_route),
  index role_id(role_id),
  index web_route(web_route)
);
INSERT INTO `sw_roleweb` VALUES
    ('管理员','/home/ldapServers','2025-02-20 16:48:07'),
    ('管理员','/home/myInfo','2025-02-20 16:48:07'),
    ('管理员','/home/setting/group_manage','2025-02-20 16:48:07'),
    ('管理员','/home/setting/ldap_group','2025-02-20 16:48:07'),
    ('管理员','/home/setting/menu_manage','2025-02-20 16:48:07'),
    ('管理员','/home/setting/rbac_manage','2025-02-20 16:48:07'),
    ('管理员','/home/setting/user_manage','2025-02-20 16:48:07');

-- 前端展示块列表
DROP TABLE IF EXISTS `sw_container`;
create table `sw_container` (
  `container_id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `web_route` varchar(190) NOT NULL COMMENT '标签所属的前端route路径',
  `container_name` varchar(30) NOT NULL COMMENT '元素块在此route的唯一标识',
  `container_desc` varchar(300) NOT NULL COMMENT '该元素块的描述',
  `date_create` datetime NOT NULL COMMENT '创建日期',
  `date_update` datetime NOT NULL COMMENT '更新日期',
  unique index route_container(web_route,container_name),
  PRIMARY KEY (`container_id`)
);
INSERT INTO `sw_container` VALUES
    (null,'/home/setting/user_manage','编辑','修改用户','2025-02-20 16:02:35','2025-02-20 16:02:35'),
    (null,'/home/setting/user_manage','删除','删除用户','2025-02-20 16:02:35','2025-02-20 16:02:35'),
    (null,'/home/setting/rbac_manage','编辑','编辑角色','2025-02-20 16:03:13','2025-02-20 16:03:13'),
    (null,'/home/setting/rbac_manage','删除','删除角色','2025-02-20 16:03:13','2025-02-20 16:03:13'),
    (null,'/home/setting/menu_manage','新增','新增页面','2025-02-20 16:04:15','2025-02-20 16:04:15'),
    (null,'/home/setting/menu_manage','编辑','编辑已有的页面','2025-02-20 16:04:15','2025-02-20 16:04:15'),
    (null,'/home/setting/menu_manage','删除','删除已有的页面','2025-02-20 16:04:15','2025-02-20 16:04:15'),
    (null,'/home/setting/rbac_manage','新增','新建一个角色','2025-02-20 16:04:35','2025-02-20 16:04:35'),
    (null,'/home/setting/user_manage','新增','新增一个用户','2025-02-20 16:04:55','2025-02-20 16:04:55'),
    (null,'/home/setting/group_manage','新增','新增一个组','2025-02-20 16:05:38','2025-02-20 16:05:38'),
    (null,'/home/setting/group_manage','编辑','编辑一个组','2025-02-20 16:05:38','2025-02-20 16:05:38'),
    (null,'/home/setting/group_manage','删除','删除一个组','2025-02-20 16:05:38','2025-02-20 16:05:38'),
    (null,'/home/setting/ldap_group','新增','','2025-02-20 16:05:55','2025-02-20 16:05:55'),
    (null,'/home/setting/ldap_group','编辑','','2025-02-20 16:05:55','2025-02-20 16:05:55'),
    (null,'/home/setting/ldap_group','删除','','2025-02-20 16:05:55','2025-02-20 16:05:55'),
    (null,'/home/ldapServers','新增连接','新增一个ldap服务器的连接','2025-02-20 16:29:49','2025-02-20 16:29:49'),
    (null,'/home/ldapServers','编辑连接','编辑指定ldap服务器的连接信息','2025-02-20 16:29:49','2025-02-20 16:29:49'),
    (null,'/home/ldapServers','删除连接','删除一个ldap服务器的连接','2025-02-20 16:29:49','2025-02-20 16:29:49'),
    (null,'/home/ldapServers','新增条目','在指定ldap服务器中新增条目','2025-02-20 16:29:49','2025-02-20 16:29:49'),
    (null,'/home/ldapServers','编辑条目','在指定ldap服务器中编辑条目','2025-02-20 16:29:49','2025-02-20 16:29:49'),
    (null,'/home/ldapServers','删除条目','在指定ldap服务器中删除条目','2025-02-20 16:29:49','2025-02-20 16:29:49');

-- 前端展示块与角色关联表
DROP TABLE IF EXISTS `sw_rolecontainer`;
create table `sw_rolecontainer` (
  `role_id` varchar(30) NOT NULL COMMENT '角色id',
  `web_route` varchar(190) NOT NULL COMMENT '标签所属的前端route路径',
  `container_name` varchar(30) NOT NULL COMMENT '元素块在此route的唯一标识',
  `date_create` datetime NOT NULL COMMENT '创建日期',
  unique index role_route_container(role_id,web_route,container_name),
  index role_id(role_id)
);
INSERT INTO `sw_rolecontainer` VALUES
    ('管理员','/home/ldapServers','删除条目','2025-02-20 16:48:07'),
    ('管理员','/home/ldapServers','删除连接','2025-02-20 16:48:07'),
    ('管理员','/home/ldapServers','新增条目','2025-02-20 16:48:07'),
    ('管理员','/home/ldapServers','新增连接','2025-02-20 16:48:07'),
    ('管理员','/home/ldapServers','编辑条目','2025-02-20 16:48:07'),
    ('管理员','/home/ldapServers','编辑连接','2025-02-20 16:48:07'),
    ('管理员','/home/setting/group_manage','删除','2025-02-20 16:48:07'),
    ('管理员','/home/setting/group_manage','新增','2025-02-20 16:48:07'),
    ('管理员','/home/setting/group_manage','编辑','2025-02-20 16:48:07'),
    ('管理员','/home/setting/ldap_group','删除','2025-02-20 16:48:07'),
    ('管理员','/home/setting/ldap_group','新增','2025-02-20 16:48:07'),
    ('管理员','/home/setting/ldap_group','编辑','2025-02-20 16:48:07'),
    ('管理员','/home/setting/menu_manage','删除','2025-02-20 16:48:07'),
    ('管理员','/home/setting/menu_manage','新增','2025-02-20 16:48:07'),
    ('管理员','/home/setting/menu_manage','编辑','2025-02-20 16:48:07'),
    ('管理员','/home/setting/rbac_manage','删除','2025-02-20 16:48:07'),
    ('管理员','/home/setting/rbac_manage','新增','2025-02-20 16:48:07'),
    ('管理员','/home/setting/rbac_manage','编辑','2025-02-20 16:48:07'),
    ('管理员','/home/setting/user_manage','删除','2025-02-20 16:48:07'),
    ('管理员','/home/setting/user_manage','新增','2025-02-20 16:48:07'),
    ('管理员','/home/setting/user_manage','编辑','2025-02-20 16:48:07');


-- 后端url接口列表
DROP TABLE IF EXISTS `sw_interface`;
create table `sw_interface` (
  `interface_id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT COMMENT '自增ID',
  `api_endpoint` varchar(190) NOT NULL COMMENT '接口的名字, 取值为接口上定义的endpoint',
  `api_url` varchar(190) NOT NULL COMMENT '接口路径',
  `api_methods` varchar(50) NOT NULL COMMENT '支持的协议',
  `date_create` datetime NOT NULL COMMENT '创建日期',
  `date_update` datetime NOT NULL COMMENT '更新日期',
  PRIMARY KEY (`interface_id`),
  unique index api_url(api_url),
  unique index api_endpoint(api_endpoint)
);

-- 后端url接口与角色关联表
DROP TABLE IF EXISTS `sw_roleinterface`;
create table `sw_roleinterface` (
  `role_id` varchar(30) NOT NULL COMMENT '角色id',
  `api_url` varchar(190) NOT NULL COMMENT '标签所属的前端route路径',
  `date_create` datetime NOT NULL COMMENT '创建日期',
  unique index role_api(role_id, api_url),
  index role_id(role_id)
);
INSERT INTO `sw_roleinterface` VALUES
    ('管理员','/api/config/get/all_kv','2025-02-20 16:48:08'),
    ('管理员','/api/crontab/info','2025-02-20 16:48:08'),
    ('管理员','/api/devops/coldlog/downLog','2025-02-20 16:48:08'),
    ('管理员','/api/devops/coldlog/getLogList','2025-02-20 16:48:08'),
    ('管理员','/api/devops/coldlog/getService','2025-02-20 16:48:08'),
    ('管理员','/api/devops/goodsPriceSync/sync','2025-02-20 16:48:08'),
    ('管理员','/api/devops/helm/modify','2025-02-20 16:48:08'),
    ('管理员','/api/devops/homeAlert','2025-02-20 16:48:08'),
    ('管理员','/api/devops/htmlLink','2025-02-20 16:48:08'),
    ('管理员','/api/devops/ldapserver/conn/add','2025-02-20 16:48:08'),
    ('管理员','/api/devops/ldapserver/conn/delete','2025-02-20 16:48:08'),
    ('管理员','/api/devops/ldapserver/conn/getall','2025-02-20 16:48:08'),
    ('管理员','/api/devops/ldapserver/conn/update','2025-02-20 16:48:08'),
    ('管理员','/api/devops/ldapserver/obj/add','2025-02-20 16:48:08'),
    ('管理员','/api/devops/ldapserver/obj/delete','2025-02-20 16:48:08'),
    ('管理员','/api/devops/ldapserver/obj/export','2025-02-20 16:48:08'),
    ('管理员','/api/devops/ldapserver/obj/getall','2025-02-20 16:48:08'),
    ('管理员','/api/devops/ldapserver/obj/move','2025-02-20 16:48:08'),
    ('管理员','/api/devops/ldapserver/obj/update','2025-02-20 16:48:08'),
    ('管理员','/api/devops/ldapserver/obj/upload','2025-02-20 16:48:08'),
    ('管理员','/api/devops/tableSync/sync','2025-02-20 16:48:08'),
    ('管理员','/api/devops/tidbShowLog','2025-02-20 16:48:08'),
    ('管理员','/api/email/send/code','2025-02-20 16:48:08'),
    ('管理员','/api/fromuser/email/send/code','2025-02-20 16:48:08'),
    ('管理员','/api/fromuser/sms/send/code','2025-02-20 16:48:08'),
    ('管理员','/api/group/create','2025-02-20 16:48:08'),
    ('管理员','/api/group/delete','2025-02-20 16:48:08'),
    ('管理员','/api/group/get','2025-02-20 16:48:08'),
    ('管理员','/api/group/update','2025-02-20 16:48:08'),
    ('管理员','/api/manage/changepasswd/user/batch','2025-02-20 16:48:08'),
    ('管理员','/api/manage/container/update','2025-02-20 16:48:08'),
    ('管理员','/api/manage/containers/create','2025-02-20 16:48:08'),
    ('管理员','/api/manage/containers/delete','2025-02-20 16:48:08'),
    ('管理员','/api/manage/create/user/batch','2025-02-20 16:48:08'),
    ('管理员','/api/manage/delete/user/batch','2025-02-20 16:48:08'),
    ('管理员','/api/manage/freeze/user/batch','2025-02-20 16:48:08'),
    ('管理员','/api/manage/get/role_id/all','2025-02-20 16:48:08'),
    ('管理员','/api/manage/get/role/dict','2025-02-20 16:48:08'),
    ('管理员','/api/manage/get/user/all','2025-02-20 16:48:08'),
    ('管理员','/api/manage/get/user/menus','2025-02-20 16:48:08'),
    ('管理员','/api/manage/get/user/my','2025-02-20 16:48:08'),
    ('管理员','/api/manage/interface/get/dict','2025-02-20 16:48:08'),
    ('管理员','/api/manage/role/create','2025-02-20 16:48:08'),
    ('管理员','/api/manage/role/delete','2025-02-20 16:48:08'),
    ('管理员','/api/manage/role/update','2025-02-20 16:48:08'),
    ('管理员','/api/manage/update/user/batch','2025-02-20 16:48:08'),
    ('管理员','/api/manage/web/create','2025-02-20 16:48:08'),
    ('管理员','/api/manage/web/delete','2025-02-20 16:48:08'),
    ('管理员','/api/manage/web/get/dict','2025-02-20 16:48:08'),
    ('管理员','/api/manage/web/update','2025-02-20 16:48:08'),
    ('管理员','/api/print','2025-02-20 16:48:08'),
    ('管理员','/api/sms/send/code','2025-02-20 16:48:08'),
    ('管理员','/api/user/check/telEmail','2025-02-20 16:48:08'),
    ('管理员','/api/user/delete/local','2025-02-20 16:48:08'),
    ('管理员','/api/user/freeze/local','2025-02-20 16:48:08'),
    ('管理员','/api/user/init','2025-02-20 16:48:08'),
    ('管理员','/api/user/ldap/login','2025-02-20 16:48:08'),
    ('管理员','/api/user/ldap/ous/manage/check','2025-02-20 16:48:08'),
    ('管理员','/api/user/ldap/ous/manage/create','2025-02-20 16:48:08'),
    ('管理员','/api/user/ldap/ous/manage/delete','2025-02-20 16:48:08'),
    ('管理员','/api/user/ldap/ous/manage/ldapattrs','2025-02-20 16:48:08'),
    ('管理员','/api/user/ldap/ous/manage/searchExists','2025-02-20 16:48:08'),
    ('管理员','/api/user/ldap/ous/manage/searchTmp','2025-02-20 16:48:08'),
    ('管理员','/api/user/ldap/ous/manage/update','2025-02-20 16:48:08'),
    ('管理员','/api/user/ldap/ous/manage/useradd','2025-02-20 16:48:08'),
    ('管理员','/api/user/ldap/ous/manage/userdel','2025-02-20 16:48:08'),
    ('管理员','/api/user/login','2025-02-20 16:48:08'),
    ('管理员','/api/user/logout','2025-02-20 16:48:08'),
    ('管理员','/api/user/signup','2025-02-20 16:48:08'),
    ('管理员','/api/user/unfreeze/local','2025-02-20 16:48:08'),
    ('管理员','/api/user/update/info/local','2025-02-20 16:48:08'),
    ('管理员','/api/user/update/passwd/local/useemail','2025-02-20 16:48:08'),
    ('管理员','/api/user/update/passwd/local/useold','2025-02-20 16:48:08'),
    ('管理员','/api/user/update/passwd/local/usetel','2025-02-20 16:48:08'),
    ('管理员','/api/user/update/photo','2025-02-20 16:48:08'),
    ('管理员','/ipput','2025-02-20 16:48:08'),
    ('管理员','/static/<path:filename>','2025-02-20 16:48:08'),
    ('访客','/api/user/update/info/local','2025-01-06 22:11:12'),
    ('访客','/api/user/update/passwd/local/useemail','2025-01-06 22:11:12'),
    ('访客','/api/user/update/passwd/local/useold','2025-01-06 22:11:12'),
    ('访客','/api/user/update/passwd/local/usetel','2025-01-06 22:11:12'),
    ('访客','/api/user/update/photo','2025-01-06 22:11:12');

-- ldap表达式汇总表
DROP TABLE IF EXISTS `sw_ldap_ous`;
create table `sw_ldap_ous` (
  `ou_id` mediumint(8) unsigned NOT NULL AUTO_INCREMENT,
  `ou_name` varchar(30) NOT NULL COMMENT 'ou搜索表达式的名字',
  `ou_base` varchar(200) NOT NULL COMMENT '要搜索的dn域',
  `ou_search` varchar(200) NOT NULL COMMENT '角色别名',
  `can_login_directly` varchar(30) NOT NULL COMMENT '能否不经管理员选定直接登录, 如果为yes, 则只要ou_search和密码可以匹配就能直接登录',
  `description` varchar(200) NOT NULL COMMENT '描述',
  `as_account` varchar(30) NOT NULL COMMENT '用哪个属性映射账户名',
  `as_displayname` varchar(30) NOT NULL COMMENT '用哪个属性映射显示名',
  `as_tel` varchar(30) NOT NULL COMMENT '用哪个属性映射电话号码',
  `as_email` varchar(30) NOT NULL COMMENT '用哪个属性映射邮箱',
  `as_password` varchar(30) NOT NULL COMMENT '用哪个属性映射密码',
  PRIMARY KEY (`ou_id`),
  UNIQUE index `ou_name` (`ou_name`)
);


-- ldap服务器管理, 用于ldap服务器管理功能
DROP TABLE IF EXISTS `sw_ldap_servers`;
create table `sw_ldap_servers` (
  `server_name` varchar(30) NOT NULL COMMENT '起的名字',
  `server_addr` varchar(200) NOT NULL COMMENT '服务器地址',
  `server_base` varchar(200) NOT NULL COMMENT '要登录的dn域',
  `server_auth_dn` varchar(200) NOT NULL COMMENT '登录用户的条目dn',
  `server_auth_passwd` varchar(200) NOT NULL COMMENT '登录用户的密码',
  `date_create` datetime NOT NULL COMMENT '创建日期',
  `date_update` datetime NOT NULL COMMENT '更新日期',
  PRIMARY KEY (`server_name`)
);

commit;