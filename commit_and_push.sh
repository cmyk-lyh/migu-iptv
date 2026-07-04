#!/bin/bash

echo "=== M3U 播放列表自动更新工具 - 提交脚本 ==="
echo

# 检查 git 状态
echo "检查 Git 状态..."
git status

echo
echo "请按以下步骤手动提交："
echo

echo "步骤 1: 添加所有文件到暂存区"
echo "git add ."

echo
echo "步骤 2: 提交更改"
echo "git commit -m \"feat: 添加 M3U 自动更新功能

- 添加 GitHub Actions 自动更新配置
- 添加本地自动化更新脚本
- 添加卫星、动漫、电影频道
- 实现定时自动更新功能
- 支持 manual 和定时触发方式
- 添加详细的使用文档\""

echo
echo "步骤 3: 推送到远程仓库"
echo "git push origin main"

echo
echo "步骤 4: 查看结果"
echo "- 浏览器打开 GitHub 仓库"
echo "- 查看 Actions 页面确认工作流正常"
echo "- 下载生成的 enhanced_channels_*.m3u 文件"

echo
echo "=== 文件说明 ==="
echo "新增的主要文件："
echo "- .github/workflows/m3u-updater.yml  # GitHub Actions 配置"
echo "- auto_update_m3u.py                   # 本地更新脚本"
echo "- enhanced_channels.m3u               # 增强版播放列表"
echo "- README.md                          # 项目说明"
echo "- setup_automation.md                # 详细设置指南"

echo
echo "=== GitHub Actions 使用说明 ==="
echo "1. 提交后，访问您的 GitHub 仓库"
echo "2. 点击 Actions 标签页"
echo "3. 点击 'M3U 自动更新' 工作流"
echo "4. 可以手动触发或等待定时执行（每天 UTC 2:00）"
echo "5. 查看执行日志确认更新成功"

echo
echo "=== 注意事项 ==="
echo "- 确保已配置正确的远程仓库地址"
echo "- 第一次提交后等待几分钟 Actions 会自动运行"
echo "- 如果 Actions 失败，检查仓库 Secrets 设置"
echo "- 生成的 M3U 文件会作为构建产物自动上传"
