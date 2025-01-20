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
| 图像描述 | :x: | :white_check_mark: | :white_check_mark: |
| 图像自然语言搜索 | :x: | :white_check_mark: | :white_check_mark: |
| 私有云 | :x: | :x: | :white_check_mark: |
| 高级AI | :x: | :x: | :white_check_mark: |

## 技术架构

- 图像分类：自己训练模型，预计使用GoogleNet深度学习网络，在蔡明辰电脑上4070GPU可以跑到100FPS。
- 图像理解：使用百度云API
- 图像审核：使用百度云API
- 图像检索：这个没有AI部分，具体在search应用里实现。
- 图像描述：使用chatGPT4o的API，让他用一句话描述图片。