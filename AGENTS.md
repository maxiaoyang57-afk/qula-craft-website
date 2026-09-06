# QulaCraft 独立站(qulacrafts.com)

## 🔒 生产询盘邮箱保护（2026-09-06）
- GitHub `main` 是唯一生产源码；禁止从旧 ZIP、Claude/Codex 临时目录或其他本地副本直接执行 Vercel Production 部署。
- 唯一询盘地址是 `sales@qulacrafts.com`；旧地址 `sale008@sola-craft.com` 与主邮箱 `monica@qulacrafts.com` 均禁止写入网站表单或 `mailto:`。
- Vercel 每次构建会运行 `node scripts/check-inquiry-email.mjs`；四个 FormSubmit 表单、全站 `mailto:` 或 AJAX 防护不一致时构建必须失败。
- GitHub Actions 每 30 分钟检查一次生产首页；检查失败表示生产域名可能被旧部署覆盖，应立即把 GitHub `main` 的最新成功部署重新设为 Production。

## 🏷 品牌改名(2026-07-15,已全站落地)
- 品牌显示名 **Qula Craft**(logo `<span>Qula</span> Craft`),域名 **www.qulacrafts.com**(已注册,Vercel 购入)
- **三个不动**:法定名 Yiwu Sola Craft Co., Ltd.(真实注册公司,版权行/schema legalName 保留)、邮箱 sales@qulacrafts.com(当前询盘收件地址；换邮箱要同步 mailto+formsubmit+schema 三处并重激活)、阿里店 solagarland 链接
- 版本 ?v=20260715;包 QulaCraft_独立站网站包_品牌域名版_20260715.zip
- 本地预览常驻:.claude/serve8101.cmd(**python.exe 别用 pythonw——无 stderr 会让 http.server 响应中断**);开机自启计划任务需管理员,待 Jacken 手动

<!-- 以下历史沿用 SolaCraft 名称记录 -->
# SolaCraft 独立站(sola-craft.com)

## ⚡ 速查(高频改动先看这)
- **产品数据源**:`assets/data/product-catalog.json`(9分类172SKU,源=客户Excel经Codex解析,Codex工作区 E:\Codex\workspace\active\SolaCraft_软陶片_接手优化_20260709 **只读**)
- **⚠️ 分类页生成器已不存在**(restructure_catalog.py 在旧会话 scratchpad,随会话销毁,2026-07-24 实证):分类页现状=手改 HTML;要再批量重构需重写生成器。改产品数据仍以 product-catalog.json 为源
- 分类页映射:polymer-clay-slices→polymer-clay-sprinkles.html / plastic-beads→acrylic-beads.html / plastic-sequins→glitter-sequins-fillers.html(保留原URL);slime-charms/pvc-plastic-charms/beads-for-pens/keychain/jewelry-accessories 同名新页
- 多AI协同:动工前读 E:\Claude\COORDINATION.md 认领
- 客户问过"加隐藏关键词 fimo clay"→ **已否**:cloaking违规+FIMO是Staedtler商标;合规替代=正文自然写 polymer clay/oven-bake clay 通用词

义乌手工艺材料 B2B 询盘站 — Yiwu Sola Craft Co., Ltd.(软陶撒/切片、树脂挂件、亚克力珠、闪粉亮片、季节主题、私标包装)。
买家:史莱姆品牌 / 美甲 / 珠宝 DIY / 手机壳 decoden / 派对 / DIY 套装。
**别人发来的成品包做二次优化**,非自营站。18 页英文静态 HTML(17 内容页 + thank-you.html),无构建步骤。

## 真实数据(已全站替换,2026-07-06)
- 域名:**sola-craft.com**(带连字符;旧占位 solacraft.com 已清零)
- 邮箱:sales@qulacrafts.com
- WhatsApp:+86 186 3202 6595(wa.me/8618632026595)
- 公司:Yiwu Sola Craft Co., Ltd.,义乌;**TüV 莱茵实地认证**
- 阿里店铺:https://solagarland.en.alibaba.com/ (footer 有链接,schema sameAs)

## 本地预览
- launch.json 配置名 `solacraft`,端口 **8101**(工作区根 E:\Claude\.claude\launch.json)
- 本会话 preview_screenshot 曾坏死:验证用 curl + preview_snapshot/eval,别死磕截图

## 已完成(07-06 全量优化,审计 50→代码侧打满)
- 表单 ×4 接 **FormSubmit**(action=formsubmit.co/sales@qulacrafts.com,_captcha=false+蜜罐,成功跳 thank-you.html)
- GA4 脚手架:`assets/js/analytics.js` — **把 G-XXXXXXXXXX 换成真实 ID 即全站生效**(含 whatsapp_click/email_click/phone_click/generate_lead 事件)
- canonical/hreflang/og:url/og:site_name/twitter card/theme-color ×17;og:image 全绝对 URL+每页专属图
- Organization schema 扩充(legalName/TüV/sameAs/E164 电话);4 分类页 ItemList→Product;seasonal 补 CollectionPage
- 152 张 img 全回填 width/height;hero fetchpriority=high;3 张大图压缩(495→271/433→246/371→216KB)
- 邮箱/电话/WhatsApp 全部可点击(mailto:/tel:/wa.me)
- 建站说明口吻文案清零(约 20 处改写成买家视角);假 500+ 数字与假社交图标换成 TüV/阿里店真事实
- products.html 筛选器由 demo 变真:标签页+复选框+实时计数(main.js)
- sitemap 干净根 URL+新域名+分级 priority;robots 同步
- **资源引用带版本参数 `?v=20260706`** — 改 CSS/JS 后必须升版本号,否则浏览器缓存吃掉更新(本次实测踩坑)

## 流量增长层(07-06 二轮,SEO/AEO/AI推荐/转化)
- **6 篇买家指南**(guide-*.html,真行业数字:尺寸段/克重换算/包装单价带/季节截单月历/标签措辞模板):resources 页 6 张原假链卡(全指向faq.html)已接真页
- 主关键词页:guide-clay-slices-vs-resin-charms-slime.html 承接 "fake sprinkles for slime"
- 每篇:直答 answer-box(AEO)+ Article/Breadcrumb/FAQ schema + 内链≥8 + CTA(quote预填+WA预填)
- 内链网:9 页挂相关指南条 + 首页 teaser 3 卡 + 全站面包屑 span→真链接(21页)
- 转化:48 个产品卡加 WhatsApp 预填直达线(.wa-line);移动端底部固定 CTA 条(Get Quote+WhatsApp,23页;thank-you 刻意排除——刚提交完不再推quote)
- AI 抓取:robots.txt 显式放行 GPTBot/OAI-SearchBot/ClaudeBot/PerplexityBot/Google-Extended 等;llms.txt 全量(联系方式与站上一致)
- sitemap 23 URL;闸门全过(0死链/JSON-LD全解析/标签平衡/占位零回归)
- **部署注意:别开 Vercel cleanUrls**(站内链接全是相对 .html,开了会 404;见 _lib/SITE-STANDARDS.md 坑库)

## 内容真实化(07-06 三轮,去AI味终审)
- **真公司数据全部落位**(来源=登录态浏览器抓 solagarland.en.alibaba.com 档案页,WebFetch抓不到要用浏览器):注册2016-07-07/1000㎡/2产线6设备/6500+SKU/年上新100款/北美40%东亚30%东欧20%/1831单$450k+/99.3%准时/≤3h响应/4.8分300评
- **真认证**(店铺档案列的批次报告):EN 71/ASTM F963/CPC/CPSC-CH-E1002/REACH/CE/RoHS + BSCI(25-0354231)+ TüV实地——quality-safety页/faq/安全指南/Organization schema已写入,措辞"batch reports available on request"
- **6张真车间照片**替换AI工厂图(_ref-alibaba/共19张实拍,已转webp同名替换:库存墙/手工称重打包/分拣/质检/散料/装袋线),alt+尺寸属性同步
- **14处建站批注清零**(about整页重建/factory/quality/applications/customization/quote/private-label/seasonal),about换真故事+真数字统计格
- **FAQ 全站去重**:58个独立问题零重复,8页各配专属问题(答案织入真数据:1 bag起订/≤3h/认证清单),resources补齐FAQPage schema
- 首页hero-proof换真数字(≤3h/99%+/1,800+),foundingDate进schema,llms.txt同步真数据
- _ref-alibaba/ 与 _ref-competitors/(竞品参考图板,175张,仅参考绝不上站)与 _scene-intake/ 是素材目录,打包/部署一律排除

## 终修轮(07-09 复检80分后,P1×5+P2 全清,22闸门过)
- **真搜索**:products hub 搜索框+main.js 前端搜 172 SKU(fetch assets/data/product-catalog.json,**该文件是运行时依赖,打包必须带**);支持 ?search= 参数,SearchAction schema 由假变真
- 孤儿 FAQPage 清除(applications/customization);404.html(noindex)+privacy-policy+terms 三页,页脚法务链接×32,表单加同意声明
- 无障碍:文本粉 #cc3868(4.85:1)/绿 #0e7d5c/#127a63 提对比度;skip-link×32;apple-touch-icon
- seasonal 页挂 15 张真节日 SKU 卡;applications 补笔珠/礼品店 2 场景卡;3 页网格标题与 h1 命名统一
- vercel.json(cleanUrls:false 显式+安全响应头);sitemap 30 URL;**资产版本已统一 ?v=20260710,再改 CSS/JS 记得升**
- 交付包:SolaCraft_独立站网站包_上线终版_20260709.zip(16.68MB/269文件,32页)

## 标准补全轮(07-11,按 SITE-STANDARDS v2 checklist 补齐,17 闸门过)
- **ux-pack 接入 ×32 页**(assets/css/ux.css + assets/js/ux.js;**本站副本给 initBackTop 打了守卫补丁**让位站内自带返回顶部,升级 ux-pack 时别覆盖丢失):入场29节点/3D卡片/灯箱/表格横滑实测过
- **询盘篮 Quote Basket**:172 产品卡 + JS 搜索卡带"＋Add to inquiry list",localStorage qcBasket,浮动chip,quote 页面板+textarea 自动预填 SKU 清单,提交后清空(闭环实测:加2→删1→预填同步)
- **文件上传**:quote/customization 表单 name="attachment" + multipart(FormSubmit 支持)
- 首页认证徽章条(TüV/BSCI/EN71/ASTM/CPC/REACH/CE/RoHS)+ 99%+ 数字滚动标记
- Inter 字体非阻塞加载 ×32(media=print onload);GA4 改 load 后延迟 1.2s 注入(事件先进 dataLayer 队列);scroll passive
- **docs/关键词-页面地图.md 已存档**(checklist#1,七类词→页面 + 缺口条件解锁 + 需手动清单)
- 版本 ?v=20260711;交付包 _标准完善版_20260711.zip(16.70MB/271文件)
- **有意不做**:172 个薄 PDP(触 scaled-content 红线,待客户给每 SKU 规格再上);圆角多档(继承模板,视觉已验收)

## 场景图接入 + 内容重规划(07-20)
- 客户交 25 张 AI 生成图 → 24 张已入库(`_scene-intake/_已处理原图-20260720/` 存原图),55MB→3.5MB
- 图分四类:flatlay 宽幅×6(hero用) / 真人场景×10 / 零售店场景×3 / 卖点信息图×5
- **首页新增「Retail Ready」版块**(零售就绪:小袋分装/货架格式/Mix&Match主题)——这是这批图带来的新叙事维度,补上了"我们的货怎么进你的店"
- 首页 hero 换 flatlay-slime-supplies;首页6+applications 8 张应用卡换真人场景图;6 个分类页 hero 换 flatlay;包装页加 4 张零售真图
- **⚠️ #15 认证信息图已扣下不上站**:图上印 CPSIA/Prop 65,我们无 Prop 65 证据(真实持有 EN71/ASTM F963/CPC/CPSC-CH-E1002/REACH/CE/RoHS/BSCI/TüV)。要用必须先重做图或拿到证据
- 版本 ?v=20260720

## 图片展示排查 + 导航下拉(07-20)
- **零裁切改造**:全站 7 类图片容器原为 `object-fit:cover`+固定高度,实测 hero 裁 36%/季节卡裁 40%/产品卡裁 35% → 全改 `aspect-ratio`+`contain`+浅色底;季节卡从"图作背景+文字压图"改成"上图下文"。10 页 172 图实测 0 裁切,375/768px 同样 0 溢出
- **遮挡修复**:hero badge 原绝对定位压图 13% → 移到图下方独立条
- **🔴 数字滚动 bug**:ux-pack 的 stat-num 卡在中间值(准时率显示 42%,真值 99%)→ **已拆掉动画改静态真值**。教训:数字准确性 > 动画效果,信任数据别上滚动动画
- **封面图代表性**:分类封面原机械取"每类第 1 个 SKU",Slime Charms 撞上木蜂蜜勺(RW5306,疑客户 Excel 归类错误)→ 改人工挑选;另有 2 个封面分辨率不足(211px 塞 391px 容器)→ 换 736px 高清
- **低分辨率清单**:172 图中 46 张 <400px,已导出 `docs/低分辨率产品图清单.md`(带 SKU+阿里链接)待客户补高清图
- **Products 导航下拉**:9 类目+带数量角标+"All 172 items",32 页全覆盖;桌面 hover 展开(带 `:after` 桥接区防菜单闪断)、移动端 `position:static` 展平、`:focus-within` 键盘可达、`aria-haspopup`
- 版本 ?v=20260720g。**改导航前必须先枚举变体**(本次 32 页有 2 种写法:`nav-link ` 带尾空格 与 thank-you 的 `nav-link` 无空格,漏了会少改页)

## 首页对标 luxopack 扩充(07-20,12→15 区块)
- 已落 6 项(闸门全过):①首屏采购参数条(1 bag/3-7天/北美东亚东欧) ②工艺 5 项对比表"Same Sprinkles. Five Things That Aren't."(厚度/色牢度/碎屑/配比/气味,每项带自测法) ③终端成品故事"What Your Customers Actually Unbox"4 卡 ④FAQ 拆两组(Before You Order 采购型 4 问 + Product Knowledge 知识型 4 问,schema 同步 8 问) ⑤指南 Updated 标 ⑥报价承诺(≤3h 首回/12-24h 带箱规正式报价,联系卡口径已同步)
- 规划文档:docs/首页规划-对标luxopack.md(含 luxopack 14 区块实拆)
- **待口径的 🟡 三项**:工厂直供vs多层转手对比表(措辞要稳,不点名阿里)/报价区放哪位销售真人/是否授权引用阿里店 4.8分·300评·1831单 做数据条
- 版本 ?v=20260720i

## PDP 已全量上线(07-24,172 页,p-<assetKey>.html)
- **生成器 = 本轮固化的正式脚本**(scratchpad gen_pdp.py 已废弃,正式版在 `scripts/gen_pdp.py`,重跑=重生成全部 172 页):页壳克隆 products.html;每页=面包屑+hero(H1全标题)+图库(01主图fetchpriority+02-04 lazy,尺寸PIL实测)+规格表(specs真值,NONE类值跳过,无Material显示"confirmed at quotation")+**价格块**+CTA(SKU预填quote/WA/询盘篮)+同类相关×4+Product/BreadcrumbList schema
- **价格口径(Jacken 07-24 拍板"只上 From $ 起步价")**:⚠️ **priceTiers 有噪声行**(如 ym109-2 混入"50 bags $0.04"三连,YX097 "$0.05/kg")——**绝不能取 min**;正式规则=取与 MOQ 匹配的档、否则首档(listing 门面价),单位白名单 bag/pcs/piece/pair/set/box/roll 才展示,重量/空单位/价<$0.03 一律降级"Quoted by pack and quantity"。结果:135 页展示 From 价 / 37 页降级
- **三处接链**:9 分类页+seasonal 15 卡(img+h3 包链,样式 inherit 零视觉变化;seasonal 卡无 SKU pill,从 quote 链接提取)+ main.js 搜索卡(p.pdp 字段);**catalog.json 已注入 pdp 字段**(备份 product-catalog.backup-20260724.json;YM109 重复 SKU 靠 catalogIndex-1 对齐,**Codex 台账 catalogIndex 是 1-based**)
- sitemap 31→**203**;llms-full.txt(172 行带价格/MOQ)+llms.txt 头部引用
- 闸门:205 页 JSON-LD 全解析/死链 0/资源 0 缺/标题唯一且≤72/main.js node --check 过/curl 200(含 p-ym109-2、p-rx311-313 特殊 slug)
- **【07-24 二次质量增强,gen_pdp.py 改 2 处+重生成全 172 页】**:①**price_min 修复首行噪声档丢价 bug**——无有效单位的"$20 噪声行"在前时旧逻辑直接 return None 丢价,改为跳过噪声取第一个白名单单位档(仍是门面价、非 min)→**36 页恢复起步价**(SLM/YX/CDK/MA 系首行都是无单位 $20 噪声),现 171 页有价/仅 1 页降级;dry-run 证已有价的 135 页零变动、0 假价、0 丢失 ②**desc 加分类语境** `Wholesale {category}`(cname 放靠前防 158 截断)→**同产品跨分类的 SLM680/YX3531 desc 去重**(两 SKU 同一阿里 listing,title 带 SKU 本不重,但 desc/h1 同源;现 desc 0 重复,h1 仍 1 组=同产品可接受) ③复扫 172 页:重复 title/desc/正文指纹雷同全 0、字数 322-406 无薄页、Product/Breadcrumb schema+图全绿
- **数据层单位不一致(待客户核对,非生成器 bug)**:极少数 SKU 阿里 listing 的 priceTier 单位≠MOQ 单位(SC048 抛光布 `From $0.06/bag · MOQ 100 pieces`、CDK001208 `$0.18/pieces · MOQ 1 bag`)——真实抓取值,有"full tier table comes back with your quote"兜底文案,**不强行统一(会编造)**,记录待客户确认真单位

## PDP 数据台账(07-24 验收,留档)
- **数据终态(07-24 验收)**:pdp-data.json **172/172 全 ok、failed=0**。Codex 三轮采集(00:21-03:05)出 152 ok,Claude 救援 20 条"missing_material 假失败"(阿里页面本身无 Material 键,其余字段全齐;补下图+翻 ok,带 salvageNote 标记)。688 张图全 WebP<300KB、全被 imagesLocal 引用、172 个 SKU 目录
- **交接单§六闸门全过**(Material 按救援口径放宽:20 条无 Material 带 salvageNote,PDP 模板对缺失键留空不编造);已知小缺口:MA302 无 moq(唯一一条)、priceTiers 0 缺
- **下一步=生成 172 个 /p-<sku>.html**(slug=SKU 定死不可改):面包屑→hero(主图+核心参数)→多图→规格表→MOQ/价格阶梯→应用场景→FAQ→相关产品→CTA,挂 Product/Breadcrumb schema,接分类页卡+sitemap 31→203;**价格上不上站等 Jacken 拍板**
- 采集期教训:**回执/"终版"都不等于收工,看板行没挪就可能再来一轮**(02:35 终版回执后 Codex 又跑了两轮补采;Claude 救援脚本差点用旧内存数据覆盖新成果,靠"写盘前杀进程"躲过)。判断收工=pdp-data 条数 172+台账停更+对方确认
- 已证伪:URL slug 反解标题无增益;阿里页逐条 CDP 抓会卡死渲染器(45s超时)——批量采集永远交 Codex 脚本
- RW5306 木蜂蜜勺归类存疑;重复 SKU YM109 两款均真实(bingsu beads),图片目录以 assetKey 区分(ym109/ym109-2)

## 首页 9 类目封面 v2(07-25,Codex 生成 + Claude 验收)
- **Codex 产出并已自行接入首页**(9 张实拍风格封面,内置 ImageGen;素材对应清单见交付目录 category_cover_plan.csv)。站用目录 `assets/images/category-covers-v2/`,交付母版在 `E:\Codex\codex_finish\SolaCraft_类目导航封面_20260725`
- 内容修正到位:软陶=成品切片(非原料泥条)/史莱姆=成品罐场景/笔珠=完整成品笔/钥匙扣=组装成品
- **Codex 加了针对性 CSS**(style.css 末尾):`.image-card figure img[src^="assets/images/category-covers-v2/"]{object-fit:cover}` —— 对 v2 封面**有意覆盖** 07-20 的零裁切 `contain` 规则。1200×1200 正方形进 4:3 容器上下各裁 12.5%,**已用 PIL 模拟真实裁切逐张验收:9 张主体全部完整无切头切脚**,构图饱满,判定合理
- **Claude 验收发现并修掉的部署问题**:9 张 PNG 母版(每张 ~2MB)+ contact-sheet.jpg 被一起放进站点目录,**部署会白传 20.5MB**。已逐个字节比对确认交付目录有完整备份后清理 → 目录 22.1MB→**1.63MB**(只留 9 张 WebP + README);复核 HTML/CSS/sitemap 三处零死链
- 验收其余全绿:width/height 标注与真实图 100% 相符(零 CLS)、alt 9 条全有意义且不重复、curl 200
- **遗留不一致(待定)**:`products.html` 的同 9 张品类卡仍用旧产品实拍图(`images/catalog/...`),与首页新封面不一致;未擅自改,等 Jacken 决定是否统一

## 品类卡 CTA + 角标改版(07-25,Jacken 要求"去数字 + 更显眼")
- **CTA**:文字链 `<span class="text-link">View all 20 items →</span>` → **满宽胶囊按钮** `<span class="btn btn-card cat-cta">View Products →</span>`(复用站内已验证组件 .btn-card,与 PDP 相关产品卡同款;**外层已是 `<a>`,内层必须用 `<span>` 不能嵌 `<a>`**)
- **角标**:`20 stock items` → **`In Stock`**(去数字,保留角标视觉锚点与"现货供应"这个 B2B 卖点)
- 新增 CSS(style.css 末尾):`.image-card .cat-cta{width:100%;justify-content:center}` + `.image-card:hover .cat-cta{填充粉色渐变+白字+投影}` —— 卡片悬停时按钮点亮,强化可点感
- 覆盖 **index + products 各 9 处 = 18 处**(两页品类卡同源,改必须同改);`?v=` 已升 20260725
- **有意保留数字的地方**:llms.txt 的 "172 live stock items"、ItemList schema 的 numberOfItems —— 那些是给机器/AI 读的,数量是有效信息
- 实测:9 卡等高 538px、角标与 CTA 全站统一、页面零"N stock items"残留、无横向溢出

## Resources 内容扩展:7 → 13 篇指南(07-25,全部达 v3 §4 标准)
- **选题依据不是拍脑袋**:pullpush.io 存档 API 挖 246 个真实 Reddit 帖(r/Entrepreneur / r/smallbusiness / r/EtsySellers 等),105 帖含 B2B 采购痛点。词频 `supplier 39 · alibaba 33 · customs 25 · wholesale 24 · import 23 · MOQ 16 · sample 9 · duty 9` —— **买家不缺产品知识,缺的是「怎么不被坑」**,而这一整块站内原本 0 覆盖(印证 07-24 排查报告的付款/物流黑洞)
- **新增 6 篇**(生成器 `scripts/gen_guides.py` + 内容 `guides_content.py`/`guides_trade.py`,数据驱动可重跑):
  - 产品长尾(吃真实 SKU 数据):beadable-pen-beads(22 SKU 最深线原本零指南)/ bingsu-beads-slime-fillers / decoden-supplies(banner 主图的承接页)
  - 交易信任簇(填黑洞):paying-a-craft-supplier / importing-craft-supplies / samples-and-inspection
- **存量 7 篇改造**:补配图(复用站内真图,原 0 图)+ 补第 2 条权威外链 + 补第 3 张相关阅读卡(顺带打通新旧内链)+ 两篇补到 ≥800 词
- **13 篇终检全绿**:词数 963–1252 / 各 ≥2 条权威外链 / 配图 / 相关阅读 ≥3 / FAQ+schema / 可见 Updated / answer-box / 0 死链 / sitemap 全覆盖
- **⚠️ 发现:存量 7 篇原来的「外链」全是自家阿里店** —— 那不算权威引用,等于 0 条。别把自家链接当外部权威源统计
- **外链纪律(受阻实录)**:2026-07-25 逐条 WebFetch 验证正文,**可用**=ICC Incoterms(Incoterms®2020,1936 首发)/ trade.gov HS 码(6 位国际、美国 10 位)/ Wikipedia Polymer clay(PVC 基、129–135°C 固化)、PET(RIC 1、不溶于水)、Resin casting(**柔性模具 25–100 件后失细节** —— 这条解释了定制 MOQ 与批次差异,是全批最有说服力的引用);**不可用**=ASTM/CPSC/ECHA/CBP 反爬 403、EUR-Lex 正文异步。**curl 200 ≠ 可引用**,WebFetch 拿不到正文就不放
- **闸门写死数字的坑(顺手修了)**:`gates_full.py` 与 `gen_image_sitemap.py` 都硬编码 `203`,加 6 篇指南后立刻误报 FAIL。已改为**动态期望值**(磁盘页数减 noindex 页 / 注入前后 URL 数不变)。以后加页不会再炸
- 版本 `?v=20260725g`;sitemap 203→**209**

## 🔴 假价上站根治(07-25,写 Resources 内容时顺带发现,本轮最有价值的修复)
- **发现过程**:为写串珠笔指南从 llms-full.txt 取真实价格时,看到大批 SKU 写 `from $20/pcs` —— 而它们是 **100pcs 一包**,一颗珠子 $20 显然荒谬。查 CZB23106 原始档:`[100Pcs@$20, 100bags@$10, 100Pcs@$2.94, 100Pcs@$2.32]`,**真实价 $2.94,站上显示 $20,高了 7 倍**
- **规模**:60/172 SKU(35%)价格档极差 >5 倍。**关键模式:`$10` 与 `$20` 跨 60 个互不相关的 SKU 反复出现**(RW5306/SLM713/YX097/YM228/CDK 全系…)——这不是单价,是阿里页面的固定促销元素被误抓。CDK 系列尤其规律:**固定序列 `$20 → $10 → 真实价`**
- **修法(gen_pdp.py `price_min` 四道闸,顺序不可换)**:
  1. **先剔系统噪声常量** `NOISE_CONST={10.0,20.0}`,两条判据任一命中即剔:**a) 位置判据**——落在前两档且存在真实替代档(专治 CDK 那种 $10 只比真价高 1.8 倍、倍数判据抓不到的);**b) 倍数判据**——> 其余档中位数×2.5(专治噪声在靠后位置的,如 SLM693 `[0.78,0.57,0.5,10.0]`)
  2. **白名单档全是噪声常量 → 直接降级**(10 个 SKU,含 CDK199/MSB164 这两个连主图都抓成平台徽标的 listing,整体不可信)
  3. **再**应用单位敏感下限:整包单位(bag/box/set/roll)$0.30、单件 $0.03。**顺序关键**——若先滤低价档会抬高中位数使噪声判据失效(实测 YM228 因此反被判成 $10)
  4. 清洗后极差仍 >5 倍 = 该 listing 价格不可信 → 降级「按量报价」
- **结果**:146 页显示真实价 / 26 页降级;**全站 `From $10|$20` 残留 = 0**。抽检 CZB23106 $20→**$2.94**、RW5306 $10→**$3.85**、CDK074 $20→**$5.75**
- **教训**:①「取首个白名单单位档」不足以防噪声,**必须识别跨 SKU 反复出现的常量** ②宁可 26 页写「按量报价」,也不让 60 页显示假价(memory 铁律「绝不显示假价」) ③**假价比无价更伤**——买家看到 $20/pcs 会直接走,或在报价时起争议

## 首页对标 SITE-STANDARDS v3 补缺(07-25)
实测 6 个缺口,Jacken 拍板修 ②③⑤⑥、页重维持现状。**已修 3 项 + 1 项受阻**:
- **② answer-box(标准硬要求,首页原本没有)**:H1 下 40–60 词可直接引用的直答段 → 插在 banner 之后、数字行之前(不撑破刚调好的首屏),内容=法定名+品类+买家类型+成立年+BSCI/TüV+认证清单+起订量,**62→精简至标准区间**
- **③ og:image 合规**:原为 `hero-product-still-life.webp` **2800×1811 / 271KB WebP**(部分社交平台不渲染 WebP,分享出去可能空白)→ 新生成 `og-qulacraft-1200x630.jpg`(**1200×630 JPG 164KB**,从 hero 图居中裁切),并补 `og:image:width/height/type` 三条声明
- **⑤ Organization 消歧字段**:补 `identifier`(BSCI 审计编号 25-0354231,真实可核验)+ `areaServed`(北美/东亚/东欧,与站上口径一致)+ `location`(Yiwu workshop)。**`numberOfEmployees` 与 `vatID/duns/naics` 有意留空** —— about/llms/阿里档案里都无员工数与注册号,**零编造原则优先于凑齐字段**
- **⑥ 权威外链(未做,受阻于网络)**:标准要核心页 ≥1 条权威引述+内联来源链接(被引率 +41%)。ASTM/CPSC **403 反爬**、EUR-Lex 返 202 但正文异步渲染 WebFetch 拿到空 → **按"引用URL必须逐条核实"铁律,验不了正文就不放链接**。待网络可达时补 CPSC 玩具安全页或 EU 玩具安全指令 2009/48/EC
- **页重维持现状(Jacken 决定)**:全量 6.75MB 字面超标准 2MB,但**拆开看首屏关键路径仅 0.51MB**(HTML 53KB+CSS/JS 75KB+eager 图 0.39MB),6.24MB 全是 41 张 lazy 图(品类封面/应用场景/零售货架/下游成品)——那是内容丰富度来源,压缩即伤画质
- **未修(Jacken 未选)**:① SearchAction 说谎(首页声明站内搜索但无搜索框,标准点名过此坑) / ④ meta description 未按钱页公式塞 MOQ 与认证名
- 验证:curl 线上确认 answer-box/新 og 图/identifier/areaServed 全生效、og 图 165KB 200、gates_full 全过;`?v=` → 20260725f

## 分类页区块重排 + 去数字(07-25,Jacken:"产品优先、去掉具体数字")
- **区块搬移**:"What Buyers Need to Confirm"/"What to Confirm Before Ordering"(采购规格)原在产品网格**之前**,挡住了买家最想看的货 → 整块移到**产品网格之后**。9 页新顺序 = hero → 直答块 → **产品网格** → 采购规格 → 定制 → FAQ → Read Before You Order
- **去数字**:h2 `Resin Charms: All 19 Stock Items` → `All Stock Items`(9 页);hero eyebrow `Live Catalog · 14 items` → `Live Catalog`(5 页)。理由:SKU 数会变,写死数字要么过期要么显小
- 搬移用**平衡计数解析顶层 section**(不能用贪婪正则,section 有嵌套);实测 9 页标签平衡(section/div 开闭相等)、h1 唯一、JSON-LD 零错、产品卡数不变(19/18/21/14/20/22/18/21)
- **全站总量也已去掉(07-25 追加,Jacken:"数量在变每次要更新")**:导航 `All 172 items & search`→`All items & search`(**205 页**)、首页 h2 `Nine Real Product Lines, 172 Stock Items`→`One Stock Catalog`、`Browse all 172 items`→`Browse the full catalog`、products h2 `172 Stock Items, Mapped...`→`Every Stock Item, Mapped...`、products 搜索框 placeholder、404 页 `Search 172 live items`、指南与分类页正文里的 `22/20/19/18 stock designs` 全部改写。**买家可见 '172' 残留 = 0**
- **⚠️ 界定清楚什么该留**(别一刀切删数字):①**包装/交期规格必须留** —— 100pcs lots / 10pcs lots / 30g / 500g / 1 bag / 3–7 days / 99%+ / 1,800+ 是产品事实,不是库存量 ②**采购建议留** —— guide 的 "Pick 6–8 SKUs, not 20" ③**举例留** —— keychain 的 "a display of 10 designs" ④**llms.txt / llms-full.txt / schema 的数量留** —— 机器可读且由生成器自动重算,不需人肉维护
- 坑:扫描脚本用 `\d+ items` 正则会把 URL 编码 `%20SKU`/`%20Product` 当命中(359 次假阳性),要加 `(?<!%)` 排除
- 验证:gates_full 过、4 页 curl 200、产品网格 top 从 3900+ 提前到 860、无溢出

## 分类页 hero 换类目封面(07-25,Jacken:"从首页点进来要对应上")
- 9 个分类页 hero 原本是杂图(flatlay-*/product-*/catalog 产品图),与首页品类卡封面对不上 → 全换成 **`category-covers-v2` 同款封面**,首页点进来视觉连贯
- **映射从 index.html 的品类卡实读**(href→封面 src),不靠猜(文件名 slug 与页面名不一致:polymer-clay-sprinkles.html ← polymer-clay-**slices**-cover、acrylic-beads.html ← **plastic-beads**-cover、glitter-sequins-fillers.html ← **plastic-sequins**-cover)
- **og:image / twitter:image 同步**换成同一张(分享卡片也一致);width/height 属性按真实 1200×1200 回填
- **踩坑同 PDP**:封面是 1:1 方图,而旧 CSS `.page-hero-grid img` 是 `aspect-ratio:16/9` 宽盒子 → contain 后两侧各留 126px 空洞。修法=新增 `.page-hero-grid > img[fetchpriority="high"]` 规则(特异性压过旧的 16:9)改 1:1 + cover + `width:min(420px,100%)` 居中,移动端 360px
- **自己踩的坑:改了 style.css 忘记 bump `?v=`**,浏览器吃缓存导致新规则完全不生效、排查半天 —— 本站铁律"改 CSS/JS 必升版本号"对我自己同样适用
- 实测:桌面 420×420、移动 351×351 **零留白零裁切**,9/9 页 hero+og 全同步,gates_full 过,curl 200;`?v=` → 20260725e

## PDP 首屏紧凑化 + 图片区重做 + 缩略图灯箱(07-25)
### ① 首屏完整展示(1440×900 实测 1469px → 902px)
- 最大吃高者是 **h1 占 253px**(62px 字号 ×4 行)——PDP 产品名长达 128 字符,套首页级大字号必然吃满屏
- 给 PDP hero 加专属类 **`.pdp-hero`**(生成器输出 `<section class="page-hero pdp-hero">`),CSS 只作用于它 + `.detail-grid`,**不影响其它二级页**的 .page-hero/.spec-table
- h1 `clamp(23px,2vw,30px)` → 2 行 67px;hero padding 64/44→20/10;规格表行距 16→7px;CTA 按钮 padding 与 gap 收紧
- 结果:标题/价格/规格表/主图/Request Quote/WhatsApp/合规说明**全部首屏内可见**,最深元素 902 vs 视口 900(差 2px)
### ② 图片区重做(压高度时踩的坑 + 修法)
- **坑**:把主图容器压成 `height:344px`+`width:100%` → 616×344 扁盒子装 1000×1000 方图,`contain` 在两侧各留 **136px 空洞**(Jacken 反馈"排版不好看")
- **关键判断**:首屏高度瓶颈在**右列(≈609px)**,左列有富余 → 主图不必压小,反而可放大
- 修法:`width:min(480px,100%)` + `aspect-ratio:1/1` + contain + 居中。**92%(158/172)的图本身就是方图→完美填满零留白**;14 张异形图 contain 居中不裁切(守住站内零裁切原则)
- 缩略图 92×92 方形 flex 居中,带 hover 上浮+粉边
### ③ 缩略图可点击放大(ux-pack 灯箱)
- **回归根因(自己引入的)**:ux.js 灯箱按 `img.width>=180` 筛选,我把缩略图从 197px 改到 92px 后**跌破阈值被排除**;且 lazy 图 `naturalWidth=0` 让判据更失准
- 修 `ux.js`:尺寸判据改 `naturalWidth || getAttribute('width') || img.width`——**用原图真实宽度而非被 CSS 缩小的渲染宽度**(本站 ux.js 是副本,可改;升级 ux-pack 时别覆盖丢失)
- CSS 补视觉提示:`cursor:zoom-in` + hover 上浮。实测点击缩略图打开灯箱且显示对应原图、点击关闭
### ④ 剔除阿里 Trade Assurance 徽标(商标风险,顺带发现)
- 排查异形图时发现 **4 个 SKU(CDK199/MA109/MSB164/RX023)的 01.webp 是阿里"Trade Assurance"徽标**(531×80),被采集误当产品主图
- 既非产品图,又是平台品牌资产(商标风险) → 剔除并把 02-04 前移补位,pdp-data.json 同步(带 imageNote 标记),原图备份在 scratchpad\badge_backup
- 生成器加防线 **`is_badge_img()`**(宽高比>4:1 且高<200px 判定为徽标,不上站),重采也不会再混入
- image sitemap 796→**792** 张(徽标已移除)
- 验证:gates_full 全过、4 个受影响 SKU 主图已是真产品图、首屏 900/900、移动端自适应无溢出;`?v=` → 20260725d

## PDP 删除 Place of Origin(07-25,Jacken 要求)
- 生成器加 `HIDE_SPEC_KEYS = {"Place of Origin"}`,**规格表与 Product schema 的 additionalProperty 两处同时排除**(只删表格不删 schema 等于没删,Google 仍读得到)
- 重跑 gen_pdp.py → 172 页全清:规格表含产地 **0/172**、schema 含产地 **0/172**
- **页脚 `Location: Yiwu, Zhejiang, China` 保留**(那是公司联系方式,不是产品属性;买家需要知道供应商在哪)。Organization schema 的 address 同样保留
- 以后要隐藏别的规格键,往 `HIDE_SPEC_KEYS` 加一个字符串再重跑即可
- 验证:gates_full 全过、curl 200、1280 视口无溢出、规格表 9 行

## 产品卡改版(07-25,Jacken 指"重新设计这些")— 修 3 个真问题
1. **标题残句(最严重)**:172 张分类页卡里 **147 张(85%)标题被历史脚本硬截断成残句**("100Pcs 80mm Handle Mini Wooden Honey" 缺 Spoon、"Night Starry Sky Star Moon" 缺后半截)。修法=**DOM 回填完整标题**(SEO/AI 可读,119-128 字符)+ **CSS `-webkit-line-clamp:2` 视觉两行省略**(整齐)。data-title(筛选用)与 basket-add 的 data-title 同步回填 → 搜索能匹配更多词
2. **CTA 高低不齐**:标题 1 行 vs 2 行(21px/42px)导致按钮错位(截图第 4 张卡明显偏高)。修法=`.product-card`/`.product-info` 改 flex column + `.btn-card{margin-top:auto}` **把 CTA 压到卡底** → 实测 4 张卡 btnTop 全等
3. **三层 CTA 拥挤**:Send Inquiry + "or WhatsApp this item ›" + "＋ Add to inquiry list" 三行堆叠 → 后两者包进 **`.card-cta-row` 并排胶囊**(绿/琥珀双色),文案缩短为 "WhatsApp" / "＋ Inquiry list",三层压两层
- 覆盖 **875 张卡**(分类页 172 + PDP 相关卡 688 + products);标题回填 860、CTA 并排 172
- **JS 零破坏**:保留 `.product-card`/`data-title`/`.basket-add`/`.wa-line` 类名与 data 属性(main.js 事件委托依赖);`main.js` 同步 3 处(搜索结果卡模板包 CTA 行 + 已加入文案 "✓ In inquiry list"→"✓ In list");node --check 过;**实测点击询盘篮:写入 localStorage + 文案变 ✓ + 完整标题 123 字符入篮**
- **生成器同步**(关键,否则重跑覆盖):`gen_pdp.py` 相关卡标题由 `cut_words(st,48)` 改为 `esc(st)` 完整值
- 移动端 `@640` 补触控:次级按钮 32→**42px**(WCAG 2.5.5),标题 17px
- 实测:分类页卡等高 509px、PDP 相关卡 406px、标题统一 2 行 40px、按钮全对齐、零溢出、gates_full 全过;`?v=` 统一 20260725b(205 页)

## 9 条品类描述重写(07-25,按真实规格 + 买家搜索词)
- **起因**:旧文案有事实错误 —— Plastic Beads 写 "3–16mm",而 18 个 SKU 实测尺寸是 4/6/8/10/12/20mm。另有几条没用上买家真在搜的词
- **方法**:先从 pdp-data.json 跑真实底料(每品类 SKU 标题高频词 / 克重 / 尺寸 / MOQ / 材质分布),再据此写,**每个数字都能在实抓数据里找到出处**
- **9 条新文案的三个原则**:①真实规格数字(尺寸段/克重/包装单位) ②植入买家搜索词(fake sprinkles / flatback cabochons / bingsu beads / beadable pens / jewelry findings / simulation food / gumball beads) ③点明使用场景(decoden、phone cases、nail art、dollhouse、display props)
- 修正的事实:Plastic Beads 3–16mm→**4–20mm**;Keychain 原写"resin food"但材质含 Alloy/Plastic→改"resin food, fruit and novelty on metal rings";Resin Charms 原写"ocean animals"但高频实为 cabochon/food/fruit→改 "flatback resin cabochons 12–36mm"
- 长度 85–103 字符(旧 58–76),**实测桌面/移动都是统一 3 行、卡片等高 563px**,未造成参差
- 覆盖 index + products 各 9 条 = 18 处(同源必须同改)

## SEO/GEO 深化轮(07-25,205 页站重扫后四项)
1. **PDP Product schema 扩真实规格**(gen_pdp.py):加 `material`149 / `mpn`142(真实制造商编号如 SS-RW5306) / `pattern`73 / `color`46 / `size`26 + `additionalProperty` 745 条(平均 4.3/页,Shape/Style/Feature/Usage/Place of Origin 等)。全部取自 pdp-data 实抓值,**零编造**
2. **实体归一(GEO 核心)**:全站 Organization 加 `@id = BASE#organization`(29 核心页),PDP 的 `manufacturer` + `offers.seller` 指向同一 @id → 172 个产品与"Qula Craft / Yiwu Sola Craft"实体绑定,AI 引用时可确认主体
3. **`is_noise()` 噪声过滤**(新):阿里 listing 的 `Other/N/A/unknown` 类占位值 77 处,**既不进 schema 也不上规格表**(进 schema 会稀释事实密度,上表是废行)。生效后 pattern 93→73、material 152→149
4. **image sitemap**(新脚本 `scripts/gen_image_sitemap.py`,幂等):796 张真实产品图挂进 sitemap 的 `image:image` 扩展(181 URL:172 PDP 每页≤4 图 + 9 分类页每页≤12 图),sitemap 209KB。手工艺材料是视觉驱动品类,Google 图片搜索是真实采购入口
5. **Slime Starter 指南脱离内链孤岛**:`guide-slime-business-supply-checklist`(ICP 第一问 "starting a slime business what supplies" 承接页)入链 **1→10**(首页 teaser/slime-charms 指南卡/6 篇 guide 相关阅读/applications)。首页 teaser 保持 3 张整齐一行——**加卡后成 3+1 落单,故移除季节指南卡**(它另有 11 入链,且首页仍链 seasonal-collections 品类页,季节入口未断)
- 验证:205 页 JSON-LD 全解析 / h1 全唯一 / gates_full 全过 / image sitemap 0 死链 0 重复 / curl 200 / 首页 teaser 3 卡等高无溢出
- **判定不做**:PDP 加 FAQPage(172 页同质 FAQ 触 scaled-content 红线,且 FAQ 富结果 2026 已死)

## 首页 Banner 整段按网站包重构(07-24,客户 V3 证书增强版包)
- 来源:D:\Edge-download-inbox\软陶片Banner单页网站包_Sequins最终优化版V3_证书增强版.zip(banner-section.html+banner.css+两图)。**Jacken 二次指令"整个 banner 设计按网站包来"→不再只换图,整段 hero 换成包的 pcraft 设计**
- **新 banner.css 入库**(assets/css/banner.css,8KB;**已剥离包里的全局 `*`/`html`/`body` reset**只保 `.pcraft-*` 作用域,防污染站点 body 背景/字体——实测 bodyBg/font 未变)。index head 加 `<link banner.css?v=>` + 双源 preload
- **index hero 三段置换**:原 `.hero hero-home` + `.trust-strip` + `.cert-strip` → 包的 `.pcraft-hero`(kicker OEM/ODM + **H1 含 Sequins** + lead + 4 highlights + 2 CTA + mini-trust 4 品类 + 底部 5 service 卡 + 8 证书 pill)。**CTA 锚点 #products/#quote 已改真链 products.html/quote.html**;图用已入库 webp
- **数字行保留另置**:包里没有 ≤3h/99%/1800+ 与 MOQ/交期/市场 这两行真转化数据,**有意保留**(是包缺的转化价值),移到 banner 下方独立 `<section class="container">`,复用 .hero-proof/.hero-specbar 样式,实测 3 列 w1220 健康、与 banner 无重叠
- 图(**07-25 已换第二版**,客户 ChatGPT 生成的 decoden 主题双图,源在 `D:\Edge-download-inbox\ChatGPT Image 2026年7月25日 01_25_30.png` 横 + `..._01_29_09.png` 竖;旧图备份在 scratchpad\hero_backup_20260725):assets/images/**flatlay-craft-range-hero.webp**(1600×900,205KB,横版源 1672×941)+ **-mobile.webp**(800×1200,189KB,**客户另给的竖版专用图 1024×1536,非裁切**);`.pcraft-hero__media` picture ≤720px 切竖图。**图 URL 带 `?v=20260725`**(同名替换必须加,否则浏览器缓存吃掉新图),preload 两行同步带版本号。alt 照实描述(decoden 手机壳/海洋树脂挂件/串珠笔/珠盒)。实测桌面 1600×900、移动 800×1200 各取对图(**缩窗不换图是 picture 正常行为,验证必须整页重载**)
- **旧 CSS 变死代码但无害**:style.css 里 .hero-home/.trust-strip/.cert-strip/.hero-visual/.hero-badge 现无页面引用(仅 index 用过),留着不删(删有风险,P2);.hero-proof/.hero-specbar 仍在用别删
- 旧图 flatlay-slime-supplies.webp **保留勿删**(slime-charms hero 与新指南 og:image 仍引用)
- **高度压缩(07-24,Jacken 要求"电脑第一屏完整显示不下拉")**:banner.css 桌面段全线收紧至 `?v=20260724e`——去掉 `min-height:100vh`(改 auto 随内容)、标题 clamp 80→52px(4行→3行)、各 margin/padding 收紧、service 卡 min-height 142→96。**关键断点修复:service 5 卡转 3 列的断点从 1320 下移到 1160**(5 卡单行永远比 2 行矮,利于一屏)。实测能力卡底进第一屏:1440×900 余 170px(证书条也进屏)/1366×768 余 47/1280×720 余 8;证书条允许下折(Jacken 已同意)。移动端 @720 断点独立值未受影响
- **部署注意:banner.css 是新增资产**,deploy 必须带上;验证:205 页闸门全过 + 无控制台错误 + 无横向溢出

## SEO/GEO/AEO/AI推荐 排查+修复轮(07-24,33 页,?v=20260724)
- **排查报告**:docs/QulaCraft-SEO-GEO-AEO-AI排查报告-20260724.html(全漏斗 72/100,代码侧≈88;P0×3 全是待 Jacken 的上线闸门)
- **已修(GATES_OK 全过)**:①答案盒×12(9 分类页+seasonal 各 40-60 词直答,含 bingsu 段;contact/quote 加"发送后 3 步时间线";about/factory 加实证块——**BSCI 编号 25-0354231 此前从未上过站,本轮首次落地**) ②6 篇指南加可见 Updated 标(日期取 schema dateModified,零虚构) ③9 分类页指南条追加 Seasonal 卡(seasonal 入链 3→12) ④Org schema×22 页补 knowsAbout+hasCredential(BSCI 带编号+TüV) ⑤robots +Applebot-Extended/Meta-ExternalAgent ⑥标题×2 压 ≤65、applications 描述压 ≤155 ⑦**新指南 guide-slime-business-supply-checklist.html**(~1550 词,ICP 第一问"开史莱姆店要囤什么",答案盒+双表格+3 FAQ+内链 12;Article/Breadcrumb/FAQPage schema 全新) ⑧resources 卡+1、llms.txt+1 行、sitemap 30→31(今日改动页 lastmod 全刷)
- **未做留待**:付款/物流指南(P1-1 黑洞,等客户给付款方式/运费口径)、EU 微塑料合规指南(须当天实测调研法规再写)、preload(P2-4 低益)、llms-full.txt+IndexNow(待 PDP/上线)
- 战略口径(姊妹站 GSC 实证):**内链不是收录瓶颈,站外实体信号才是**——上线后力气花在阿里店互链/目录档案/GSC/IndexNow,别再堆站内结构

## 待办(需 Jacken/客户数据)
1. **品牌改名 Qula Craft 范围待确认**:显示名必改;域名 sola-craft.com/邮箱 sale008@ 是否跟改要 Jacken 拍板(阿里店链接 solagarland 永远不动)
2. GA4 真实衡量 ID → 换进 analytics.js 一处
3. FormSubmit 首次提交激活;部署(Vercel,vercel.json 已配)+ DNS + GSC sitemap(30 URL)
4. 上线后:垃圾询盘观察;客户补:街道地址/真实评价/每 SKU 规格(解锁 PDP)

## 铁律
- 交付前跑闸门:scratchpad fix_solacraft.py 尾部 GATES 段可复用(占位残留/canonical/JSON-LD 解析/智能引号)
- 中文编辑防智能引号混入属性(grep `=”` / `”>`)
- 内容零套话、零"这个模块对 SEO 有用"式自我说明;规格宁缺毋假
