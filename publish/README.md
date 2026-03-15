# 发布目录说明

## 目录结构

```
publish/
├── current/                    # 当前发布视图
│   └── consumers/              # 消费者视图
│       ├── v2/                 # V2 运行时消费目录
│       └── xiakedao/           # 侠客岛消费目录
├── releases/                   # 历史发布快照
│   └── <release_id>/           # 按发布ID组织
│       ├── consumers/
│       │   ├── v2/
│       │   └── xiakedao/
│       └── manifest.json       # 发布清单
```

## 发布契约

### 1. 消费者默认读取路径

消费者默认读取 `publish/current/consumers/<consumer>/` 目录下的发布物。

### 2. 历史回放

显式指定 `release_id` 时，读取 `publish/releases/<release_id>/consumers/<consumer>/`。

### 3. current 指向规则

- `current` 只能指向 `status=published` 的发布版本
- 切换必须是原子的，不允许消费者读到半切换状态

### 4. manifest 必需字段

```json
{
  "release_id": "REL-YYYYMMDD-HHMMSS",
  "created_at": "ISO8601 时间戳",
  "schema_version": "1.0.0",
  "status": "building|published|failed|retired",
  "exporters": ["v2", "xiakedao"]
}
```

### 5. status 合法取值

- `building`: 发布构建中，不可被消费者读取
- `published`: 已完成发布，可被 current 指向
- `failed`: 发布失败，不可被消费者读取
- `retired`: 已退役，不可被 current 指向，但允许显式 release_id 回放

## 使用方式

### V2 运行时

配置 `KNOWLEDGE_ROOT` 指向：
```
D:\汇度编辑部1\藏经阁\publish\current\consumers\v2\
```

### 侠客岛

通过 `asset_bridge` 配置 `consumer_root` 指向：
```
D:\汇度编辑部1\藏经阁\publish\current\consumers\xiakedao\
```