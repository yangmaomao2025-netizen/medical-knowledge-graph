"use client";

import { useEffect, useState, useRef } from 'react';
import dynamic from 'next/dynamic';
import axios from 'axios';

// 动态导入 Force Graph（避免 SSR 问题）
const ForceGraph2D = dynamic(() => import('react-force-graph-2d'), {
  ssr: false,
  loading: () => <div className="loading">加载图谱中...</div>
});

interface Node {
  id: string;
  name: string;
  type: string;
  val: number;
}

interface Link {
  source: string;
  target: string;
  type: string;
}

interface GraphData {
  nodes: Node[];
  links: Link[];
}

const TYPE_COLORS: Record<string, string> = {
  '疾病': '#ef4444',    // 红色
  '症状': '#f97316',    // 橙色
  '药物': '#22c55e',    // 绿色
  '科室': '#3b82f6',    // 蓝色
  '医院': '#8b5cf6',    // 紫色
};

export default function Home() {
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], links: [] });
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNode, setSelectedNode] = useState<Node | null>(null);
  const [loading, setLoading] = useState(true);
  const graphRef = useRef<any>(null);

  // 加载图谱数据
  useEffect(() => {
    axios.get('http://localhost:8000/graph')
      .then(res => {
        const nodes = res.data.nodes.map((n: any) => ({
          ...n,
          val: 10,
        }));
        setGraphData({ nodes, links: res.data.links });
        setLoading(false);
      })
      .catch(() => {
        // 如果后端未启动，使用示例数据
        setGraphData({
          nodes: [
            { id: 'd1', name: '高血压', type: '疾病', val: 20 },
            { id: 'd2', name: '糖尿病', type: '疾病', val: 20 },
            { id: 's1', name: '头痛', type: '症状', val: 10 },
            { id: 's2', name: '多饮', type: '症状', val: 10 },
            { id: 's3', name: '多尿', type: '症状', val: 10 },
            { id: 'dr1', name: '硝苯地平', type: '药物', val: 15 },
            { id: 'dr2', name: '二甲双胍', type: '药物', val: 15 },
            { id: 'dept1', name: '心内科', type: '科室', val: 12 },
            { id: 'dept2', name: '内分泌科', type: '科室', val: 12 },
          ],
          links: [
            { source: 'd1', target: 's1', type: '引起' },
            { source: 'd2', target: 's2', type: '引起' },
            { source: 'd2', target: 's3', type: '引起' },
            { source: 'd1', target: 'dr1', type: '治疗' },
            { source: 'd2', target: 'dr2', type: '治疗' },
            { source: 'd1', target: 'dept1', type: '所属' },
            { source: 'd2', target: 'dept2', type: '所属' },
          ],
        });
        setLoading(false);
      });
  }, []);

  // 搜索过滤
  const filteredData = searchQuery
    ? {
        nodes: graphData.nodes.filter(n => 
          n.name.toLowerCase().includes(searchQuery.toLowerCase())
        ),
        links: graphData.links.filter(l => {
          const source = graphData.nodes.find(n => n.id === l.source);
          const target = graphData.nodes.find(n => n.id === l.target);
          return source?.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                 target?.name.toLowerCase().includes(searchQuery.toLowerCase());
        }),
      }
    : graphData;

  return (
    <div className="container">
      <header className="header">
        <h1>🧬 医学知识图谱</h1>
        <p>Medical Knowledge Graph Visualization</p>
      </header>

      <div className="controls">
        <input
          type="text"
          placeholder="搜索疾病、症状、药物..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="search-input"
        />
      </div>

      <div className="legend">
        {Object.entries(TYPE_COLORS).map(([type, color]) => (
          <span key={type} className="legend-item">
            <span className="legend-dot" style={{ background: color }}></span>
            {type}
          </span>
        ))}
      </div>

      <div className="graph-container">
        {loading ? (
          <div className="loading">加载中...</div>
        ) : (
          <ForceGraph2D
            ref={graphRef}
            graphData={filteredData}
            nodeLabel={(node: any) => `${node.name} (${node.type})`}
            nodeColor={(node: any) => TYPE_COLORS[node.type] || '#999'}
            nodeVal="val"
            linkColor={() => '#666'}
            linkWidth={2}
            linkDirectionalArrowLength={6}
            linkDirectionalArrowRelPos={1}
            onNodeClick={(node) => setSelectedNode(node)}
            backgroundColor="#0f172a"
          />
        )}
      </div>

      {selectedNode && (
        <div className="panel">
          <h3>{selectedNode.name}</h3>
          <p>类型: {selectedNode.type}</p>
          <button onClick={() => setSelectedNode(null)}>关闭</button>
        </div>
      )}

      <style jsx>{`
        .container {
          min-height: 100vh;
          background: #0f172a;
          color: white;
        }
        .header {
          padding: 20px;
          text-align: center;
        }
        .header h1 {
          margin: 0;
          font-size: 2rem;
        }
        .controls {
          padding: 0 20px;
          display: flex;
          justify-content: center;
        }
        .search-input {
          width: 100%;
          max-width: 400px;
          padding: 12px;
          border-radius: 8px;
          border: 1px solid #334155;
          background: #1e293b;
          color: white;
          font-size: 16px;
        }
        .legend {
          padding: 10px 20px;
          display: flex;
          justify-content: center;
          gap: 20px;
          flex-wrap: wrap;
        }
        .legend-item {
          display: flex;
          align-items: center;
          gap: 6px;
        }
        .legend-dot {
          width: 12px;
          height: 12px;
          border-radius: 50%;
        }
        .graph-container {
          height: calc(100vh - 200px);
          position: relative;
        }
        .loading {
          display: flex;
          align-items: center;
          justify-content: center;
          height: 100%;
          font-size: 1.2rem;
        }
        .panel {
          position: fixed;
          right: 20px;
          top: 100px;
          background: #1e293b;
          padding: 20px;
          border-radius: 12px;
          min-width: 200px;
        }
        .panel button {
          margin-top: 10px;
          padding: 8px 16px;
          background: #3b82f6;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
        }
      `}</style>
    </div>
  );
}
