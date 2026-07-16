import { useState, useEffect } from 'react';
import { uploadKnowledge, queryKnowledge, getKnowledgeStats } from '../lib/api';

export default function KnowledgeBase() {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<{ success: boolean; message: string } | null>(null);
  
  const [question, setQuestion] = useState('');
  const [isQuerying, setIsQuerying] = useState(false);
  const [answer, setAnswer] = useState('');
  const [sources, setSources] = useState<Array<{ content: string; source: string; page: string }>>([]);
  const [chatHistory, setChatHistory] = useState<Array<{ question: string; answer: string }>>([]);
  
  const [stats, setStats] = useState<{ vector_count: number } | null>(null);
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
      setUploadResult(null);
    }
  };
  
  const handleUpload = async () => {
    if (files.length === 0) return;
    
    setUploading(true);
    setUploadResult(null);
    
    try {
      const formData = new FormData();
      files.forEach(file => formData.append('files', file));
      
      const response = await uploadKnowledge(formData);
      setUploadResult({ 
        success: true, 
        message: `成功添加 ${response.data.chunk_count} 个文档片段`
      });
      setFiles([]);
      fetchStats();
    } catch (error) {
      setUploadResult({ success: false, message: '上传失败，请重试' });
    } finally {
      setUploading(false);
    }
  };
  
  const handleQuery = async () => {
    if (!question.trim()) return;
    
    setIsQuerying(true);
    setAnswer('');
    setSources([]);
    
    try {
      const response = await queryKnowledge(question.trim());
      const ans = response.data.answer;
      setAnswer(ans);
      setSources(response.data.sources || []);
      setChatHistory(prev => [...prev.slice(-4), { question: question.trim(), answer: ans }]);
    } catch (error) {
      setAnswer('查询失败，请重试');
    } finally {
      setIsQuerying(false);
    }
  };
  
  const fetchStats = async () => {
    try {
      const response = await getKnowledgeStats();
      setStats(response.data);
    } catch {}
  };
  
  useEffect(() => {
    fetchStats();
  }, []);
  
  return (
    <div className="knowledge-page">
      <div className="knowledge-header">
        <h2>知识库</h2>
        <div className="knowledge-stats">
          <div className="stat-item">
            <span className="stat-value">{stats?.vector_count || 0}</span>
            <span className="stat-label">文档片段</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">FAISS</span>
            <span className="stat-label">向量数据库</span>
          </div>
          <div className="stat-item">
            <span className="stat-value">text2vec</span>
            <span className="stat-label">Embedding</span>
          </div>
        </div>
      </div>
      
      <div className="knowledge-body">
        <div className="knowledge-panel">
          <div className="knowledge-panel-header">
            <h3>上传文档</h3>
            <span className="badge">PDF / Word / TXT</span>
          </div>
          
          <div 
            className={`knowledge-upload-area ${files.length > 0 ? 'has-files' : ''}`}
            onClick={() => document.getElementById('kb-file-input')?.click()}
          >
            <input
              id="kb-file-input"
              type="file"
              multiple
              accept=".pdf,.docx,.doc,.txt,.md"
              onChange={handleFileChange}
              className="hidden-input"
            />
            
            {files.length > 0 ? (
              <div className="file-list">
                <div className="file-list-header">
                  <span>已选择 {files.length} 个文件</span>
                  <button 
                    className="btn-tool"
                    onClick={(e) => { e.stopPropagation(); setFiles([]); }}
                  >
                    清除
                  </button>
                </div>
                <div className="files-list">
                  {files.map((file, index) => (
                    <div key={index} className="file-item">
                      <span className="file-name">{file.name}</span>
                      <span className="file-size">{(file.size / 1024).toFixed(1)} KB</span>
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <>
                <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ width: 36, height: 36, margin: '0 auto 8px', display: 'block' }}>
                  <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
                <p className="upload-title">点击或拖拽上传文档</p>
                <p className="upload-desc">支持 PDF、Word、TXT、Markdown 格式</p>
              </>
            )}
          </div>
          
          <div className="knowledge-upload-actions">
            <button 
              className="btn-primary"
              onClick={handleUpload}
              disabled={uploading || files.length === 0}
            >
              {uploading ? '上传中...' : '上传到知识库'}
            </button>
          </div>
          
          {uploadResult && (
            <div className={`knowledge-upload-status ${uploadResult.success ? 'success' : 'error'}`}>
              {uploadResult.message}
            </div>
          )}
        </div>
        
        <div className="knowledge-panel">
          <div className="knowledge-panel-header">
            <h3>智能问答</h3>
            <span className="badge">RAG 检索增强</span>
          </div>
          
          <div className="knowledge-query-input-wrapper">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleQuery()}
              placeholder="输入您的问题，例如：简历应该包含哪些部分？"
              className="knowledge-query-input"
            />
            <button 
              className="btn-primary"
              onClick={handleQuery}
              disabled={isQuerying || !question.trim()}
              style={{ whiteSpace: 'nowrap' }}
            >
              {isQuerying ? '思考中...' : '提问'}
            </button>
          </div>
          
          {chatHistory.length > 0 && (
            <div>
              <div className="knowledge-history-title">历史记录</div>
              <div className="knowledge-history-list">
                {chatHistory.map((item, index) => (
                  <span key={index} className="knowledge-history-item" onClick={() => {
                    setQuestion(item.question);
                    setAnswer(item.answer);
                  }}>
                    {item.question}
                  </span>
                ))}
              </div>
            </div>
          )}
          
          {answer && (
            <div className="knowledge-answer-section">
              <div className="knowledge-answer-header">
                <h4>回答</h4>
                <span className="badge">AI 生成</span>
              </div>
              <div className="knowledge-answer-content">{answer}</div>
              
              {sources.length > 0 && (
                <div className="knowledge-sources">
                  <h4>引用来源</h4>
                  {sources.map((source, index) => (
                    <div key={index} className="knowledge-source-card">
                      <div>
                        <span className="source-file">{source.source}</span>
                        {source.page !== '未知' && (
                          <span className="source-page">第 {source.page} 页</span>
                        )}
                      </div>
                      <div className="source-preview">{source.content}...</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
