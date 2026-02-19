"""
決策儲存系統
管理決策記錄的讀寫
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
import uuid


class DecisionStorage:
    """本地端決策儲存系統"""
    
    def __init__(self, storage_path: Optional[str] = None):
        if storage_path:
            self.storage_path = Path(storage_path)
        else:
            # 預設儲存位置
            self.storage_path = Path.home() / ".decision-copilot" / "decisions.json"
        
        # 確保目錄存在
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 初始化檔案
        if not self.storage_path.exists():
            self._save({"decisions": [], "next_id": 1})
    
    def _load(self) -> dict:
        """載入決策資料"""
        try:
            with open(self.storage_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {"decisions": [], "next_id": 1}
    
    def _save(self, data: dict):
        """儲存決策資料"""
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def add_decision(self, question: str, answers: dict, analysis: dict, recommendation: str) -> int:
        """新增決策"""
        data = self._load()
        
        decision = {
            "id": data["next_id"],
            "question": question,
            "answers": answers,
            "analysis": analysis,
            "recommendation": recommendation,
            "created_at": datetime.now().isoformat(),
            "status": "pending",  # pending, done, abandoned
            "review_at": None,
            "result": None
        }
        
        data["decisions"].append(decision)
        data["next_id"] += 1
        
        self._save(data)
        return decision["id"]
    
    def list_decisions(self) -> list:
        """列出所有決策"""
        data = self._load()
        return data["decisions"]
    
    def get_decision(self, decision_id: int) -> Optional[dict]:
        """取得特定決策"""
        data = self._load()
        for decision in data["decisions"]:
            if decision["id"] == decision_id:
                return decision
        return None
    
    def update_status(self, decision_id: int, status: str, result: Optional[str] = None):
        """更新決策狀態"""
        data = self._load()
        for decision in data["decisions"]:
            if decision["id"] == decision_id:
                decision["status"] = status
                if result:
                    decision["result"] = result
                if status == "done" or status == "abandoned":
                    decision["review_at"] = datetime.now().isoformat()
                break
        self._save(data)
    
    def get_pending_reviews(self) -> list:
        """取得待回顧的決策"""
        data = self._load()
        pending = []
        now = datetime.now()
        
        for decision in data["decisions"]:
            if decision["status"] == "pending":
                pending.append(decision)
        
        return pending
    
    def get_statistics(self) -> dict:
        """取得決策統計"""
        data = self._load()
        decisions = data["decisions"]
        
        total = len(decisions)
        pending = sum(1 for d in decisions if d["status"] == "pending")
        done = sum(1 for d in decisions if d["status"] == "done")
        abandoned = sum(1 for d in decisions if d["status"] == "abandoned")
        
        # 統計建議採納率
        采纳_count = 0
        for d in decisions:
            if d.get("result") and d.get("recommendation"):
                if d["result"].lower() in ["接受", "同意", "去", "做"]:
                    采纳_count += 1
        
        return {
            "total": total,
            "pending": pending,
            "done": done,
            "abandoned": abandoned,
            "adoption_rate": 采纳_count / done * 100 if done > 0 else 0
        }
