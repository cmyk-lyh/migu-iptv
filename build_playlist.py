#!/usr/bin/env python3
"""Build a clean M3U playlist from Migu (咪咕) live streaming sources."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


EXTINF_RE = re.compile(r"^#EXTINF:(?P<meta>.*?),(?P<name>.*)$", re.IGNORECASE)
ATTR_RE = re.compile(r'(?P<key>[\w-]+)="(?P<value>[^"]*)"')
URL_SCHEMES = {"http", "https", "rtmp", "rtsp"}

MIGU_PROXY_PATTERNS = [
    re.compile(r"go\.bkpcp\.top/mg/(?P<code>\w+)"),
]

MIGU_CHANNEL_DB: list[dict[str, str]] = [
    {"code": "bjws", "name": "BRTV 北京卫视", "group": "General", "tvg_id": "BeijingSatelliteTV.cn"},
    {"code": "bjys", "name": "BRTV 影视", "group": "Entertainment", "tvg_id": "BeijingFilm.cn"},
    {"code": "bjwt", "name": "BRTV 文艺", "group": "Entertainment", "tvg_id": "BeijingLiterature.cn"},
    {"code": "bjkj", "name": "BRTV 科教", "group": "Education", "tvg_id": "BeijingScience.cn"},
    {"code": "bjsh", "name": "BRTV 生活", "group": "Lifestyle", "tvg_id": "BeijingLife.cn"},
    {"code": "bjxw", "name": "BRTV 新闻", "group": "News", "tvg_id": "BeijingNews.cn"},
    {"code": "bjqn", "name": "BRTV 青年", "group": "Entertainment", "tvg_id": "BeijingYouth.cn"},
    {"code": "bjty", "name": "BRTV 体育休闲", "group": "Sports", "tvg_id": "BeijingSports.cn"},
    {"code": "cctv1", "name": "CCTV-1 综合", "group": "General", "tvg_id": "CCTV1.cn"},
    {"code": "cctv2", "name": "CCTV-2 财经", "group": "Finance", "tvg_id": "CCTV2.cn"},
    {"code": "cctv3", "name": "CCTV-3 综艺", "group": "Entertainment", "tvg_id": "CCTV3.cn"},
    {"code": "cctv4", "name": "CCTV-4 中文国际", "group": "News", "tvg_id": "CCTV4.cn"},
    {"code": "cctv5", "name": "CCTV-5 体育", "group": "Sports", "tvg_id": "CCTV5.cn"},
    {"code": "cctv5p", "name": "CCTV-5+ 体育赛事", "group": "Sports", "tvg_id": "CCTV5Plus.cn"},
    {"code": "cctv6", "name": "CCTV-6 电影", "group": "Movies", "tvg_id": "CCTV6.cn"},
    {"code": "cctv7", "name": "CCTV-7 军事农业", "group": "General", "tvg_id": "CCTV7.cn"},
    {"code": "cctv8", "name": "CCTV-8 电视剧", "group": "Entertainment", "tvg_id": "CCTV8.cn"},
    {"code": "cctv9", "name": "CCTV-9 纪录", "group": "Documentary", "tvg_id": "CCTV9.cn"},
    {"code": "cctv10", "name": "CCTV-10 科教", "group": "Education", "tvg_id": "CCTV10.cn"},
    {"code": "cctv11", "name": "CCTV-11 戏曲", "group": "Entertainment", "tvg_id": "CCTV11.cn"},
    {"code": "cctv12", "name": "CCTV-12 社会与法", "group": "News", "tvg_id": "CCTV12.cn"},
    {"code": "cctv13", "name": "CCTV-13 新闻", "group": "News", "tvg_id": "CCTV13.cn"},
    {"code": "cctv14", "name": "CCTV-14 少儿", "group": "Kids", "tvg_id": "CCTV14.cn"},
    {"code": "cctv15", "name": "CCTV-15 音乐", "group": "Music", "tvg_id": "CCTV15.cn"},
    {"code": "cctv16", "name": "CCTV-16 奥林匹克", "group": "Sports", "tvg_id": "CCTV16.cn"},
    {"code": "cctv17", "name": "CCTV-17 农业农村", "group": "General", "tvg_id": "CCTV17.cn"},
    {"code": "dfty", "name": "东方卫视", "group": "General", "tvg_id": "DragonTV.cn"},
    {"code": "hnws", "name": "湖南卫视", "group": "General", "tvg_id": "HunanTV.cn"},
    {"code": "jsws", "name": "江苏卫视", "group": "General", "tvg_id": "JiangsuTV.cn"},
    {"code": "zjws", "name": "浙江卫视", "group": "General", "tvg_id": "ZhejiangTV.cn"},
    {"code": "gdws", "name": "广东卫视", "group": "General", "tvg_id": "GuangdongTV.cn"},
    {"code": "shdws", "name": "深圳卫视", "group": "General", "tvg_id": "ShenzhenTV.cn"},
    {"code": "sdws", "name": "山东卫视", "group": "General", "tvg_id": "ShandongTV.cn"},
    {"code": "scws", "name": "四川卫视", "group": "General", "tvg_id": "SichuanTV.cn"},
    {"code": "ahws", "name": "安徽卫视", "group": "General", "tvg_id": "AnhuiTV.cn"},
    {"code": "hubws", "name": "湖北卫视", "group": "General", "tvg_id": "HubeiTV.cn"},
    {"code": "henws", "name": "河南卫视", "group": "General", "tvg_id": "HenanTV.cn"},
    {"code": "lnws", "name": "辽宁卫视", "group": "General", "tvg_id": "LiaoningTV.cn"},
    {"code": "hljws", "name": "黑龙江卫视", "group": "General", "tvg_id": "HeilongjiangTV.cn"},
    {"code": "tjws", "name": "天津卫视", "group": "General", "tvg_id": "TianjinTV.cn"},
    {"code": "cqws", "name": "重庆卫视", "group": "General", "tvg_id": "ChongqingTV.cn"},
    {"code": "fjjw", "name": "东南卫视", "group": "General", "tvg_id": "SoutheastTV.cn"},
    {"code": "gsjd", "name": "甘肃卫视", "group": "General", "tvg_id": "GansuTV.cn"},
    {"code": "ynws", "name": "云南卫视", "group": "General", "tvg_id": "YunnanTV.cn"},
    {"code": "gxws", "name": "广西卫视", "group": "General", "tvg_id": "GuangxiTV.cn"},
    {"code": "nxws", "name": "宁夏卫视", "group": "General", "tvg_id": "NingxiaTV.cn"},
    {"code": "xztv", "name": "西藏卫视", "group": "General", "tvg_id": "TibetTV.cn"},
    {"code": "xjdj", "name": "新疆卫视", "group": "General", "tvg_id": "XinjiangTV.cn"},
    {"code": "nmtv", "name": "内蒙古卫视", "group": "General", "tvg_id": "InnerMongoliaTV.cn"},
    {"code": "qhws", "name": "青海卫视", "group": "General", "tvg_id": "QinghaiTV.cn"},
    {"code": "shaxtv", "name": "陕西卫视", "group": "General", "tvg_id": "ShaanxiTV.cn"},
    {"code": "shanxitv", "name": "山西卫视", "group": "General", "tvg_id": "ShanxiTV.cn"},
    {"code": "jxtv", "name": "江西卫视", "group": "General", "tvg_id": "JiangxiTV.cn"},
    {"code": "haintv", "name": "海南卫视", "group": "General", "tvg_id": "HainanTV.cn"},
    {"code": "gzws", "name": "贵州卫视", "group": "General", "tvg_id": "GuizhouTV.cn"},
    {"code": "jlws", "name": "吉林卫视", "group": "General", "tvg_id": "JilinTV.cn"},
    {"code": "hmtv", "name": "河北卫视", "group": "General", "tvg_id": "HebeiTV.cn"},
    {"code": "movie1", "name": "芒果电影", "group": "Movies", "tvg_id": "MangoMovie.cn"},
]

DEFAULT_MIGU_BASE = "http://go.bkpcp.top/mg/"


@dataclass(frozen=True)
class Channel:
    name: str
    url: str
    extinf: str
    group: str = ""


def read_lines(path: Path) -> list[str]:
    if not path.exists():
        return []
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def fetch_text(url: str, timeout: float) -> str:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "m3u-subscription-builder/1.0",
            "Accept": "application/vnd.apple.mpegurl,application/x-mpegurl,text/plain,*/*",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read()
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def fetch_json(url: str, timeout: float) -> dict | list:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "application/json,text/plain,*/*",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def is_url(value: str) -> bool:
    parsed = urllib.parse.urlparse(value)
    return parsed.scheme.lower() in URL_SCHEMES and bool(parsed.netloc)


def absolutize_url(base_url: str, maybe_url: str) -> str:
    if is_url(maybe_url):
        return maybe_url
    return urllib.parse.urljoin(base_url, maybe_url)


def parse_m3u(text: str, base_url: str = "") -> list[Channel]:
    channels: list[Channel] = []
    pending_extinf = ""
    pending_group = ""

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.upper().startswith("#EXTINF:"):
            pending_extinf = line
            continue

        if line.upper().startswith("#EXTGRP:"):
            pending_group = line.split(":", 1)[1].strip()
            continue

        if line.startswith("#"):
            continue

        url = absolutize_url(base_url, line)
        if not is_url(url):
            pending_extinf = ""
            pending_group = ""
            continue

        name = url
        extinf = pending_extinf
        match = EXTINF_RE.match(extinf)
        if match:
            name = match.group("name").strip() or url
        else:
            extinf = f"#EXTINF:-1,{name}"

        channels.append(Channel(name=name, url=url, extinf=extinf, group=pending_group))
        pending_extinf = ""
        pending_group = ""

    return channels


def read_manual_channels(path: Path) -> list[Channel]:
    if not path.exists():
        return []

    channels: list[Channel] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        filtered = (line for line in handle if line.strip() and not line.lstrip().startswith("#"))
        reader = csv.DictReader(filtered, fieldnames=["name", "url", "group", "logo", "tvg_id"])
        for row in reader:
            name = (row.get("name") or "").strip()
            url = (row.get("url") or "").strip()
            group = (row.get("group") or "").strip()
            logo = (row.get("logo") or "").strip()
            tvg_id = (row.get("tvg_id") or "").strip()
            if not name or not is_url(url):
                continue

            attrs = []
            if tvg_id:
                attrs.append(f'tvg-id="{escape_attr(tvg_id)}"')
            if logo:
                attrs.append(f'tvg-logo="{escape_attr(logo)}"')
            if group:
                attrs.append(f'group-title="{escape_attr(group)}"')
            attr_text = " " + " ".join(attrs) if attrs else ""
            channels.append(Channel(name=name, url=url, extinf=f"#EXTINF:-1{attr_text},{name}", group=group))
    return channels


def read_logo_map(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    logo_map: dict[str, str] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        filtered = (line for line in handle if line.strip() and not line.lstrip().startswith("#"))
        reader = csv.DictReader(filtered, fieldnames=["name", "logo"])
        for row in reader:
            name = (row.get("name") or "").strip()
            logo = (row.get("logo") or "").strip()
            if name and is_url(logo):
                logo_map[normalize_name(name)] = logo
    return logo_map


def normalize_name(value: str) -> str:
    return re.sub(r"\s+", "", value).casefold()


def extinf_attrs(extinf: str) -> dict[str, str]:
    match = EXTINF_RE.match(extinf)
    if not match:
        return {}
    return {attr.group("key"): attr.group("value") for attr in ATTR_RE.finditer(match.group("meta"))}


def add_extinf_attr(extinf: str, key: str, value: str) -> str:
    if not value or f"{key}=" in extinf:
        return extinf
    return extinf.replace(",", f' {key}="{escape_attr(value)}",', 1)


def escape_attr(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"')


def normalize_channel(channel: Channel, default_group: str, logo_map: dict[str, str]) -> Channel:
    group = channel.group or default_group
    extinf = channel.extinf
    attrs = extinf_attrs(extinf)
    logo = attrs.get("tvg-logo", "") or logo_map.get(normalize_name(channel.name), "")
    extinf = add_extinf_attr(extinf, "group-title", group)
    extinf = add_extinf_attr(extinf, "tvg-logo", logo)
    return Channel(name=channel.name.strip(), url=channel.url.strip(), extinf=extinf, group=group)


def build_migu_channels(base_url: str, proxy_list: list[dict[str, str]] | None = None) -> list[Channel]:
    channels: list[Channel] = []
    db = proxy_list or MIGU_CHANNEL_DB

    for entry in db:
        code = entry["code"]
        name = entry["name"]
        group = entry.get("group", "")
        tvg_id = entry.get("tvg_id", "")

        url = f"{base_url.rstrip('/')}/{code}"

        attrs = []
        if tvg_id:
            attrs.append(f'tvg-id="{escape_attr(tvg_id)}"')
        if group:
            attrs.append(f'group-title="{escape_attr(group)}"')
        attr_text = " " + " ".join(attrs) if attrs else ""

        channels.append(Channel(name=name, url=url, extinf=f"#EXTINF:-1{attr_text},{name}", group=group))

    return channels


def update_migu_channels_from_csv(path: Path, base_url: str) -> list[Channel]:
    if not path.exists():
        return []

    entries: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        filtered = (line for line in handle if line.strip() and not line.lstrip().startswith("#"))
        reader = csv.DictReader(filtered, fieldnames=["code", "name", "group", "logo", "tvg_id"])
        for row in reader:
            code = (row.get("code") or "").strip()
            name = (row.get("name") or "").strip()
            if not code or not name:
                continue
            entries.append({
                "code": code,
                "name": name,
                "group": (row.get("group") or "").strip(),
                "logo": (row.get("logo") or "").strip(),
                "tvg_id": (row.get("tvg_id") or "").strip(),
            })

    if not entries:
        return []

    return build_migu_channels(base_url, entries)


def dedupe(channels: Iterable[Channel]) -> list[Channel]:
    seen_urls: set[str] = set()
    result: list[Channel] = []
    for channel in channels:
        key = channel.url.rstrip("/")
        if key in seen_urls:
            continue
        seen_urls.add(key)
        result.append(channel)
    return result


def probe_url(url: str, timeout: float) -> bool:
    request = urllib.request.Request(url, headers={"User-Agent": "m3u-subscription-builder/1.0"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", 200)
            return 200 <= status < 400
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def write_m3u(path: Path, channels: Iterable[Channel]) -> None:
    lines = ["#EXTM3U"]
    for channel in channels:
        lines.append(channel.extinf)
        lines.append(channel.url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def build(args: argparse.Namespace) -> int:
    all_channels: list[Channel] = []

    source_urls = read_lines(Path(args.sources))
    for source_url in source_urls:
        if not is_url(source_url):
            print(f"skip invalid source: {source_url}", file=sys.stderr)
            continue
        try:
            text = fetch_text(source_url, args.timeout)
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            print(f"fetch failed: {source_url} ({exc})", file=sys.stderr)
            continue
        all_channels.extend(parse_m3u(text, source_url))

    if args.migu_csv:
        migu_csv_path = Path(args.migu_csv)
        if migu_csv_path.exists():
            all_channels.extend(update_migu_channels_from_csv(migu_csv_path, args.migu_base))
            print(f"loaded Migu channels from {args.migu_csv}", file=sys.stderr)

    if args.migu_channels:
        all_channels.extend(build_migu_channels(args.migu_base))
        print(f"added {len(MIGU_CHANNEL_DB)} built-in Migu channels", file=sys.stderr)

    all_channels.extend(read_manual_channels(Path(args.channels)))
    logo_map = read_logo_map(Path(args.logos))
    normalized = [normalize_channel(channel, args.default_group, logo_map) for channel in all_channels]
    unique = dedupe(normalized)

    if args.check:
        checked: list[Channel] = []
        for channel in unique:
            if probe_url(channel.url, args.probe_timeout):
                checked.append(channel)
            else:
                print(f"dead or unreachable: {channel.name} {channel.url}", file=sys.stderr)
        unique = checked

    if args.limit:
        unique = unique[: args.limit]

    write_m3u(Path(args.output), unique)
    print(f"wrote {len(unique)} channels to {args.output}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Build M3U playlist from Migu (咪咕) live streams.")
    parser.add_argument("--sources", default="sources.txt", help="text file with public M3U source URLs")
    parser.add_argument("--channels", default="channels.csv", help="manual channel CSV (name,url,group,logo,tvg_id)")
    parser.add_argument("--logos", default="logos.csv", help="channel logo CSV (name,logo)")
    parser.add_argument("--migu-csv", default="migu_channels.csv", help="Migu channel codes CSV (code,name,group,logo,tvg_id)")
    parser.add_argument("--migu-base", default=DEFAULT_MIGU_BASE, help="Migu proxy base URL")
    parser.add_argument("--migu-channels", action="store_true", default=True,
                        help="include built-in Migu channel database (default: True)")
    parser.add_argument("--no-migu-channels", action="store_false", dest="migu_channels",
                        help="skip built-in Migu channel database")
    parser.add_argument("--output", default="playlist.m3u", help="output M3U path")
    parser.add_argument("--default-group", default="General", help="default group title")
    parser.add_argument("--timeout", type=float, default=20.0, help="source fetch timeout in seconds")
    parser.add_argument("--check", action="store_true", help="probe each stream, keep only reachable URLs")
    parser.add_argument("--probe-timeout", type=float, default=6.0, help="stream probe timeout in seconds")
    parser.add_argument("--limit", type=int, default=0, help="max channels (0 = unlimited)")
    return build(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
