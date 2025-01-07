from main import process_wallets

def main():
    print("开始查询钱包空投资格...")
    
    # 配置文件路径
    input_file = "wallets.csv"    # 输入的钱包地址文件
    output_file = "results.csv"   # 结果输出文件
    
    # 如果要重新处理所有地址，删除或重命名之前的结果文件
    import os
    if os.path.exists(output_file):
        backup_file = "results_backup.csv"
        print(f"发现已存在的结果文件，备份为: {backup_file}")
        if os.path.exists(backup_file):
            os.remove(backup_file)
        os.rename(output_file, backup_file)
    
    try:
        # 减小批次大小
        process_wallets(
            input_file=input_file,
            output_file=output_file,
            batch_size=3  # 每批只处理3个地址
        )
    except Exception as e:
        print(f"运行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 