import requests
import json
import os
class BasicInfoManager:
    def __init__(self):
        self.base_url = 'https://www.imf.org/external/datamapper/api/v1'
        if not os.path.exists('available_indicators.json'):
            self.available_indicators = self.get_available_indicators()
        else:
            self.available_indicators = self.read_available_indicators('available_indicators.json')
        if not os.path.exists('available_entities.json'):
            self.available_entities = self.get_available_entities()
        else:
            self.available_entities = self.read_available_entities('available_entities.json')
        if self.available_indicators is None or self.available_entities is None:
            raise ValueError("无法获取可用指标或国家/地区信息")
            
        
    def get_available_indicators(self):
        """
        获取可用的指标
        :return: 可用指标（字典）
        """
        try:
            response = requests.get(self.base_url + '/indicators')
            response.raise_for_status()
            data = response.json()
            return data['indicators']
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return None
        
    def save_available_indicators(self, filename):
        """
        将可用的指标字典保存到文件
        :param filename: 文件名
        """
        indicators = self.get_available_indicators()
        if indicators:
            with open(filename, 'w') as f:
                json.dump(indicators, f)
            print(f"可用指标已保存到 {filename}")
        else:
            print("无法获取可用指标")
    
    def read_available_indicators(self, filename):
        """
        从文件中读取可用指标
        :param filename: 文件名
        :return: 可用指标（字典）
        """
        try:
            with open(filename, 'r') as f:
                indicators = json.load(f)
        except FileNotFoundError:
            print(f"文件 {filename} 不存在")
            return None
        return indicators
        
    
    def get_available_entities(self):
        """
        获取可用的国家/地区
        :return: 可用国家/地区（字典）
        """
        try:
            response = requests.get(self.base_url + '/countries')
            response.raise_for_status()
            data = response.json()
            return data['countries']
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return None
    
    def save_available_entities(self, filename):
        """
        将可用的国家/地区字典保存到文件
        :param filename: 文件名
        """
        entities = self.get_available_entities()
        if entities:
            with open(filename, 'w') as f:
                json.dump(entities, f)
            print(f"可用国家/地区已保存到 {filename}")
        else:
            print("无法获取可用国家/地区")
    
    def read_available_entities(self, filename):
        """
        从文件中读取可用国家/地区
        :param filename: 文件名
        :return: 可用国家/地区（字典）
        """
        try:
            with open(filename, 'r') as f:
                entities = json.load(f)
        except FileNotFoundError:
            print(f"文件 {filename} 不存在")
            return None
        return entities
        
class DataManager:
    def __init__(self):
        self.base_url = 'https://www.imf.org/external/datamapper/api/v1'
    
    def query_params_check(self, basic_info_manager, indicators, entities, years):
        """
        检查查询参数的有效性
        :param indicators: 指标ID列表 (如: ['NGDP_RPCH','LP'])
        :param entities: 国家/地区代码列表 (如: ['USA', 'CHN'])
        :param years: 年份范围 (如: [2019, 2020])
        :return: 是否有效的布尔值
        """
        if indicators is None :
            return False
        for indicator in indicators:
            if indicator not in basic_info_manager.available_indicators:
                return False
        for entity in entities:
            if entity not in basic_info_manager.available_entities:
                return False
        if min(years) < 1980 or max(years) > 2029:
            return False
        return True
    
    def query_data(self, indicators, entities, years):
        """
        从IMF API获取数据
        :param indicators: 指标ID列表 (如: ['NGDP_RPCH','LP'])
        :param entities: 国家/地区代码列表 (如: ['USA', 'CHN'])
        :param years: 年份范围 (如: [2019, 2020])
        :return: 解析后的数据字典，三层嵌套结构，第一层为指标，第二层为国家/地区，第三层为年份和对应的值，年份和值都是列表
        """
        base_url = self.base_url

        # 若提供了指标，则将其添加到URL中
        if indicators:
            base_url += '/' + '/'.join(indicators)
        # 若提供了国家/地区代码，则将其添加到URL中
        if entities:
            base_url += '/' + '/'.join(entities)

        # 若提供了年份范围，则将其添加为查询参数，使用逗号分隔
        params = {'periods': ','.join(map(str, years))} if years else None

        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            result = dict()
            for indicator, entities in data['values'].items():
                result[indicator] = dict()
                for entity, entity_data in entities.items():
                    result[indicator][entity] = dict()
                    # 获取年份和对应的值
                    years = list(entity_data.keys())
                    values = [entity_data[year] for year in years]
                    years = list(map(int, years))
                    #异常处理：如果没有数据，则跳过
                    if not years or not values:
                        print(f"警告: {entity} 在指标 {indicator} 中没有数据")
                        continue
                    result[indicator][entity]['years'] = years
                    result[indicator][entity]['values'] = values
            
            return result
        except requests.exceptions.RequestException as e:
            print(f"请求错误: {e}")
            return None
