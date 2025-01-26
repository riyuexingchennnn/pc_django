# AI 应用开发

> 负责人：蔡明辰

## 面向用户功能

(gold用户正好对应了我们可能不做的东西，至少要把silver用户的功能都做了)

| 功能     | free用户 | silver用户 | gold用户 |
| ------- | -------- | ---------- | -------- |
| 价格     | 免费     | ￥8/月    | ￥18/月 |
| 云存储大小 | 1G | 5G | 10G |
| 图像分类 | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| 图像理解 | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| 图像检索 | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| 相似图像搜索 | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| 图像描述 | :x: | :white_check_mark: | :white_check_mark: |
| 图像自然语言搜索 | :x: | :white_check_mark: | :white_check_mark: |
| 私有云 | :x: | :x: | :white_check_mark: |
| 高级AI | :x: | :x: | :white_check_mark: |

## 功能实现

> 此ai应用模块，不做所有的AI功能。部分常用AI基础功能，通常是上传图片时被动发起的，比如图像分类、图像理解、图像描述、图像审核，已移交到images应用模块。此ai应用模块制作相似图像搜索、图像风格迁移、图像超高分辨率等高级功能，通常是由用户主动发起的。