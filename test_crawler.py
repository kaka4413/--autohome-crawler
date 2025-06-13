from car_crawler import AutoHomeCrawler
import pandas as pd

def test_volkswagen():
    """测试大众品牌数据爬取"""
    crawler = AutoHomeCrawler()
    
    # 大众品牌ID为1
    brand_id = "1"
    brand_name = "大众"
    
    print(f"\n开始爬取{brand_name}品牌数据...")
    
    # 获取车系数据
    series_data = crawler.get_series(brand_id, brand_name)
    
    # 保存数据到Excel
    output_file = f"{brand_name}_car_data.xlsx"
    crawler.save_to_excel(series_data, output_file)
    
    # 分析数据
    df = pd.DataFrame(series_data)
    
    # 统计能源类型分布
    print("\n能源类型统计:")
    energy_stats = df['energy_type'].value_counts()
    print(energy_stats)
    
    # 打印详细信息
    print("\n详细数据:")
    for _, row in df.iterrows():
        print(f"{row['name']}: {row['energy_type']}")

if __name__ == "__main__":
    test_volkswagen() 