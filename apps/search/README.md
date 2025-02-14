# search 应用

> 负责人： 张行

## 接口说明
用于搜索图片，分了多种搜索方法，详情如下
## 接口文档
### SelectImagesByTime（按时间查找）
>http://localhost:8000/search/image/time
#### 1、请求方式：post <br>
#### 2、请求参数 <br>
&emsp;user_id: 用户id（string）<br>
&emsp;time: 时间（用 ‘-’ 分隔年月日， string）<br>
&emsp;**参数写入请求体中，使用json格式**
#### 3、返回参数
##### 成功：
&emsp;state： success（成功时固定返回 ”success“ ）<br>
&emsp;image_id: 符合条件的图片id集合（array）<br>
&emsp;image_url: 符合条件的图片url集合（array）<br>
##### 失败：
&emsp;state： failed<br>
&emsp;message： 描述（未找到这个时间的图片）<br>


### SelectImagesByTimeZone（按时间段查找）
>http://localhost:8000/search/image/timezone
#### 1、请求方式：post <br>
#### 2、请求参数 <br>
&emsp;user_id: 用户id（string）<br>
&emsp;starttime: 开始时间（用 ‘-’ 分隔年月日， string）<br>
&emsp;endttime: 结束时间（用 ‘-’ 分隔年月日， string）<br>
&emsp;**参数写入请求体中，使用json格式**
#### 3、返回参数
##### 成功：
&emsp;state： success（成功时固定返回 ”success“ ）<br>
&emsp;image_id: 符合条件的图片id集合（array）<br>
&emsp;image_url: 符合条件的图片url集合（array）<br>
##### 失败：
&emsp;state： failed<br>
&emsp;message： 描述（未找到这个时间段的图片）<br>


### SelectImagesByPosition（按地点查找）
>http://localhost:8000/search/image/position
#### 1、请求方式：post <br>
#### 2、请求参数 <br>
&emsp;user_id: 用户id（string）<br>
&emsp;position: 地点（string）<br>
&emsp;**参数写入请求体中，使用json格式**
#### 3、返回参数
##### 成功：
&emsp;state： success（成功时固定返回 ”success“ ）<br>
&emsp;image_id: 符合条件的图片id集合（array）<br>
&emsp;image_url: 符合条件的图片url集合（array）<br>
##### 失败：
&emsp;state： failed<br>
&emsp;message： 描述（未找到这个时间段的图片）<br>


### SelectImagesByTags（按标签查找）
>http://localhost:8000/search/image/tags
#### 1、请求方式：post <br>
#### 2、请求参数 <br>
&emsp;user_id: 用户id（string）<br>
&emsp;tags: 标签列表（array）<br>
&emsp;**参数写入请求体中，使用json格式**
#### 3、返回参数
##### 成功：
&emsp;state： success（成功时固定返回 ”success“ ）<br>
&emsp;image_id: 符合条件的图片id集合（array）<br>
&emsp;image_url: 符合条件的图片url集合（array）<br>
##### 失败：
&emsp;state： failed<br>
&emsp;message： 描述（未找到这个时间段的图片）<br>


### SelectImagesByDescription（按描述查找）
>http://localhost:8000/search/image/description
#### 1、请求方式：post <br>
#### 2、请求参数 <br>
&emsp;user_id: 用户id（string）<br>
&emsp;description: 描述（string）<br>
&emsp;**参数写入请求体中，使用json格式**
#### 3、返回参数
##### 成功：
&emsp;state： success（成功时固定返回 ”success“ ）<br>
&emsp;image_id: 符合条件的图片id集合（array）<br>
&emsp;image_url: 符合条件的图片url集合（array）<br>
##### 失败：
&emsp;state： failed<br>
&emsp;message： 描述（未找到这个时间段的图片）<br>


### SelectImagesByTPT（按时间段、位置、标签查找）
>http://localhost:8000/search/image
#### 1、请求方式：post <br>
#### 2、请求参数 <br>
&emsp;user_id: 用户id（string）<br>
&emsp;starttime: 开始时间（用 ‘-’ 分隔年月日， string）<br>
&emsp;endttime: 结束时间（用 ‘-’ 分隔年月日， string）<br>
&emsp;position: 地点（string）<br>
&emsp;tags: 标签列表（array）<br>
&emsp;**参数写入请求体中，使用json格式**
#### 3、返回参数
##### 成功：
&emsp;state： success（成功时固定返回 ”success“ ）<br>
&emsp;image_id: 符合条件的图片id集合（array）<br>
&emsp;image_url: 符合条件的图片url集合（array）<br>
##### 失败：
&emsp;state： failed<br>
&emsp;message： 描述（未找到这个时间段的图片）<br>


### GetTags（查找用户设置的标签）
>http://localhost:8000/search/image/tag
#### 1、请求方式：post <br>
#### 2、请求参数 <br>
&emsp;user_id: 用户id（string）<br>
&emsp;**参数写入请求体中，使用json格式**
#### 3、返回参数
&emsp;tags： 标签列表（array）<br>
