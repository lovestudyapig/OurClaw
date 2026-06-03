name: get_weather
description: 获取指定城市的实时天气信息，支持Open-Meteo API获取细粒度逐小时气象数据


# 获取天气技能 (get_weather)


## 使用场景
当用户询问某个城市的天气情况时，使用此技能。

## 执行步骤

1. **提取城市名称**：从用户消息中准确提取目标城市名称并生成问答，（例如：“北京今天天气怎么样？”或“查询上海的天气”）
2. **调用工具获取数据**：调用search 工具进行查询
3. **解析 JSON 数据**：从返回的数据包中提取以下核心指标：
    * **当前温度**
    * **天气状况**
    * **湿度**
    * **风速**
4. **生成回复**：用简洁的自然语言向用户汇总并汇报天气情况。


## 示例

**用户：** 「查询北京的天气」

**执行流程：**
1. **提取城市：** 北京 (Beijing)
2. **调用：** ` search("北京今天天气怎么样")`
3. **解析 JSON 结果**
4. **回复格式：** xx当前天气：晴，温度 25°C，湿度 40%，东南风 3 级。


---


## 进阶模式：Open-Meteo 细粒度气象数据查询

当用户需要**更详细的逐小时气象数据**（如历史逐小时温度、湿度、风速、降水等）时，使用本模式。

### API 说明

**Open-Meteo Archive API** 提供全球范围的 ERA5 再分析历史气象数据，覆盖1940年至今。

- **API 地址**: `https://archive-api.open-meteo.com/v1/archive`
- **数据类型**: 支持逐小时和逐日粒度的温度、湿度、降水量、风速、气压等多种气象要素
- **数据来源**: ECMWF ERA5 再分析数据集（结合历史观测 + 数值模式重建）
- **查询方式**: 通过 `GET` 请求传入经纬度、时间范围、所需气象要素参数

### 使用步骤

#### Step 1：获取目标城市的经纬度
从用户消息中提取城市名称，通过联网搜索获取该城市的经纬度坐标。

#### Step 2：确定查询参数
向用户确认：
- **时间范围**：如今天、昨天、某历史时段
- **时间粒度**：逐小时或逐日
- **所需气象要素**：

| 参数名 | 含义 |
|--------|------|
| `temperature_2m` | 2米气温（℃） |
| `relative_humidity_2m` | 相对湿度（%） |
| `precipitation` | 降水量（mm） |
| `surface_pressure` | 地表气压（hPa） |
| `wind_speed_10m` | 10米风速（km/h） |
| `wind_direction_10m` | 10米风向（°） |
| `cloud_cover` | 总云量（%） |
| `shortwave_radiation` | 短波辐射（W/m²） |
| `direct_radiation` | 直接辐射（W/m²） |
| `dew_point_2m` | 露点温度（℃） |

#### Step 3：构造并执行API请求
使用 `fetch_url` 工具调用 Open-Meteo API，URL格式如下：

```
https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={start}&end_date={end}&hourly={param1},{param2},...&timezone=Asia/Shanghai
```

**示例**：查询北京（39.9°N, 116.4°E）2023年7月17日逐小时温度与湿度

```
https://archive-api.open-meteo.com/v1/archive?latitude=39.9&longitude=116.4&start_date=2023-07-17&end_date=2023-07-17&hourly=temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m&timezone=Asia/Shanghai
```

#### Step 4：解析返回结果
API返回的JSON格式如下：
```json
{
  "latitude": 39.9,
  "longitude": 116.4,
  "hourly": {
    "time": ["2023-07-17T00:00", "2023-07-17T01:00", ...],
    "temperature_2m": [24.5, 23.8, ...],
    "relative_humidity_2m": [65, 68, ...]
  }
}
```

#### Step 5：生成回复
以表格或列表形式呈现查询结果，按时间顺序排列，格式如：

```
北京 2023-07-17 天气详情：
时间      温度(℃)  湿度(%)  降水量(mm)  风速(km/h)
00:00    24.5     65       0.0        8.3
01:00    23.8     68       0.0        7.5
...
```

如需统计汇总，可额外提供：
- 当日最高/最低温度
- 平均湿度
- 总降水量
- 日出/日落时间

### 注意事项
1. Open-Meteo 免费使用，无需 API Key
2. 时间范围不要超过 1 年（单次请求限制）
3. 如需历史逐小时温度插值到任意时间戳，可通过 Python 线性插值实现
4. 坐标精度建议保留 2 位小数
5. 如果用户问的是实时天气，优先使用原始 search 方式
