# 医学知识图谱

医学知识图谱 - 构建图数据库、发布知识服务、前端可视化展示

## 技术栈

- **图数据库**: Neo4j
- **后端**: FastAPI (Python)
- **前端**: Next.js + React Force Graph
- **数据源**: PubMed, CNKI, 医学百科

## 项目结构

```
medical-knowledge-graph/
├── backend/           # 后端服务
│   ├── api/         # API接口
│   ├── models/      # 数据模型
│   └── services/    # 业务逻辑
├── frontend/        # 前端应用
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   └── public/
│   └── public/
├── data/            # 数据文件
└── README.md
```

## 功能

1. 知识图谱构建 - 实体抽取 + 关系抽取
2. 图数据库存储 - Neo4j 存储医学实体关系
3. API 服务 - 查询、推理、推荐
4. 前端可视化 - 图谱展示、搜索、交互

## 快速开始

### 后端

```bash
cd backend
pip install -r requirements.txt
python main.py
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## License

MIT
