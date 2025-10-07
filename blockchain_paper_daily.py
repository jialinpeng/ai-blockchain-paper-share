# blockchain_paper_daily.py

import arxiv
import time
from datetime import datetime, timedelta
import re
import requests
import json
import os
from typing import List, Dict, Optional
import random  # 添加随机数导入

# 默认配置值
DEFAULT_MODEL_NAME = "qwen-plus"
DEFAULT_OUTPUT_FILENAME = "daily_blockchain_paper.md"
DEFAULT_SCHEDULE_TIME = "09:00"
DEFAULT_GENERATION_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
DEFAULT_ARXIV_CATEGORIES = ['cs.CR', 'cs.DC', 'cs.NI']
DEFAULT_SEARCH_KEYWORDS = ['blockchain', 'smart contract', 'consensus', 'distributed ledger', 'ethereum', 'bitcoin', 'defi']
DEFAULT_MAX_RESULTS_PER_CATEGORY = 100
DEFAULT_DAYS_TO_LOOK_BACK = 30

# 尝试导入本地配置文件
try:
    from config import (
        DASHSCOPE_API_KEY as LOCAL_API_KEY,
        MODEL_NAME as LOCAL_MODEL_NAME,
        OUTPUT_FILENAME as LOCAL_OUTPUT_FILENAME,
        SCHEDULE_TIME as LOCAL_SCHEDULE_TIME,
        GENERATION_URL as LOCAL_GENERATION_URL,
        ARXIV_CATEGORIES as LOCAL_ARXIV_CATEGORIES,
        SEARCH_KEYWORDS as LOCAL_SEARCH_KEYWORDS,
        MAX_RESULTS_PER_CATEGORY as LOCAL_MAX_RESULTS_PER_CATEGORY,
        DAYS_TO_LOOK_BACK as LOCAL_DAYS_TO_LOOK_BACK
    )
    DASHSCOPE_API_KEY = LOCAL_API_KEY
    MODEL_NAME = LOCAL_MODEL_NAME if LOCAL_MODEL_NAME else DEFAULT_MODEL_NAME
    OUTPUT_FILENAME = LOCAL_OUTPUT_FILENAME if LOCAL_OUTPUT_FILENAME else DEFAULT_OUTPUT_FILENAME
    SCHEDULE_TIME = LOCAL_SCHEDULE_TIME if LOCAL_SCHEDULE_TIME else DEFAULT_SCHEDULE_TIME
    GENERATION_URL = LOCAL_GENERATION_URL if LOCAL_GENERATION_URL else DEFAULT_GENERATION_URL
    ARXIV_CATEGORIES = LOCAL_ARXIV_CATEGORIES if LOCAL_ARXIV_CATEGORIES else DEFAULT_ARXIV_CATEGORIES
    SEARCH_KEYWORDS = LOCAL_SEARCH_KEYWORDS if LOCAL_SEARCH_KEYWORDS else DEFAULT_SEARCH_KEYWORDS
    MAX_RESULTS_PER_CATEGORY = LOCAL_MAX_RESULTS_PER_CATEGORY if LOCAL_MAX_RESULTS_PER_CATEGORY else DEFAULT_MAX_RESULTS_PER_CATEGORY
    DAYS_TO_LOOK_BACK = LOCAL_DAYS_TO_LOOK_BACK if LOCAL_DAYS_TO_LOOK_BACK else DEFAULT_DAYS_TO_LOOK_BACK
except ImportError:
    # 如果没有本地配置文件，则从环境变量或默认值获取
    DASHSCOPE_API_KEY = os.environ.get("DASHSCOPE_API_KEY", "YOUR_DASHSCOPE_API_KEY_HERE")
    MODEL_NAME = os.environ.get("MODEL_NAME", DEFAULT_MODEL_NAME)
    OUTPUT_FILENAME = os.environ.get("OUTPUT_FILENAME", DEFAULT_OUTPUT_FILENAME)
    SCHEDULE_TIME = os.environ.get("SCHEDULE_TIME", DEFAULT_SCHEDULE_TIME)
    GENERATION_URL = os.environ.get("GENERATION_URL", DEFAULT_GENERATION_URL)
    ARXIV_CATEGORIES = os.environ.get("ARXIV_CATEGORIES", DEFAULT_ARXIV_CATEGORIES)
    SEARCH_KEYWORDS = os.environ.get("SEARCH_KEYWORDS", DEFAULT_SEARCH_KEYWORDS)
    MAX_RESULTS_PER_CATEGORY = os.environ.get("MAX_RESULTS_PER_CATEGORY", DEFAULT_MAX_RESULTS_PER_CATEGORY)
    DAYS_TO_LOOK_BACK = os.environ.get("DAYS_TO_LOOK_BACK", DEFAULT_DAYS_TO_LOOK_BACK)

# -------------------------------
# 配置区域
# -------------------------------

# 1. DashScope API Key (已从config.py或环境变量导入)

# 2. 设置搜索参数 (已从config.py或环境变量导入)

# 3. CCF-A类区块链相关会议和期刊列表
CCF_A_VENUES = [
    # 网络与信息安全领域
    'CCS',           # ACM Conference on Computer and Communications Security
    'CRYPTO',        # International Association for Cryptologic Research
    'EUROCRYPT',     # European Cryptologic Conference
    'S&P',           # IEEE Symposium on Security and Privacy
    'USENIX Security', # USENIX Security Symposium
    
    # 计算机体系结构/高性能计算/存储系统领域
    'ASPLOS',        # ACM International Conference on Architectural Support for Programming Languages and Operating Systems
    'ISCA',          # ACM/IEEE International Symposium on Computer Architecture
    'MICRO',         # IEEE/ACM International Symposium on Microarchitecture
    'HPCA',          # IEEE International Symposium on High-Performance Computer Architecture
    
    # 计算机网络领域
    'SIGCOMM',       # ACM International Conference on Applications, Technologies, Architectures, and Protocols for Computer Communication
    'NSDI',          # USENIX Symposium on Networked Systems Design and Implementation
    
    # 数据库/数据挖掘/内容检索领域
    'SIGMOD',        # ACM International Conference on Management of Data
    'VLDB',          # International Conference on Very Large Data Bases
    'ICDE',          # IEEE International Conference on Data Engineering
    
    # 软件工程/系统软件/程序设计语言领域
    'ICSE',          # International Conference on Software Engineering
    'ESEC/FSE',      # European Software Engineering Conference / Foundations of Software Engineering
    'ASE',           # International Conference on Automated Software Engineering
    'ISSTA',         # International Symposium on Software Testing and Analysis
    
    # 人工智能领域
    'AAAI',          # Association for the Advancement of Artificial Intelligence
    'IJCAI',         # International Joint Conference on Artificial Intelligence
    'ICML',          # International Conference on Machine Learning
    'NeurIPS',       # Conference on Neural Information Processing Systems
]

# 4. 模型配置 (已从config.py或环境变量导入)

# 5. 输出文件 (已从config.py或环境变量导入)

# 6. 定时任务配置 (已从config.py或环境变量导入)


# -------------------------------
# 辅助函数
# -------------------------------

def contains_keywords(text: str, keywords: List[str]) -> bool:
    """检查文本是否包含任一关键词"""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in keywords)

def call_qwen(prompt: str) -> Optional[str]:
    """调用通义千问 API"""
    if DASHSCOPE_API_KEY == "YOUR_DASHSCOPE_API_KEY_HERE" or DASHSCOPE_API_KEY == "your-actual-api-key-here":
        print("[WARN] 未配置 DashScope API Key，将使用模拟响应")
        # 模拟API响应
        time.sleep(1)
        return "是"
    
    headers = {
        "Authorization": f"Bearer {DASHSCOPE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL_NAME,
        "input": {
            "messages": [
                {"role": "user", "content": prompt}
            ]
        },
        "parameters": {
            "temperature": 0.1,
            "top_p": 0.9,
            "result_format": "message"
        }
    }

    try:
        response = requests.post(GENERATION_URL, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        result = response.json()
        return result['output']['choices'][0]['message']['content']
    except Exception as e:
        print(f"[ERROR] 调用大模型失败: {e}")
        return None

def is_blockchain_related(title: str, abstract: str) -> bool:
    """使用大模型判断论文是否与区块链相关"""
    prompt = f"""
你是一位计算机科学领域的专家。请根据以下论文信息，判断其研究内容是否主要属于"区块链"或"分布式账本技术"领域。
这包括但不限于：共识算法、智能合约、密码学协议、去中心化应用、Layer2扩容方案、跨链技术等。

论文标题：{title}
摘要：{abstract}

请仅回答"是"或"否"。不要解释原因。
""".strip()

    answer = call_qwen(prompt)
    if not answer:
        return False
    
    # 简单处理，提取第一个词
    first_word = answer.strip().split()[0].lower() if answer.strip() else ""
    return first_word in ["是", "yes", "true", "✅"]

def is_ccf_a_venue(venue: str) -> bool:
    """判断发表 venue 是否为 CCF-A 类"""
    venue_lower = venue.lower()
    for ccf_a in CCF_A_VENUES:
        if ccf_a.lower() in venue_lower:
            return True
    return False

def generate_summary_and_insights(title: str, abstract: str, entry_id: str) -> Dict:
    """使用大模型生成中文摘要和核心亮点"""
    if DASHSCOPE_API_KEY == "YOUR_DASHSCOPE_API_KEY_HERE" or DASHSCOPE_API_KEY == "your-actual-api-key-here":
        print("[WARN] 未配置 DashScope API Key，将使用模拟响应")
        # 模拟API响应
        time.sleep(1)
        return {
            "summary": "这是模拟的论文摘要内容。在实际使用中，这里会是通过AI模型生成的详细摘要。",
            "insights": ["模拟要点1", "模拟要点2", "模拟要点3"],
            "recommendation": "这是模拟的推荐理由。"
        }
    
    prompt = f"""
你是一位专业的科研内容解读助手，尤其擅长将复杂的计算机科学研究转化为通俗易懂的语言。

请阅读以下论文信息，并完成下列任务：

1. **撰写摘要**：用一段简洁的中文（约100-150字），概述这篇论文的核心思想、解决的问题以及取得的主要成果。要求语言生动，能让非专业读者大致了解这项工作的意义。
2. **提炼要点**：列出三个最重要的技术贡献或发现，每一点控制在20字以内。
3. **推荐理由**：写一句话说明为什么这篇文章值得关注。

论文标题：{title}
摘要原文：{abstract}
论文链接：{entry_id}

请严格按照如下JSON格式返回结果，不附加其他文字：
{{
  "summary": "这里是你的中文摘要...",
  "insights": ["要点1...", "要点2...", "要点3..."],
  "recommendation": "这句话应能激发读者兴趣..."
}}
""".strip()

    raw_response = call_qwen(prompt)
    if not raw_response:
        return {
            "summary": "未能生成摘要。",
            "insights": ["-", "-", "-"],
            "recommendation": "暂无推荐语。"
        }
    
    try:
        # 尝试解析 JSON
        parsed_data = json.loads(raw_response)
        return {
            "summary": parsed_data.get("summary", "未提供摘要"),
            "insights": parsed_data.get("insights", ["-", "-", "-"]),
            "recommendation": parsed_data.get("recommendation", "暂无推荐语")
        }
    except json.JSONDecodeError:
        print("[WARN] 大模型返回内容无法解析为JSON，使用默认值。")
        return {
            "summary": "摘要生成出错。",
            "insights": ["-", "-", "-"],
            "recommendation": "暂无有效推荐语。"
        }


def get_recent_candidate_papers() -> List[Dict]:
    """获取最近的候选论文列表"""
    client = arxiv.Client()
    candidates = []
    
    # 计算搜索时间范围
    end_date = datetime.now()
    start_date = end_date - timedelta(days=DAYS_TO_LOOK_BACK)
    
    # 统一时区处理
    import pytz
    if end_date.tzinfo is None:
        # 如果是naive datetime，添加本地时区信息
        local_tz = pytz.timezone('UTC')  # 使用UTC时区
        end_date = local_tz.localize(end_date)
        start_date = local_tz.localize(start_date)
    
    try:
        # 按关键词搜索
        for keyword in SEARCH_KEYWORDS:
            print(f"[INFO] 正在搜索关键词 '{keyword}' ...")
            
            # 构造搜索关键词
            search = arxiv.Search(
                query=f"all:{keyword}",
                max_results=MAX_RESULTS_PER_CATEGORY,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            try:
                results_batch = list(client.results(search))
                print(f"[INFO] 关键词 '{keyword}' 找到 {len(results_batch)} 篇论文")
                
                for paper in results_batch:
                    # 检查是否在时间范围内
                    paper_date = paper.published
                    # 统一时区处理
                    if paper_date.tzinfo is None and start_date.tzinfo is not None:
                        # 如果论文日期是naive datetime，但我们的日期是aware datetime
                        paper_date = pytz.UTC.localize(paper_date)
                    elif paper_date.tzinfo is not None and start_date.tzinfo is None:
                        # 如果论文日期是aware datetime，但我们的日期是naive datetime
                        paper_date = paper_date.replace(tzinfo=None)
                        start_date = start_date.replace(tzinfo=None)
                        end_date = end_date.replace(tzinfo=None)
                        
                    if start_date <= paper_date <= end_date:
                        candidates.append({
                            "title": paper.title,
                            "summary": paper.summary,
                            "authors": [author.name for author in paper.authors],
                            "link": paper.entry_id,
                            "published": paper.published,
                            "comment": getattr(paper, 'comment', '')
                        })
            except Exception as e:
                print(f"[WARN] 搜索关键词 '{keyword}' 时出错: {e}")
                continue
                
        print(f"[INFO] 总共筛选出 {len(candidates)} 篇候选论文")
        return candidates
        
    except Exception as e:
        print(f"[ERROR] 获取论文时发生网络错误: {e}")
        print("[INFO] 将使用模拟数据进行演示")
        # 提供一些不同的模拟数据用于测试
        mock_papers = [
            {
                "title": "LMM-Incentive: Large Multimodal Model-based Incentive Design for User-Generated Content in Web 3.0",
                "summary": "Web 3.0让每个人都能拥有和赚钱自己的内容，但也引来偷懒刷低质内容骗奖励的用户。本文提出LMM-Incentive，用强大的多模态AI模型当'裁判'，结合智能合约和强化学习，设计出能自动激励高质量创作的奖励机制，有效防止作弊，提升平台公平与效率。",
                "authors": ["Jinbo Wen", "Jiawen Kang", "Linfeng Zhang", "Xiaoying Tang", "Jianhang Tang", "Yang Zhang", "Zhaohui Yang", "Dusit Niyato"],
                "link": "http://arxiv.org/abs/2510.04765v1",
                "published": datetime.now() - timedelta(days=1),
                "comment": ""
            },
            {
                "title": "ConsensusNet: A Novel High-Throughput Consensus Algorithm for Blockchain Networks",
                "summary": "区块链网络的共识算法直接影响系统的吞吐量和安全性。本文提出了一种名为ConsensusNet的新共识算法，结合了拜占庭容错和权益证明的优点，显著提高了交易处理速度，同时保持了良好的安全性。",
                "authors": ["Alice Johnson", "Bob Smith", "Charlie Brown", "Diana Lee"],
                "link": "http://arxiv.org/abs/2510.04766v1",
                "published": datetime.now() - timedelta(days=2),
                "comment": ""
            },
            {
                "title": "Privacy-Preserving Smart Contracts with zk-SNARKs Integration",
                "summary": "智能合约的透明性虽然带来了信任，但也暴露了用户的隐私。本文提出了一种基于zk-SNARKs的隐私保护智能合约框架，在保证合约正确执行的同时，有效隐藏了交易的敏感信息。",
                "authors": ["Eva Martinez", "Frank Wilson", "Grace Davis", "Henry Garcia"],
                "link": "http://arxiv.org/abs/2510.04767v1",
                "published": datetime.now() - timedelta(days=3),
                "comment": ""
            },
            {
                "title": "Cross-chain Atomic Swaps with Game-Theoretic Security Guarantees",
                "summary": "跨链原子交换是实现不同区块链间价值转移的关键技术。本文提出了一种具有博弈论安全保证的新型跨链交换协议，通过经济激励机制确保交换过程的安全性和公平性。",
                "authors": ["Ivy Rodriguez", "Jack Anderson", "Kate Thomas", "Leo Jackson"],
                "link": "http://arxiv.org/abs/2510.04768v1",
                "published": datetime.now() - timedelta(days=4),
                "comment": ""
            },
            {
                "title": "Decentralized Identity Verification using Blockchain and Biometrics",
                "summary": "去中心化身份验证是Web 3.0的重要基础设施。本文提出了一种结合区块链和生物识别技术的去中心化身份验证系统，既保证了身份的唯一性，又保护了用户的隐私数据。",
                "authors": ["Mia White", "Noah Harris", "Olivia Martin", "Peter Thompson"],
                "link": "http://arxiv.org/abs/2510.04769v1",
                "published": datetime.now() - timedelta(days=5),
                "comment": ""
            },
            {
                "title": "Energy-Efficient Mining with Renewable Energy Certificates on Blockchain",
                "summary": "区块链挖矿的高能耗问题引起了广泛关注。本文提出了一种结合可再生能源证书的节能挖矿机制，通过经济激励引导矿工使用清洁能源，实现可持续发展。",
                "authors": ["Quinn Moore", "Rachel Taylor", "Steve Allen", "Tina Young"],
                "link": "http://arxiv.org/abs/2510.04770v1",
                "published": datetime.now() - timedelta(days=6),
                "comment": ""
            },
            {
                "title": "Scalable Layer-2 Solutions with Optimistic Rollups and Fraud Proofs",
                "summary": "Layer-2扩容方案是解决区块链性能瓶颈的重要方向。本文提出了一种结合乐观汇总和欺诈证明的新型Layer-2架构，在提高交易处理速度的同时，确保了资金的安全性。",
                "authors": ["Uma Scott", "Victor King", "Wendy Wright", "Xavier Hill"],
                "link": "http://arxiv.org/abs/2510.04771v1",
                "published": datetime.now() - timedelta(days=7),
                "comment": ""
            },
            {
                "title": "Quantum-Resistant Cryptographic Algorithms for Future Blockchains",
                "summary": "随着量子计算的发展，传统密码学面临挑战。本文设计了一套抗量子计算的密码学算法，并探讨了其在下一代区块链中的应用，为系统的长期安全性提供保障。",
                "authors": ["Yara Green", "Zack Baker", "Amy Adams", "Ben Clark"],
                "link": "http://arxiv.org/abs/2510.04772v1",
                "published": datetime.now() - timedelta(days=8),
                "comment": ""
            },
            {
                "title": "Machine Learning-Based Anomaly Detection in Blockchain Networks",
                "summary": "区块链网络中的异常行为检测对系统安全至关重要。本文提出了一种基于机器学习的异常检测框架，能够实时识别和预警潜在的安全威胁，提高系统的鲁棒性。",
                "authors": ["Cindy Lewis", "Dan Walker", "Ella Hall", "Fred Allen"],
                "link": "http://arxiv.org/abs/2510.04773v1",
                "published": datetime.now() - timedelta(days=9),
                "comment": ""
            },
            {
                "title": "Tokenomics Design for Sustainable Decentralized Autonomous Organizations",
                "summary": "代币经济学设计直接影响去中心化自治组织(DAO)的可持续性。本文通过博弈论和控制论的方法，提出了一种新型代币经济模型，有效激励长期参与并防止恶意行为。",
                "authors": ["Gina Young", "Harry King", "Iris Wright", "Jack Lopez"],
                "link": "http://arxiv.org/abs/2510.04774v1",
                "published": datetime.now() - timedelta(days=10),
                "comment": ""
            }
        ]
        return mock_papers


def format_output(paper_info: Dict) -> str:
    """格式化最终输出内容"""
    # 构建基础模板
    template = f"""# 📚 ArXiv 区块链论文日报 ({datetime.now().strftime('%Y-%m-%d')})

> 🔍 来源：自动抓取 ArXiv 最新论文并通过通义千问精选

---

## 📘 论文标题
[{paper_info['title']}]({paper_info['link']})

## 👥 作者
{', '.join(paper_info['authors'])}
"""
    
    # 添加第一单位信息（如果存在）
    if 'affiliation' in paper_info and paper_info['affiliation']:
        template += f"\n\n🏢 第一单位\n{paper_info['affiliation']}"
    
    # 添加发表信息
    template += f"""

## 🗂️ 发表信息
ArXiv 预印本"""
    
    if 'published' in paper_info:
        template += f" • 提交日期: {paper_info['published'].strftime('%Y-%m-%d')}"
    
    # 添加内容速览
    template += f"""

## 🧾 内容速览

### 💡 核心摘要
{paper_info['summary']}

### ⭐ 关键看点
"""
    for insight in paper_info['insights']:
        template += f"- {insight}\n"

    template += f"\n## 🎯 推荐理由\n{paper_info['recommendation']}\n\n"

    template += "---\n*🤖 由 AI 自动生成，仅供参考*\n"
    return template


def format_xiaohongshu_output(paper_info: Dict) -> str:
    """生成小红书风格的输出内容"""
    # 生成动态话题标签
    hashtags = generate_xiaohongshu_hashtags(paper_info)
    
    template = f"""
📖 论文标题：{paper_info['title']}

👥 作者信息：{', '.join(paper_info['authors'])}

📅 发布日期：{paper_info['published'].strftime('%Y年%m月%d日')}

🔍 论文摘要：
{paper_info['summary']}

⭐ 关键看点："""
    
    for i, insight in enumerate(paper_info['insights'], 1):
        template += f"\n{i}. {insight}"

    template += f"""

🎯 推荐理由：
{paper_info['recommendation']}

🔗 原文链接：{paper_info['link']}

🤖 本内容由AI生成，访问项目了解更多：
https://github.com/jialinpeng/ai-blockchain-paper-share

{hashtags}
"""
    return template


def generate_xiaohongshu_hashtags(paper_info: Dict) -> str:
    """根据论文内容和搜索关键词生成小红书话题标签"""
    title = paper_info['title'].lower()
    summary = paper_info['summary'].lower()
    
    # 定义一些常见的区块链相关主题词
    topics = {
        '区块链': ['blockchain', '区块链'],
        '共识机制': ['consensus', '共识', 'bft', '拜占庭', 'pbft'],
        '智能合约': ['smart contract', '智能合约', 'solidity'],
        '网络安全': ['security', 'attack', '安全', '攻击', '防护'],
        '隐私保护': ['privacy', '匿名', '零知识', 'zk', 'private'],
        '性能优化': ['performance', 'scalability', 'sharding', '分片', '扩展', '性能'],
        '跨链技术': ['cross-chain', 'interoperability', '跨链'],
        '数字钱包': ['wallet', '钱包'],
        '预言机': ['oracle', '预言机'],
        '去中心化治理': ['governance', '治理'],
        '去中心化金融': ['defi', '去中心化金融'],
        'NFT': ['nft', '非同质化代币'],
        'Layer2': ['layer 2', 'layer2', 'rollup', '二层'],
        '挖矿': ['miner', 'mining', '挖矿', '矿工'],
        '加密货币': ['cryptocurrency', 'token', '代币', '数字货币'],
        '分布式系统': ['distributed', '分布式'],
        '数据存储': ['storage', '存储'],
        '网络协议': ['network', '网络'],
        '密码学': ['cryptographic', '密码', '哈希', '签名'],
        '以太坊': ['ethereum', '以太坊'],
        '比特币': ['bitcoin', '比特币']
    }
    
    # 查找匹配的主题词
    found_topics = []
    for topic, keywords in topics.items():
        for keyword in keywords:
            if keyword in title or keyword in summary:
                found_topics.append(topic)
                break
        if len(found_topics) >= 5:  # 最多提取5个主题
            break
    
    # 如果没有找到特定主题，则使用通用词
    if not found_topics:
        found_topics = ['区块链技术']
    
    # 生成话题标签字符串
    hashtags = ' '.join([f"#{topic}" for topic in found_topics])
    return hashtags + " #学术分享 #科技前沿 #AI #论文推荐"


def record_paper_history(paper_info: Dict):
    """记录论文历史到 markdown 文件"""
    history_file = "paper_history.md"
    
    # 检查文件是否存在
    file_exists = os.path.exists(history_file)
    
    with open(history_file, 'a', encoding='utf-8') as f:
        # 如果是第一次写入，添加标题
        if not file_exists:
            f.write("# 区块链论文历史记录\n\n")
        
        # 添加论文记录
        record = f"""## [{paper_info['title']}]({paper_info['link']})
- **日期**：{datetime.now().strftime('%Y-%m-%d')}
- **作者**：{', '.join(paper_info['authors'])}
- **摘要**：{paper_info['summary'][:200]}...
- **推荐理由**：{paper_info['recommendation'][:100]}...

---
"""
        f.write(record)


def select_best_paper(papers: List[Dict]) -> Optional[Dict]:
    """使用LLM选择最佳论文"""
    if not papers:
        return None
        
    if len(papers) == 1:
        return papers[0]
    
    # 构造提示词，让LLM选择最佳论文
    paper_summaries = []
    for i, paper in enumerate(papers):
        summary = f"""论文 {i+1}:
标题: {paper['title']}
摘要: {paper['summary'][:500]}..."""  # 限制摘要长度以避免超出上下文窗口
        paper_summaries.append(summary)
    
    prompt = f"""
你是一位区块链领域的专家，需要从以下 {len(papers)} 篇区块链相关论文中选择最具价值和创新性的一篇进行深入解读。
请综合考虑以下因素进行选择：
1. 研究的创新性和技术深度
2. 对区块链领域的潜在影响
3. 研究的完整性和实用性
4. 是否解决了重要问题

{chr(10).join(paper_summaries)}

请仅回复你选择的论文编号（1-{len(papers)}），不要包含其他内容。
""".strip()

    # 调用LLM获取选择结果
    answer = call_qwen(prompt)
    if not answer:
        # 如果调用失败，返回第一篇论文
        return papers[0]
    
    # 解析选择结果
    try:
        # 提取数字
        import re
        numbers = re.findall(r'\d+', answer)
        if numbers:
            selected_index = int(numbers[0])
            if 1 <= selected_index <= len(papers):
                return papers[selected_index - 1]
    except Exception as e:
        print(f"[WARN] 解析论文选择结果时出错: {e}")
    
    # 如果解析失败，返回第一篇论文
    return papers[0]


def main():
    print("[START] 开始执行每日区块链论文推送任务...")
    
    # Step 1: 获取候选论文
    candidates = get_recent_candidate_papers()
    if not candidates:
        print("[END] 近期未找到符合条件的候选论文。")
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            f.write("# 📚 ArXiv 区块链论文日报\n\n今日暂无推荐。\n")
        return

    # Step 2: 筛选出与区块链相关的论文，最多50篇
    related_papers = []
    
    # 创建一个候选论文的副本来进行随机选择
    candidate_pool = list(candidates)
    # 如果候选论文数量超过20篇，则随机选择20篇进行分析
    if len(candidate_pool) > 20:
        print(f"[INFO] 从 {len(candidate_pool)} 篇候选论文中随机选择 20 篇进行分析...")
        candidate_pool = random.sample(candidate_pool, 20)
    
    for i, paper in enumerate(candidate_pool):
        if len(related_papers) >= 50:  # 最多只需要50篇
            break
            
        print(f"[PROCESS] 正在分析第 {i+1}/{len(candidate_pool)} 篇候选论文: {paper['title']}...")
        
        # 首先判断是否与区块链相关
        if is_blockchain_related(paper['title'], paper['summary']):
            related_papers.append(paper)
            print(f"[SELECT] ✅ 找到相关论文 ({len(related_papers)}/50): {paper['title']}... 链接: {paper['link']}")
            
        time.sleep(1)  # 礼貌等待，避免频繁请求
        
    if not related_papers:
        print("[END] 经过筛选，未发现完全符合'区块链'主题的论文。")
        with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            f.write("# 📚 ArXiv 区块链论文日报\n\n今日暂无比选中的区块链论文。\n")
        return

    print(f"[INFO] 共找到 {len(related_papers)} 篇区块链相关论文，开始选择最优论文...")
    
    # Step 3: 使用LLM从相关论文中选择1篇最优论文进行精读
    selected_paper = select_best_paper(related_papers)
    if selected_paper:
        print(f"[SELECT] ✅ 选择最优论文: {selected_paper['title'][:50]}...")
    else:
        print("[ERROR] 论文选择失败")
        return
    
    # 获取论文详细信息
    published_venue = selected_paper['comment'] if selected_paper['comment'] else ""
    if published_venue and is_ccf_a_venue(published_venue):
        print(f"[INFO] 论文发表在 CCF-A 类会议/期刊: {published_venue}")
    
    details = generate_summary_and_insights(selected_paper['title'], selected_paper['summary'], selected_paper['link'])
    
    # 尝试提取第一单位信息
    affiliation = ""
    if 'affiliation' in selected_paper and selected_paper['affiliation']:
        affiliation = selected_paper['affiliation']
    elif 'authors' in selected_paper and len(selected_paper['authors']) > 0:
        # 简单处理，使用第一个作者作为示例
        affiliation = "未知单位"  # 实际项目中可以使用更复杂的逻辑提取单位信息
    
    final_paper_info = {
        "title": selected_paper['title'],
        "authors": selected_paper['authors'],
        "link": selected_paper['link'],
        "published": selected_paper['published'],
        "summary": details["summary"],
        "insights": details["insights"],
        "recommendation": details["recommendation"],
        "venue": published_venue,
        "affiliation": affiliation
    }

    # Step 4: 格式化并保存结果
    final_content = format_output(final_paper_info)
    
    with open(OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    # Step 5: 记录历史论文
    record_paper_history(final_paper_info)
    
    # Step 6: 生成小红书风格的内容
    xiaohongshu_content = format_xiaohongshu_output(final_paper_info)
    with open("xiaohongshu_post.md", 'w', encoding='utf-8') as f:
        f.write(xiaohongshu_content)
    
    # Step 7: 生成小红书封面文字信息
    xiaohongshu_cover = generate_xiaohongshu_cover_text(final_paper_info)
    with open("xiaohongshu_cover.txt", 'w', encoding='utf-8') as f:
        f.write(xiaohongshu_cover)
    
    print(f"[SUCCESS] 已成功生成报告并保存至 '{OUTPUT_FILENAME}'")
    print(f"[SUCCESS] 已记录论文历史到 'paper_history.md'")
    print(f"[SUCCESS] 已生成小红书风格内容并保存至 'xiaohongshu_post.md'")
    print(f"[SUCCESS] 已生成小红书封面文字并保存至 'xiaohongshu_cover.txt'")


def get_paper_by_id(paper_id: str) -> Optional[Dict]:
    """通过论文ID获取论文信息"""
    try:
        # 处理完整链接的情况，提取ID
        if paper_id.startswith("http"):
            # 从链接中提取ID，例如从 http://arxiv.org/abs/2510.03697v1 提取 2510.03697
            import re
            match = re.search(r'/(\d+\.\d+)(v\d+)?$', paper_id)
            if match:
                paper_id = match.group(1)
            else:
                print(f"[ERROR] 无法从链接 {paper_id} 中提取论文ID")
                return None
        
        search = arxiv.Search(id_list=[paper_id])
        results = list(search.results())
        if results:
            paper = results[0]
            return {
                'title': paper.title,
                'authors': [author.name for author in paper.authors],
                'summary': paper.summary,
                'link': paper.entry_id,
                'published': paper.published,
                'comment': paper.comment if paper.comment else ""
            }
        else:
            print(f"[ERROR] 未找到ID为 {paper_id} 的论文")
            return None
    except Exception as e:
        print(f"[ERROR] 获取论文时发生错误: {e}")
        return None


def generate_report_from_arxiv_id(paper_id: str):
    """通过ArXiv ID生成论文日报"""
    print(f"[START] 开始处理论文 ID: {paper_id}")
    
    # 创建单独的文件夹来保存单篇论文分析结果
    single_paper_dir = "single_paper_reports"
    os.makedirs(single_paper_dir, exist_ok=True)
    
    # 获取论文信息
    paper_info = get_paper_by_id(paper_id)
    if not paper_info:
        print("[ERROR] 无法获取论文信息")
        return
    
    print(f"[INFO] 成功获取论文: {paper_info['title']}")
    print(f"[INFO] 论文链接: {paper_info['link']}")
    
    # 生成论文摘要和关键点
    details = generate_summary_and_insights(paper_info['title'], paper_info['summary'], paper_info['link'])
    
    # 获取发表信息
    published_venue = paper_info['comment'] if paper_info['comment'] else ""
    if published_venue and is_ccf_a_venue(published_venue):
        print(f"[INFO] 论文发表在 CCF-A 类会议/期刊: {published_venue}")
    
    # 尝试提取第一单位信息
    affiliation = ""
    if 'affiliation' in paper_info and paper_info['affiliation']:
        affiliation = paper_info['affiliation']
    elif 'authors' in paper_info and len(paper_info['authors']) > 0:
        # 简单处理，使用第一个作者作为示例
        affiliation = "未知单位"  # 实际项目中可以使用更复杂的逻辑提取单位信息
    
    final_paper_info = {
        "title": paper_info['title'],
        "authors": paper_info['authors'],
        "link": paper_info['link'],
        "published": paper_info['published'],
        "summary": details["summary"],
        "insights": details["insights"],
        "recommendation": details["recommendation"],
        "venue": published_venue,
        "affiliation": affiliation
    }

    # 格式化并保存结果
    final_content = format_output(final_paper_info)
    
    # 处理文件名，确保使用正确的ID（去除版本号等）
    clean_paper_id = paper_id
    if paper_id.startswith("http"):
        import re
        match = re.search(r'/(\d+\.\d+)(v\d+)?$', paper_id)
        if match:
            clean_paper_id = match.group(1)
    
    # 保存到单独的文件夹中
    output_filename = f"{single_paper_dir}/paper_{clean_paper_id}.md"
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(final_content)
    
    # 生成小红书风格的内容
    xiaohongshu_content = format_xiaohongshu_output(final_paper_info)
    xiaohongshu_filename = f"{single_paper_dir}/paper_{clean_paper_id}_xiaohongshu.md"
    with open(xiaohongshu_filename, 'w', encoding='utf-8') as f:
        f.write(xiaohongshu_content)
    
    # 生成小红书封面文字信息
    xiaohongshu_cover = generate_xiaohongshu_cover_text(final_paper_info)
    xiaohongshu_cover_filename = f"{single_paper_dir}/paper_{clean_paper_id}_cover.txt"
    with open(xiaohongshu_cover_filename, 'w', encoding='utf-8') as f:
        f.write(xiaohongshu_cover)
    
    print(f"[SUCCESS] 已成功生成报告并保存至 '{output_filename}'")
    print(f"[SUCCESS] 已生成小红书风格内容并保存至 '{xiaohongshu_filename}'")
    print(f"[SUCCESS] 已生成小红书封面文字并保存至 '{xiaohongshu_cover_filename}'")
    print(f"[INFO] 论文链接: {paper_info['link']}")

def generate_xiaohongshu_cover_text(paper_info: Dict):
    """生成小红书风格的封面文字信息，基于实际论文内容"""
    # 根据论文标题和摘要提取关键词作为主要内容总结
    title = paper_info['title'].lower()
    summary = paper_info['summary'].lower()
    
    # 定义一些常见的区块链相关主题词
    topics = {
        '共识': ['consensus', '共识', 'bft', '拜占庭', 'pbft'],
        '智能合约': ['smart contract', '智能合约', 'solidity'],
        '安全': ['security', 'attack', '安全', '攻击', '防护'],
        '隐私': ['privacy', '匿名', '零知识', 'zk', 'private'],
        '性能': ['performance', 'scalability', 'sharding', '分片', '扩展', '性能'],
        '跨链': ['cross-chain', 'interoperability', '跨链'],
        '钱包': ['wallet', '钱包'],
        '预言机': ['oracle', '预言机'],
        '治理': ['governance', '治理'],
        'defi': ['defi', '去中心化金融'],
        'nft': ['nft', '非同质化代币'],
        'layer2': ['layer 2', 'layer2', 'rollup', '二层'],
        '矿工': ['miner', 'mining', '挖矿', '矿工'],
        '数字货币': ['cryptocurrency', 'token', '代币', '数字货币'],
        '分布式': ['distributed', '分布式'],
        '存储': ['storage', '存储'],
        '网络': ['network', '网络']
    }
    
    # 查找匹配的主题词
    found_topics = []
    for topic, keywords in topics.items():
        for keyword in keywords:
            if keyword in title or keyword in summary:
                found_topics.append(topic)
                break
        if len(found_topics) >= 2:  # 最多提取2个主题
            break
    
    # 如果没有找到特定主题，则使用通用词
    if not found_topics:
        found_topics = ['区块链技术']
    
    # 生成一句话封面文字，30字以内
    main_content = ' & '.join(found_topics)
    cover_text = f"ArXiv区块链论文分享 {main_content}"
    
    return cover_text

# 添加定时任务支持
def schedule_daily_task():
    """设置每日定时任务"""
    import schedule
    
    # 安排每日任务
    schedule.every().day.at(SCHEDULE_TIME).do(main)
    
    print(f"[SCHEDULE] 已设置每日定时任务，将在每天 {SCHEDULE_TIME} 执行")
    
    # 保持程序运行
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次


if __name__ == "__main__":
    # 检查是否需要定时执行
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == "--schedule":
            schedule_daily_task()
        elif sys.argv[1] == "--arxiv-id" and len(sys.argv) > 2:
            # 通过ArXiv ID生成报告
            paper_id = sys.argv[2]
            generate_report_from_arxiv_id(paper_id)
        else:
            print("用法:")
            print("  python blockchain_paper_daily.py                     # 执行每日论文筛选")
            print("  python blockchain_paper_daily.py --schedule         # 定时执行每日论文筛选")
            print("  python blockchain_paper_daily.py --arxiv-id <ID>    # 通过ArXiv ID生成论文报告")
    else:
        main()