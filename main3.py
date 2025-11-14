import socket
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import dns.resolver
import ssl

# 新加坡 DNS 服务器
DNS_SERVERS = {
    # DigitalOcean - Singapore
    's1': '210.16.67.138',
}

# 存储 IP 和对应的 DNS 来源（使用 set 防止重复）
ip_to_dns_source = {}

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
                    for ip in result_ips:
                        ips.add(ip)
                        # 记录 IP 来源（使用 set 防止重复）
                        if ip not in ip_to_dns_source:
                            ip_to_dns_source[ip] = set()
                        ip_to_dns_source[ip].add(name)
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
        
        # 添加到结果，保存 IP 和域名对应关系
        for ip in top_ips:
            all_hosts.append((ip, domain))
    
    # 写入文件
    write_hosts_file(all_hosts, output_file)

def write_hosts_file(hosts, output_file="host_cp.txt"):
    """将所有主机写入 hosts 文件，包含 DNS 来源注释"""
    print(f"\n将结果写入 {output_file}...\n")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# GitHub Hosts\n")
            f.write(f"# Generated at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Total: {len(hosts)} entries\n")
            f.write(f"# DNS Source: Singapore (idcbest.com)\n\n")
            
            for ip, domain in hosts:
                # 获取该 IP 的 DNS 来源
                sources = ip_to_dns_source.get(ip, {'Unknown'})
                source_str = ', '.join(sorted(sources))
                f.write(f"{ip} {domain}  # DNS from: {source_str}\n")
        
        print(f"✓ 成功写入 {len(hosts)} 条记录到 {output_file}")
        
        # 显示文件内容
        print(f"\n{output_file} 内容:")
        print("-" * 80)
        with open(output_file, 'r', encoding='utf-8') as f:
            print(f.read())
        print("-" * 80)
        
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