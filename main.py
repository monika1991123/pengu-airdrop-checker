import pandas as pd
import time
import json
import random
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

def get_random_delay():
    base_delay = random.uniform(2, 5)
    if random.random() < 0.1:
        base_delay += random.uniform(3, 7)
    return base_delay

def setup_driver(proxy=None):
    try:
        print("正在配置 Chrome 驱动...")
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        # 添加反爬虫选项
        ua = UserAgent()
        chrome_options.add_argument(f'user-agent={ua.random}')
        
        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')
        
        # 使用 webdriver_manager 自动管理 ChromeDriver
        from selenium.webdriver.chrome.service import Service as ChromeService
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("正在安装并配置 ChromeDriver...")
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        return driver
        
    except Exception as e:
        print(f"设置驱动程序时出错: {str(e)}")
        print("正在尝试其他配置方式...")
        try:
            # 备选方案：使用简化配置
            driver = webdriver.Chrome(options=chrome_options)
            return driver
        except Exception as e2:
            print(f"备选方案也失败: {str(e2)}")
            raise

def check_wallet_eligibility(driver, wallet_address, max_retries=5):
    url = f"https://api.clusters.xyz/v0.1/airdrops/pengu/eligibility/{wallet_address}"
    
    print(f"\n正在检查钱包地址: {wallet_address}")
    print(f"访问 URL: {url}")
    
    retries = 0
    while retries < max_retries:
        try:
            # 增加页面加载超时时间
            driver.set_page_load_timeout(30)
            driver.set_script_timeout(30)
            
            print("正在加载页面...")
            driver.get(url)
            
            # 增加等待时间
            time.sleep(random.uniform(3, 5))
            
            try:
                print("等待页面元素加载...")
                # 增加等待时间到30秒
                pre_element = WebDriverWait(driver, 30).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'pre'))
                )
                
                # 添加更多调试信息
                print("检查页面状态...")
                if "error" in driver.page_source.lower():
                    print("页面可能包含错误信息")
                
            except Exception as wait_error:
                print(f"等待元素超时: {wait_error}")
                print("页面源代码:")
                print(driver.page_source[:1000])  # 打印更多页面内容
                raise
            
            time.sleep(random.uniform(2, 3))
            response_text = pre_element.text
            print(f"获取到的响应: {response_text[:200]}")
            
            try:
                data = json.loads(response_text)
                print(f"解析的数据: {data}")
            except json.JSONDecodeError as json_error:
                print(f"JSON解析错误: {json_error}")
                print(f"原始响应文本: {response_text}")
                raise
            
            result = {
                'wallet_address': wallet_address,
                'total': int(data.get('total', 0)),
                'total_unclaimed': int(data.get('totalUnclaimed', 0))
            }
            print(f"处理结果: {result}")
            return result
            
        except Exception as e:
            print(f"第 {retries + 1} 次尝试失败")
            print(f"错误详情: {str(e)}")
            retries += 1
            
            if retries < max_retries:
                # 增加重试等待时间
                delay = (2 ** retries) + random.uniform(3, 8)
                print(f"等待 {delay:.1f} 秒后重试...")
                time.sleep(delay)
                
                # 在重试前重新启动浏览器
                if retries % 2 == 0:  # 每两次重试重启一次浏览器
                    print("重新启动浏览器...")
                    driver.quit()
                    driver = setup_driver()
            else:
                print(f"达到最大重试次数，钱包地址 {wallet_address} 检查失败")
    
    return {
        'wallet_address': wallet_address,
        'total': 0,
        'total_unclaimed': 0,
        'error': 'Max retries exceeded'
    }

def save_result(result, output_file):
    """Save single result to CSV file"""
    df = pd.DataFrame([result])
    
    if Path(output_file).exists():
        df.to_csv(output_file, mode='a', header=False, index=False)
    else:
        df.to_csv(output_file, index=False)

def get_processed_wallets(output_file):
    """Get list of already processed wallets"""
    if Path(output_file).exists():
        try:
            df = pd.read_csv(output_file)
            return set(df['wallet_address'].values)
        except Exception as e:
            print(f"Error reading existing results file: {e}")
    return set()

def process_wallets(input_file, output_file, proxies=None, batch_size=50):
    print("\n=== 程序开始运行 ===")
    print(f"当前工作目录: {Path.cwd()}")
    print(f"输入文件: {input_file}")
    print(f"输出文件: {output_file}")
    
    # 检查输入文件是否存在
    if not Path(input_file).exists():
        print(f"错误: 输入文件 {input_file} 不存在!")
        return
        
    # 读取并验证输入文件
    try:
        wallets_df = pd.read_csv(input_file, header=None, names=['wallet_address'])
        print(f"成功读取到 {len(wallets_df)} 个钱包地址")
        print("前5个钱包地址示例:")
        print(wallets_df.head())
    except Exception as e:
        print(f"读取输入文件时出错: {e}")
        return
    
    all_wallets = set(wallets_df['wallet_address'].values)
    
    # Get already processed wallets
    processed_wallets = get_processed_wallets(output_file)
    wallets_to_process = list(all_wallets - processed_wallets)
    
    if not wallets_to_process:
        print("All wallets have been already processed!")
        return
    
    print(f"Found {len(processed_wallets)} already processed wallets")
    print(f"Remaining wallets to process: {len(wallets_to_process)}")
    
    total_wallets = len(wallets_to_process)
    total_airdrop = 0
    
    # Process in batches
    for batch_start in range(0, total_wallets, batch_size):
        batch_end = min(batch_start + batch_size, total_wallets)
        batch_wallets = wallets_to_process[batch_start:batch_end]
        
        print(f"\nProcessing batch {batch_start//batch_size + 1}")
        
        driver = setup_driver()
        
        try:
            for index, wallet in enumerate(batch_wallets, 1):
                print(f"Processing wallet {batch_start + index}/{total_wallets}: {wallet}")
                
                result = check_wallet_eligibility(driver, wallet)
                total_airdrop += result['total']
                
                # Save result immediately after processing each wallet
                save_result(result, output_file)
                print(f"Saved result for wallet: {wallet}")
                
                time.sleep(get_random_delay())
                
        finally:
            driver.quit()
        
        # Delay between batches
        batch_delay = random.uniform(10, 20)
        print(f"Batch completed. Waiting {batch_delay:.1f} seconds before next batch...")
        time.sleep(batch_delay)
    
    print(f"\nAll results saved to {output_file}")
    print(f"Total airdrop amount for this session: {total_airdrop}")

if __name__ == "__main__":
    input_file = "wallets.csv"
    output_file = "results.csv"
    
    if not Path(input_file).exists():
        print(f"Error: Input file {input_file} not found")
        exit(1)
    
    process_wallets(input_file, output_file)