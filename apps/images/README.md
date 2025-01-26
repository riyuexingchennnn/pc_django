# Images 应用

> 负责人: 蔡明辰

## 一、实现功能

1. 图片上传：用户可以上传图片，并设置图片的标题、描述、标签等信息。
2. 图片查看：用户可以查看自己上传的图片。
3. 图片搜索：用户可以根据标题、描述、标签等信息搜索图片。
4. 图片分类：用户可以对图片进行分类，并可以根据分类查看图片。
5. 图片存储：用户上传的图片会存储在腾讯云 COS 服务器上。

## 二、数据库设计

### 1. image表

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| id | string | 图片ID |
| name | varchar(255) | 图片名称 |
| description | text | 图片描述 |
| category | varchar(255) | 图片分类 |
| position | varchar(255) | 图片位置 |
| time | datetime | 图片上传时间 |
| user_id | int | 图片上传用户ID |

### 2. image_tag关系表

| 字段名 | 类型 | 说明 |
| --- | --- | --- |
| image_id | string | 图片ID |
| tag_name | varchar(255) | 标签名称 |


## 三、详细设计

图片增、删、改、下载

### 1. 图片上传

内容审核-->图像理解-->图像分类-->图像描述(免费会员没有)-->写入mysql数据库-->存储到腾讯云COS

### 2. 图片删除

删除腾讯云COS上的图片-->删除数据库记录

### 3. 图片修改

修改数据库记录

### 4. 图片下载

根据user_id一次性将所有的图片的签名url发送给前端

## 四、图片AI

1. 图像审核：百度AI开放平台图像审核API
2. 图像理解：百度AI开放平台图像理解API
3. 图像描述：chatgpt4o-mini模型API
4. 图像分类：百度EasyDL平台图像分类API，自己准备训练数据集

分类类别:
- 人物: 自拍、人像、人脸
- 动植物: 动物、植物
- 风景: 自然风景、建筑风景
- 美食：美食、菜肴
- 杂物：各种死物、杂物
- 事件：生日、活动、节日

百度AI开放平台图像审核应用:https://console.bce.baidu.com/ai/?fromai=1#/ai/antiporn/app/list
EasyDL平台图像分类数据集:https://console.bce.baidu.com/easydl/datav/imgcls/dataset/list