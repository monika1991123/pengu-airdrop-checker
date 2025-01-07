import pandas as pd

def check_results():
    try:
        results = pd.read_csv('results.csv')
        print("\n=== 查询结果统计 ===")
        print(f"总计查询钱包数：{len(results)}")
        print("\n符合条件的钱包：")
        eligible = results[results['total'] > 0]
        print(f"数量：{len(eligible)}")
        if not eligible.empty:
            print("\n符合条件的钱包地址：")
            for _, row in eligible.iterrows():
                print(f"地址: {row['wallet_address']}, 数量: {row['total']}")
    except FileNotFoundError:
        print("还没有生成结果文件")
    except Exception as e:
        print(f"检查结果时出错：{e}")

if __name__ == "__main__":
    check_results() 