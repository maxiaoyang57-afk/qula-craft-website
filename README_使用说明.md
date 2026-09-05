# Qula Craft B2B 独立站网站包 · 品牌域名版(2026-07-15)

**品牌 Qula Craft** · 法定主体 Yiwu Sola Craft Co., Ltd. · 域名 **www.qulacrafts.com**(已注册)
32 个英文页面(9 真分类页 + 13 内容页 + 6 买家指南 + thank-you/404/隐私/条款),纯静态 HTML/CSS/JS,零依赖。

## 站点能力速览(六轮优化沉淀)
- **真产品目录**:9 分类 × 172 真 SKU(客户 Excel 驱动),每卡真图+真编号+SKU 预填询盘+WhatsApp 直达
- **转化**:4 表单接 FormSubmit 真后端 + **询盘篮**(选多品一次询价)+ 定制表单文件上传 + 移动端底部双 CTA 条
- **站内搜索**:products 页实时搜 172 SKU(支持 ?search= 直达)
- **流量**:canonical/og/twitter/schema(Organization/Product/Article/FAQ)全套 + sitemap 30 URL + robots 放行 AI 爬虫 + llms.txt
- **内容**:6 篇真买家指南 + 58 问零重复 FAQ + 真认证(EN 71/ASTM F963/CPC/REACH/CE/RoHS + BSCI + TüV)+ 真车间照片
- **体验**:滚动入场/产品图灯箱/3D 卡片/数字滚动(ux-pack)+ 404/隐私/条款 + WCAG AA 文本对比度
- **统计**:GA4 脚手架已埋(assets/js/analytics.js,load 后延迟 1.2s 注入,含询盘/WhatsApp 转化事件)

## 上线前 3 步
1. **GA4**:打开 `assets/js/analytics.js`,第一行 `G-XXXXXXXXXX` 换成真实衡量 ID → 全站生效
2. **表单激活**:上线后任意表单提交一次,FormSubmit 发激活邮件到 sales@qulacrafts.com(当前收信邮箱),点确认即通
3. **收录**:Google Search Console 提交 `sitemap.xml`(30 URL)

## 邮箱说明(重要)
当前收询盘邮箱为 **sales@qulacrafts.com**(真实可收信,保持工作)。若在新域名开通邮箱(如 sale@qulacrafts.com),
需同步替换三处:①各页 mailto 链接 ②formsubmit.co/ 后端地址(换后要重新激活一次) ③Organization schema 联系点。

## 部署说明
- Vercel / Netlify / Cloudflare Pages 均可,根目录上传本文件夹内容
- vercel.json 已带:cleanUrls:false(**别开启,否则相对 .html 链接 404**)+ 安全响应头
- 改 CSS/JS 后同步升级页面里 `?v=20260715` 版本参数,否则浏览器缓存不更新
- 域名统一 www.qulacrafts.com(canonical/sitemap/schema/og 均按此配置)

## 目录结构
- `*.html` — 32 页
- `assets/css` — style.css + ux.css(交互动效层)
- `assets/js` — main.js(导航/搜索/询盘篮)+ analytics.js(GA4)+ ux.js(动效)
- `assets/images` — 站点图 + `catalog/`(172 张真产品图,9 分类目录)
- `assets/data/product-catalog.json` — 产品数据源(**站内搜索运行时依赖,勿删**)
- `robots.txt` `sitemap.xml` `llms.txt` `vercel.json`
