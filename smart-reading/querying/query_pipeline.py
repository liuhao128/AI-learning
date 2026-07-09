from typing import List, Dict, Any
from langchain_community.chat_models import ChatTongyi
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_chroma import Chroma
from langchain_core.messages import BaseMessage

from config.setting import QaConfig
from indexing.vector_storage import VectorStoreManager
from .query_rewrite import QueryRewriter
from .rerank import RerankPipeline
from .answer import AnswerGenerator
from .vector_retriever import recall_with_scores

class RagPipeline:
    """RAG 在线问答流水线（只负责查询，不负责索引构建）"""

    def __init__(self, config: QaConfig):
        self._cfg = config
        self._llm = None
        self._embeddings = None
        self._vectorstores = {}  # 缓存向量库

    def _init_llm(self, api_key: str) -> ChatTongyi:
        if self._llm is None:
            self._llm = ChatTongyi(model="qwen3-max", api_key=api_key)
        return self._llm

    def _init_embeddings(self, api_key: str) -> DashScopeEmbeddings:
        if self._embeddings is None:
            self._embeddings = DashScopeEmbeddings(
                model=self._cfg.embedding_model,
                dashscope_api_key=api_key
            )
        return self._embeddings

    def _load_vectorstore(self, file_hash: str, api_key: str) -> Chroma:
        """加载向量库（带缓存）"""
        cache_key = file_hash
        if cache_key not in self._vectorstores:
            embeddings = self._init_embeddings(api_key)
            manager = VectorStoreManager(self._cfg, embeddings)
            self._vectorstores[cache_key] = manager.load_or_build(file_hash)
        return self._vectorstores[cache_key]

    def query(self,
              dashscope_api_key: str,
              file_hash: str,
              question: str,
              chat_history: List[BaseMessage],
              *,
              recall_k: int = 10,
              top_k: int = 4) -> Dict[str, Any]:
        """
        执行 RAG 查询（默认启用查询改写和重排序）

        Args:
            dashscope_api_key: API密钥
            file_hash: 文件哈希
            question: 用户问题
            chat_history: 聊天历史
            top_k: 最终返回文档数
            recall_k: 初始召回数量
        """
        try:
            llm = self._init_llm(dashscope_api_key)
            vectorstore = self._load_vectorstore(file_hash, dashscope_api_key)

            # 1. 查询改写（默认启用）
            rewriter = QueryRewriter(llm)
            search_query = rewriter.rewrite(question, chat_history)

            # 2. 向量召回
            recalled_docs, vec_scores = recall_with_scores(
                search_query,
                vectorstore,
                k=recall_k
            )

            # 3. 重排序
            rerank_pipeline = RerankPipeline(self._cfg, llm)
            evidence_list, context = rerank_pipeline.rerank(
                query=search_query,
                recalled_docs=recalled_docs,
                vec_scores=vec_scores,
                final_top_n=top_k,
            )

            # 4. 生成答案
            answer_gen = AnswerGenerator(llm)
            answer = answer_gen.generate(search_query, chat_history, context)

            return {
                "answer": answer,
                "context": context,
                "evidence": evidence_list,
                "search_query": search_query,
                "rewritten": search_query != question,
                "doc_count": len(evidence_list)
            }

        except Exception as e:
            return {
                "error": f"查询失败: {str(e)}",
                "answer": "抱歉，处理您的请求时出现错误。",
                "context": "",
                "evidence": [],
                "search_query": question,
                "rewritten": False,
                "doc_count": 0
            }
