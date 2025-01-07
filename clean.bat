@echo off
echo 正在备份旧的结果文件...
if exist results.csv (
    if exist results_backup.csv del results_backup.csv
    ren results.csv results_backup.csv
)
echo 开始新的查询...
python test.py
pause 