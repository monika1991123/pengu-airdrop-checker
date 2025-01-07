from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def test_chrome_setup():
    print("开始测试 Chrome 设置...")
    try:
        print("1. 创建 Chrome 选项...")
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        
        print("2. 安装 Chrome 驱动...")
        driver = webdriver.Chrome(
            options=chrome_options
        )
        
        print("3. 访问测试页面...")
        driver.get("https://www.google.com")
        
        print("4. 获取页面标题...")
        print(f"页面标题: {driver.title}")
        
        print("5. 关闭浏览器...")
        driver.quit()
        
        print("测试成功完成！")
        
    except Exception as e:
        print(f"测试过程中出错: {str(e)}")
        print("错误详细信息:")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    test_chrome_setup() 