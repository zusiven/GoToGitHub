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
# GitHub Hosts
# Generated at 2025-12-02 01:01:45
# Total: 102 entries

20.200.245.247	github.com
20.205.243.166	github.com
185.199.111.153	github.io
185.199.108.153	github.io
185.199.109.153	github.io
185.199.109.133	objects.githubusercontent.com
185.199.108.133	objects.githubusercontent.com
185.199.111.133	objects.githubusercontent.com
185.199.108.133	raw.githubusercontent.com
185.199.111.133	raw.githubusercontent.com
185.199.109.133	raw.githubusercontent.com
140.82.113.26	alive.github.com
140.82.113.25	alive.github.com
140.82.112.25	alive.github.com
20.200.245.245	api.github.com
20.205.243.168	api.github.com
140.82.116.5	api.github.com
140.82.113.22	api.individual.githubcopilot.com
140.82.113.21	api.individual.githubcopilot.com
140.82.114.22	api.individual.githubcopilot.com
185.199.109.133	avatars.githubusercontent.com
185.199.110.133	avatars.githubusercontent.com
185.199.111.133	avatars.githubusercontent.com
185.199.108.133	avatars0.githubusercontent.com
185.199.110.133	avatars0.githubusercontent.com
185.199.109.133	avatars0.githubusercontent.com
185.199.109.133	avatars1.githubusercontent.com
185.199.108.133	avatars1.githubusercontent.com
185.199.111.133	avatars1.githubusercontent.com
185.199.111.133	avatars2.githubusercontent.com
185.199.109.133	avatars2.githubusercontent.com
185.199.108.133	avatars2.githubusercontent.com
185.199.109.133	avatars3.githubusercontent.com
185.199.108.133	avatars3.githubusercontent.com
185.199.111.133	avatars3.githubusercontent.com
185.199.109.133	avatars4.githubusercontent.com
185.199.110.133	avatars4.githubusercontent.com
185.199.111.133	avatars4.githubusercontent.com
185.199.109.133	avatars5.githubusercontent.com
185.199.110.133	avatars5.githubusercontent.com
185.199.108.133	avatars5.githubusercontent.com
185.199.108.133	camo.githubusercontent.com
185.199.111.133	camo.githubusercontent.com
185.199.110.133	camo.githubusercontent.com
140.82.112.21	central.github.com
140.82.113.21	central.github.com
140.82.114.21	central.github.com
185.199.108.133	cloud.githubusercontent.com
185.199.111.133	cloud.githubusercontent.com
185.199.109.133	cloud.githubusercontent.com
20.27.177.114	codeload.github.com
20.200.245.246	codeload.github.com
20.205.243.165	codeload.github.com
140.82.113.21	collector.github.com
140.82.112.22	collector.github.com
140.82.112.21	collector.github.com
185.199.109.133	desktop.githubusercontent.com
185.199.111.133	desktop.githubusercontent.com
185.199.110.133	desktop.githubusercontent.com
185.199.111.133	favicons.githubusercontent.com
185.199.108.133	favicons.githubusercontent.com
185.199.109.133	favicons.githubusercontent.com
192.0.66.2	github.blog
140.82.112.18	github.community
140.82.112.17	github.community
140.82.113.18	github.community
185.199.110.154	github.githubassets.com
185.199.109.154	github.githubassets.com
185.199.111.154	github.githubassets.com
185.199.109.133	github.map.fastly.net
185.199.111.133	github.map.fastly.net
185.199.110.133	github.map.fastly.net
185.199.109.153	githubstatus.com
185.199.110.153	githubstatus.com
185.199.108.153	githubstatus.com
140.82.114.25	live.github.com
140.82.114.26	live.github.com
140.82.112.25	live.github.com
185.199.108.133	media.githubusercontent.com
185.199.111.133	media.githubusercontent.com
185.199.110.133	media.githubusercontent.com
185.199.108.133	user-images.githubusercontent.com
185.199.110.133	user-images.githubusercontent.com
185.199.111.133	user-images.githubusercontent.com
13.107.213.59	vscode.dev
13.107.246.59	vscode.dev
13.107.213.74	vscode.dev
140.82.112.22	education.github.com
140.82.113.21	education.github.com
140.82.112.21	education.github.com
185.199.111.133	private-user-images.githubusercontent.com
185.199.110.133	private-user-images.githubusercontent.com
185.199.109.133	private-user-images.githubusercontent.com
140.82.112.21	token.actions.githubusercontent.com
140.82.114.21	token.actions.githubusercontent.com
140.82.112.22	token.actions.githubusercontent.com
140.82.112.21	copilot-telemetry.githubusercontent.com
140.82.113.21	copilot-telemetry.githubusercontent.com
140.82.112.22	copilot-telemetry.githubusercontent.com
185.199.108.133	pkg.githubusercontent.com
185.199.109.133	pkg.githubusercontent.com
185.199.110.133	pkg.githubusercontent.com

# hosts END
```

如果本地第一个失效，建议注释测试下一个

希望给你带来友好的体验~

Thanks [GitHub520](https://github.com/521xueweihan/GitHub520) 