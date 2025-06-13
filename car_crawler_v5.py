import requests
import json
import time
import random
import pandas as pd
import re
import traceback
import argparse
from datetime import datetime
from bs4 import BeautifulSoup

class CarCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 能源类型映射
        self.fuel_type_map = {
            4: "纯电动",
            3: "插电混动",
            2: "增程式",
            1: "汽油",
            5: "柴油",
            6: "油电混合",
            7: "氢燃料"
        }
        
        # 初始化数据存储
        self.all_data = []
        self.processed_brands = set()
        
    def get_fuel_type_url(self, fuel_type_id):
        """获取指定能源类型的URL"""
        return f'https://www.autohome.com.cn/price/fueltypedetail_{fuel_type_id}'
        
    def get_brands(self):
        """获取品牌列表"""
        print("正在获取品牌列表...")
        
        url = 'https://car.autohome.com.cn/javascript/NewSpecCompare.js'
        
        try:
            response = requests.get(url, headers=self.headers)
            print(f"Response status code: {response.status_code}")
            
            if response.status_code == 200:
                # 从JavaScript文件中提取JSON数据
                json_str = re.search(r'var listCompare\$100\s*=\s*(\[.*?\]);', response.text, re.DOTALL)
                if not json_str:
                    print("未找到品牌数据")
                    return None
                    
                data = json.loads(json_str.group(1))
                brands = []
                
                # 解析品牌数据
                for brand in data:
                    try:
                        brand_info = {
                            'id': brand['I'],
                            'name': brand['N'].strip()
                        }
                        brands.append(brand_info)
                        print(f"成功解析品牌: {brand_info['name']} (ID: {brand_info['id']})")
                    except Exception as e:
                        print(f"解析品牌数据失败: {str(e)}")
                        continue
                
                return brands
            else:
                print(f"获取品牌列表失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"获取品牌列表时发生错误: {str(e)}")
            print(f"错误详情: {traceback.format_exc()}")
            return None
            
    def get_series_by_brand(self, brand_id, brand_name, status=1):
        """获取品牌下的车系列表
        
        Args:
            brand_id: 品牌ID
            brand_name: 品牌名称
            status: 销售状态 (1: 停售, 2: 在售)
        """
        status_text = "在售" if status == 2 else "停售"
        series_list = []
        processed_series_ids = set()  # 用于去重的集合
        page = 1
        max_pages = 10  # 最大页数限制，避免无限循环
        
        while page <= max_pages:
            try:
                print(f"正在获取品牌ID {brand_id} ({brand_name}) 的{status_text}车系列表（第 {page} 页）...")
                
                # 构建API URL，确保URL中包含正确的页码
                url = f'https://www.autohome.com.cn/_next/data/nextweb-prod-c_1.0.160-p_1.50.0/cars/brand-{brand_id}-x-{status}-x-x-{page}.html.json'
                
                # 构建查询参数
                params = {
                    'brandId': str(brand_id),
                    'factoryId': 'x',
                    'sellingId': str(status),
                    'energyId': 'x',
                    'sortId': 'x',
                    'pageIdx': str(page)
                }
                
                response = requests.get(url, params=params, headers=self.headers)
                print(f"请求URL: {response.url}")
                
                # 检查是否重定向（可能表示状态改变）
                if 'brand-' in response.url and f'-{status}-' not in response.url:
                    actual_url = response.url
                    print(f"页面重定向到: {actual_url}")
                    # 从URL中提取实际的销售状态
                    try:
                        actual_status = int(actual_url.split('-')[3])
                        if actual_status != status:
                            print(f"销售状态从 {status} 更新为 {actual_status}")
                            print(f"品牌 {brand_name} 在当前状态下没有车系")
                            return []
                    except:
                        print("无法从重定向URL中提取销售状态")
                        return []
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 检查是否有重定向
                    if data.get('pageProps', {}).get('__N_REDIRECT'):
                        redirect_url = data['pageProps']['__N_REDIRECT']
                        print(f"页面重定向到: {redirect_url}")
                        return []
                    
                    # 获取总数和每页数量
                    page_props = data.get('pageProps', {})
                    if 'seriesList' not in page_props:
                        print("返回数据格式错误，缺少seriesList")
                        break
                    
                    series_list_data = page_props.get('seriesList', {}).get('fctinfo', [])
                    total = page_props.get('seriesList', {}).get('total', 0)
                    size = page_props.get('seriesList', {}).get('size', 15)
                    print(f"总数: {total}, 每页数量: {size}, 当前页: {page}")
                    
                    # 解析车系数据
                    for factory in series_list_data:
                        factory_name = factory.get('name', '')
                        for series in factory.get('seriesgrouplist', []):
                            # 检查是否已处理过该车系
                            series_id = series.get('seriesid')
                            if series_id and series_id not in processed_series_ids:
                                series_info = {
                                    'brand_id': brand_id,
                                    'brand_name': brand_name,
                                    'factory_name': factory_name,
                                    'series_id': series_id,
                                    'series_name': series.get('seriesname', ''),
                                    'price_range': f"{series.get('seriesminprice', '')}-{series.get('seriesmaxprice', '')}",
                                    'level': series.get('levelname', ''),
                                    'status': status_text
                                }
                                series_list.append(series_info)
                                processed_series_ids.add(series_id)
                                print(f"成功解析车系: {series_info['series_name']} (ID: {series_id}) - {status_text}")
                    
                    # 检查是否还有下一页
                    if page * size >= total:
                        print("已到达最后一页")
                        break
                    
                    # 准备获取下一页
                    page += 1
                    wait_time = random.uniform(1, 3)
                    print(f"等待 {wait_time:.2f} 秒后获取下一页...")
                    time.sleep(wait_time)
                else:
                    print(f"获取车系列表失败，状态码: {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"获取车系列表时发生错误: {str(e)}")
                print(f"错误详情: {traceback.format_exc()}")
                break
                
        print(f"品牌 {brand_name} 在当前状态下总共获取到 {len(series_list)} 个车系\n")
        return series_list
        
    def get_fuel_type_data(self, series_info):
        """获取车系的能源类型数据
        
        直接搜索具体的能源类型字样
        """
        series_id = series_info['series_id']
        
        # 定义所有可能的能源类型
        ENERGY_TYPES = [
            "纯电动",
            "插电式混合动力",
            "增程式",
            "汽油",
            "柴油",
            "油电混合",
            "天然气",
            "汽油电驱",
            "甲醇",
            "氢燃料",
            "48V轻混系统汽油",
            "24V轻混系统"
        ]
        
        try:
            # 使用API获取配置数据
            api_url = 'https://car-web-api.autohome.com.cn/car/param/getParamConf'
            params = {
                'mode': '1',
                'site': '1',
                'seriesid': str(series_id)
            }
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Origin': 'https://www.autohome.com.cn',
                'Referer': 'https://www.autohome.com.cn/'
            }
            
            print(f"\n获取车型配置数据: {api_url}")
            response = requests.get(api_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['returncode'] == 0:
                    # 将整个响应转换为字符串以便搜索
                    response_text = json.dumps(data, ensure_ascii=False)
                    
                    # 搜索所有能源类型
                    found_types = []
                    for energy_type in ENERGY_TYPES:
                        if energy_type in response_text:
                            found_types.append(energy_type)
                            print(f"找到能源类型: {energy_type}")
                    
                    if found_types:
                        return found_types
            
            print(f"未能获取到能源类型数据")
            return ["未知"]
            
        except Exception as e:
            print(f"获取能源类型数据时出错: {str(e)}")
            return ["未知"]
        
    def process_brand(self, brand):
        """处理单个品牌的数据"""
        brand_id = brand['id']
        brand_name = brand['name']
        
        # 获取在售车系
        on_sale_series = self.get_series_by_brand(brand_id, brand_name, status=2)
        
        # 获取停售车系
        discontinued_series = self.get_series_by_brand(brand_id, brand_name, status=1)
        
        # 合并所有车系数据
        all_series = on_sale_series + discontinued_series
        
        # 获取每个车系的能源类型
        for series in all_series:
            series['fuel_types'] = self.get_fuel_type_data(series)
            self.all_data.append(series)
            
        self.processed_brands.add(brand_id)
        
    def save_data(self, test_mode=False):
        """保存数据到Excel文件"""
        if not self.all_data:
            print("没有数据需要保存")
            return
            
        # 转换为DataFrame
        df = pd.DataFrame(self.all_data)
        
        # 数据去重
        df_dedup = df.drop_duplicates(subset=['series_id'], keep='first')
        
        # 统计信息
        total_before = len(df)
        total_after = len(df_dedup)
        on_sale_count = len(df_dedup[df_dedup['status'] == '在售'])
        discontinued_count = len(df_dedup[df_dedup['status'] == '停售'])
        
        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'car_data_{timestamp}.xlsx'
        
        # 保存数据
        df_dedup.to_excel(filename, index=False)
        
        print("\n数据去重结果:")
        print(f"去重前记录数: {total_before}")
        print(f"去重后记录数: {total_after}")
        print(f"数据已保存到文件: {filename}\n")
        
        print("各状态车型数量:")
        print(f"在售: {on_sale_count}个")
        print(f"停售: {discontinued_count}个\n")
        
        # 统计各能源类型的车型数量
        print("各能源类型车型数量:")
        fuel_type_counts = {}
        for series in self.all_data:
            for fuel_type in series['fuel_types']:
                fuel_type_counts[fuel_type] = fuel_type_counts.get(fuel_type, 0) + 1
        
        for fuel_type, count in fuel_type_counts.items():
            print(f"{fuel_type}: {count}个")
        
    def run(self, test_mode=False, specific_brand=None, resume_brand=None):
        """运行爬虫"""
        # 获取品牌列表
        brands = self.get_brands()
        if not brands:
            return
            
        total_brands = len(brands)
        processed_count = 0
        errors = 0
        
        # 根据参数确定要处理的品牌
        if specific_brand:
            # 修改为支持通过ID或名称查找品牌
            try:
                brand_id = int(specific_brand)
                brands = [b for b in brands if b['id'] == brand_id]
            except ValueError:
                brands = [b for b in brands if b['name'] == specific_brand]
                
            if not brands:
                print(f"未找到品牌: {specific_brand}")
                return
                
        if resume_brand:
            start_index = next((i for i, b in enumerate(brands) if b['name'] == resume_brand), None)
            if start_index is None:
                print(f"未找到品牌: {resume_brand}")
                return
            brands = brands[start_index:]
            
        if test_mode:
            brands = brands[:15]
            
        # 处理每个品牌
        for brand in brands:
            processed_count += 1
            print(f"\n正在处理第 {processed_count}/{total_brands} 个品牌: {brand['name']}")
            
            try:
                self.process_brand(brand)
            except Exception as e:
                print(f"处理品牌 {brand['name']} 时发生错误: {str(e)}")
                print(f"错误详情: {traceback.format_exc()}")
                errors += 1
                
            # 每处理30个品牌保存一次数据
            if processed_count % 30 == 0:
                print(f"\n已处理 {processed_count} 个品牌，保存阶段性数据...")
                self.save_data(test_mode)
                
        # 保存最终数据
        print("\n所有品牌处理完成，保存最终数据...")
        self.save_data(test_mode)
        
        # 输出统计信息
        print("\n爬虫统计信息:")
        print(f"总品牌数: {total_brands}")
        print(f"已处理品牌数: {processed_count}")
        print(f"在售车系数: {len([s for s in self.all_data if s['status'] == '在售'])}")
        print(f"停售车系数: {len([s for s in self.all_data if s['status'] == '停售'])}")
        print(f"总车系数: {len(self.all_data)}")
        print(f"错误数: {errors}")

def main():
    parser = argparse.ArgumentParser(description='汽车之家车型数据爬虫')
    parser.add_argument('--test', action='store_true', help='测试模式（只爬取前15个品牌）')
    parser.add_argument('--brand', type=str, help='爬取指定品牌')
    parser.add_argument('--resume', type=str, help='从指定品牌继续爬取')
    parser.add_argument('--series', type=str, help='测试指定车系ID的能源类型')
    
    args = parser.parse_args()
    
    crawler = CarCrawler()
    
    if args.series:
        # 测试单个车系
        series_info = {
            'series_id': args.series,
            'series_name': f'测试车系 {args.series}'
        }
        fuel_types = crawler.get_fuel_type_data(series_info)
        print(f"\n车系 {args.series} 的能源类型: {', '.join(fuel_types)}")
    else:
        # 正常爬取流程
        crawler.run(test_mode=args.test, specific_brand=args.brand, resume_brand=args.resume)

if __name__ == '__main__':
    main() 