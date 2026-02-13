"""
医学知识图谱 API 服务
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

app = FastAPI(
    title="医学知识图谱 API",
    description="提供医学实体查询、关系推理、知识推荐服务",
    version="1.0.0"
)

# 医学实体模型
class MedicalEntity(BaseModel):
    id: str
    name: str
    type: str  # 疾病、症状、药物、科室、医院等
    properties: dict = {}

class Relationship(BaseModel):
    source: str
    target: str
    type: str  # 治疗、引起、所属等
    properties: dict = {}

# 示例数据（实际项目中从Neo4j获取）
SAMPLE_ENTITIES = [
    {"id": "d1", "name": "高血压", "type": "疾病", "properties": {"icd10": "I10"}},
    {"id": "d2", "name": "糖尿病", "type": "疾病", "properties": {"icd10": "E11"}},
    {"id": "s1", "name": "头痛", "type": "症状", "properties": {}},
    {"id": "s2", "name": "多饮", "type": "症状", "properties": {}},
    {"id": "s3", "name": "多尿", "type": "症状", "properties": {}},
    {"id": "d1", "name": "硝苯地平", "type": "药物", "properties": {"category": "降压药"}},
    {"id": "d2", "name": "二甲双胍", "type": "药物", "properties": {"category": "降糖药"}},
    {"id": "d1", "name": "心内科", "type": "科室", "properties": {}},
    {"id": "d2", "name": "内分泌科", "type": "科室", "properties": {}},
]

SAMPLE_RELATIONSHIPS = [
    {"source": "d1", "target": "s1", "type": "引起"},
    {"source": "d2", "target": "s2", "type": "引起"},
    {"source": "d2", "target": "s3", "type": "引起"},
    {"source": "d1", "target": "d1", "type": "治疗"},
    {"source": "d2", "target": "d2", "type": "治疗"},
    {"source": "d1", "target": "d1", "type": "所属"},
    {"source": "d2", "target": "d2", "type": "所属"},
]

@app.get("/")
async def root():
    return {"message": "医学知识图谱 API", "version": "1.0.0"}

@app.get("/entities", response_model=List[MedicalEntity])
async def get_entities(type: Optional[str] = None, limit: int = 100):
    """获取医学实体列表"""
    entities = SAMPLE_ENTITIES
    if type:
        entities = [e for e in entities if e["type"] == type]
    return entities[:limit]

@app.get("/entities/{entity_id}")
async def get_entity(entity_id: str):
    """获取单个实体详情"""
    for entity in SAMPLE_ENTITIES:
        if entity["id"] == entity_id:
            return entity
    raise HTTPException(status_code=404, detail="实体不存在")

@app.get("/relationships", response_model=List[Relationship])
async def get_relationships(
    source_type: Optional[str] = None,
    target_type: Optional[str] = None,
    limit: int = 100
):
    """获取关系列表"""
    return SAMPLE_RELATIONSHIPS[:limit]

@app.get("/search")
async def search(q: str, limit: int = 10):
    """搜索实体"""
    results = [
        e for e in SAMPLE_ENTITIES 
        if q.lower() in e["name"].lower()
    ]
    return results[:limit]

@app.get("/graph")
async def get_graph():
    """获取图谱数据（用于前端可视化）"""
    return {
        "nodes": SAMPLE_ENTITIES,
        "links": SAMPLE_RELATIONSHIPS
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
