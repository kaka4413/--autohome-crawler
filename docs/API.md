# API 文档

## 接口说明

### 1. 品牌列表接口

获取汽车之家所有品牌信息。

**请求URL:**
```
https://www.autohome.com.cn/_next/data/nextweb-prod-c_1.0.160-p_1.50.0/cars/brand-x-x-x-x-x-1.html.json
```

**返回数据:**
```json
{
    "brandList": [
        {
            "id": "品牌ID",
            "name": "品牌名称",
            ...
        }
    ]
}
```

### 2. 车系列表接口

获取指定品牌下的车系信息。

**请求URL:**
```
https://www.autohome.com.cn/_next/data/nextweb-prod-c_1.0.160-p_1.50.0/cars/brand-{brandId}-x-{status}-x-x-{page}.html.json
```

**参数说明:**
- brandId: 品牌ID
- status: 销售状态（1:停售, 2:在售）
- page: 页码

### 3. 车型配置接口

获取车型详细配置信息。

**请求URL:**
```
https://car-web-api.autohome.com.cn/car/param/getParamConf
```

**请求参数:**
```json
{
    "seriesId": "车系ID"
}
```

## 数据结构

### 1. 能源类型分类

```python
ENERGY_TYPES = [
    "汽油",
    "柴油",
    "油电混合",
    "天然气",
    "汽油电驱",
    "甲醇",
    "纯电动",
    "插电式混合动力",
    "增程式",
    "氢燃料",
    "48V轻混系统汽油",
    "24V轻混系统"
]
```

### 2. 输出数据格式

保存为Excel文件，包含以下字段：
- 品牌ID
- 品牌名称
- 车系ID
- 车系名称
- 销售状态
- 能源类型

## 使用示例

### 1. 爬取指定品牌

```python
python car_crawler_v5.py --brand "大众"
```

### 2. 测试模式

```python
python car_crawler_v5.py --test
```

### 3. 从指定品牌继续爬取

```python
python car_crawler_v5.py --resume "特斯拉"
``` 