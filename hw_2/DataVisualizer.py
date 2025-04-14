import matplotlib.pyplot as plt
import numpy as np
class DataVisualizer:
    """
    可视化IMF数据的类
    """
    def __init__(self, data):
        """
        初始化可视化类
        :param data: 转换后的数据（years/values为列表形式）
        """
        self.data = data
        plt.rcParams["font.sans-serif"]=["SimHei"] #设置字体
        plt.rcParams["axes.unicode_minus"]=False

    def _smart_xticks(self, ax, years):
        """
        智能调整x轴刻度
        当年份数>8时自动旋转45度，超过15个年份时改为纵向显示
        """
        if len(years) > 8:
            rotation = 45 if len(years) <= 15 else 90
            ha = 'right' if rotation == 45 else 'center'
            ax.set_xticks(years)
            ax.set_xticklabels(years, rotation=rotation, ha=ha)
            
            # 调整底部边距防止标签被裁剪
            plt.subplots_adjust(bottom=0.25 if rotation == 45 else 0.4)
        else:
            ax.set_xticks(years)
            
    def _smart_labels(self, ax, years, values):
        """
        智能调整数据标签
        :param ax: Axes对象
        :param years: 年份列表
        :param values: 指标值列表
        """
        if len(years) > 15:
            # 如果年份数大于15，则不显示数据标签
            return
        else:
            for x, y in zip(years, values):
                ax.text(
                    x, y, f'{y:.2f}',
                    fontsize=9,
                    ha='center',
                    va='bottom' if y >= 0 else 'top',
                    bbox=dict(
                        facecolor='white',
                        alpha=0.7,
                        edgecolor='none',
                        boxstyle='round,pad=0.2'
                    )
                )
    
    def plot_data(self, indicator, indicator_label, indicator_unit, entities, figsize=(10, 7)):
        """
        数据可视化函数
        :param indicator: 指标ID (如: 'NGDP_RPCH')
        :param indicator_label: 指标名称
        :param indicator_unit: 指标单位描述
        :param entities: 国家/地区代码列表 (如: ['USA', 'CHN'])
        :param figsize: 图表尺寸 (宽, 高)
        """
        if indicator not in self.data:
            raise ValueError(f"指标 {indicator} 不存在于数据中")
        indicator_data = self.data[indicator]
        # 获取所有年份范围（用于统一x轴）
        all_years = set()
        for entity in entities:
            all_years.update(indicator_data[entity]['years'])
        min_year, max_year = min(all_years), max(all_years)
        
        fig, ax = plt.subplots(figsize=figsize)
        colors = plt.cm.tab10(np.linspace(0, 1, len(entities)))
        
        # 绘制每个实体的数据
        for idx, entity in enumerate(entities):
            years = indicator_data[entity]['years']
            values = indicator_data[entity]['values']
            
            # 绘制折线
            ax.plot(years,values, marker='o', markersize=8, linewidth=2.5,color=colors[idx], label=entity, alpha=0.9)
            # 添加数据标签
            self._smart_labels(ax, years, values)
            
        
        ax.set_title(f"指标: {indicator} ({indicator_label})\n单位: {indicator_unit}", fontsize=14, pad=20, fontweight='bold')
        ax.set_xlabel("年份", fontsize=12, labelpad=10)
        ax.set_ylabel("指标值", fontsize=12, labelpad=10)
        ax.grid(True, linestyle='--', alpha=0.4)
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1), frameon=True, framealpha=0.8, title='国家/地区')
        self._smart_xticks(ax, range(min_year, max_year + 1))
        plt.tight_layout()
        plt.show()
        

