"""
Neo4j 数据导入脚本
用法: python import_data.py
"""
import pandas as pd
from neo4j import GraphDatabase
import os
import glob

# Neo4j 连接配置
NEO4J_URI = "http://217.142.229.55:7474"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "yzt20000"

# 数据目录
DATA_DIR = "/home/yangzhengtao/下载/sj"

def get_connection():
    """创建 Neo4j 连接"""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    return driver

def clear_database(driver):
    """清空数据库"""
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
        print("✓ 数据库已清空")

def import_entities(driver, file_path):
    """导入实体数据"""
    print(f"正在导入实体: {file_path}")
    df = pd.read_csv(file_path)
    
    # 实体类型映射
    type_mapping = {
        '成品药': '成品药',
        '诊断': '诊断',
        '中药材': '中药材',
        '疾病': '疾病',
        '中成药': '中成药',
        '症状': '症状',
        '药品': '药品',
        '手术': '手术',
        '药物': '药物',
        '检查': '检查',
        '检验指标': '检验指标',
        '检验项目': '检验项目',
    }
    
    with driver.session() as session:
        for _, row in df.iterrows():
            entity_id = row.get('entity_id:ID', row.get('entity_id', ''))
            entity_type = row.get('entity_type:LABEL', row.get('entity_type', ''))
            entity_name = row.get('entity_name', '')
            
            if entity_id and entity_name:
                # 映射类型
                node_type = type_mapping.get(entity_type, entity_type)
                cypher = """
                MERGE (n:Entity {id: $id})
                SET n.name = $name, n.type = $type
                """
                session.run(cypher, id=entity_id, name=entity_name, type=node_type)
    
    print(f"✓ 导入 {len(df)} 个实体")

def import_relationships(driver, file_path):
    """导入关系数据"""
    print(f"正在导入关系: {file_path}")
    df = pd.read_csv(file_path)
    
    with driver.session() as session:
        for _, row in df.iterrows():
            rel_type = row.get('relation_name:TYPE', row.get('relation_name', ''))
            source_id = row.get('subject_entity_id:START_ID', row.get('subject_entity_id', ''))
            target_id = row.get('object_entity_id:END_ID', row.get('object_entity_id', ''))
            
            if source_id and target_id:
                cypher = """
                MATCH (s:Entity {id: $source_id})
                MATCH (t:Entity {id: $target_id})
                MERGE (s)-[r:RELATION {type: $rel_type}]->(t)
                """
                session.run(cypher, source_id=source_id, target_id=target_id, rel_type=rel_type)
    
    print(f"✓ 导入 {len(df)} 个关系")

def create_indexes(driver):
    """创建索引"""
    with driver.session() as session:
        session.run("CREATE INDEX entity_name IF NOT EXISTS FOR (n:Entity) ON (n.name)")
        session.run("CREATE INDEX entity_type IF NOT EXISTS FOR (n:Entity) ON (n.type)")
        print("✓ 索引创建完成")

def main():
    print("=" * 50)
    print("医学知识图谱数据导入")
    print("=" * 50)
    
    # 连接数据库
    driver = get_connection()
    
    # 测试连接
    with driver.session() as session:
        result = session.run("RETURN 1 as test")
        print(f"✓ Neo4j 连接成功: {result.single()}")
    
    # 清空数据库
    clear_database(driver)
    
    # 创建索引
    create_indexes(driver)
    
    # 查找所有数据文件
    data_dirs = [
        "网新知识库2024年1月",
        "网新知识库2024年7月",
        "网新知识库2024年10月",
    ]
    
    for dir_name in data_dirs:
        dir_path = os.path.join(DATA_DIR, dir_name)
        if os.path.exists(dir_path):
            print(f"\n处理目录: {dir_name}")
            
            # 导入实体
            entity_file = os.path.join(dir_path, "ENTITY_UPDATE.csv")
            if os.path.exists(entity_file):
                import_entities(driver, entity_file)
            
            # 导入关系
            rel_file = os.path.join(dir_path, "RELATIONSHIP_UPDATE.csv")
            if os.path.exists(rel_file):
                import_relationships(driver, rel_file)
    
    # 统计
    with driver.session() as session:
        entity_count = session.run("MATCH (n:Entity) RETURN count(n) as count").single()
        rel_count = session.run("MATCH ()-[r:RELATION]->() RETURN count(r) as count").single()
        
        print("\n" + "=" * 50)
        print("导入完成!")
        print(f"实体总数: {entity_count['count']}")
        print(f"关系总数: {rel_count['count']}")
        print("=" * 50)
    
    driver.close()

if __name__ == "__main__":
    main()
