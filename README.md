# Riverse

**River Algorithm** memory consolidation for AI applications.

Multilingual: [English](#english) | [中文](#中文) | [日本語](#日本語)

---

## English

A Python package that gives your AI persistent, evolving memory — similar to [mem0](https://github.com/mem0ai/mem0), but with the River Algorithm's unique three-layer confidence model, contradiction detection, and offline consolidation.

### Features

- **Three-layer confidence model**: Facts progress `suspected` → `confirmed` through cross-verification
- **Contradiction detection**: Automatically detects and resolves conflicting information
- **Sleep consolidation**: Offline pipeline that processes conversations into structured memory
- **User profiling**: Builds rich profiles with categories, evidence chains, and decay
- **Trajectory tracking**: Understands life phases, key anchors, and volatile areas
- **Multilingual**: Built-in prompts for English, Chinese, and Japanese — set `language` parameter
- **Zero config storage**: SQLite backend, no external database needed
- **OpenAI-compatible**: Works with OpenAI, DeepSeek, Ollama, Groq, and any compatible API

### Installation

```bash
pip install riverse
```

### Quick Start

```python
from riverse import Riverse

# language="en" for English prompts (default)
r = Riverse(api_key="sk-...", model="gpt-4o-mini", language="en")

r.add(messages=[
    {"role": "user", "content": "I just moved to Tokyo for a new job at Google."},
    {"role": "assistant", "content": "That's exciting! How's the transition going?"},
], user_id="alex")

# Run Sleep consolidation (River Algorithm core)
r.sleep(user_id="alex")

# Get user profile
profile = r.get_profile(user_id="alex")
for fact in profile:
    print(f"[{fact['category']}] {fact['subject']}: {fact['value']} ({fact['layer']})")

# Search memory
results = r.search("Where does he live?", user_id="alex")

# Get user model (personality + trajectory)
model = r.get_user_model(user_id="alex")
```

### Configuration

```python
r = Riverse(
    api_key="sk-...",
    api_base="https://api.openai.com",   # Or Ollama/DeepSeek/Groq URL
    model="gpt-4o-mini",
    language="en",                        # "en" | "zh" | "ja"
    db_path="~/.riverse/memory.db",       # SQLite path
    temperature=0.7,
    max_tokens=4096,
)
```

#### Using with Ollama

```python
r = Riverse(
    api_base="http://localhost:11434",
    model="llama3.1",
    language="en",
)
```

#### Using with DeepSeek

```python
r = Riverse(
    api_key="sk-...",
    api_base="https://api.deepseek.com",
    model="deepseek-chat",
    language="en",
)
```

### API Reference

#### `r.add(messages, user_id, session_id=None)`

Store conversation messages for later consolidation.

- `messages`: List of `{"role": "user"|"assistant", "content": "..."}`
- `user_id`: User identifier
- `session_id`: Optional session grouping (auto-generated if omitted)

#### `r.sleep(user_id)`

Run the full River Algorithm consolidation pipeline:

1. Extracts observations, events, and relationships from unprocessed conversations
2. Classifies observations against existing profile
3. Creates new facts and detects contradictions
4. Cross-verifies suspected facts for promotion
5. Resolves disputed fact pairs
6. Updates maturity decay and user model
7. Generates trajectory summary

Returns a summary dict with counts of actions taken.

#### `r.get_profile(user_id)`

Returns all active profile facts as a list of dicts.

#### `r.get_user_model(user_id)`

Returns `{"dimensions": [...], "trajectory": {...}}` with personality analysis and life trajectory.

#### `r.search(query, user_id, top_k=10)`

Keyword search across profile facts, events, and observations.

### How It Works

The River Algorithm models human memory consolidation (like sleep):

1. **Awake phase** (`add()`): Raw conversations are stored
2. **Sleep phase** (`sleep()`): A multi-step pipeline processes memories:
   - **Extract**: Pull observations, events, relationships from dialogue
   - **Classify**: Match observations to existing profile (support/contradict/new)
   - **Consolidate**: Create facts, resolve contradictions, promote verified facts
   - **Synthesize**: Update user model and trajectory summary

Facts have a **three-layer confidence model**:
- `suspected`: Initial extraction, unverified
- `confirmed`: Cross-verified through multiple mentions or corroboration
- `closed`: Superseded by newer information or expired

### Full Version

`riverse` is the standalone Python SDK extracted from [JKRiver](https://github.com/JKRiver/JKRiver) — a full-featured AI assistant with River Algorithm memory built in.

- Want a ready-to-use AI assistant with persistent memory → [JKRiver](https://github.com/JKRiver/JKRiver)
- Want to integrate River Algorithm memory into your own app → `riverse`

---

## 中文

一个让你的 AI 拥有持久、进化记忆的 Python 包——类似 [mem0](https://github.com/mem0ai/mem0)，但具有 River Algorithm 独特的三层置信度模型、矛盾检测与离线巩固能力。

### 特性

- **三层置信度模型**: 事实经过交叉验证从 `suspected` 晋升为 `confirmed`
- **矛盾检测**: 自动检测并解决冲突信息
- **睡眠巩固**: 离线管线将对话处理为结构化记忆
- **用户画像**: 构建包含分类、证据链和衰减的丰富画像
- **轨迹追踪**: 理解人生阶段、关键锚点和不稳定领域
- **多语言**: 内置英中日三语提示词，通过 `language` 参数切换
- **零配置存储**: SQLite 后端，无需外部数据库
- **OpenAI 兼容**: 支持 OpenAI、DeepSeek、Ollama、Groq 及任何兼容 API

### 安装

```bash
pip install riverse
```

### 快速开始

```python
from riverse import Riverse

# language="zh" 使用中文提示词
r = Riverse(api_key="sk-...", model="gpt-4o-mini", language="zh")

r.add(messages=[
    {"role": "user", "content": "我刚搬到东京，在 Google 找了份新工作。"},
    {"role": "assistant", "content": "太棒了！适应得怎么样？"},
], user_id="alex")

# 运行 Sleep 巩固（River Algorithm 核心）
r.sleep(user_id="alex")

# 获取用户画像
profile = r.get_profile(user_id="alex")
for fact in profile:
    print(f"[{fact['category']}] {fact['subject']}: {fact['value']} ({fact['layer']})")

# 搜索记忆
results = r.search("他住在哪里？", user_id="alex")

# 获取用户模型（人格 + 轨迹）
model = r.get_user_model(user_id="alex")
```

### 配置

```python
r = Riverse(
    api_key="sk-...",
    api_base="https://api.openai.com",   # 或 Ollama/DeepSeek/Groq 地址
    model="gpt-4o-mini",
    language="zh",                        # "en" | "zh" | "ja"
    db_path="~/.riverse/memory.db",       # SQLite 路径
    temperature=0.7,
    max_tokens=4096,
)
```

#### 使用 DeepSeek

```python
r = Riverse(
    api_key="sk-...",
    api_base="https://api.deepseek.com",
    model="deepseek-chat",
    language="zh",
)
```

#### 使用 Ollama

```python
r = Riverse(
    api_base="http://localhost:11434",
    model="llama3.1",
    language="zh",
)
```

### API 参考

#### `r.add(messages, user_id, session_id=None)`

存储对话消息以供后续巩固。

- `messages`: 消息列表 `{"role": "user"|"assistant", "content": "..."}`
- `user_id`: 用户标识符
- `session_id`: 可选会话分组（省略则自动生成）

#### `r.sleep(user_id)`

运行完整的 River Algorithm 巩固管线：

1. 从未处理的对话中提取观察、事件和关系
2. 将观察与现有画像分类对比
3. 创建新事实并检测矛盾
4. 交叉验证可疑事实以晋升
5. 解决争议事实对
6. 更新成熟度衰减和用户模型
7. 生成轨迹摘要

返回操作计数的摘要字典。

#### `r.get_profile(user_id)`

返回所有活跃的画像事实列表。

#### `r.get_user_model(user_id)`

返回 `{"dimensions": [...], "trajectory": {...}}`，包含人格分析和人生轨迹。

#### `r.search(query, user_id, top_k=10)`

跨画像事实、事件和观察的关键词搜索。

### 工作原理

River Algorithm 模拟人类记忆巩固过程（类似睡眠）：

1. **清醒阶段** (`add()`): 存储原始对话
2. **睡眠阶段** (`sleep()`): 多步管线处理记忆：
   - **提取**: 从对话中提取观察、事件、关系
   - **分类**: 将观察与现有画像匹配（支持/矛盾/新增）
   - **巩固**: 创建事实、解决矛盾、晋升已验证事实
   - **合成**: 更新用户模型和轨迹摘要

事实具有**三层置信度模型**：
- `suspected`: 初始提取，未验证
- `confirmed`: 通过多次提及或佐证交叉验证
- `closed`: 被更新信息取代或过期

### 完整版

`riverse` 是从 [JKRiver](https://github.com/JKRiver/JKRiver) 项目中提取的独立 Python SDK。JKRiver 是一个内置 River Algorithm 记忆系统的完整 AI 助手。

- 想要一个开箱即用的、具备持久记忆的 AI 助手 → [JKRiver](https://github.com/JKRiver/JKRiver)
- 想将 River Algorithm 记忆能力集成到你自己的应用中 → `riverse`

---

## 日本語

AIに持続的で進化する記憶を与えるPythonパッケージ——[mem0](https://github.com/mem0ai/mem0)に似ていますが、River Algorithmの独自の三層信頼度モデル、矛盾検出、オフライン統合機能を備えています。

### 特徴

- **三層信頼度モデル**: 事実は交差検証を経て `suspected` → `confirmed` に昇格
- **矛盾検出**: 矛盾する情報を自動検出・解決
- **睡眠統合**: オフラインパイプラインが会話を構造化メモリに処理
- **ユーザープロファイリング**: カテゴリ、証拠チェーン、減衰を含む豊富なプロファイルを構築
- **軌跡追跡**: ライフフェーズ、キーアンカー、不安定な領域を理解
- **多言語対応**: 英語・中国語・日本語のプロンプトを内蔵、`language` パラメータで切替
- **ゼロコンフィグストレージ**: SQLiteバックエンド、外部データベース不要
- **OpenAI互換**: OpenAI、DeepSeek、Ollama、Groq、その他互換APIに対応

### インストール

```bash
pip install riverse
```

### クイックスタート

```python
from riverse import Riverse

# language="ja" で日本語プロンプトを使用
r = Riverse(api_key="sk-...", model="gpt-4o-mini", language="ja")

r.add(messages=[
    {"role": "user", "content": "東京に引っ越して、Googleで新しい仕事を始めました。"},
    {"role": "assistant", "content": "すごいですね！慣れましたか？"},
], user_id="alex")

# Sleep統合を実行（River Algorithmのコア）
r.sleep(user_id="alex")

# ユーザープロファイルを取得
profile = r.get_profile(user_id="alex")
for fact in profile:
    print(f"[{fact['category']}] {fact['subject']}: {fact['value']} ({fact['layer']})")

# メモリを検索
results = r.search("彼はどこに住んでいますか？", user_id="alex")

# ユーザーモデルを取得（人格 + 軌跡）
model = r.get_user_model(user_id="alex")
```

### 設定

```python
r = Riverse(
    api_key="sk-...",
    api_base="https://api.openai.com",   # またはOllama/DeepSeek/GroqのURL
    model="gpt-4o-mini",
    language="ja",                        # "en" | "zh" | "ja"
    db_path="~/.riverse/memory.db",       # SQLiteパス
    temperature=0.7,
    max_tokens=4096,
)
```

#### Ollamaで使用

```python
r = Riverse(
    api_base="http://localhost:11434",
    model="llama3.1",
    language="ja",
)
```

### APIリファレンス

#### `r.add(messages, user_id, session_id=None)`

会話メッセージを保存し、後で統合処理します。

- `messages`: メッセージリスト `{"role": "user"|"assistant", "content": "..."}`
- `user_id`: ユーザー識別子
- `session_id`: オプションのセッショングループ（省略時は自動生成）

#### `r.sleep(user_id)`

River Algorithmの完全な統合パイプラインを実行：

1. 未処理の会話から観察、イベント、関係を抽出
2. 観察を既存プロファイルに対して分類
3. 新しい事実を作成し、矛盾を検出
4. 疑わしい事実を交差検証して昇格
5. 争議のある事実ペアを解決
6. 成熟度減衰とユーザーモデルを更新
7. 軌跡サマリーを生成

アクション数のサマリー辞書を返します。

#### `r.get_profile(user_id)`

すべてのアクティブなプロファイル事実をリストで返します。

#### `r.get_user_model(user_id)`

`{"dimensions": [...], "trajectory": {...}}` を返します（人格分析とライフ軌跡）。

#### `r.search(query, user_id, top_k=10)`

プロファイル事実、イベント、観察にわたるキーワード検索。

### 仕組み

River Algorithmは人間の記憶統合プロセス（睡眠のような）をモデル化：

1. **覚醒フェーズ** (`add()`): 生の会話を保存
2. **睡眠フェーズ** (`sleep()`): マルチステップパイプラインがメモリを処理：
   - **抽出**: 会話から観察、イベント、関係を抽出
   - **分類**: 観察を既存プロファイルにマッチング（支持/矛盾/新規）
   - **統合**: 事実の作成、矛盾の解決、検証済み事実の昇格
   - **合成**: ユーザーモデルと軌跡サマリーの更新

事実には**三層信頼度モデル**があります：
- `suspected`: 初期抽出、未検証
- `confirmed`: 複数回の言及や裏付けによる交差検証済み
- `closed`: 新しい情報に置き換えられたか期限切れ

### フルバージョン

`riverse` は [JKRiver](https://github.com/JKRiver/JKRiver) から抽出されたスタンドアロンPython SDKです。JKRiverはRiver Algorithmメモリシステムを内蔵した完全なAIアシスタントです。

- すぐに使える持続記憶付きAIアシスタントが欲しい → [JKRiver](https://github.com/JKRiver/JKRiver)
- River Algorithmメモリを自分のアプリに統合したい → `riverse`

---

## License

AGPL-3.0
