# 七日杀 V3.4 数据速查

天赋 / 装甲 / 武器 / 模组 四张速查表，纯静态站点，数据全部从本机游戏文件提取。

- 天赋：5 属性 · 50 天赋 · 7 通用 · 19 套书籍 133 卷，带加点模拟
- 装甲：轻 / 中 / 重共 16 套 64 件，逐件词条与 4 件套奖励
- 武器：51 把武器 13 类，伤害 / 射速 / 弹匣 / 射程 / 耐久
- 模组：97 个模组 7 类，按安装接口分类

每张卡片都有自己的品质滑杆（1–6 级），拖动即可查看该等级数值。

## 目录结构

```
7dtd-site/
├─ site/            生成出来的网站（部署的就是这个目录）
│  ├─ index.html    首页导航
│  ├─ perks.html    天赋
│  ├─ armor.html    装甲
│  ├─ weapons.html  武器
│  ├─ mods.html     模组
│  ├─ og.png        微信/QQ 分享预览图 1200×630
│  └─ favicon.png
├─ data/            从游戏文件解析出的 JSON 快照
├─ scripts/         解析与渲染脚本
└─ README.md
```

## 本地预览

```bat
python scripts/build_site.py
cd site
python -m http.server 8000
```

浏览器打开 http://127.0.0.1:8000/ （不要直接双击 html，`<details>` 和跳转在 file:// 下也能用，但用 http 更接近线上）。

## 重新生成

```bat
python scripts/build_site.py
```

部署到线上后，建议带上站点地址重新构建一次，这样分享出去的链接才有预览图：

```bat
python scripts/build_site.py --url https://你的项目.pages.dev
```

## 游戏更新后怎么更新数据

解析需要读取本机游戏文件，只能在装了游戏的电脑上跑：

```bat
python scripts/parse_perks.py     :: -> data/perks_v34.json
python scripts/parse_armor.py     :: -> data/armor_v34.json
python scripts/parse_mods.py      :: -> data/mods_v34.json
python scripts/parse_weapons.py   :: -> data/weapons_v34.json
python scripts/build_site.py --url https://你的项目.pages.dev
```

> 注意：解析脚本里的游戏路径写的是 `E:\Steam\steamapps\common\7 Days To Die`，
> 换电脑需要改脚本顶部的 `GAME` 常量。

## 部署（GitHub + Cloudflare Pages）

### 1. 安装 Git（本机目前没有）

```bat
winget install Git.Git
```

装完重开终端，`git --version` 能出版本号即可。不想装 Git 的话，用 GitHub Desktop 也可以，
或者跳到下面「备用：直接上传」。

### 2. 建仓库并推送

在 GitHub 新建一个**空仓库**（不要勾 README），然后在 `7dtd-site` 目录里执行：

```bat
cd /d C:\Users\RunHao\Documents\ChatGPT\fgo小助手\7dtd-site
git init
git add .
git commit -m "七日杀 V3.4 数据速查"
git branch -M main
git remote add origin https://github.com/<你的用户名>/<仓库名>.git
git push -u origin main
```

### 3. Cloudflare Pages

1. 注册 https://dash.cloudflare.com （免费）
2. Workers & Pages → Create → Pages → Connect to Git → 授权并选中该仓库
3. 构建设置：
   - Framework preset：`None`
   - Build command：**留空**
   - Build output directory：`site`
4. Save and Deploy，几分钟后拿到 `https://<项目名>.pages.dev`

以后每次 `git push`，Cloudflare 会自动发布新版本。

### 4. 让分享预览图生效

拿到域名后，本地跑一次：

```bat
python scripts/build_site.py --url https://<项目名>.pages.dev
git add . && git commit -m "set og url" && git push
```

### 备用：不用 Git 直接上传

Cloudflare Pages → Create → **Direct Upload**，把 `site` 目录整个拖进去即可。
缺点是没有版本记录，每次更新都要重新拖。

## 国内访问说明

`*.pages.dev` 在国内多数网络能打开，但速度和稳定性因运营商、时段而异。
如果以后要求“稳定秒开”，可以换备案域名 + 国内对象存储（阿里云 OSS / 腾讯云 COS），
页面文件完全不用改，只换托管。

## 免责声明

非官方粉丝资料，与 The Fun Pimps 无关。页面中的数值与中文文本取自游戏文件，
版权归原公司所有；本仓库仅用于游戏数据查询。
