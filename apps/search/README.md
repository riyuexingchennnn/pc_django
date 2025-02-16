# search模块
> 负责人： 张行
## 模块作用
提供各种搜索接口，来寻找图片
## 工具包

```
目录结构
.
└── utils
    ├──citydata.py
    ├──Cosine_similarity.py
    ├──position.py
    └──Select_methods.py
```
### citydata.py
&emsp;内部只有一个字典，包含了全国所有范围从国家到区县的行政区划分等信息，是通过position.py中的代码调用高德地图API获得的
### Cosine_similarity.py
&emsp;内部定义了计算两句话余弦相似度的方法，用于按描述搜索时使用
### position.py
用于生成citydata.py中的字典
### Select_methods.py
包含了各种搜索的方法（按时间（段）搜索、按地点搜索、按标签搜索等），实现代码复用
# 功能细节
### 按时间搜索（SelectImagesByTime）
#### 说明
前端发送POST请求，json中携带两个参数 user_id 和 time，这个接口会根据参数返回这个用户在这个时间的图片
#### 实现过程
1、获取POST请求传来的用户id和查询时间
<br>
2、先调用Select_methods.py中的 select_by_userid(user_id)（按用户id搜索），得到用户所有图片（images）
<br>
3、将images和时间传入Select_methods.py中的select_by_time(images, time)（按时间搜索）方法
<br>
4、在select_by_time方法中，通过django的ORM（对象关系映射）查询即可得到对应时间的所有图片，返回一个 QuerySet 对象（images），表示查询到的所有符合条件的 Image 对象的集合
<br>
5、将images中每个图片的id和url组成idList和urlList，返回给前端




