# QRcode模块
> 负责人：张行
## 模块作用
用于 web 端的扫码登录
## 数据库表
### QRcodeId(二维码id表)
| 字段名 | 类型          | 说明                    |
| --- |-------------|-----------------------|
| qrcode_id | char(32)    | 二维码 id（主键）            |
| state | varchar（10） | 二维码状态 |
#### 说明
&emsp;用于存放二维码 id 和记录二维码状态，以实现扫码登录
### TemporaryToken（临时令牌表）
| 字段名 | 类型       | 说明                                    |
| --- |----------|---------------------------------------|
| temporary_token | char(32) | 临时token（主键）                           |
| qrcode | char（32） | 二维码 id（外键，与 QRcodeId 表中 qrcode_id 对应） |
| user | int      | 用户 id                                 |
#### 说明
&emsp;用于保存临时 token，防止他人干扰确认登陆，同时与 User 表建立联系，可以确认是哪个用户扫码登陆
## 过程说明
### 第一步
&emsp;web前端向后端发请求，
<br>
&emsp;后端生成一个二维码的 Base64 编码数据并发给web端
<br>
&emsp;后端保存二维码id，存到数据库里的二维码表（字段包含二维码id、使用情况）
### 第二步
&emsp;web前端显示二维码，并不断向后端查询这个二维码的状态
<br>
&emsp;手机扫描二维码，将手机上的token(这里用用户id代替)和扫描二维码得到的二维码id发给后端
<br>
&emsp;后端先检查这个用户是否在线，以及这个二维码是否被扫描过，如果在线且未被扫描，生成一个临时token并存入临时token表（字段包含二维码id、临时token），并将二维码表中对应的使用情况变为“已扫描”（scanned）。
<br>
&emsp;这个临时token表是为了确保后面确认登陆时不会被别人确认
<br>
后端还会将临时token发送给手机端
### 第三步
&emsp;web前端查询到二维码已扫描，会显示待确认，
<br>
&emsp;手机端收到后端发来的临时token也显示待确认
### 第四步
&emsp;手机端点击确认，将临时token再发给后端
<br>
&emsp;后端根据临时token找到对应二维码id，从而修改二维码状态为“已使用”（used）
<br>
&emsp;web端轮询查找二维码状态，发现是 “used” 后，后端将 user 的登录信息发给前端并将二维码状态改为 “stop”，前端收到登录信息后调用登录接口即可登录
