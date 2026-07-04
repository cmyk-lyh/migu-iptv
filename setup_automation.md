# M3U 自动化设置指南

## 概述

现在这个项目已经支持 GitHub Actions 自动定时更新，无需手动操作。

## 自动更新配置

### 1. GitHub Actions 定时执行
- **执行时间**: 每天凌晨2点 (UTC时间，北京时间上午10点)
- **触发方式**: 自动定时 + 手动触发
- **更新内容**: 从 iptv-org 仓库获取最新频道数据

### 2. 自动化流程
```
1. 检出代码
2. 设置 Python 环境
3. 下载最新 IPTV 数据
4. 解析并过滤频道
5. 合并新旧频道
6. 生成增强版 M3U
7. 提交并推送更改
8. 上传更新文件
```

### 3. 手动触发方法
在 GitHub 仓库的 Actions 页面：
- 点击 "M3U 自动更新"
- 点击 "Run workflow"
- 可以填写更新原因（可选）
- 点击 "Run workflow" 开始执行

## 文件结构

```
.
├── channels.m3u                    # 您的原始文件
├── enhanced_channels_*.m3u          # 自动生成的增强版
├── .github/
│   └── workflows/
│       └── m3u-updater.yml        # GitHub Actions 配置
├── auto_update_m3u.py            # 本地更新脚本
├── README.md                     # 项目说明
└── setup_automation.md            # 本文档
```

## 使用方法

### 方法一：完全自动化（推荐）
1. 将代码推送到 GitHub
2. 等待定时执行或手动触发
3. 在 Actions 页面查看执行状态
4. 下载生成的增强版 M3U 文件

### 方法二：本地手动更新
```bash
# 克隆仓库
git clone <your-repo-url>
cd m3u-subscription

# 运行本地脚本
python3 auto_update_m3u.py
```

## 输出结果

### 自动生成的文件命名规则
- 格式：`enhanced_channels_YYYYMMDD_HHMMSS.m3u`
- 示例：`enhanced_channels_20240101_120000.m3u`
- 包含更新时间和频道统计信息

### 更新内容
- ✅ 保留您现有的所有频道
- ✅ 新增缺失的卫视频道
- ✅ 添加动漫相关频道
- ✅ 添加电影频道
- ✅ 添加其他目标类型频道

## 监控和日志

### GitHub Actions 日志
在 Actions 页面可以查看：
- 执行状态（成功/失败）
- 详细的执行日志
- 错误信息（如果有）

### 更新通知
- 每次更新都会自动提交代码
- 可以设置仓库 Webhook 通知
- 邮件通知（如需要）

## 自定义配置

### 修改更新时间
编辑 `.github/workflows/m3u-updater.yml` 中的 cron 表达式：
```yaml
schedule:
  - cron: '0 2 * * *'  # 当前是每天2点
```

### 添加新的频道类型
修改脚本中的 `target_groups` 列表。

## 故障排除

### 常见问题
1. **网络超时**: iptv-org 服务器暂时不可用
2. **权限问题**: GitHub token 权限不足
3. **文件冲突**: 并发更新时的冲突

### 解决方案
1. 等待下一次定时执行
2. 检查 GitHub Actions 权限设置
3. 手动触发前先拉取最新代码

## 联系和支持

如果遇到问题，请：
1. 查看 GitHub Actions 日志
2. 检查网络连接
3. 尝试手动触发
4. 查看 README.md 获取更多帮助
