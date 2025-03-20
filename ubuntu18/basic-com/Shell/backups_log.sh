#!/bin/bash

set -e  # 如果任何命令失败，脚本会停止执行

# 定义日志路径
sys_log_path="/var/log"
server_log_path="/root/auborobotstudio/robotstudio/service/bin/logfiles"
client_log_path="/root/auborobotstudio/robotstudio/teachpendant/bin/logfiles"
agv_plugin_log_path="/root/auborobotstudio/robotstudio/teachpendant/bin/agv_plugin_logs"
server_backtrace_file="/root/auborobotstudio/robotstudio/service/bin/backtrace_server"
aubope_backtrace_file="/root/auborobotstudio/robotstudio/teachpendant/bin/backtrace_aubope"

# 临时目录和输出文件
log_export_dir="/root/log_export_dir"
backup_dir="/root/backups"
log_backup_file="log_backup_$(date +%Y%m%d%H%M%S).tar.gz"

# 创建备份目录和临时目录
mkdir -p "$backup_dir"
mkdir -p "$log_export_dir"

echo "开始导出日志..."

# 检查并复制日志文件，如果文件夹为空或文件不存在，则跳过
function check_and_copy() {
    local src=$1
    local dest=$2
    if [ -d "$src" ] && [ "$(ls -A "$src")" ]; then
        # 使用 rsync 只复制变化的文件，避免不必要的覆盖
        rsync -av --ignore-existing "$src" "$dest"
        echo "已复制日志目录: $src"
    elif [ -f "$src" ]; then
        # 如果是单个文件，使用 rsync
        rsync -av --ignore-existing "$src" "$dest"
        echo "已复制文件: $src"
    else
        echo "警告：源文件或目录不存在或为空，跳过：$src"
    fi
}

# 复制日志文件
check_and_copy "$server_log_path" "$log_export_dir"
check_and_copy "$client_log_path" "$log_export_dir"
check_and_copy "$agv_plugin_log_path" "$log_export_dir"
check_and_copy "$server_backtrace_file" "$log_export_dir"
check_and_copy "$aubope_backtrace_file" "$log_export_dir"

# 直接使用 tar 创建压缩包
echo "创建压缩包..."
tar -czf "$backup_dir/$log_backup_file" -C "$log_export_dir" .

# 检查 tar 创建是否成功
if [ $? -eq 0 ]; then
    echo "日志导出成功，文件保存在：$backup_dir/$log_backup_file"
else
    echo "错误：创建 tar 包失败。"
    exit 1
fi

# 删除临时文件
echo "删除临时文件..."
rm -rf "$log_export_dir"

# 清理缓存文件，确保没有残留的临时文件或缓存
echo "清理缓存文件..."
sync  # 确保所有的更改已经写入磁盘

# 确保系统缓存也被清除
echo 3 > /proc/sys/vm/drop_caches

echo "脚本执行完成。"
exit 0