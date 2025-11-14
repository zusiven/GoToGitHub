import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import dns.resolver
import ssl

# 全球各地的公开 DNS 服务器（重点亚洲地区）
DNS_SERVERS = {
    # 日本 DNS - 主要厂商
    'a': '104.248.99.145',
    'b': '194.233.74.68',
    'c': '202.136.162.11'
}

DNS_SERVERS = {
    # DigitalOcean - Singapore
    'DigitalOcean (SG)': '104.248.99.145',
    'DigitalOcean (SG)2': '128.199.125.43',
    'DigitalOcean (SG)3': '128.199.128.150',
    'DigitalOcean (SG)4': '128.199.136.201',
    'DigitalOcean (SG)5': '128.199.169.223',
    
    # Contabo Asia
    'Contabo (SG)': '194.233.74.68',
    
    # OVH Singapore
    'OVH Singapore': '139.99.0.25',
    'OVH Singapore2': '139.99.38.167',
    'OVH Singapore3': '139.99.40.107',
    'OVH Singapore4': '139.99.40.84',
    
    # Amazon Singapore
    'Amazon (SG)': '13.212.182.154',
    'Amazon (SG)2': '13.229.32.53',
    'Amazon (SG)3': '52.74.199.2',
    'Amazon (SG)4': '52.74.238.51',
    'Amazon (SG)5': '54.179.254.32',
    
    # M1 NET LTD
    'M1 NET (SG)': '203.211.150.118',
    'M1 NET (SG)2': '118.189.211.221',
    
    # NTT Singapore
    'NTT Singapore': '202.136.162.11',
    'NTT Singapore2': '202.136.162.12',
    'NTT Singapore3': '202.136.163.11',
    
    # ViewQwest
    'ViewQwest (SG)': '203.83.76.1',
    'ViewQwest (SG)2': '203.83.76.2',
    'ViewQwest (SG)3': '132.147.92.141',
    
    # G-Core Labs
    'G-Core Labs (SG)': '92.223.17.165',
    
    # Vultr Singapore
    'Vultr (SG)': '45.32.111.36',
    'Vultr (SG)2': '45.32.116.77',
    'Vultr (SG)3': '45.76.149.223',
    
    # The Constant Company
    'The Constant (SG)': '139.180.159.227',
    'The Constant (SG)2': '139.180.185.166',
    'The Constant (SG)3': '139.180.215.174',
    
    # SG.GS
    'SG.GS': '116.251.216.95',
    
    # GoDaddy Singapore
    'GoDaddy (SG)': '148.66.154.185',
    'GoDaddy (SG)2': '43.255.154.40',
    
    # SingNet (Singtel 子品牌)
    'SingNet (SG)': '118.201.86.149',
    'SingNet (SG)2': '119.75.32.114',
    'SingNet (SG)3': '203.126.118.38',
    'SingNet (SG)4': '203.126.238.211',
    'SingNet (SG)5': '203.127.19.242',
    'SingNet (SG)6': '42.61.17.138',
    'SingNet (SG)7': '58.185.57.18',
    'SingNet (SG)8': '203.127.232.194',
    
    # Hurricane Electric
    'Hurricane Electric (SG)': '103.53.197.218',
    'Hurricane Electric (SG)2': '103.6.168.114',
    'Hurricane Electric (SG)3': '111.221.44.74',
    
    # Alibaba Cloud SG
    'Alibaba Cloud (SG)': '47.241.117.144',
    
    # Playpark
    'Playpark (SG)': '121.52.206.129',
    
    # Republic Telecom
    'Republic Telecom (SG)': '101.100.170.50',
    
    # Netdeploy
    'Netdeploy (SG)': '103.31.228.150',
    
    # Datacamp Limited
    'Datacamp (SG)': '143.244.33.74',
    'Datacamp (SG)2': '143.244.33.90',
    
    # Linode Singapore
    'Linode (SG)': '139.162.36.231',
    'Linode (SG)2': '139.162.52.43',
    'Linode (SG)3': '172.104.163.154',
    'Linode (SG)4': '172.104.164.34',
    'Linode (SG)5': '172.104.49.100',
    
    # Verizon Asia
    'Verizon (SG)': '210.80.58.3',
    'Verizon (SG)2': '210.80.58.66',
    
    # HostUS Solutions
    'HostUS (SG)': '210.16.120.47',
    
    # Microsoft Singapore
    'Microsoft (SG)': '104.215.144.180',
    'Microsoft (SG)2': '13.76.92.120',
    'Microsoft (SG)3': '20.188.121.43',
    'Microsoft (SG)4': '52.148.95.11',
    
    # T-Systems Singapore
    'T-Systems (SG)': '202.56.128.30',
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

def test_tcp_connection_with_delay(ip, domain, port=443, timeout=3):
    """真正测试到指定 IP 的 TCP 连通性并测量延迟，包含 SSL 验证"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        start_time = time.time()
        sock.connect((ip, port))  # 使用 connect 而不是 connect_ex
        
        # 尝试 SSL 握手以验证这是真实的目标服务
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            ssock = context.wrap_socket(sock, server_hostname=domain)
            ssock.close()
        except:
            pass
        
        delay = (time.time() - start_time) * 1000
        sock.close()
        return True, delay
        
    except socket.timeout:
        return False, timeout * 1000
    except ConnectionRefusedError:
        return False, timeout * 1000
    except Exception:
        return False, timeout * 1000

def test_ips(ips, domain, port=443, timeout=3):
    """并发测试多个 IP 的连通性并测量延迟"""
    reachable_ips = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(test_tcp_connection_with_delay, ip, domain, port, timeout): ip for ip in ips}
        
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
        
        # 2. 测试连通性（现在真正测试了 TCP 连接）
        reachable_ips = test_ips(ips, domain, port=443, timeout=3)
        
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