##  github hosts 本地 DNS 优化
**介绍**
- 问题:
    - github clone 失败、访问速度慢、静态资源加载延迟高
- 方案:
    - 通过不同 DNS 获取可用IP，本地校验, 优化 `git clone` 和访问的体验

- 备忘路径:
    - `windows`: `C:\Windows\System32\drivers\etc\hosts`
    - `linux`: `/etc/hosts`

- 欢迎提交 `issues` 添加更多域名

### 🚀 更愉快的 clone 🚀                



```txt
# GitHub Hosts - Auto Generated
# Generated at: 2026-01-15 01:01:04
# Total entries: 3
# DNS Servers: 10

# github.com
20.205.243.166	github.com
140.82.116.3	github.com
140.82.116.4	github.com

# Hosts END
```

如果本地第一个失效，建议注释测试下一个

希望给你带来友好的体验~

Thanks [GitHub520](https://github.com/521xueweihan/GitHub520)
