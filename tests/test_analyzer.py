"""
測試 Decision Co-Pilot
"""
import pytest
from decision_copilot.analyzer import DecisionAnalyzer
from decision_copilot.storage import DecisionStorage
import tempfile
import os


class TestAnalyzer:
    """測試分析引擎"""
    
    def setup_method(self):
        self.analyzer = DecisionAnalyzer()
    
    def test_detect_category_work(self):
        """測試偵測工作類型"""
        assert self.analyzer.detect_category("我要不要接受這份新工作？") == "工作"
    
    def test_detect_category_investment(self):
        """測試偵測投資類型"""
        assert self.analyzer.detect_category("要不要投資這檔股票？") == "投資"
    
    def test_detect_category_relocation(self):
        """測試偵測搬家類型"""
        assert self.analyzer.detect_category("要不要搬家到台北？") == "搬家"
    
    def test_analyze_positive(self):
        """測試正面分析"""
        question = "要不要接受新工作？"
        answers = {
            "這份工作的薪水比目前高多少": "30%",
            "這是您有興趣的產業嗎": "是",
            "您了解未來團隊文化嗎": "了解",
        }
        analysis = self.analyzer.analyze(question, answers, "工作")
        
        assert analysis["score"] > 0
        assert "積極" in analysis["recommendation"] or "可以" in analysis["recommendation"]
    
    def test_analyze_negative(self):
        """測試負面分析"""
        question = "要不要接受新工作？"
        answers = {
            "這份工作的薪水比目前高多少": "0%",
            "這是您有興趣的產業嗎": "否",
            "您了解未來團隊文化嗎": "不了解",
        }
        analysis = self.analyzer.analyze(question, answers, "工作")
        
        assert analysis["score"] < 0


class TestStorage:
    """測試儲存系統"""
    
    def setup_method(self):
        # 使用暫時檔案
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.storage = DecisionStorage(self.temp_file.name)
    
    def teardown_method(self):
        os.unlink(self.temp_file.name)
    
    def test_add_decision(self):
        """測試新增決策"""
        question = "要不要接受新工作？"
        answers = {"薪水": "30%"}
        analysis = {"score": 3, "recommendation": "積極考慮"}
        
        decision_id = self.storage.add_decision(question, answers, analysis, "積極考慮")
        
        assert decision_id == 1
    
    def test_list_decisions(self):
        """測試列出決策"""
        self.storage.add_decision(
            "問題1",
            {},
            {"score": 1},
            "建議1"
        )
        
        decisions = self.storage.list_decisions()
        assert len(decisions) == 1
    
    def test_get_decision(self):
        """測試取得特定決策"""
        decision_id = self.storage.add_decision(
            "問題1",
            {},
            {"score": 1},
            "建議1"
        )
        
        decision = self.storage.get_decision(decision_id)
        assert decision is not None
        assert decision["question"] == "問題1"
    
    def test_update_status(self):
        """測試更新狀態"""
        decision_id = self.storage.add_decision(
            "問題1",
            {},
            {"score": 1},
            "建議1"
        )
        
        self.storage.update_status(decision_id, "done", "已執行")
        
        decision = self.storage.get_decision(decision_id)
        assert decision["status"] == "done"
