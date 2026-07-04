#!/usr/bin/env python3
import re

def parse_m3u(file_path):
    """Parse M3U file and return list of channels"""
    channels = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#EXTINF:'):
                # Extract info from EXTINF line
                match = re.search(r'#EXTINF:-1(?: tvg-logo="([^"]*)")? group-title="([^"]*)",(.+)', line)
                if match:
                    channel = {
                        'logo': match.group(1),
                        'group': match.group(2),
                        'name': match.group(3).strip()
                    }
                    channels.append(channel)
    
    return channels

def extract_channel_name(channel):
    """Extract just the channel name from channel info"""
    return channel.get('name', '')

def find_missing_satellite_channels():
    """Find commonly missing satellite channels"""
    # Common satellite channels that might be missing
    missing_channels = [
        {'group': '卫视', 'name': '重庆卫视', 'url': 'http://example.com/cqws'},
        {'group': '卫视', 'name': '山西卫视', 'url': 'http://example.com/sxws'},
        {'group': '卫视', 'name': '宁夏卫视', 'url': 'http://example.com/nxws'},
        {'group': '卫视', 'name': '青海卫视', 'url': 'http://example.com/qhws'},
        {'group': '卫视', 'name': '新疆卫视', 'url': 'http://example.com/xjws'},
        {'group': '卫视', 'name': '山东卫视', 'url': 'http://example.com/sdws'},
        {'group': '卫视', 'name': '河北卫视', 'url': 'http://example.com/hbws'},
        {'group': '卫视', 'name': '江西卫视', 'url': 'http://example.com/jxws'},
        {'group': '卫视', 'name': '湖南卫视', 'url': 'http://example.com/hnws'},
        {'group': '卫视', 'name': '陕西卫视', 'url': 'http://example.com/sxws'},
        {'group': '央视', 'name': 'CCTV-新闻', 'url': 'http://example.com/cctvnews'},
        {'group': '央视', 'name': 'CCTV-戏曲', 'url': 'http://example.com/cctvopera'},
        {'group': '动漫', 'name': '金鹰卡通', 'url': 'http://example.com/jykt'},
        {'group': '动漫', 'name': '卡酷少儿', 'url': 'http://example.com/kkse'},
        {'group': '动漫', 'name': '炫动卡通', 'url': 'http://example.com/xdkt'},
        {'group': '电影', 'name': '电影频道', 'url': 'http://example.com/movie1'},
        {'group': '电影', 'name': '动作电影', 'url': 'http://example.com/movie2'},
        {'group': '电影', 'name': '喜剧电影', 'url': 'http://example.com/movie3'},
    ]
    return missing_channels

def generate_enhanced_m3u():
    """Generate enhanced M3U with missing channels"""
    
    # Read existing channels
    existing_channels = parse_m3u('channels.m3u')
    
    # Get missing channels
    missing_channels = find_missing_satellite_channels()
    
    # Combine channels
    all_channels = existing_channels + missing_channels
    
    # Generate M3U content
    m3u_content = '#EXTM3U\n'
    
    for channel in all_channels:
        extinf = f'#EXTINF:-1'
        if channel.get('logo'):
            extinf += f' tvg-logo="{channel["logo"]}"'
        if channel.get('group'):
            extinf += f' group-title="{channel["group"]}"'
        extinf += f',{channel["name"]}'
        m3u_content += extinf + '\n'
        
        # Use placeholder URL for missing channels
        if 'example.com' in channel.get('url', ''):
            m3u_content += f'# NOTE: Placeholder URL for {channel["name"]} - replace with actual URL\n'
        else:
            m3u_content += channel['url'] + '\n'
        
        m3u_content += '\n'
    
    # Write enhanced M3U
    with open('enhanced_channels.m3u', 'w', encoding='utf-8') as f:
        f.write(m3u_content)
    
    return len(all_channels), len(missing_channels)

if __name__ == '__main__':
    existing_channels = parse_m3u('channels.m3u')
    print(f"Existing channels:")
    for channel in existing_channels:
        print(f"  {channel['group']} | {channel['name']}")
    
    total_count, missing_count = generate_enhanced_m3u()
    print(f"\nGenerated enhanced_channels.m3u with {total_count} channels ({missing_count} new)")
