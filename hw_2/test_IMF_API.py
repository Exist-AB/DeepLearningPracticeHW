import requests
import matplotlib.pyplot as plt
from collections import defaultdict
    
def get_imf_data(indicators=None, entities=None, periods=None):
    """
    从IMF API获取数据
    :param indicator: 指标ID列表 (如: ['NGDP_RPCH','LP'])
    :param entities: 国家/地区代码列表 (如: ['USA', 'CHN'])
    :param periods: 年份范围 (如: [2019, 2020])
    :return: 解析后的数据字典，三层嵌套结构，第一层为指标，第二层为国家/地区，第三层为年份和对应的值，年份和值都是列表
    """
    base_url = f"https://www.imf.org/external/datamapper/api/v1"
    
    # 若提供了指标，则将其添加到URL中
    if indicators:
        base_url += '/' + '/'.join(indicators)
    # 若提供了国家/地区代码，则将其添加到URL中
    if entities:
        base_url += '/' + '/'.join(entities)
    
    # 若提供了年份范围，则将其添加为查询参数，使用逗号分隔
    params = {'periods': ','.join(map(str, periods))} if periods else None
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        # 新建字典用于存储最终结果
        final_result = dict()
        
        # 对每个指标进行处理
        for indicator in indicators:
            # 新建字典用于存储指标结果
            indicator_result = dict()
            # 获取指标元数据
            indicator_data = data['values'].get(indicator, {})
            # 对每个国家/地区进行处理
            for entity in entities:
                entity_data = indicator_data.get(entity, {})
                # 获取年份和对应的值
                years = list(entity_data.keys())
                values = [entity_data[year] for year in years]
                #异常处理：如果没有数据，则跳过
                if not years or not values:
                    print(f"警告: {entity} 在指标 {indicator} 中没有数据")
                    continue
                # 将数据存储到结果字典中
                result = dict()
                result['years'] = years
                result['values'] = values
                indicator_result[entity] = result
            # 将这一个指标的结果存储到指标结果字典中
            final_result[indicator] = indicator_result
        print(final_result)
        return dict(final_result)
    except requests.exceptions.RequestException as e:
        print(f"请求错误: {e}")
        return None

# 使用示例
if __name__ == "__main__":
    # 配置参数
    INDICATOR = ['NGDP_RPCH','LP']  # 实际GDP增长率和人口
    COUNTRIES = ['USA', 'CHN', 'JPN', 'IND']  # 美国、中国、日本、印度
    YEARS = list(range(2018, 2023))  # 获取2018-2022年数据
    
    # 获取数据
    data = get_imf_data(INDICATOR, COUNTRIES, YEARS)
    
    if data:
        # 打印数据
        print("获取数据成功:")
        for indicator, entity_data in data.items():
            for entity, values in entity_data.items():
                print(f"指标: {indicator}, 国家/地区: {entity}, 年份: {values['years']}, 值: {values['values']}")

    else:
        print("未能获取数据")