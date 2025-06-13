# 开发文档

## 项目结构

```
autohome-crawler/
├── car_crawler_v5.py     # 主程序
├── test_crawler.py       # 测试文件
├── requirements.txt      # 依赖列表
├── .gitignore           # Git忽略文件
├── README.md            # 项目说明
├── LICENSE              # MIT许可证
└── docs/               # 文档目录
    ├── API.md          # API文档
    └── DEVELOPMENT.md  # 开发文档
```

## 开发环境设置

1. 克隆仓库：
```bash
git clone git@github.com:kaka4413/--autohome-crawler.git
cd --autohome-crawler
```

2. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖：
```bash
pip install -r requirements.txt
```

## 代码结构说明

### 主要类和函数

1. `CarCrawler` 类
   - `__init__`: 初始化爬虫配置
   - `get_brand_list`: 获取品牌列表
   - `get_series_list`: 获取车系列表
   - `get_energy_type`: 获取能源类型
   - `process_brand`: 处理单个品牌数据
   - `save_data`: 保存数据到Excel

2. 工具函数
   - `setup_logging`: 配置日志
   - `parse_args`: 解析命令行参数
   - `retry_on_failure`: 请求重试装饰器

### 数据处理流程

1. 品牌数据获取
   - 请求品牌列表API
   - 解析JSON响应
   - 提取品牌信息

2. 车系数据获取
   - 遍历品牌列表
   - 获取在售和停售车系
   - 处理分页数据

3. 能源类型识别
   - 请求配置接口
   - 解析配置数据
   - 匹配能源类型

4. 数据存储
   - 数据去重
   - 格式化处理
   - 保存到Excel

## 测试

1. 单元测试：
```bash
pytest test_crawler.py -v
```

2. 测试覆盖率：
```bash
pytest --cov=. test_crawler.py
```

## 部署

### GitHub Actions

项目使用GitHub Actions进行自动化测试和部署：
- 代码提交时自动运行测试
- 每周自动运行完整爬虫任务
- 生成测试报告

### 本地部署

1. 安装依赖：
```bash
pip install -r requirements.txt
```

2. 运行爬虫：
```bash
python car_crawler_v5.py
```

## 注意事项

1. 反爬虫处理
   - 添加随机延时
   - 使用请求头
   - 处理异常响应

2. 数据质量
   - 自动去重
   - 数据验证
   - 错误日志

3. 性能优化
   - 并发请求
   - 数据缓存
   - 断点续爬

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交代码
4. 创建 Pull Request

## 版本历史

### V5.0
- 优化品牌获取方式
- 改进数据结构解析
- 实现新的去重逻辑
- 支持多种能源类型识别 