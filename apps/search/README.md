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
### 按时间段搜索（SelectImagesByTimeZone）
#### 说明
与按时间搜索类似，不过不再传递time，而是传递starttime和endtime，接口会根据这两个参数来返回在这段时间内用户的图片
#### 实现过程
1、获取POST请求传来的用户id、starttime和endtime
<br>
2、先调用Select_methods.py中的 select_by_userid(user_id)（按用户id搜索），得到用户所有图片（images）
<br>
3、将images、starttime和endtime传入Select_methods.py中的select_by_timezone(images, start_time, end_time)（按时间段搜索）方法
<br>
4、在select_by_timezone方法中，通过django的ORM（对象关系映射）查询即可得到时间段内的所有图片，返回一个 QuerySet 对象（images），表示查询到的所有符合条件的 Image 对象的集合
<br>
5、将images中每个图片的id和url组成idList和urlList，返回给前端
### 按位置搜索（SelectImagesByPosition）
#### 说明
前端发送POST请求，json中携带两个参数 user_id 和 position，这个接口会根据参数返回这个用户在这个位置所有的图片
#### 实现过程
1、获取POST请求传来的用户id 和 position
<br>
2、先调用 Select_methods.py 中的 select_by_userid(user_id)（按用户id搜索），得到用户所有图片（images）
<br>
3、将 images 和 position 传入 Select_methods.py 中的 select_by_position(image_list, position)（按位置搜索）方法
<br>
4、在 select_by_position 方法中，调用了高德地图地理编码API，使得无论用户输入是否规范都能得到一个可从省具体到区县的位置，再通过 django 的 ORM（对象关系映射）查询即可得到时间段内的所有图片，返回一个 QuerySet 对象（images），表示查询到的所有符合条件的 Image 对象的集合
<br>
5、将images中每个图片的id和url组成idList和urlList，返回给前端
### 按标签搜索（SelectImagesByTags）
#### 说明
前端发送POST请求，json中携带两个参数 user_id 和 tags（array），这个接口会根据参数返回这个用户所有带tags中所有标签的图片
#### 实现过程
1、获取POST请求传来的用户 id 和 tags（array）
<br>
2、先调用 Select_methods.py 中的 select_by_userid(user_id)（按用户id搜索），得到用户所有图片（images）
<br>
3、将 images 和 tags 传入 Select_methods.py 中的 select_by_tags(images, tags_list)（按标签搜索）方法
<br>
4、在 select_by_tags 方法中，会先分别取出 tags 中所有标签，在 ImageTag 表中找到带有这单个标签的图片集（imageList），再对所有imageList取交集，即可得到包含所有标签的图片集（images）
<br>
5、将images中每个图片的id和url组成idList和urlList，返回给前端
### 按描述搜索（SelectImagesByDescription）
#### 说明
前端发送POST请求，json中携带两个参数 user_id 和 description，这个接口会根据参数返回这个用户所有与描述比较贴切的图片
#### 实现过程
1、获取POST请求传来的用户 id 和 description
<br>
2、先调用 Select_methods.py 中的 select_by_userid(user_id)（按用户id搜索），得到用户所有图片（images）
<br>
3、将 images 和 description 传入 Select_methods.py 中的 select_by_description(images, description)（按描述搜索）方法
<br>
4、在 select_by_description 方法中，会便利用户所有的图片，得到每个图片的描述，计算其与用户输入的 description 的余弦相似度，去除余弦相似度小于0.1的图片，按照相似度从大到小的顺序排序，组成images
<br>
5、将images中每个图片的id和url组成idList和urlList，返回给前端
### 按时间段、地点、和标签搜索（SelectImagesByTPT）
#### 说明
前端发送POST请求，json中携带多个参数 user_id 、starttime 、endtime 、position 和 tags（array），这个接口会根据参数返回这个用户所有符合搜索条件的图片
#### 实现过程
1、获取POST请求传来的用户 id 、starttime 、endtime 、position 和 tags（array）
<br>
2、先调用 Select_methods.py 中的 select_by_userid(user_id)（按用户id搜索），得到用户所有图片（images）
<br>
3、如果starttime 、endtime 、position 和 tags（array）中有些参数为空，那么不会进行对应的搜索
<br>
4、将 images 和相应的参数传入 Select_methods.py 中的相应的方法中
<br>
4、在 select_by_description 方法中，会便利用户所有的图片，得到每个图片的描述，计算其与用户输入的 description 的余弦相似度，去除余弦相似度小于0.1的图片，按照相似度从大到小的顺序排序，组成images
<br>
5、将images中每个图片的id和url组成idList和urlList，返回给前端
### 获取用户所有标签（GetTags）
#### 说明
前端发送POST请求，json中携带一个参数 user_id，这个接口会根据参数返回这个用户所有图片的所有的标签
#### 实现过程
1、获取POST请求传来的用户 id
<br>
2、通过 django 的ORM（对象关系映射）查询 Image 表得到用户所有图片的 id
<br>
3、根据图片 id 即可在 ImageTag 表中查询到图片的所有标签
<br>
4、将所有的标签经过去重后得到标签集，然后发送给前端
### 获取省级行政区（GetProvinces）
#### 说明
前端发送GET请求，不用携带任何参数，接口会返回全国所有的省份集合
#### 实现过程
收到GET请求，进入 utils 工具包中的 citydata.py 文件，对里面的 data_ 字典进行操作即可获取所有省份
### 获取市级行政区（GetCity）
#### 说明
前端发送 POST 请求，json 中包含参数 province，接口会返回对应省份的所有城市
#### 实现过程
1、收到 POST 请求，获取 province
<br>
2、根据 province 的值对 citydata.py 文件面的 data_ 字典进行操作，得到该省份的所有市级行政区
### 获取区县及县级市（GetDistrict）
#### 说明
前端发送 POST 请求，json 中包含参数 city，接口会返回对应市级行政区的区县和县级市
#### 实现过程
1、收到 POST 请求，获取 city
<br>
2、根据 city 的值对 citydata.py 文件面的 data_ 字典进行操作，得到该市级行政区的所有区县和县级市





