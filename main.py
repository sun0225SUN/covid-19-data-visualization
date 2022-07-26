import os
import json
import pprint
import numpy as np
import requests
import pandas as pd
from pyecharts.charts import *
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
from pyecharts.globals import ThemeType, ChartType

############################################# 数据请求 #############################################

def catch_data(api_name):
    url = 'https://api.inews.qq.com/newsqa/v1/query/inner/publish/modules/list?modules=' + api_name
    reponse = requests.get(url=url).json()
    return reponse

def catch_world_data(api_name):
    url = 'https://api.inews.qq.com/newsqa/v1/automation/modules/list?modules=' + api_name
    reponse = requests.get(url=url).json()
    return reponse

############################################# 数据获取及清洗 #############################################

############## 近60天国内累计数据汇总 ##############
china_daylist = catch_data('chinaDayList')
china_daylist = pd.DataFrame(china_daylist['data']['chinaDayList'])
china_daylist['date'] = pd.to_datetime(china_daylist['y'].astype('str') + '.' + china_daylist['date'])
china_daylist = china_daylist[['date','confirm','heal','dead','importedCase','nowConfirm','nowSevere','localConfirm']]
#china_daylist.columns = ['日期','累计确诊','累计治愈','累计死亡','累计境外输入','现有确诊','现有重症','本土现有确诊']
china_daylist.to_csv('./assets/china_daylist.csv',index=False)

############## 国内每日新增数据 ##############
china_daynewadd = catch_data('chinaDayAddListNew')
china_daynewadd = pd.DataFrame(china_daynewadd['data']['chinaDayAddListNew'])
china_daynewadd['date'] = pd.to_datetime(china_daynewadd['y'].astype('str') + '.' + china_daynewadd['date'])
china_daynewadd = china_daynewadd[['date','confirm','dead','heal','infect','importedCase','localConfirmadd','localinfectionadd']]
# china_daynewadd.columns = ['日期','新增确诊','新增死亡','新增治愈','新增无症状','新增境外','本土新增确诊','本土新增无症状']
china_daynewadd.to_csv('./assets/china_daynewadd.csv',index=False)

############## 国内当日全国累计确诊数据 ##############
china_data = catch_data('diseaseh5Shelf')['data']['diseaseh5Shelf']
# print(china_data['chinaTotal']['confirm'])
china_Total = china_data['chinaTotal']
# print(china_Total['showLocalConfirm'])
china_Add = china_data['chinaAdd']

lastUpdateTime = china_data['lastUpdateTime']

chinaTotal = {}
chinaTotal['确诊'] = china_Total['confirm']
# print(china_Total['确诊'])
chinaTotal['疑似'] = china_Total['suspect']
chinaTotal['死亡'] = china_Total['dead']
chinaTotal['治愈'] = china_Total['heal']

chinaAdd = {}
chinaAdd['新增确诊'] = china_Add['confirm']
# print(china_Add['新增确诊'])
chinaAdd['新增疑似'] = china_Add['suspect']
chinaAdd['新增死亡'] = china_Add['dead']
chinaAdd['新增治愈'] = china_Add['heal']

sum = chinaTotal['确诊'] + chinaTotal['疑似'] + chinaTotal['死亡'] + chinaTotal['治愈']

############### 国内当日各市的数据 ###############
china_area_data = china_data['areaTree'][0]['children']
# print(china_area_data[0]['total']['wzz'])

# 把国内的数据组成一个字典列表存放起来
china_area_list = []
# 遍历国内各个省份的数据，重新组成一个列表
for i in range(len(china_area_data)):
    # 当前遍历的省份
    province = china_area_data[i]['name']
    province_total = china_area_data[i]['total']['confirm']
    # 该省份的数据
    province_list = china_area_data[i]['children']
    for j in range(len(province_list)):
        city = province_list[j]['name']
        total = province_list[j]['total']
        today = province_list[j]['today']
        china_dict = {'province': province, 'city': city, 'total': total, 'today': today}
        china_area_list.append(china_dict)
# pprint.pprint(china_area_list)

china_area_data = pd.DataFrame(china_area_list)
# china_area_data.head()
# pprint.pprint(china_area_data)
china_area_data.to_csv('./assets/china_data_01.csv', encoding='utf-8')

# 再次清洗
china_area_data['confirm'] = china_area_data['total'].map(lambda x:eval(str(x))['confirm'])
# print(china_area_data['confirm'])
china_area_data['dead'] = china_area_data['total'].map(lambda x:eval(str(x))['dead'])
china_area_data['heal'] = china_area_data['total'].map(lambda x:eval(str(x))['heal'])
china_area_data['add_confirm'] = china_area_data['today'].map(lambda x:eval(str(x))['confirm'])
china_area_data = china_area_data[
    ["province", "city", "confirm", "dead", "heal", "add_confirm"]]
# china_area_data.head()
china_area_data.to_csv('./assets/china_data_02.csv', encoding='utf-8')

############### 国内各个省份的数据 ###############
china_province_area_data = china_data['areaTree'][0]['children']

# 把国内的数据组成一个字典列表存放起来
china_province_area_list = []
# 遍历国内各个省份的数据，重新组成一个列表
for i in range(len(china_province_area_data)):
    # 当前遍历的省份
    province = china_province_area_data[i]['name']
    province_total = china_province_area_data[i]['total']['confirm']
    # 省份的数据
    china_province_dict = {'province': province, 'province_total_confirm': province_total}
    china_province_area_list.append(china_province_dict)

china_province_area_data = pd.DataFrame(china_province_area_list)
# 降序排序
china_province_area_data.sort_values(by='province_total_confirm', ascending=False, inplace=True)
china_province_area_data.to_csv('./assets/china_data_03.csv', encoding='utf-8')

############### 全球疫情数据 ###############
world_data=catch_world_data('WomAboard')['data']['WomAboard']

data_set = []
for i in world_data:
    data_dict = {}
    # data_dict['pub_date'] = i['pub_date']  # 当前日期
    data_dict['name'] = i['name']  # 国家
    data_dict['confirmAdd'] = i['confirmAdd']  # 新增确诊
    data_dict['confirm'] = i['confirm']  # 累计确诊
    data_dict['heal'] = i['heal']  # 治愈
    data_dict['dead'] = i['dead']  # 死亡
    data_set.append(data_dict)

# 国外疫情缺少国内数据，放在一起才是全球数据
china_Total = [china_Total]
china_Add = [china_Add]
china_data_dict = {}

for i in china_Total:
    china_data_dict['name'] = '中国'
    china_data_dict['confirm'] = i['confirm']  # 累计确诊
    china_data_dict['heal'] = i['heal']  # 治愈
    china_data_dict['dead'] = i['dead']  # 死亡
# print(china_Add)
for j in china_Add:
    china_data_dict['confirmAdd'] = j['confirm']  # 新增确诊

data_set.append(china_data_dict)
world_data = pd.DataFrame(data_set)
world_data.to_csv('./assets/world_data_01.csv', encoding='utf-8')
# 替换成英文名称
world_name = pd.read_excel("./assets/zh2en.xlsx")
world_data = pd.merge(world_data, world_name, left_on=None, right_on=None, how="inner")
world_data.to_csv('./assets/world_data_02.csv', encoding='utf-8')
world_data = world_data[["name", "english", "confirm", "dead", "heal", "confirmAdd"]]
# 降序排列
world_data.sort_values(by='confirm', ascending=False, inplace=True)
world_data.to_csv('./assets/world_data_03.csv', encoding='utf-8')


########################################## 数据可视化 ############################################

################# 全球疫情地图 #################
world_map = (
    Map(
        # 初始化配置项 
        init_opts=opts.InitOpts(chart_id="chart_00", theme=ThemeType.DARK,width="100%",height="750px",bg_color="transparent"))
        # 添加数据
        .add("累计确诊", [list(z) for z in zip(list(world_data["english"]), list(world_data["confirm"]))], "world",
             is_map_symbol_show=False)
        .add("新增确诊", [list(z) for z in zip(list(world_data["english"]), list(world_data["confirmAdd"]))], "world",
             is_map_symbol_show=False)
        # 系列配置项
        .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
            toolbox_opts=opts.ToolboxOpts(orient='vertical', pos_right="10%"))
        # 全局配置项
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="全球疫情分布图",
                title_link='./results/world_map.html',
                title_target="blank",
                title_textstyle_opts = opts.TextStyleOpts(color='#52b1ff'),
                pos_left="center", #标题位置
                pos_top="5%"),
            visualmap_opts=opts.VisualMapOpts(
                is_piecewise=True,
                background_color="transparent",
                textstyle_opts=opts.TextStyleOpts(color="#52b1ff",font_size="12"),
                pieces=[
                        {"max": 99, "label": '<99'},
                        {"min": 100, "max": 999, "label": '100-999',},
                        {"min": 1000, "max": 9999, "label": '1000-9999'},
                        {"min": 10000, "max": 99999, "label": '10000-99999'},
                        {"min": 100000, "max": 999999, "label": '100000-999999'},
                        {"min": 1000000, "max": 9999999, "label": '1000000-999999'},
                        {"min": 10000000, "max": 99999999, "label": '10000000-9999999'},
                ])))
world_map.render('./results/world_map.html')   

################ 中国疫情地图 #################
china_area_map = (
    Map(
        # 初始化配置项
        init_opts=opts.InitOpts(chart_id="chart_01",theme=ThemeType.DARK, width="100%", height="750px", bg_color="transparent"))
        # 添加数据
        .add("累计数量", [list(z) for z in zip(list(china_area_data["province"]), list(china_area_data["confirm"]))], "china",
             is_map_symbol_show=False, label_opts=opts.LabelOpts(color="#fff"),
             tooltip_opts=opts.TooltipOpts(is_show=True))
        .add("新增数量", [list(z) for z in zip(list(china_area_data["province"]), list(china_area_data["add_confirm"]))], "china",
             is_map_symbol_show=False, label_opts=opts.LabelOpts(color="#fff"),
             tooltip_opts=opts.TooltipOpts(is_show=True))
        # 系列配置项
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        # 全局配置项
        .set_global_opts(title_opts=opts.TitleOpts(
            title="中国疫情分布图",
            title_link='./results/china_area_map.html',
            title_target="blank",
            pos_left="center",
            pos_top='5%',
            title_textstyle_opts=opts.TextStyleOpts(color="#52b1ff")),
            visualmap_opts=opts.VisualMapOpts(
                is_piecewise=True, pos_left=0, pos_bottom=0,
                textstyle_opts=opts.TextStyleOpts(
                    color="#52b1ff"),
                    pieces=[
                            {"max": 0, "label": '0'},
                            {"min": 1, "max": 5, "label": '1-5'},
                            {"min": 5, "max": 9, "label": '5-9'},
                            {"min": 10, "max": 49, "label": '10-49'},
                            {"min": 50, "max": 100, "label": '50-100'},
                            {"min": 100, "max": 999, "label": '100-999',},
                            {"min": 1000, "max": 4999, "label": '1000-4999'},
                            {"min": 5000, "max": 9999, "label": '5000-9999'},
                            {"min": 10000, "max": 49999, "label": '10000-49999'},
                            {"min": 50000, "max": 99999, "label": '50000-99999'},
                            {"min": 100000, "label": '>100000'},])))
china_area_map.render('./results/china_area_map.html')           

#################### 国内疫情总数饼图 ####################
total_pie = (
    Pie(
        # 初始化配置项
        init_opts=opts.InitOpts(chart_id="chart_02",theme=ThemeType.LIGHT, width='400px', height='400px', bg_color="transparent"))
        # 添加数据
        .add("", [list(z) for z in zip(chinaAdd.keys(), chinaAdd.values())], center=["50%", "50%"], radius=[0, 50])
        .add("", [list(z) for z in zip(['确     诊  ', '疑     似  ', '死     亡  ', '治     愈  '], chinaTotal.values())],
            center=["50%", "50%"], radius=[75, 100], )
        # 全局配置
        .set_global_opts(title_opts=opts.TitleOpts(
            title="全国总量",
            title_link='./results/china_total_pie.html',
            title_target="blank",
            title_textstyle_opts = opts.TextStyleOpts(color='#52b1ff'),
            pos_left="center", #标题位置
            pos_top="5%"),
            legend_opts=opts.LegendOpts(pos_bottom=0, textstyle_opts=opts.TextStyleOpts(color="#52b1ff")))
        # 系列配置
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}:{c}")))

total_pie.render('./results/china_total_pie.html')

################## 中国疫情分布热力图 #####################
city_data = china_area_data.groupby('city')['confirm'].sum().reset_index()
# print(city_data)
city_data.columns = ["city", "confirm"]

# 判断一个城市能否在pyechasts提供的地图中找到
def is_city(item):
    lists_1 = []
    # 添加城市
    lists_1.append(item)
    lists_2 = [20]
    geo = Geo()
    geo.add_schema(maptype="china")
    try:
        geo.add("确诊城市", [list(z) for z in zip(lists_1, lists_2)])
        return True
    except:
        return False


city_index = []
i = 0
for item in city_data['city']:
    if is_city(item) == False:
        city_index.append(i)
    i += 1

for x in city_index:
    del (city_data['city'][x])
    del (city_data['confirm'][x])

city_index_ = []
i = 0
for item in city_data['confirm']:
    if item > 1000:
        city_index_.append(i)
    i += 1

serious_city = []  # 严重城市
serious_submit = []  # 严重人数
for y in city_index_:
    serious_city.append(list(city_data['city'])[y])
    serious_submit.append(list(city_data['confirm'])[y])

list_1 = ["拉萨"]
list_2 = [1]

area_heat_geo = (
    Geo(
        # 初始化配置项
        init_opts=opts.InitOpts(chart_id="chart_03",theme=ThemeType.DARK, width="100%", height="750px",bg_color='transparent'))
        # 添加数据
        .add_schema(maptype="china")
        .add("确诊城市", [list(z) for z in zip(list(city_data["city"]), list(city_data["confirm"]))], symbol_size=10)
        .add("确诊城市", [list(z) for z in zip(list_1, list_2)], symbol_size=10)
        .add("确诊城市", [list(z) for z in zip(list(serious_city), list(serious_submit))],  # 感染者超1000的城市
             type_=ChartType.EFFECT_SCATTER, effect_opts=opts.EffectOpts(
                is_show=True, color="black",symbol_size=30, scale=4, period=1))
        .add("", [list(z) for z in zip(list(city_data["city"]), list(city_data["confirm"]))],
             type_=ChartType.HEATMAP)
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        # 全局配置项
        .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(range_size=[0, 25, 50, 75, 100], max_=1000, orient='horizontal',pos_bottom=0),
            title_opts=opts.TitleOpts(
                title="中国疫情分布热图",
                title_link='./results/china_area_heat_geo.html',
                title_target="blank",
                pos_left="center",
                pos_top='5%',
                title_textstyle_opts=opts.TextStyleOpts(color="#52b1ff")),
            legend_opts=opts.LegendOpts(pos_bottom='10%', pos_left=0)))

area_heat_geo.render('./results/china_area_heat_geo.html')

#################### 城市词云 #############################

wc = (
    WordCloud(init_opts=opts.InitOpts(chart_id="chart_04", theme=ThemeType.DARK, width="100%", height="750px",bg_color='transparent'))
    .add("", [list(z) for z in zip(list(city_data["city"]), list(city_data["confirm"]))], word_gap=0, word_size_range=[10, 30])
    .set_global_opts(title_opts=opts.TitleOpts(
        title="城市词云图",
        title_link='./results/china_city_wordcloud.html',
        title_target="blank",
        pos_left="center",
        pos_top='',
        title_textstyle_opts=opts.TextStyleOpts(color="#52b1ff"))
    )
)
wc.render('./results/china_city_wordcloud.html')


# wc = (
#     WordCloud(init_opts=opts.InitOpts(chart_id="chart_04", theme=ThemeType.DARK, width="100%", height="750px",bg_color='transparent'))
#     .add("", ,
#              word_gap=0, word_size_range=[10, 30]))
#     .set_global_opts(title_opts=opts.TitleOpts(title="WordCloud-自定义图片"))
# wc.render('./results/china_city_wordcloud.html')

################### 国内疫情总数条形图 #############################
china_province_bar = (
    Bar(init_opts=opts.InitOpts(chart_id="chart_05", theme=ThemeType.DARK, width="100%", height="750px",bg_color='transparent'))
    .add_xaxis(china_province_area_data["province"].tolist())
    .add_yaxis("累计确诊", china_province_area_data["province_total_confirm"].tolist())
    .set_global_opts(
        #图形标题的设置
        title_opts=opts.TitleOpts(
            title= "中国各省份累计新冠肺炎确诊病例",
            title_link='./results/china_province_bar.html',
            title_target="blank",
            title_textstyle_opts = opts.TextStyleOpts(color='#52b1ff'),
            pos_left="center", #标题位置
            pos_top=""),
        # tip 设置
        tooltip_opts=opts.TooltipOpts(
            is_show=True, 
            trigger="axis", 
            axis_pointer_type="shadow"),
        # 图例的设置
        legend_opts=opts.LegendOpts(is_show=False),
        # 视觉映射配置项
        visualmap_opts=opts.VisualMapOpts(is_show=False),
        # x轴坐标配置项
        xaxis_opts=opts.AxisOpts(name="省份",axislabel_opts={"interval":"0"}),
        # y轴配置项
        yaxis_opts=opts.AxisOpts(
            name="总计",min_=0,
            type_="value",axislabel_opts=opts.LabelOpts(formatter="{value} 人"),),
        # 区域缩放配置项
        datazoom_opts=opts.DataZoomOpts(range_start=0,range_end=30),
    )
)
china_province_bar.render('./results/china_province_bar.html')

####################### 全球疫情总数条形图 #############################
world_country_bar = (
    Bar(init_opts=opts.InitOpts(chart_id="chart_06", theme=ThemeType.DARK, width="100%", height="750px",bg_color='transparent'))
    .add_xaxis(world_data["name"].tolist())
    .add_yaxis("累计确诊", world_data["confirm"].tolist())
    .set_global_opts(
        #图形标题的设置
        title_opts=opts.TitleOpts(
            title= "全球各国累计新冠肺炎确诊病例",
            title_link='./results/world_country_bar.html',
            title_target="blank",
            title_textstyle_opts = opts.TextStyleOpts(color='#52b1ff'),
            pos_left="center", #标题位置
            pos_top="5%"),
         # 'shadow'：阴影指示器
        tooltip_opts=opts.TooltipOpts(
            is_show=True, 
            trigger="axis", 
            axis_pointer_type="shadow"),
        # 图例的设置
        legend_opts=opts.LegendOpts(is_show=False),
        # 视觉映射配置项
        visualmap_opts=opts.VisualMapOpts(is_show=False),
        # x轴坐标配置项
        xaxis_opts=opts.AxisOpts(name="国家",axislabel_opts={"interval":"0"}),
        # y轴配置项
        yaxis_opts=opts.AxisOpts(
            name="总计",min_=0,
            type_="value",axislabel_opts=opts.LabelOpts(formatter="{value} 人"),),
        # 区域缩放配置项
        datazoom_opts=opts.DataZoomOpts(range_start=0,range_end=10),
    )
)
world_country_bar.render('./results/world_country_bar.html')


####################### 国内疫情3D图 #############################
# 添加坐标
dicts_all = {'黑龙江': [127.9688, 45.368], '上海': [121.4648, 31.2891],
             '内蒙古': [110.3467, 41.4899], '吉林': [125.8154, 44.2584],
             '辽宁': [123.1238, 42.1216], '河北': [114.4995, 38.1006],
             '天津': [117.4219, 39.4189], '山西': [112.3352, 37.9413],
             '陕西': [109.1162, 34.2004], '甘肃': [103.5901, 36.3043],
             '宁夏': [106.3586, 38.1775], '青海': [101.4038, 36.8207],
             '新疆': [87.9236, 43.5883], '西藏': [91.11, 29.97],
             '四川': [103.9526, 30.7617], '重庆': [108.384366, 30.439702],
             '山东': [117.1582, 36.8701], '河南': [113.4668, 34.6234],
             '江苏': [118.8062, 31.9208], '安徽': [117.29, 32.0581],
             '湖北': [114.3896, 30.6628], '浙江': [119.5313, 29.8773],
             '福建': [119.4543, 25.9222], '江西': [116.0046, 28.6633],
             '湖南': [113.0823, 28.2568], '贵州': [106.6992, 26.7682],
             '广西': [108.479, 23.1152], '海南': [110.3893, 19.8516],
             '广东': [113.28064, 23.125177], '北京': [116.405289, 39.904987],
             '云南': [102.71225, 25.040609], '香港': [114.165460, 22.275340],
             '澳门': [113.549130, 22.198750], '台湾': [121.5200760, 25.0307240]}
for item in [list(z) for z in zip(china_province_area_data["province"], china_province_area_data["province_total_confirm"])]:
    dicts_all[item[0]].append(item[1])

china_3D_map = (
    Map3D(init_opts=opts.InitOpts(chart_id="chart_07",theme=ThemeType.DARK, width="100%", height="750px",bg_color='transparent'))
    .add_schema(
        itemstyle_opts=opts.ItemStyleOpts(
            color="rgb(5,101,123)",
            opacity=1,
            border_width=0.8,
            border_color="rgb(62,215,213)"),
        map3d_label=opts.Map3DLabelOpts(
            is_show=False,
            formatter=JsCode(
                "function(data){return data.name + " " + data.value[2];}")),
        emphasis_label_opts=opts.LabelOpts(
            is_show=False,
            color="#fff",
            font_size=10,
            background_color="rgba(0,23,11,0)"),
        light_opts=opts.Map3DLightOpts(
            main_color="#fff",
            main_intensity=1.2,
            main_shadow_quality="high",
            is_main_shadow=False,
            main_beta=10,
            ambient_intensity=0.3))
    .add(
        series_name="",
        data_pair=list(zip(list(dicts_all.keys()), list(dicts_all.values()))),
        type_=ChartType.BAR3D,
        bar_size=2,
        shading="realistic",
        label_opts=opts.LabelOpts(
            is_show=True,
            formatter=JsCode(
                "function(data){return data.name + ' ' + data.value[2];}")))
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title="全国疫情3D分布图",
            title_link='./results/china_3D_map.html',
            title_target="blank",
            title_textstyle_opts = opts.TextStyleOpts(color='#52b1ff'),
                                pos_left="center", #标题位置
                                pos_top="5%"),
        visualmap_opts=opts.VisualMapOpts(
            is_piecewise=True,
            background_color="transparent",
            textstyle_opts=opts.TextStyleOpts(color="#52b1ff",font_size="12"),
            pieces=[
                    {"max": 99, "label": '<99'},
                    {"min": 100, "max": 999, "label": '100-999',},
                    {"min": 1000, "max": 9999, "label": '1000-9999'},
                    {"min": 10000, "max": 99999, "label": '10000-99999'},
                    {"min": 100000, "max": 999999, "label": '100000-999999'},
                    {"min": 1000000, "max": 9999999, "label": '1000000-999999'},
                    {"min": 10000000, "max": 99999999, "label": '1000000-999999'},
            ])))
china_3D_map.render('./results/china_3D_map.html')

# 确诊、死亡、治愈柱状图
line_bar = (
    Line(
        init_opts=opts.InitOpts(chart_id="chart_08", theme=ThemeType.DARK, width="100%", height="750px",bg_color='transparent'))
        .add_xaxis(list(china_daylist["date"]))
        .add_yaxis("累计确诊", list(china_daylist["confirm"]), is_smooth=True, yaxis_index=1)
        .add_yaxis("累计死亡", list(china_daylist["dead"]), is_smooth=True, yaxis_index=1)
        .add_yaxis("累计治愈", list(china_daylist["heal"]), is_smooth=True, yaxis_index=1)
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(legend_opts=opts.LegendOpts(pos_left='center')
        )
    )

china_bar = (
    Bar(
        init_opts=opts.InitOpts(chart_id="chart_09", theme=ThemeType.DARK, width="100%", height="750px",bg_color='transparent'))
        .add_xaxis(list(china_daynewadd["date"]))
        .add_yaxis("单日确诊", list(china_daynewadd["confirm"]))
        .add_yaxis("单日死亡", list(china_daynewadd["dead"]))
        .add_yaxis("单日治愈", list(china_daynewadd["heal"]))
        .extend_axis(yaxis=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}")))
        .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="国内疫情增长趋势",
                title_link='./results/china_bar.html',
                title_target="blank",
                title_textstyle_opts = opts.TextStyleOpts(color='#52b1ff'),
                pos_left="center", #标题位置
                pos_top="0%"),
            legend_opts=opts.LegendOpts(pos_left='center',pos_top="10%"),
            yaxis_opts=opts.AxisOpts(axislabel_opts=opts.LabelOpts(formatter="{value}")),
            datazoom_opts=opts.DataZoomOpts())).overlap(line_bar)
china_bar.render('./results/china_bar.html')

# 新增确诊，本土确诊、新增疑似条形图
china_line =(
    Line(init_opts=opts.InitOpts(chart_id="chart_10", theme=ThemeType.DARK, width="100%", height="750px",bg_color='transparent'))
    .add_xaxis(list(china_daynewadd["date"].astype('str')))  #添加x轴
    .add_yaxis(series_name = "新增确诊",
                y_axis = list(china_daynewadd["confirm"]), #增加Y轴数据
                is_smooth=True,#添加Y轴，平滑曲线
                areastyle_opts=opts.AreaStyleOpts(opacity=0.3), #区域阴影透明度
                is_symbol_show = True,
                label_opts=opts.LabelOpts(is_show=False),
                yaxis_index = 0)
    .add_yaxis(series_name = "新增本土",
                y_axis = list(china_daynewadd["localinfectionadd"]),
                is_smooth=True,
                areastyle_opts=opts.AreaStyleOpts(opacity=0.3),
                is_symbol_show = True,#是否显示标记
                label_opts=opts.LabelOpts(is_show=False),
                yaxis_index = 1)
    #增加副轴
    .extend_axis(yaxis=opts.AxisOpts(
                        name="新增本土(人)",
                        name_location="end", #轴标题位置
                        type_="value",#轴类型
                        is_inverse=False, #逆序刻度值
                        axistick_opts=opts.AxisTickOpts(is_show=True),
                        splitline_opts=opts.SplitLineOpts(is_show=True)
                        )
                )
    .set_global_opts(
        title_opts=opts.TitleOpts(
            title="国内每日新增确诊趋势", 
            title_link='./results/china_line.html',
            title_target="blank",
            title_textstyle_opts = opts.TextStyleOpts(color='#52b1ff'),
            pos_left="center", 
            pos_top="0%"),
        legend_opts=opts.LegendOpts(pos_left="40%",pos_top='10%'), #图例位置-左侧
        xaxis_opts=opts.AxisOpts(type_="category",axislabel_opts=opts.AxisTickOpts()),
        yaxis_opts=opts.AxisOpts(name="新增确诊（人）", type_="value", ),
        datazoom_opts=opts.DataZoomOpts(type_= 'slider',
                                        range_start=80 ,#横轴开始百分百
                                        range_end=100) #横轴结束百分比
            )
)
china_line.render('./results/china_line.html')

# 主标题
big_title = (
    Pie(init_opts=opts.InitOpts(chart_id="chart_11", theme=ThemeType.DARK, width="100%", height="250px",bg_color='transparent'))
        .set_global_opts(
            title_opts=opts.TitleOpts(title="新冠疫情时空大数据可视化分析",
            title_link='https://www.sunguoqi.com',
            title_target="blank",
            title_textstyle_opts=opts.TextStyleOpts(font_size=40, color='#52b1ff',border_radius=True, border_color="white"),
            pos_top=0)))

# 更新时间
times = (
    Pie(init_opts=opts.InitOpts(chart_id="chart_12", theme=ThemeType.DARK, width="100%", height="250px",bg_color='transparent'))
        .set_global_opts(
            title_opts=opts.TitleOpts(subtitle=("截至 " + lastUpdateTime),
            subtitle_textstyle_opts=opts.TextStyleOpts(font_size=13, color='#52b1ff'),
            pos_top=0))
)

# ##################################### 拼接图表 ###########################################

page = Page(page_title="GIS开发组——安理地信",layout=Page.DraggablePageLayout)
page.add(
       world_map,
       china_bar,
       china_line,
       big_title,
       times,
       china_3D_map,
       world_country_bar,
       china_province_bar,
       area_heat_geo,
       total_pie,
       china_area_map,
       wc,
    )
page.render()

page.save_resize_html("render.html", cfg_file="chart_config.json", dest="index.html")

# 给文件添加黑色背景
def add_dark_bg(file):
    with open(file, "r+", encoding='utf-8') as f:
        old = f.read()
        f.seek(0)
        f.write("<style>body{background-color:#181a1b;}</style>\n")
        f.write(old)
        f.close()

# 单个图表批量添加
files= os.listdir("./results") 
for file in files: #遍历文件夹
    file = os.path.join("./results", file) #将文件夹与文件名合成一个路径
    add_dark_bg(file)
# 给大屏添加黑色背景
add_dark_bg("./index.html")
print("生成成功！")