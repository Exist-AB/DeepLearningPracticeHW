from pywebio import start_server,config
from pywebio.input import *
from pywebio.output import *
from pywebio.pin import put_select, put_slider, put_actions, get_pin_values, pin_wait_change
from pywebio.session import run_async
from DataManager import BasicInfoManager, DataManager
from DataVisualizer import DataVisualizer
import time 
class WebPage:
    def __init__(self):
        """Web应用初始化"""
        self.basic_info_manager = BasicInfoManager()
        print("BasicInfoManager initialized")
        self.data_manager = DataManager()
        print("DataManager initialized")
        self.available_indicators = self.basic_info_manager.available_indicators
        self.available_entities = self.basic_info_manager.available_entities
        
    async def main_app(self):
        """主应用界面"""
        config(title="IMF经济数据可视化分析", description="IMF经济数据可视化分析", theme='default')
        clear(scope='input')
        clear(scope='result')
        
        # 初始化 created_scopes
        if not hasattr(self, 'created_scopes'):
            self.created_scopes = set()
        
        # 创建 input scope
        if 'input' not in self.created_scopes:
            put_scope('input')
            self.created_scopes.add('input')
        
        # 在 input scope 中输出标题和各个 pin 控件
        put_markdown("# IMF经济数据可视化分析", scope='input')
        # 指标选择（多选，下拉列表）
        put_select("indicator", 
                   label="选择指标（可多选）",
                   options=[{'label': info['label'], 'value': k} for k, info in self.available_indicators.items()],
                   multiple=True,
                   value=['NGDP_RPCH', 'LP'],
                   scope="input")
        
        # 国家/地区选择（多选，下拉列表）
        put_select("entities",
                   label="选择国家/地区（可多选）",
                   options=[{'label': info['label'], 'value': k} for k, info in self.available_entities.items()],
                   multiple=True,
                   value=['USA', 'CHN'],
                   scope="input")
        
        # 年份范围选择：采用两个滑块分别选择起始和结束年份
        put_slider("start_year",
                   label="选择起始年份",
                   min_value=1980,
                   max_value=2029,
                   step=1,
                   value=1980,
                   scope="input")
        
        put_slider("end_year",
                   label="选择结束年份",
                   min_value=1980,
                   max_value=2029,
                   step=1,
                   value=2029,
                   scope="input")
        
        # 动作按钮：分析数据
        put_actions("actions",
                    label="",
                    buttons=[
                        {'label': '分析数据', 'value': 'analyze','type': 'submit'}
                    ],
                    scope="input")
        changed = await pin_wait_change(['actions'])
        # 获取用户选择
        form_data = await get_pin_values(['indicator', 'entities', 'start_year', 'end_year', 'actions'])
        # 检查并处理输入数据
        if form_data.get("actions") != "analyze":
            return
        if not form_data.get("indicator"):
            toast("请至少选择一个指标", color='error')
            return
        if not form_data.get("entities"):
            toast("请至少选择一个国家/地区", color='error')
            return
        if not (form_data.get("start_year") and form_data.get("end_year")):
            toast("请至少选择一个年份", color='error')
            return
        if form_data.get("start_year") > form_data.get("end_year"):
            toast("起始年份不能大于结束年份", color='error')
            return
        # 构造年份范围列表
        start_year = form_data["start_year"]
        end_year = form_data["end_year"]
        years = list(range(start_year, end_year + 1))
        
        # 创建 result scope 
        if 'result' not in self.created_scopes:
            put_scope('result')
            self.created_scopes.add('result')
        
        # 处理分析请求并生成图表、显示结果
        with put_loading('border', color='primary', scope='result'):
            imgs = list()
            all_warnings = []
            for indicator in form_data["indicator"]:
                data = self.data_manager.query_data(
                    indicator,
                    form_data["entities"],
                    sorted(years)
                )
                # 如果查询数据中包含警告信息，则加入 all_warnings
                if data and "_warnings" in data:
                    all_warnings.extend(data["_warnings"])
                data_visualizer = DataVisualizer(data)
                indicator_label = self.basic_info_manager.available_indicators[indicator]["label"]
                indicator_unit = self.basic_info_manager.available_indicators[indicator]["unit"]
                imgs.append(
                    data_visualizer.plot_data(
                        indicator,
                        indicator_label,
                        indicator_unit,
                        form_data["entities"],
                    )
                )
        put_markdown("## 分析结果", scope='result')
        if all_warnings:
            for warn in all_warnings:
                put_text(warn, scope='result')
        for img in imgs:
            put_image(img, format='png', width='90%', scope='result').show()
        
        # 添加重置选项按钮
        put_button("重置选项", onclick=lambda: run_async(self.main_app()), scope='result')

    def get_available_port(self):
        """获取可用端口"""
        import socket
        port = 8081
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('localhost', port)) != 0:
                    break
                port += 1
        return port
    
    def run(self):
        """启动Web应用"""
        port = self.get_available_port()
        start_server(self.main_app, port, debug=True)