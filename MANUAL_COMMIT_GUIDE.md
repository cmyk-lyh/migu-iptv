# 手动提交指南

## 当前状态
由于系统权限限制，无法直接执行 git 命令。请按照以下步骤手动提交到 GitHub。

## 提交步骤

### 1. 初始化 git 仓库（如果还没有）
```bash
git init
git add .
git commit -m "Initial commit: M3U 自动更新工具"
git branch -M main
git remote add origin <你的GitHub仓库地址>
git push -u origin main
```

### 2. 添加所有文件
```bash
git add .
```

### 3. 提交更改
```bash
git commit -m "feat: 添加 M3U 自动更新功能

- 添加 GitHub Actions 自动更新配置
- 添加本地自动化更新脚本
- 添加卫星、动漫、电影频道
- 实现定时自动更新功能
- 支持 manual 和定时触发方式
- 添加详细的使用文档

Co-authored-by: M3U Updater <action@github.com>"
```

### 4. 推送到 GitHub
```bash
git push origin main
```

## 文件清单

需要提交的文件：
```
├── .github/
│   └── workflows/
│       └── m3u-updater.yml          # GitHub Actions 配置
├── auto_update_m3u.py              # 本地更新脚本
├── channels.m3u                    # 原始播放列表
├── enhanced_channels.m3u          # 增强版播放列表
├── README.md                       # 项目说明
├── setup_automation.md             # 详细设置指南
├── analyze_channels.py             # 分析脚本
├── analyze_channels_fixed.py       # 修复版分析脚本
├── process_m3u.py                  # M3U 处理脚本
└── commit_and_push.sh              # 提交脚本（可选）
```

## GitHub Actions 配置说明

### 自动更新特点
- **执行时间**: 每天 UTC 2:00 (北京时间 10:00)
- **触发方式**: 定时 + 手动
- **更新源**: iptv-org 仓库
- **过滤目标**: 卫视、央视、动漫、电影等

### 使用方法
1. 提交后等待 Actions 自动运行
2. 或在 GitHub Actions 页面手动触发
3. 下载生成的 enhanced_channels_*.m3u 文件

## 后续使用

### 自动更新
无需任何操作，系统会自动：
1. 每天获取最新 IPTV 数据
2. 过滤和合并频道
3. 生成新的 M3U 文件
4. 自动提交和推送

### 手动更新
如需手动触发更新：
1. 访问 GitHub 仓库
2. 点击 Actions 标签
3. 点击 "M3U 自动更新"
4. 点击 "Run workflow"

## 故障排除

### 常见问题
1. **Actions 失败**: 检查仓库权限设置
2. **网络超时**: iptv-org 服务器暂时不可用
3. **文件冲突**: 手动前先拉取最新代码

### 解决方案
1. 等待下次定时执行
2. 检查网络连接
3. 手动触发前执行 `git pull`
