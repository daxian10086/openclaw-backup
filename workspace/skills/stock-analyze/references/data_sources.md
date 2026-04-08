# 股票数据源参考

## BaoStock 详细接口

### 登录/登出
```python
import baostock as bs
lg = bs.login()
print(lg.error_msg)  # 'success' 表示成功
bs.logout()
```

### 查询股票基本信息
```python
rs = bs.query_stock_basic(code="sh.600519")
# 返回字段: code, code_name, ipoDate, outDate, type
while rs.error_code == '0' and rs.next():
    print(rs.get_row_data())
```

### 查询行业分类
```python
rs = bs.query_stock_industry()
# 返回字段: updateDate, code, code_name, industry, industryClassification
while rs.error_code == '0' and rs.next():
    print(rs.get_row_data())
```

### 查询日K线
```python
rs = bs.query_history_k_data_plus(
    "sh.600519",
    "date,code,open,high,low,close,volume,amount,pctChg",
    start_date='2026-01-01',
    end_date='2026-04-02',
    frequency="d",  # d=日k, w=周, m=月, 5=5分钟
    adjustflag="3"  # 1=前复权, 2=不复权, 3=后复权
)
```

## 腾讯财经实时行情

```python
import requests
headers = {'User-Agent': 'Mozilla/5.0'}

# 获取多只股票行情
stocks = "sh600519,sz000001"
url = f"https://qt.gtimg.cn/q={stocks}"
resp = requests.get(url, headers=headers, timeout=10)

# 解析数据
for line in resp.text.strip().split('\n'):
    parts = line.split('~')
    if len(parts) > 32:
        code = parts[2]      # sh600519
        name = parts[1]      # 贵州茅台
        price = parts[3]     # 当前价
        change = parts[31]   # 涨跌额
        pct = parts[32]      # 涨跌幅
        high = parts[33]     # 最高
        low = parts[34]      # 最低
        volume = parts[36]   # 成交量
```

## 新浪财经涨幅榜

```python
import requests
headers = {'User-Agent': 'Mozilla/5.0'}

url = "https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeDataSimple?page=1&num=100&sort=changepercent&asc=0&node=hs_a&symbol="
resp = requests.get(url, headers=headers, timeout=10)
data = resp.json()

# 筛选涨停股（涨幅>=9.9%）
zt_stocks = [s for s in data if float(s.get('changepercent', 0)) >= 9.9]
```

## 情绪评分标准

| 涨停家数 | 情绪等级 | 评分 |
|----------|----------|------|
| >=100 | 高潮 | 90 |
| 60-99 | 活跃 | 75 |
| 30-59 | 平稳 | 60 |
| 10-29 | 低迷 | 40 |
| <10 | 冰点 | 20 |

## 行业分类（证监会）

常见行业代码：
- C15 酒、饮料和精制茶制造业
- C27 医药制造业
- C26 化学原料和化学制品制造业
- C39 计算机、通信和其他电子设备制造业
- C36 汽车制造业
- J66 货币金融服务
