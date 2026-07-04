#!/usr/bin/env python3
import re
import urllib.request
import urllib.parse
from datetime import datetime
import os

def parse_m3u(file_path):
    """Parse M3U file and return list of channels"""
    channels = []
    current_channel = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#EXTINF:'):
                # Extract info from EXTINF line
                match = re.search(r'#EXTINF:-1(?: tvg-logo="([^"]*)")? group-title="([^"]*)",(.+)', line)
                if match:
                    current_channel = {
                        'logo': match.group(1),
                        'group': match.group(2),
                        'name': match.group(3).strip()
                    }
            elif line.startswith('http'):
                if current_channel:
                    current_channel['url'] = line
                    channels.append(current_channel)
                    current_channel = {}
    
    return channels

def fetch_iptv_data():
    """Fetch IPTV data from iptv-org repository"""
    try:
        url = 'https://raw.githubusercontent.com/iptv-org/iptv/master/streams/cn.m3u'
        with urllib.request.urlopen(url) as response:
            content = response.read().decode('utf-8')
        return content
    except Exception as e:
        print(f"Error fetching IPTV data: {e}")
        return None

def generate_enhanced_m3u(existing_channels, iptv_content):
    """Generate enhanced M3U with existing and new channels"""
    
    # Parse IPTV content
    iptv_lines = iptv_content.strip().split('\n')
    iptv_channels = []
    current_channel = {}
    
    for line in iptv_lines:
        line = line.strip()
        if line.startswith('#EXTINF:'):
            match = re.search(r'#EXTINF:-1(?: tvg-logo="([^"]*)")? group-title="([^"]*)",(.+)', line)
            if match:
                current_channel = {
                    'logo': match.group(1),
                    'group': match.group(2),
                    'name': match.group(3).strip()
                }
        elif line.startswith('http'):
            if current_channel:
                current_channel['url'] = line
                iptv_channels.append(current_channel)
                current_channel = {}
    
    # Filter for target groups
    target_groups = ['卫视', '央视', '动漫', '电影', '少儿', '纪录片', '体育', '娱乐', '戏曲']
    filtered_channels = []
    
    for channel in iptv_channels:
        group = channel.get('group', '')
        if any(target.lower() in group.lower() for target in target_groups):
            filtered_channels.append(channel)
    
    # Combine channels
    all_channels = existing_channels + filtered_channels
    
    # Generate M3U content
    m3u_content = '#EXTM3U\n'
    m3u_content += f'# Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
    m3u_content += f'# Total channels: {len(all_channels)}\n'
    m3u_content += f'# Existing channels: {len(existing_channels)}\n'
    m3u_content += f'# New channels: {len(filtered_channels)}\n\n'
    
    for channel in all_channels:
        extinf = f'#EXTINF:-1'
        if channel.get('logo'):
            extinf += f' tvg-logo="{channel["logo"]}"'
        if channel.get('group'):
            extinf += f' group-title="{channel["group"]}"'
        extinf += f',{channel["name"]}'
        m3u_content += extinf + '\n'
        
        if 'url' in channel:
            m3u_content += channel['url'] + '\n'
        else:
            m3u_content += '# URL missing\n'
        
        m3u_content += '\n'
    
    return m3u_content

def main():
    print("=== M3U 自动更新脚本 ===")
    
    # 1. Read existing channels
    if not os.path.exists('channels.m3u'):
        print("错误: channels.m3u 文件不存在")
        return
    
    existing_channels = parse_m3u('channels.m3u')
    print(f"已读取 {len(existing_channels)} 个现有频道")
    
    # 2. Fetch IPTV data
    print("正在获取 IPTV 数据...")
    iptv_content = fetch_iptv_data()
    if not iptv_content:
        print("无法获取 IPTV 数据，使用本地数据")
        return
    
    # 3. Generate enhanced M3U
    print("正在生成增强版 M3U...")
    enhanced_content = generate_enhanced_m3u(existing_channels, iptv_content)
    
    # 4. Save enhanced M3U
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f'enhanced_channels_{timestamp}.m3u'
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(enhanced_content)
    
    print(f"已生成 {output_filename}")
    print(f"总频道数: {len(existing_channels) + len([c for c in enhanced_content.split('\n') if c.startswith('#EXTINF:')]) - len([c for c in enhanced_content.split('\n') if c.startswith('#EXTINF:') and 'Generated on:' in c])}")

if __name__ == '__main__':
    main()
