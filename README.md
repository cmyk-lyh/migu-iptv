# M3U 播放列表自动更新工具

这个项目用于自动更新和管理 M3U 播放列表文件。

## 功能特点

- 自动从 iptv-org 仓库获取最新的中文频道数据
- 智能过滤目标频道类型（卫视、央视、动漫、电影等）
- 自动合并现有频道和新频道
- 生成带时间戳的增强版 M3U 文件
- 支持定时自动更新

## 文件说明

- `channels.m3u` - 您的原始咪咕源文件
- `enhanced_channels_YYYYMMDD_HHMMSS.m3u` - 自动生成的增强版文件
- `auto_update_m3u.py` - 本地自动更新脚本
- `.github/workflows/m3u-updater.yml` - GitHub Actions 自动化配置

## 使用方法

### 本地手动更新

```bash
# 运行本地更新脚本
python3 auto_update_m3u.py

# 或者直接运行
python3 auto_update_m3u.py
```

### GitHub Actions 自动更新

1. 将此仓库推送到 GitHub
2. GitHub Actions 会自动定时每天凌晨2点 (UTC) 执行更新
3. 也可以在 Actions 页面手动触发更新

### 自动更新时间表

- **定时执行**: 每天凌晨2点 (UTC时间，对应北京时间上午10点)
- **手动触发**: 在 GitHub Actions 页面可以手动触发
- **更新内容**: 从 iptv-org 仓库获取最新频道数据

## 输出文件说明

生成的增强版 M3U 文件包含：
- 您的所有现有频道
- 新增的卫视频道
- 动漫相关频道
- 电影频道
- 其他目标类型频道

## 注意事项

1. 确保您的 GitHub 仓库 Secrets 中配置了必要的权限
2. 第一次运行时需要手动触发或等待定时执行
3. 生成的文件包含时间戳，便于管理版本
4. 建议定期检查生成的文件质量

## 自定义配置

如需修改频道过滤条件，可以在脚本中修改 `target_groups` 列表：
```python
target_groups = ['卫视', '央视', '动漫', '电影', '少儿', '纪录片', '体育', '娱乐', '戏曲']
```

## 故障排除

如果遇到网络问题，脚本会提示错误并跳过更新。可以尝试：
1. 检查网络连接
2. 手动触发 GitHub Actions
3. 查看 Actions 日志详情
