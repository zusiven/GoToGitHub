import socket
import datetime as dt
import time
import dns.resolver
import ssl
import logging
from pathlib import Path
from typing import List, Tuple, Set, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ==================== 配置区 ====================

# 全球 DNS 服务器列表
DNS_SERVERS = {
    'Google-US': '8.8.8.8',
    'Google-US-2': '8.8.4.4',
    'Cloudflare': '1.1.1.1',
    'Cloudflare-2': '1.0.0.1',
    'Quad9': '9.9.9.9',
    'OpenDNS': '208.67.222.222',
    'China-Ali': '223.5.5.5',
    'China-Tencent': '119.29.29.29',
    'Japan': '210.146.64.2',
    'Singapore': '165.21.83.88',
}

# 配置参数
class Config:
    DNS_TIMEOUT = 5  # DNS 查询超时（秒）
    DNS_LIFETIME = 3  # DNS 查询生命周期（秒）
    TCP_TIMEOUT = 5  # TCP 连接超时（秒）
    SSL_TIMEOUT = 5  # SSL 握手超时（秒）
    MAX_WORKERS = 15  # 最大并发数
    MAX_IPS_PER_DOMAIN = 3  # 每个域名保留的 IP 数量
    RETRY_TIMES = 2  # 重试次数
    PORT = 443  # 测试端口

# ==================== 数据结构 ====================

@dataclass
class IPInfo:
    ip: str
    delay: float
    dns_sources: Set[str]
    ssl_verified: bool = False

# ==================== DNS 查询 ====================

def query_dns_server(dns_server: str, domain: str, dns_name: str) -> Tuple[str, List[str]]:
    """
    从指定 DNS 服务器查询域名
    
    返回: (DNS名称, IP列表)
    """
    try:
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [dns_server]
        resolver.timeout = Config.DNS_TIMEOUT
        resolver.lifetime = Config.DNS_LIFETIME
        
        answers = resolver.resolve(domain, 'A')
        ips = [str(rdata) for rdata in answers]
        
        if ips:
            logger.debug(f"  ✓ {dns_name}({dns_server}): {len(ips)} IPs")
        
        return dns_name, ips
        
    except dns.resolver.NXDOMAIN:
        logger.debug(f"  ✗ {dns_name}: 域名不存在")
    except dns.resolver.Timeout:
        logger.debug(f"  ✗ {dns_name}: 查询超时")
    except dns.resolver.NoAnswer:
        logger.debug(f"  ✗ {dns_name}: 无应答")
    except Exception as e:
        logger.debug(f"  ✗ {dns_name}: {type(e).__name__}")
    
    return dns_name, []

def get_ips_from_multiple_dns_servers(domain: str) -> Dict[str, IPInfo]:
    """
    从多个全球 DNS 服务器查询获取 IP
    
    返回: {ip: IPInfo}
    """
    logger.info(f"\n{'='*80}")
    logger.info(f"正在查询域名: {domain}")
    logger.info(f"{'='*80}")
    
    ip_dict = {}
    
    with ThreadPoolExecutor(max_workers=Config.MAX_WORKERS) as executor:
        futures = {
            executor.submit(query_dns_server, dns_ip, domain, name): name
            for name, dns_ip in DNS_SERVERS.items()
        }
        
        for future in as_completed(futures):
            dns_name = futures[future]
            try:
                name, ips = future.result()
                for ip in ips:
                    if ip not in ip_dict:
                        ip_dict[ip] = IPInfo(
                            ip=ip,
                            delay=float('inf'),
                            dns_sources=set()
                        )
                    ip_dict[ip].dns_sources.add(name)
                    
            except Exception as e:
                logger.error(f"  处理 {dns_name} 结果时出错: {e}")
    
    logger.info(f"✓ 从 DNS 获取到 {len(ip_dict)} 个不同的 IP")
    
    return ip_dict

# ==================== 连接测试 ====================

def test_tcp_connection_with_ssl(
    ip: str, 
    domain: str, 
    port: int = 443, 
    timeout: int = 5
) -> Tuple[bool, float, bool]:
    """
    测试 TCP 连接和 SSL 握手
    
    返回: (连接成功, 延迟ms, SSL验证成功)
    """
    sock = None
    ssock = None
    
    try:
        # 1. TCP 连接测试
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        start_time = time.time()
        sock.connect((ip, port))
        tcp_delay = (time.time() - start_time) * 1000
        
        # 2. SSL 握手测试
        ssl_verified = False
        try:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            ssock = context.wrap_socket(sock, server_hostname=domain)
            ssl_delay = (time.time() - start_time) * 1000
            ssl_verified = True
            
            logger.debug(f"    ✓ {ip}: TCP={tcp_delay:.0f}ms, SSL={ssl_delay:.0f}ms")
            
            return True, ssl_delay, True
            
        except ssl.SSLError as e:
            logger.debug(f"    ⚠ {ip}: TCP成功({tcp_delay:.0f}ms) 但SSL失败 - {e}")
            # TCP 成功但 SSL 失败，仍然返回这个结果（可能是代理或 CDN）
            return True, tcp_delay, False
            
        except Exception as e:
            logger.debug(f"    ⚠ {ip}: SSL异常 - {type(e).__name__}")
            return True, tcp_delay, False
    
    except socket.timeout:
        logger.debug(f"    ✗ {ip}: 连接超时")
        return False, timeout * 1000, False
        
    except ConnectionRefusedError:
        logger.debug(f"    ✗ {ip}: 连接被拒绝")
        return False, timeout * 1000, False
        
    except OSError as e:
        logger.debug(f"    ✗ {ip}: {e}")
        return False, timeout * 1000, False
        
    except Exception as e:
        logger.debug(f"    ✗ {ip}: {type(e).__name__} - {e}")
        return False, timeout * 1000, False
        
    finally:
        # 确保资源被释放
        if ssock:
            try:
                ssock.close()
            except:
                pass
        if sock:
            try:
                sock.close()
            except:
                pass

def test_ips(
    ip_dict: Dict[str, IPInfo], 
    domain: str, 
    port: int = 443, 
    timeout: int = 5
) -> List[IPInfo]:
    """
    并发测试多个 IP 的连通性
    
    返回: 按延迟排序的可用 IP 列表
    """
    logger.info(f"\n开始测试 {len(ip_dict)} 个 IP 的连通性...")
    
    reachable_ips = []
    failed_count = 0
    
    with ThreadPoolExecutor(max_workers=Config.MAX_WORKERS) as executor:
        futures = {
            executor.submit(test_tcp_connection_with_ssl, ip_info.ip, domain, port, timeout): ip_info
            for ip_info in ip_dict.values()
        }
        
        for future in as_completed(futures):
            ip_info = futures[future]
            try:
                success, delay, ssl_verified = future.result()
                
                if success:
                    ip_info.delay = delay
                    ip_info.ssl_verified = ssl_verified
                    reachable_ips.append(ip_info)
                    
                    ssl_status = "✓SSL" if ssl_verified else "⚠NoSSL"
                    sources = ', '.join(sorted(list(ip_info.dns_sources)[:3]))
                    logger.info(f"  ✓ {ip_info.ip:15s} | {delay:6.0f}ms | {ssl_status} | [{sources}]")
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"  ✗ {ip_info.ip}: 测试异常 - {e}")
                failed_count += 1
    
    # 按延迟排序，优先选择 SSL 验证成功的
    reachable_ips.sort(key=lambda x: (not x.ssl_verified, x.delay))
    
    logger.info(f"\n测试结果: ✓ {len(reachable_ips)} 个可用, ✗ {failed_count} 个失败")
    
    return reachable_ips

# ==================== 域名处理 ====================

def process_domains(
    domains: List[str], 
    max_ips_per_domain: int = 3, 
    output_file: str = "hosts.txt"
) -> None:
    """处理多个域名并生成 hosts 文件"""
    
    logger.info(f"\n{'#'*80}")
    logger.info(f"# 开始处理 {len(domains)} 个域名")
    logger.info(f"{'#'*80}\n")
    
    all_hosts = []
    stats = {'success': 0, 'failed': 0, 'no_ip': 0}
    
    for idx, domain in enumerate(domains, 1):
        logger.info(f"\n[{idx}/{len(domains)}] 处理域名: {domain}")
        
        try:
            # 1. DNS 查询
            ip_dict = get_ips_from_multiple_dns_servers(domain)
            
            if not ip_dict:
                logger.warning(f"✗ 未获取到任何 IP")
                stats['no_ip'] += 1
                continue
            
            # 2. 连通性测试
            reachable_ips = test_ips(ip_dict, domain, Config.PORT, Config.TCP_TIMEOUT)
            
            if not reachable_ips:
                logger.warning(f"✗ 所有 IP 均不可达")
                stats['failed'] += 1
                continue
            
            # 3. 选择最优 IP
            top_ips = reachable_ips[:max_ips_per_domain]
            logger.info(f"\n✓ 为 {domain} 选择了 {len(top_ips)} 个最优 IP:")
            
            for rank, ip_info in enumerate(top_ips, 1):
                ssl_mark = "🔒" if ip_info.ssl_verified else "⚠️"
                sources_str = ', '.join(sorted(list(ip_info.dns_sources)[:2]))
                logger.info(f"  #{rank}. {ip_info.ip:15s} | {ip_info.delay:6.0f}ms | {ssl_mark} | [{sources_str}]")
                all_hosts.append((ip_info.ip, domain))
            
            stats['success'] += 1
            
        except Exception as e:
            logger.error(f"✗ 处理 {domain} 时出错: {e}", exc_info=True)
            stats['failed'] += 1
    
    # 4. 生成输出
    logger.info(f"\n{'#'*80}")
    logger.info(f"# 处理完成")
    logger.info(f"# 成功: {stats['success']}, 失败: {stats['failed']}, 无IP: {stats['no_ip']}")
    logger.info(f"# 共获得 {len(all_hosts)} 条 hosts 记录")
    logger.info(f"{'#'*80}\n")
    
    if all_hosts:
        host_infos = generate_hosts_content(all_hosts)
        write_hosts_file(host_infos, output_file)
        write_hosts_file(host_infos, "hosts.txt")
        
        # 更新 README（如果存在）
        try:
            write_hosts_to_readme(host_infos)
        except Exception as e:
            logger.warning(f"更新 README 失败: {e}")
    else:
        logger.error("没有生成任何 hosts 记录！")

# ==================== 文件输出 ====================

def generate_hosts_content(hosts: List[Tuple[str, str]]) -> str:
    """生成 hosts 文件内容"""
    lines = [
        "# GitHub Hosts - Auto Generated",
        f"# Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"# Total entries: {len(hosts)}",
        f"# DNS Servers: {len(DNS_SERVERS)}",
        "",
    ]
    
    # 按域名分组
    domain_groups = {}
    for ip, domain in hosts:
        if domain not in domain_groups:
            domain_groups[domain] = []
        domain_groups[domain].append(ip)
    
    # 生成内容
    for domain in sorted(domain_groups.keys()):
        lines.append(f"# {domain}")
        for ip in domain_groups[domain]:
            lines.append(f"{ip}\t{domain}")
        lines.append("")
    
    lines.append("# Hosts END")
    
    return "\n".join(lines)

def write_hosts_file(content: str, output_file: str) -> bool:
    """写入 hosts 文件"""
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"✓ 成功写入到: {output_path.absolute()}")
        
        # 显示预览
        lines = content.split('\n')
        if len(lines) > 20:
            preview = '\n'.join(lines[:10] + ['...', f'(省略 {len(lines)-20} 行)', '...'] + lines[-10:])
        else:
            preview = content
            
        logger.info(f"\n文件内容预览:\n{'-'*80}\n{preview}\n{'-'*80}\n")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ 写入文件失败: {e}")
        return False

def write_hosts_to_readme(content: str) -> None:
    """更新 README.md"""
    readme_path = Path("README.md")
    
    if not readme_path.exists():
        logger.warning("README.md 不存在，跳过更新")
        return
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 查找插入位置
        insert_index = -1
        for i, line in enumerate(lines):
            if "### 🚀 更愉快的 clone 🚀" in line:
                insert_index = i + 2
                break
        
        if insert_index == -1:
            logger.warning("未在 README.md 中找到插入标记")
            return
        
        # 构建新内容
        new_content = [
            lines[insert_index],  # 保留原有标题
            "\n",
            "```txt\n",
            content,
            "\n```\n",
            "\n",
            "如果本地第一个失效，建议注释测试下一个\n",
            "\n",
            "希望给你带来友好的体验~\n",
            "\n",
            "Thanks [GitHub520](https://github.com/521xueweihan/GitHub520)\n",
        ]
        
        # 重建文件
        final_lines = lines[:insert_index] + new_content
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.writelines(final_lines)
        
        logger.info("✓ 成功更新 README.md")
        
    except Exception as e:
        logger.error(f"✗ 更新 README.md 失败: {e}")

# ==================== 工具函数 ====================

def load_domains_from_file(filename: str) -> List[str]:
    """从文件读取域名列表"""
    try:
        file_path = Path(filename)
        
        if not file_path.exists():
            logger.error(f"✗ 文件不存在: {file_path.absolute()}")
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            domains = []
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                
                # 跳过空行和注释
                if not line or line.startswith('#'):
                    continue
                
                # 简单验证域名格式
                if '.' in line and ' ' not in line:
                    domains.append(line)
                else:
                    logger.warning(f"第 {line_num} 行格式可能有误: {line}")
            
            logger.info(f"✓ 从 {filename} 读取到 {len(domains)} 个域名")
            return domains
            
    except Exception as e:
        logger.error(f"✗ 读取文件失败: {e}")
        return []

# ==================== 主程序 ====================

def query_ips():
    """主函数"""
    logger.info("="*80)
    logger.info("GitHub Hosts 自动查询工具")
    logger.info("="*80)
    
    # 读取域名列表
    conf_path = Path("conf/domains.txt")
    domains = load_domains_from_file(conf_path)
    
    if not domains:
        logger.error("没有找到需要查询的域名，程序退出")
        return
    
    # 创建输出目录
    save_dir = Path("data")
    save_dir.mkdir(exist_ok=True)
    
    # 生成输出文件名
    timestamp = dt.datetime.now().strftime("%Y_%m_%d_%H%M%S")
    save_path = save_dir / f"{timestamp}.txt"
    
    # 处理域名
    start_time = time.time()
    process_domains(
        domains, 
        max_ips_per_domain=Config.MAX_IPS_PER_DOMAIN, 
        output_file=str(save_path)
    )
    
    elapsed = time.time() - start_time
    logger.info(f"\n{'='*80}")
    logger.info(f"✓ 任务完成！总耗时: {elapsed:.1f} 秒")
    logger.info(f"{'='*80}")

if __name__ == "__main__":
    try:
        query_ips()
    except KeyboardInterrupt:
        logger.warning("\n用户中断程序")
    except Exception as e:
        logger.error(f"\n程序异常退出: {e}", exc_info=True)