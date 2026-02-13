"""
医学知识图谱 API 服务 - Neo4j 版本
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from neo4j import GraphDatabase
import os

# Neo4j 配置
NEO4J_URI = "http://217.142.229.55:7474"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "yzt20000"

app = FastAPI(
    title="医学知识图谱 API",
    description="基于 Neo4j 的医学知识图谱查询服务",
    version="1.0.0"
)

# 连接 Neo4j
driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# 模型
class Entity(BaseModel):
    id: str
    name: str
    type: str
    properties: dict = {}

class Relationship(BaseModel):
    source: str
    target: str
    type: str

class GraphData(BaseModel):
    nodes: List[dict]
    links: List[dict]

@app.get("/")
async def root():
    return {"message": "医学知识图谱 API", "version": "1.0.0", "database": "Neo4j"}

@app.get("/stats")
async def get_stats():
    """获取图谱统计信息"""
    with driver.session() as session:
        entity_count = session.run("MATCH (n:Entity) RETURN count(n) as count").single()
        rel_count = session.run("MATCH ()-[r:RELATION]->() RETURN count(r) as count").single()
        
        # 按类型统计实体
        type_stats = session.run("""
            MATCH (n:Entity) 
            RETURN n.type as type, count(n) as count 
            ORDER BY count DESC
        """)
        
        types = []
        for record in type_stats:
            types.append({"type": record["type"], "count": record["count"]})
        
        return {
            "entities": entity_count["count"],
            "relationships": rel_count["count"],
            "entity_types": types
        }

@app.get("/entities", response_model=List[Entity])
async def get_entities(type: Optional[str] = None, limit: int = 100):
    """获取医学实体列表"""
    with driver.session() as session:
        if type:
            query = "MATCH (n:Entity) WHERE n.type = $type RETURN n.id as id, n.name as name, n.type as type LIMIT $limit"
            result = session.run(query, type=type, limit=limit)
        else:
            query = "MATCH (n:Entity) RETURN n.id as id, n.name as name, n.type as type LIMIT $limit"
            result = session.run(query, limit=limit)
        
        entities = []
        for record in result:
            entities.append({
                "id": record["id"],
                "name": record["name"],
                "type": record["type"],
                "properties": {}
            })
        return entities

@app.get("/entities/{entity_id}")
async def get_entity(entity_id: str):
    """获取单个实体详情及关联"""
    with driver.session() as session:
        # 获取实体
        entity = session.run("""
            MATCH (n:Entity) WHERE n.id = $id OR n.name = $id
            RETURN n.id as id, n.name as name, n.type as type
        """, id=entity_id).single()
        
        if not entity:
            raise HTTPException(status_code=404, detail="实体不存在")
        
        # 获取关联实体
        related = session.run("""
            MATCH (n:Entity)-[r:RELATION]->(m:Entity)
            WHERE n.id = $id OR n.name = $id
            RETURN m.id as id, m.name as name, m.type as type, r.type as relation
            LIMIT 20
        """, id=entity_id)
        
        relations = []
        for record in related:
            relations.append({
                "entity": {
                    "id": record["id"],
                    "name": record["name"],
                    "type": record["type"]
                },
                "relation": record["relation"]
            })
        
        return {
            "id": entity["id"],
            "name": entity["name"],
            "type": entity["type"],
            "relations": relations
        }

@app.get("/search")
async def search(q: str, limit: int = 20):
    """搜索实体"""
    with driver.session() as session:
        result = session.run("""
            MATCH (n:Entity) 
            WHERE n.name CONTAINS $q
            RETURN n.id as id, n.name as name, n.type as type
            LIMIT $limit
        """, q=q, limit=limit)
        
        entities = []
        for record in result:
            entities.append({
                "id": record["id"],
                "name": record["name"],
                "type": record["type"]
            })
        return entities

@app.get("/graph")
async def get_graph(limit: int = 200):
    """获取图谱数据（用于前端可视化）"""
    with driver.session() as session:
        # 获取实体
        nodes_result = session.run("""
            MATCH (n:Entity) 
            RETURN n.id as id, n.name as name, n.type as type
            LIMIT $limit
        """, limit=limit)
        
        nodes = []
        for record in nodes_result:
            nodes.append({
                "id": record["id"],
                "name": record["name"],
                "type": record["type"],
                "val": 10
            })
        
        # 获取关系
        links_result = session.run("""
            MATCH (s:Entity)-[r:RELATION]->(t:Entity)
            RETURN s.id as source, t.id as target, r.type as type
            LIMIT $limit
        """, limit=limit)
        
        links = []
        for record in links_result:
            links.append({
                "source": record["source"],
                "target": record["target"],
                "type": record["type"]
            })
        
        return {"nodes": nodes, "links": links}

@app.get("/diseases")
async def get_diseases(limit: int = 50):
    """获取疾病列表"""
    with driver.session() as session:
        result = session.run("""
            MATCH (n:Entity {type: '疾病'})
            RETURN n.id as id, n.name as name
            LIMIT $limit
        """, limit=limit)
        
        diseases = []
        for record in result:
            diseases.append({"id": record["id"], "name": record["name"]})
        return diseases

@app.get("/drugs")
async def get_drugs(limit: int = 50):
    """获取药物列表"""
    with driver.session() as session:
        result = session.run("""
            MATCH (n:Entity) 
            WHERE n.type IN ['药物', '药品', '中成药', '成品药']
            RETURN n.id as id, n.name as name, n.type as type
            LIMIT $limit
        """, limit=limit)
        
        drugs = []
        for record in result:
            drugs.append({
                "id": record["id"], 
                "name": record["name"],
                "type": record["type"]
            })
        return drugs

@app.get("/disease/{disease_id}/treatment")
async def get_disease_treatment(disease_id: str):
    """获取疾病的治疗方案"""
    with driver.session() as session:
        # 查找治疗该疾病的药物
        result = session.run("""
            MATCH (d:Entity)-[:RELATION]->(dr:Entity)
            WHERE (d.id = $id OR d.name = $id) 
            AND r.type = '治疗'
            RETURN dr.id as id, dr.name as name, dr.type as type
        """, id=disease_id)
        
        treatments = []
        for record in result:
            treatments.append({
                "id": record["id"],
                "name": record["name"],
                "type": record["type"]
            })
        return {"disease_id": disease_id, "treatments": treatments}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
