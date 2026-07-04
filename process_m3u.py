#!/usr/bin/env python3
import re
import sys
import argparse

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

def extract_channel_name(channel):
    """Extract just the channel name from channel info"""
    return channel.get('name', '')

def is_similar_name(name1, name2):
    """Check if two channel names are similar"""
    # Remove common prefixes/suffixes and compare
    name1_clean = re.sub(r'^(CCTV|卫视|电视|台|频道)$', '', name1.strip())
    name2_clean = re.sub(r'^(CCTV|卫视|电视|台|频道)$', '', name2.strip())
    return name1_clean.lower() == name2_clean.lower()

def find_missing_channels(existing_channels, new_channels):
    """Find channels in new_channels that are not in existing_channels"""
    existing_names = [extract_channel_name(ch) for ch in existing_channels]
    missing_channels = []
    
    for channel in new_channels:
        channel_name = extract_channel_name(channel)
        if not any(is_similar_name(channel_name, existing_name) for existing_name in existing_names):
            missing_channels.append(channel)
    
    return missing_channels

def filter_channels_by_groups(channels, target_groups):
    """Filter channels by target groups"""
    filtered = []
    for channel in channels:
        group = channel.get('group', '')
        if any(target.lower() in group.lower() for target in target_groups):
            filtered.append(channel)
    return filtered

def generate_m3u(channels):
    """Generate M3U content from channels"""
    m3u_content = '#EXTM3U\n'
    for channel in channels:
        extinf = f'#EXTINF:-1'
        if channel.get('logo'):
            extinf += f' tvg-logo="{channel["logo"]}"'
        if channel.get('group'):
            extinf += f' group-title="{channel["group"]}"'
        extinf += f',{channel["name"]}'
        m3u_content += extinf + '\n'
        m3u_content += channel['url'] + '\n'
    return m3u_content

def main():
    parser = argparse.ArgumentParser(description='Process and combine M3U files')
    parser.add_argument('--existing', help='Existing M3U file')
    parser.add_argument('--new', help='New M3U file to fetch from iptv-org')
    parser.add_argument('--output', help='Output M3U file')
    parser.add_argument('--filter-groups', nargs='+', help='Filter channels by groups (e.g., 卫视 央视 动漫 电影)')
    
    args = parser.parse_args()
    
    if args.existing:
        existing_channels = parse_m3u(args.existing)
        print(f"Loaded {len(existing_channels)} existing channels")
    
    if args.new:
        new_channels = parse_m3u(args.new)
        print(f"Loaded {len(new_channels)} new channels")
        
        if args.filter_groups:
            filtered_channels = filter_channels_by_groups(new_channels, args.filter_groups)
            print(f"Filtered to {len(filtered_channels)} channels in target groups")
        else:
            filtered_channels = new_channels
        
        if args.existing:
            missing_channels = find_missing_channels(existing_channels, filtered_channels)
            print(f"Found {len(missing_channels)} missing channels")
            
            # Combine existing + missing
            combined_channels = existing_channels + missing_channels
        else:
            combined_channels = filtered_channels
        
        if args.output:
            m3u_content = generate_m3u(combined_channels)
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(m3u_content)
            print(f"Generated {args.output} with {len(combined_channels)} channels")
        else:
            print("No output file specified")
    else:
        print("No new M3U file specified")

if __name__ == '__main__':
    main()
