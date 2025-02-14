# Django后端应用组件

## 任务分工

划分成7块，3人分工完成。

- 蔡明辰：images、ai
- 张行：pay、search
- 李灿：accounts、admin

> 注意utils文件夹为公共组件，不属于任何一个应用。

## 目录结构

```
.
├── accounts
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── migrations
│   ├── models.py
│   ├── __pycache__
│   ├── README.md
│   ├── tests.py
│   └── views.py
├── admin
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── migrations
│   ├── models.py
│   ├── README.md
│   ├── tests.py
│   └── views.py
├── ai
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── migrations
│   ├── models.py
│   ├── __pycache__
│   ├── README.md
│   ├── tests.py
│   └── views.py
├── images
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── migrations
│   ├── models.py
│   ├── __pycache__
│   ├── README.md
│   ├── tests.py
│   ├── utils
│   └── views.py
├── pay
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── migrations
│   ├── models.py
│   ├── __pycache__
│   ├── README.md
│   ├── tests.py
│   └── views.py
├── README.md
├── search
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── migrations
│   ├── models.py
│   ├── __pycache__
│   ├── README.md
│   ├── tests.py
│   └── views.py
└── utils
    ├── cos_util.py
    ├── email_util.py
    ├── middleware.py
    └── token_util.py
```