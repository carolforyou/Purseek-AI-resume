import os
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from langchain.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader, UnstructuredFileLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms.base import LLM

from app.services.groq_service import GroqService
from app.services.deepseek_service import DeepSeekService


class KnowledgeService:
    def __init__(self):
        self.db_dir = Path(__file__).resolve().parents[3] / "data" / "knowledge"
        self.db_dir.mkdir(parents=True, exist_ok=True)
        
        self.embeddings = HuggingFaceEmbeddings(
            model_name="shibing624/text2vec-base-chinese",
            model_kwargs={"device": "cpu"}
        )
        
        self.groq_service = GroqService()
        self.deepseek_service = DeepSeekService()
        
        self.vector_store = self._load_or_create_vector_store()
        self.qa_chain = self._create_qa_chain()
    
    def _load_or_create_vector_store(self) -> FAISS:
        db_path = self.db_dir / "faiss_index"
        
        if db_path.exists():
            try:
                return FAISS.load_local(str(db_path), self.embeddings, allow_dangerous_deserialization=True)
            except Exception as e:
                print(f"加载向量数据库失败，创建新数据库: {e}")
        
        return FAISS.from_texts(["初始化知识库"], self.embeddings)
    
    def _save_vector_store(self):
        db_path = self.db_dir / "faiss_index"
        self.vector_store.save_local(str(db_path))
    
    def _create_qa_chain(self) -> RetrievalQA:
        class DynamicLLM(LLM):
            groq_service: GroqService
            deepseek_service: DeepSeekService
            
            @property
            def _llm_type(self) -> str:
                return "dynamic"
            
            def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
                if self.groq_service.is_configured():
                    response = self.groq_service.chat(system_prompt="", user_prompt=prompt)
                else:
                    response = self.deepseek_service.chat(system_prompt="", user_prompt=prompt)
                return response
        
        llm = DynamicLLM(groq_service=self.groq_service, deepseek_service=self.deepseek_service)
        
        return RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 5}),
            return_source_documents=True,
            chain_type_kwargs={
                "prompt": """你是一个专业的企业知识库问答助手。请根据以下提供的文档内容回答用户的问题。

文档内容：
{context}

用户问题：
{question}

要求：
1. 必须基于提供的文档内容回答，不要编造信息
2. 如果文档中没有相关内容，请明确说明"未找到相关信息"
3. 回答要准确、简洁，使用中文
4. 可以适当引用文档中的具体条款或数据

回答："""
            }
        )
    
    def _load_document(self, file_path: str) -> List[Any]:
        ext = os.path.splitext(file_path)[1].lower()
        
        loaders = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.doc': Docx2txtLoader,
            '.txt': TextLoader,
        }
        
        if ext in loaders:
            loader = loaders[ext](file_path)
        else:
            loader = UnstructuredFileLoader(file_path)
        
        return loader.load()
    
    def _split_text(self, documents: List[Any]) -> List[Any]:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "！", "？", "；", "、", " ", ""],
            length_function=len
        )
        return text_splitter.split_documents(documents)
    
    def add_documents(self, file_paths: List[str]) -> Dict[str, Any]:
        all_chunks = []
        
        for file_path in file_paths:
            try:
                documents = self._load_document(file_path)
                chunks = self._split_text(documents)
                all_chunks.extend(chunks)
                print(f"成功加载文件: {file_path}, 分割为 {len(chunks)} 个片段")
            except Exception as e:
                print(f"加载文件失败: {file_path}, 错误: {e}")
        
        if all_chunks:
            self.vector_store.add_documents(all_chunks)
            self._save_vector_store()
            
            return {
                "success": True,
                "message": f"成功添加 {len(all_chunks)} 个文档片段",
                "file_count": len(file_paths),
                "chunk_count": len(all_chunks)
            }
        else:
            return {
                "success": False,
                "message": "未能加载任何文档"
            }
    
    def query(self, question: str) -> Dict[str, Any]:
        try:
            result = self.qa_chain({"query": question})
            
            sources = []
            if "source_documents" in result:
                for doc in result["source_documents"]:
                    source_info = {
                        "content": doc.page_content[:200],
                        "source": doc.metadata.get("source", "未知"),
                        "page": doc.metadata.get("page", "未知")
                    }
                    sources.append(source_info)
            
            return {
                "success": True,
                "answer": result.get("result", ""),
                "sources": sources,
                "question": question
            }
        except Exception as e:
            print(f"查询失败: {e}")
            return {
                "success": False,
                "answer": f"查询失败: {str(e)}",
                "sources": [],
                "question": question
            }
    
    def get_stats(self) -> Dict[str, Any]:
        try:
            vector_count = 0
            if hasattr(self.vector_store, 'index'):
                vector_count = self.vector_store.index.ntotal
            
            return {
                "success": True,
                "vector_count": vector_count,
                "embedding_model": "text2vec-base-chinese",
                "vector_store": "FAISS"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


knowledge_service = KnowledgeService()