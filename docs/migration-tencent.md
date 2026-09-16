# 腾讯云境外静态站迁移方案（本地待审阅）

## 当前状态与边界

- 用户已提供域名 **shapeofai.cn**，目标 URL 为 `https://shapeofai.cn/`。服务器尚未购买，公网 IP、SSH 登录信息、DNS 切换时间均未确定。
- 腾讯云迁移目前只交付本地构建包、脚本、配置和验证证据；没有购买、登录远端服务器、修改 DNS 或申请公网证书。网站优化另行更新源网页与 GitHub Pages 工作流，向现有 Pages 发布不等于完成新域名迁移。
- 已阅读 `README.md` 和 `.github/workflows/pages.yml`。初始 CI 会生成 notebook 并上传整个仓库；主 agent 已独立改成调用本构建器、使用原 GitHub 子路径并只上传 `$RUNNER_TEMP/site-release/public`，不在发布时运行训练。当前参数已在本地验证，**GitHub Actions 全流程尚未验证**。
- 不引入 Node、Docker、数据库、Jupyter 服务或反向代理应用栈。服务器只运行官方 systemd 管理的 Caddy，发布使用 Bash、Python 3 标准库、OpenSSH、curl 和 Ubuntu 自带的 util-linux/flock。

## 选购候选

当前官网价格、地域、网络限制与 DNS 核查记录统一见 [腾讯云境外服务器选型](tencent-server-options.md)，本文不重复维护采购表。默认起步方案仍是新加坡 Lighthouse、Ubuntu Server 24.04 LTS、2 核 2 GB；这是静态站容量判断，不是压测或跨境网络质量承诺。最终地域、套餐和购买必须由用户确认，当前尚未购机。

用户随后确认了新加坡通用型 2 核 2 GB、60 GB SSD、30 Mbps、1,024 GB 月流量、35 元/月的月付方案；本次只确认选型，尚未下单或付款。

## 文件与构建契约

核心只有 `scripts/build_site.py`、`deploy/deploy.sh`、`deploy/Caddyfile`，另有必须人工审阅的 `deploy/public-files.json` 和部署测试。

公开白名单逐项列出文件，无 glob、目录递归复制或 Git tracked-files 自动发布：

- 24 份 `.ipynb` 逐字节保留，24 份已有预渲染 HTML 必须一一匹配。构建不执行 notebook、不修改源网页，也不更新渲染脚本。
- 保留章节、Hub、notebook 导航 HTML，`app.js`、`js/reading.js` 等公开 JS，以及 `hub.css`、`commercial.css`、`course.css` 等样式、favicon 和社交 SVG。构建读取当前工作区内容，不要求这些文件已提交。
- 当前 notebook 图表内嵌在 HTML 中，无需另发 `labs/`。未来新增本地 `assets/` 文件必须审阅后逐项加入白名单；不会自动包含同目录中未列出的文件。
- `.git`、`.github`、`docs`、`scripts`、`deploy`、`labs`、README、私有数据及任意未列出的 HTML/JS/notebook 均不进入公开包。禁止符号链接、路径穿越、缺失文件；缺少 `js/reading.js` 会失败，不会静默省略。
- 白名单保证文件边界，不是敏感内容扫描器。列入清单的 notebook 输出、内嵌源码/数据以及公开 JS 仍须由维护者审阅，不可放入凭据或私人数据。

在仓库根目录执行，仅写新的本地临时目录：

```bash
WORK=$(mktemp -d /tmp/shapeofai-build.XXXXXX)
bash deploy/deploy.sh build --site-url https://shapeofai.cn --output "$WORK/package"
```

`--site-url` 必填，不会猜测 IP 或域名。`--output` 必须是仓库外不存在的新目录；已有目录、覆盖源仓库和输出到仓库内均被拒绝。可用 `--remote-root /srv/ai-thinking-labs` 指定未来服务器目录，但不创建远端目录。

产物：

```text
package/
  public/             # 唯一可作为 Web root 的内容
  site.tar.gz         # 仅包含 public 的文件，可直接传输
  build-report.json   # 源文件/产物 SHA-256、计数、体积和归档校验和，不公开
  Caddyfile           # 已渲染目标域名和 current 路径，不公开
```

构建器依据实际 URL 统一输出 canonical、`og:url`、`twitter:url`、社交图片 URL；消除旧首页重复 canonical。保留其他页面文字、相对链接、查询参数和锚点。旧 GitHub Pages 绝对 URL 与 `/ai-thinking-labs/` 路径引用在产物中改写。社交图片仍使用已有 SVG；部分平台不支持 SVG 预览，迁移不额外生成图片。

生成 `sitemap.xml`、`robots.txt` 和 `404.html`；404 使用 `deploy/404.html` 中文模板和本地 `hub.css`，深层不存在路径也通过根相对样式/目录链接正常显示。sitemap 收录 34 个非跳转内容页，不收录 404、旧索引跳转与 query 跳转工具页。动态 notebook 列表使用其基础页 canonical，24 个阅读页有独立 canonical。直接读取 404 文件或不存在的资源均由 Caddy 返回真实 404，不作 SPA fallback。

构建器支持带路径的 URL。当前 Pages CI 的构建命令等价于：

```bash
python3 scripts/build_site.py \
  --site-url https://zhesun-0209.github.io/ai-thinking-labs/ \
  --output "$WORK/github-package"
```

CI 只上传该包的 `public/`。其 canonical、社交 URL、robots、sitemap 和中文 404 本地样式链接均保留 `/ai-thinking-labs/` 前缀。这些包不生成 Caddyfile，报告的 `deployment_ready: false` 仅表示不适用于腾讯云根域 Caddy 发布；**不影响 GitHub Pages 上传**。腾讯云部署脚本有意拒绝子路径包，Caddy 迁移配置仅服务域名根路径。

## HTTP 与 TLS

- Caddy 自动取得并续期公网 TLS，并把 HTTP 重定向到 HTTPS；必须先由用户配置域名 A/AAAA 指向所购服务器、开放 TCP 80/443、确保 Caddy 数据目录可持续写入。只有真正提供 IPv6 服务才添加 AAAA。不要使用 `tls internal` 代替公网证书。[官方自动 HTTPS 条件](https://caddyserver.com/docs/automatic-https)
- `encode zstd gzip` 做响应协商压缩；传输包另用 gzip 压缩，无需维护双份预压缩资源。[官方压缩说明](https://caddyserver.com/docs/caddyfile/directives/encode)
- HTML、目录首页、robots、sitemap：`no-cache, max-age=0, must-revalidate`，允许存储但每次重用必须验证，保留 ETag/Last-Modified 条件请求。JS/CSS/图片/字体/ipynb：`public, max-age=3600, must-revalidate`，不使用 `immutable`。错误响应 `no-store`。未指纹化资源最多存在一小时旧缓存，未来改动不兼容资源时应由页面维护者同步更换现有 `?v=` 版本。
- `.ipynb` 使用 `application/x-ipynb+json`；现有下载链接保留。不开目录列表。安全头不使用可能破坏现有内联脚本的强 CSP。
- 新域名上的 `/ai-thinking-labs/...` 以 308 跳转到根路径对应 URL，保留 query。**无法让本服务器替旧 GitHub 域名发重定向**；旧域名的迁移公告或跳转需在新站验收后安排。当前不关闭旧站，也不将旧站请求强制转向尚未准备好的域名。
- 404 错误处理保留状态码。[Caddy file_server 文档](https://caddyserver.com/docs/caddyfile/directives/file_server)、[错误处理文档](https://caddyserver.com/docs/caddyfile/directives/handle_errors)

## DNS 现状与切换位置

2026-09-16 审计时通过 Google DoH 核查的公开 DNS 快照如下；没有执行 DNS 写操作：

| 查询 | 公开查询结果 |
| --- | --- |
| `shapeofai.cn` NS | `house.dnspod.net`、`octagon.dnspod.net` |
| `shapeofai.cn` A | NOERROR，Answer 为空，无 A 答案 |
| `www.shapeofai.cn` CNAME | NXDOMAIN |

当前权威 DNS 在 **DNSPod，不是 Cloudflare**。本方案默认保留现有 NS，购机并获用户批准后在当前权威 DNSPod 的 `shapeofai.cn` 区域配置根域 `@` 的 A 记录，值为实际公网 IPv4。不要填示例 IP。当前没有 A 答案，不能宣称域名已指向新服务器；该快照也不代表已核查 AAAA、CAA 或证书状态。

仅在 Cloudflare 中添加记录、却不改变权威 NS，不会完成本域名的公共解析切换。若用户另行选择 Cloudflare，需先盘点并完整迁移现有 DNS 记录（含可能的 MX/TXT 等）、处理 DNSSEC/DS，再在注册商变更 NS，并验证新委派生效；这是另一个需用户授权的迁移步骤，本次不执行。`www` 是否启用也由用户另行选择，当前配置只服务 `shapeofai.cn`。

## 未来人工初始化（本次不执行）

用户先完成选购、取得实际 IP，再通过腾讯云可信控制台准备服务器。下面不是已完成记录，也不要在本机执行这些服务器命令。

1. 采用纯 Ubuntu 24.04 系统镜像。按 [Caddy 官方 Ubuntu 安装指引](https://caddyserver.com/docs/install) 安装签名软件包，并确认 Python 3、curl、util-linux 和 OpenSSH 可用。使用官方 `caddy.service`，服务用户为 `caddy`，禁止长期用 root 跑 `python -m http.server`、手工 root Caddy 或开发服务器。[systemd 服务说明](https://caddyserver.com/docs/running)
2. 用管理员账号创建独立、无 sudo 权限的 `site-deploy` 用户，只给它部署目录写权限；只给 `caddy` 读取公开文件的权限。示例初始化命令如下，目录参数必须与构建包一致：

```bash
sudo adduser --disabled-password --gecos '' site-deploy
sudo install -d -o site-deploy -g site-deploy -m 0755 /srv/ai-thinking-labs
sudo install -d -o site-deploy -g site-deploy -m 0755 /srv/ai-thinking-labs/releases
sudo install -d -o site-deploy -g site-deploy -m 0700 /srv/ai-thinking-labs/incoming
sudo install -d -o site-deploy -g site-deploy -m 0700 /home/site-deploy/.ssh
```

3. 将维护者的**公钥**配置到该用户的 `authorized_keys`，权限 0600、属主 `site-deploy`。私钥只保存在本地仓库外的 `~/.ssh/`，不上传、不提交、不放入包。加密私钥可提前解锁到本地 ssh-agent；不向服务器转发 agent。
4. SSH 防火墙只允许维护者来源 IP；轻量实例防火墙和 OS 防火墙均须检查。对公网开放 TCP 80/443；UDP 443 可选用于 HTTP/3。Caddy 管理端口 2019 不得暴露公网。确认没有其他程序抢占 80/443。
5. 独立验证 host key：从腾讯云可信控制台查看 `ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub` 的指纹。之后才在本地使用 `ssh-keyscan` 收集候选公钥，并逐字核对 `ssh-keygen -lf 候选文件`；一致后保存为 `~/.ssh/shapeofai_known_hosts`。**仅运行 keyscan 不等于验证**，不得自动接受未知或变化的 host key。
6. 人工审阅 `package/Caddyfile`。用已验证 host key 的 SCP 传给管理员（同样必须 `StrictHostKeyChecking=yes`），备份服务器已有 `/etc/caddy/Caddyfile`，安装审阅配置。以 `sudo -u caddy caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile` 验证，再 `sudo systemctl reload caddy`。没有首次 release 时出现短暂 404 属正常；不要把 `package/` 整体作为 Web root。后续普通内容发布无需 sudo 或 reload。
7. 在用户批准的切换窗口内，于当前权威 **DNSPod** 配置根域 A（或先完成另行授权的整套 NS 迁移）。新站证书、网络及内容检查通过后，才另行处理旧站迁移。新域名不自动包含 `www.shapeofai.cn`，本方案未替用户新增该域名。

保留 `/var/lib/caddy` 中的证书状态。日常检查 `systemctl status caddy`、`journalctl -u caddy` 与磁盘容量；配置改动由管理员单独审阅，内容回滚不包含 Caddy 配置回滚。

## 发布与回滚（未来才执行）

脚本默认 dry-run，连 SSH 都不运行；只有显式 `--execute` 才能传输并激活。实际 IP 尚未分配，以下命令要求操作者先设置变量，不给虚构地址：

```bash
: "${SERVER_IP:?请在购机后设置实际服务器 IP}"
: "${WORK:?请指向已审阅的本地构建工作目录}"
SSH_USER=site-deploy
KNOWN_HOSTS="$HOME/.ssh/shapeofai_known_hosts"
SSH_KEY="$HOME/.ssh/shapeofai_deploy"

bash deploy/deploy.sh deploy --package "$WORK/package" \
  --host "$SERVER_IP" --user "$SSH_USER" --known-hosts "$KNOWN_HOSTS" --identity "$SSH_KEY"
# 审阅无误、人工初始化和 DNS 就绪后，操作者才给同一命令加 --execute。
```

默认 SSH 端口 22，可用 `--port` 指定其他端口。SSH/SCP 固定 `StrictHostKeyChecking=yes`、指定的 known_hosts、`BatchMode=yes`、`ForwardAgent=no`，忽略 SSH config 中可能不安全的覆盖设置。脚本拒绝 root 用户和仓库内的私钥路径。

发布过程：校验 gzip 归档 SHA-256，上传非公开 `incoming/`，flock 拒绝并发激活，验证归档条目/类型/大小/内容哈希后解包到新 release；拒绝目录穿越和链接。原子切换 `current`，从服务器回环地址用目标域名/SNI 和**正常证书验证**请求 Hub 与一份 notebook，逐字节校验响应。失败或可捕获中断会恢复旧 `current`；首次发布失败则撤销 `current`。没有 `curl -k`。

```text
/srv/ai-thinking-labs/
  current -> releases/RELEASE_ID/public
  previous -> releases/PREVIOUS_ID/public
  releases/RELEASE_ID/public/
  releases/RELEASE_ID/build-report.json
  incoming/
```

脚本输出新旧 release ID。手动回滚需填入真实保留 ID，不是日期占位符：

```bash
: "${RELEASE_ID:?填入发布日志中待恢复的真实 release ID}"
bash deploy/deploy.sh rollback --release "$RELEASE_ID" --site-url https://shapeofai.cn \
  --host "$SERVER_IP" --user "$SSH_USER" --known-hosts "$KNOWN_HOSTS" --identity "$SSH_KEY"
# 同样默认 dry-run；确认后加 --execute。
```

回滚先校验保留文件集与哈希，拒绝不同 site URL，再切换并健康检查。所有 release 保留，不自动清理；人工只清理既非 current 也非 previous 的旧 release，保留至少两个可用版本。若进程被 SIGKILL、机器断电或 SSH 上传中断，可能留下 staging/incoming；先检查 current 和 release 日志再清理，不能宣称断电事务保证。

## 验收与证据

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s deploy/tests -v
bash -n deploy/deploy.sh
# 可选：指定本地 Caddy 可执行文件，增加回环 HTTP 实测；不绑定公网端口，不申请证书。
PYTHONDONTWRITEBYTECODE=1 CADDY_BIN=/绝对路径/caddy python3 -m unittest discover -s deploy/tests -v
```

构建测试覆盖白名单诱饵、缺失文件/符号链接/路径穿越拒绝、24+24 文件完整性、notebook 字节不变、实际域名与旧 base path 改写、canonical/社交字段、sitemap/robots/404、归档可重现、静态本地链接和源码哈希。发布模拟运行真实远端脚本主体，但模拟 curl 与 GNU mv/flock 兼容层，不接触 SSH 或服务器。

本地实测记录见 [deploy/validation.md](../deploy/validation.md)。它不是上线证明。购买后仍须外网独立验证 DNS、HTTP→HTTPS、证书链/续期、80/443 可达性、缓存压缩头、24 个下载链接和课堂交互，再认定迁移完成。
