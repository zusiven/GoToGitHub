import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import dns.resolver

# 全球各地的公开 DNS 服务器（重点亚洲地区）
DNS_SERVERS = {
    # 日本 DNS - 主要厂商
    'IIJ DNS (Japan)': '203.112.2.4',
    'IIJ DNS (Japan)2': '203.112.6.4',
    'JPRS DNS (Japan)': '156.131.103.5',
    'NTT Communications (Japan)': '129.250.35.250',
    'NTT Com (Japan)2': '202.238.156.1',
    'Softbank DNS (Japan)': '202.26.220.227',
    'Softbank (Japan)2': '202.26.220.228',
    'Yahoo Japan DNS': '182.22.24.52',
    'Yahoo Japan DNS2': '182.22.25.120',
    'GMO Internet (Japan)': '210.188.224.65',
    'Kawachi Net (Japan)': '202.238.192.135',
    'BIGLOBE (Japan)': '203.109.145.66',
    'BIGLOBE (Japan)2': '210.201.176.33',
    'So-net (Japan)': '210.209.110.194',
    'Nifty (Japan)': '202.239.20.1',
    
    # 韩国 DNS - 主要厂商
    'KT (Korea)': '168.126.63.1',
    'KT (Korea)2': '168.126.63.2',
    'KT (Korea)3': '168.126.62.1',
    'SKT (Korea)': '210.220.163.82',
    'SKT (Korea)2': '219.248.45.48',
    'LG (Korea)': '164.124.107.9',
    'LG (Korea)2': '164.124.101.2',
    'Hanaro (Korea)': '210.117.6.115',
    'Daum (Korea)': '164.124.101.2',
    'Naver (Korea)': '210.89.160.88',
    'Korea Telecom': '164.124.101.2',
    'Korea Telecom2': '210.220.165.18',
    'eGov (Korea)': '210.102.0.1',
    
    # 新加坡 DNS - 主要厂商
    'Singtel (Singapore)': '165.21.100.84',
    'Singtel (Singapore)2': '165.21.209.84',
    'Singtel (Singapore)3': '203.84.214.165',
    'ViewQwest (Singapore)': '203.83.76.1',
    'ViewQwest (Singapore)2': '203.83.76.2',
    'Starhub (Singapore)': '202.166.200.1',
    'Starhub (Singapore)2': '202.166.200.131',
    'MyRepublic (Singapore)': '208.73.210.7',
    'Fiber Home (Singapore)': '119.81.191.205',
    'SG OpenDNS': '202.130.97.4',
    'Pacific Internet (SG)': '203.118.166.1',
    
    # 香港 DNS - 主要厂商
    'PCCW HKT (Hong Kong)': '202.45.84.58',
    'PCCW (Hong Kong)2': '202.45.84.39',
    'PCCW (Hong Kong)3': '203.198.73.212',
    'Hong Kong Telecom': '203.198.73.212',
    'Hutchison (Hong Kong)': '210.233.0.112',
    'Hutchison (Hong Kong)2': '210.233.0.113',
    'New World Telecom (HK)': '203.187.98.66',
    'CSL (Hong Kong)': '202.45.84.123',
    'Netvigator (Hong Kong)': '203.123.145.66',
    'Hong Kong Cable': '202.180.160.1',
    'HK ISP': '202.51.132.1',
    'HKBN (Hong Kong)': '202.45.84.58',
    
    # 台湾 DNS - 主要厂商
    'Chunghwa (Taiwan)': '168.95.1.1',
    'Chunghwa (Taiwan)2': '168.95.192.1',
    'Chunghwa (Taiwan)3': '168.95.1.2',
    'TWNIC (Taiwan)': '210.243.160.18',
    'So-net (Taiwan)': '219.80.96.1',
    'Seed Net (Taiwan)': '203.99.14.5',
    'Giga (Taiwan)': '203.115.195.1',
    
    # 东南亚其他 DNS
    'Thailand CAT': '202.28.0.1',
    'Thailand TRUE': '202.44.38.1',
    'Vietnam VNPT': '203.162.4.191',
    'Philippines PLDT': '202.56.231.1',
    'Indonesia Telkom': '202.134.1.1',
    'Malaysia Maxis': '202.75.159.200',
    
    # 国内 DNS - 主要厂商
    'Alibaba DNS (China)': '223.5.5.5',
    'Alibaba DNS (China)2': '223.6.6.6',
    'Tencent DNS (China)': '119.29.29.29',
    'Tencent DNS (China)2': '119.28.28.28',
    'Tencent DNS (China)3': '119.29.29.28',
    'Baidu DNS (China)': '180.76.76.76',
    'DNSPod (China)': '119.29.29.29',
    'CNNIC (China)': '1.2.4.8',
    '114DNS': '114.114.114.114',
    '114DNS2': '114.114.115.115',
    
    # 欧美 DNS
    'Google (USA)': '8.8.8.8',
    'Google (USA)2': '8.8.4.4',
    'Cloudflare (USA)': '1.1.1.1',
    'Cloudflare (USA)2': '1.0.0.1',
    'Quad9 (USA)': '9.9.9.9',
}

def get_ips_from_multiple_dns_servers(domain):
    """从多个全球 DNS 服务器查询获取 IP"""
    print(f"\n正在查询 {domain}...")
    
    ips = set()
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(query_dns_server, dns_ip, domain): (name, dns_ip)
            for name, dns_ip in DNS_SERVERS.items()
        }
        
        for future in as_completed(futures):
            name, dns_ip = futures[future]
            try:
                result_ips = future.result()
                if result_ips:
                    ips.update(result_ips)
            except Exception:
                pass
    
    return list(ips)

def query_dns_server(dns_server, domain):
    """使用 socket 直接查询 DNS 服务器"""
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [dns_server]
        resolver.timeout = 3
        resolver.lifetime = 0.5
        
        answers = resolver.resolve(domain, 'A')
        ips = [str(rdata) for rdata in answers]
        return ips
    except Exception:
        return []

def test_tcp_connection_with_delay(ip, port=443, timeout=3):
    """测试到指定 IP 的 TCP 连通性并测量延迟"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        start_time = time.time()
        result = sock.connect_ex((ip, port))
        delay = (time.time() - start_time) * 1000
        sock.close()
        
        if result == 0:
            return True, delay
        else:
            return False, delay
    except Exception:
        return False, timeout * 1000

def test_ips(ips, port=443, timeout=3):
    """并发测试多个 IP 的连通性并测量延迟"""
    reachable_ips = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(test_tcp_connection_with_delay, ip, port, timeout): ip for ip in ips}
        
        for future in as_completed(futures):
            ip = futures[future]
            try:
                result, delay = future.result()
                if result:
                    reachable_ips.append((ip, delay))
            except Exception:
                pass
    
    # 按延迟从低到高排序
    reachable_ips.sort(key=lambda x: x[1])
    return [ip for ip, _ in reachable_ips]

def process_domains(domains, max_ips_per_domain=3, output_file="host_cp.txt"):
    """处理多个域名"""
    print(f"开始处理 {len(domains)} 个域名...\n")
    
    all_hosts = []
    
    for domain in domains:
        print(f"处理: {domain}")
        
        # 1. 从多个 DNS 服务器获取 IP
        ips = get_ips_from_multiple_dns_servers(domain)
        
        if not ips:
            print(f"  ✗ 未能获取到 IP")
            continue
        
        print(f"  ✓ 获取到 {len(ips)} 个 IP")
        
        # 2. 测试连通性
        reachable_ips = test_ips(ips, port=443, timeout=3)
        
        if not reachable_ips:
            print(f"  ✗ 无可用 IP")
            continue
        
        # 3. 只保留前三个 IP
        top_ips = reachable_ips[:max_ips_per_domain]
        print(f"  ✓ 选择前 {len(top_ips)} 个可用 IP: {', '.join(top_ips)}")
        
        # 添加到结果
        for ip in top_ips:
            all_hosts.append((ip, domain))
    
    # 写入文件
    write_hosts_file(all_hosts, output_file)

def write_hosts_file(hosts, output_file="host_cp.txt"):
    """将所有主机写入 hosts 文件"""
    print(f"\n将结果写入 {output_file}...\n")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# GitHub Hosts\n")
            f.write(f"# Generated at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total: {len(hosts)} entries\n\n")
            
            for ip, domain in hosts:
                f.write(f"{ip} {domain}\n")
        
        print(f"✓ 成功写入 {len(hosts)} 条记录到 {output_file}")
        
        # 显示文件内容
        print(f"\n{output_file} 内容:")
        print("-" * 60)
        with open(output_file, 'r', encoding='utf-8') as f:
            print(f.read())
        print("-" * 60)
        
        return True
    
    except Exception as e:
        print(f"写入文件失败: {e}")
        return False

def main():
    domains = [
        'alive.github.com',
        'api.github.com',
        'api.individual.githubcopilot.com',
        'avatars.githubusercontent.com',
        'avatars0.githubusercontent.com',
        'avatars1.githubusercontent.com',
        'avatars2.githubusercontent.com',
        'avatars3.githubusercontent.com',
        'avatars4.githubusercontent.com',
        'avatars5.githubusercontent.com',
        'camo.githubusercontent.com',
        'central.github.com',
        'cloud.githubusercontent.com',
        'codeload.github.com',
        'collector.github.com',
        'desktop.githubusercontent.com',
        'favicons.githubusercontent.com',
        'gist.github.com',
        'github.blog',
        'github.com',
        'github.community',
        'github.githubassets.com',
        'github.global.ssl.fastly.net',
        'github.io',
        'github.map.fastly.net',
        'githubstatus.com',
        'live.github.com',
        'media.githubusercontent.com',
        'objects.githubusercontent.com',
        'raw.githubusercontent.com',
        'user-images.githubusercontent.com',
        'vscode.dev',
        'education.github.com',
        'private-user-images.githubusercontent.com',
    ]
    
    process_domains(domains, max_ips_per_domain=3, output_file="host_cp.txt")
    print("\n✓ 任务完成！")

if __name__ == "__main__":
    main()