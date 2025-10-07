# ai-blockchain-paper-share

通过大语言模型（LLM）实现 ArXiv 区块链论文的分享与传播，结合AI技术提升学术内容的理解与可访问性。

项目地址: [https://github.com/jialinpeng/ai-blockchain-paper-share](https://github.com/jialinpeng/ai-blockchain-paper-share)

## 功能特性

- 自动获取 ArXiv 上最新的区块链相关论文
- 利用LLM生成论文摘要和关键点
- 每日定时分享一篇精选论文
- 生成多种格式的内容输出，包括标准Markdown、小红书风格内容等
- 记录历史分享的论文信息
- 保存每日的完整搜索结果供进一步分析
- 支持通过 ArXiv 链接直接生成论文分析报告

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置说明

### DashScope API Key 配置

本项目使用通义千问模型生成论文摘要，需要配置DashScope API Key：

1. 复制 `config.py.example` 文件为 `config.py`：
   ```bash
   cp config.py.example config.py
   ```

2. 编辑 `config.py` 文件，填入你的 DashScope API Key：
   ```python
   DASHSCOPE_API_KEY = "your-actual-api-key-here"
   ```

### 自定义搜索关键词

你还可以自定义 ArXiv 搜索的关键词和分类：

- `ARXIV_CATEGORIES`: ArXiv 分类列表
- `SEARCH_KEYWORDS`: 搜索关键词列表
- `MAX_RESULTS_PER_CATEGORY`: 每个分类最多返回结果数
- `DAYS_TO_LOOK_BACK`: 回溯天数

### 环境变量方式配置（可选）

你也可以通过设置环境变量来配置参数：

```bash
export DASHSCOPE_API_KEY=your-actual-api-key-here
export SEARCH_KEYWORDS="blockchain,smart contract,consensus"
```

## 生成的文件

运行程序后会生成以下文件：

- `daily_blockchain_paper.md`: 标准格式的每日区块链论文日报
- `paper_history.md`: 历史分享论文记录
- `xiaohongshu_post.md`: 小红书风格的内容输出
- `xiaohongshu_cover.txt`: 小红书封面文字信息
- `arxiv_search_results/`: 包含每日完整搜索结果的文件夹，每个文件以日期命名

注意：`paper_history.md`、`xiaohongshu_post.md` 和 `xiaohongshu_cover.txt` 已添加到 `.gitignore` 中，不会被提交到版本控制系统。
注意：`arxiv_search_results/` 文件夹已添加到 `.gitignore` 中，其中包含的每日搜索结果文件不会被提交到版本控制系统。

## 使用方法

### 单次运行
```bash
python blockchain_paper_daily.py
```

### 定时运行（每天9点）
```bash
python blockchain_paper_daily.py --schedule
```

### 通过 ArXiv ID 生成论文报告
```bash
python blockchain_paper_daily.py --arxiv-id 2510.03697
```

其中 `2510.03697` 是论文的 ArXiv ID。你也可以使用完整的 ArXiv 链接，例如：
```bash
python blockchain_paper_daily.py --arxiv-id http://arxiv.org/abs/2510.03697v1
```

这将生成以下文件：
- `paper_2510.03697.md`: 标准格式的论文分析报告
- `paper_2510.03697_xiaohongshu.md`: 小红书风格的内容输出
- `paper_2510.03697_cover.txt`: 小红书封面文字信息

## 自动分享到小红书

目前项目生成的小红书风格内容需要手动复制到小红书平台发布。自动发布功能由于小红书平台没有提供公开API，实现较为复杂且可能违反平台规定，因此暂未实现。

如果你希望实现自动分享，可以考虑以下方案：
1. 使用第三方社交媒体管理工具
2. 开发基于浏览器自动化的脚本（如Selenium或Playwright）
3. 通过小红书官方合作渠道接入

注意：任何自动化发布方案都需要仔细考虑账号安全和平台政策风险。

## 安全说明

- `config.py` 文件已添加到 `.gitignore`，不会被提交到版本控制系统
- 建议使用环境变量方式配置 API Key，特别是在生产环境中