"""
決策分析引擎
分析用戶的決策問題，生成建議
"""
from typing import Dict, List, Any
import random


class DecisionAnalyzer:
    """決策分析引擎"""
    
    def __init__(self):
        # 預設問題模板
        self.question_templates = {
            "工作": [
                "這份工作的薪水比目前高多少？（%）",
                "這是您有興趣的產業嗎？（是/普通/否）",
                "您了解未來團隊文化嗎？（了解/不了解）",
                "這份工作會讓您通勤時間增加嗎？（增加/不變/減少）",
                "這份工作有發展前景嗎？（很有前景/普通/不明）",
            ],
            "投資": [
                "這筆投資的預期報酬率是多少？（%）",
                "您能承受的最大損失是多少？（%）",
                "這筆資金您需要多久能動用？（越短越好/1年以上/隨時）",
                "您對這個投資標的有多少了解？（很了解/一般/不了解）",
            ],
            "搬家": [
                "新地點的房租/房價比目前高多少？（%）",
                "新地點通勤時間有改善嗎？（變短/差不多/變長）",
                "您喜歡新地點的環境嗎？（喜歡/普通/不喜歡）",
                "新地點有您需要的人脈資源嗎？（有/沒有/不重要）",
            ],
            "學習": [
                "這個學習投資需要多少費用？（金額）",
                "學成後對您的事业有幫助嗎？（很大/普通/沒有）",
                "您有足夠的時間投入嗎？（有/普通/沒有）",
                "這是您有興趣的領域嗎？（是/普通/否）",
            ],
        }
        
        # 決策類型關鍵詞
        self.category_keywords = {
            "工作": ["工作", "辭職", "跳槽", "面試", "offer", "公司", "同事"],
            "投資": ["投資", "股票", "基金", "理財", "賺錢", "獲利"],
            "搬家": ["搬家", "搬家的", "新房子", "租房", "遷徙"],
            "學習": ["學習", "課程", "進修", "培訓", "讀書", "MBA", "語言"],
        }
    
    def detect_category(self, question: str) -> str:
        """偵測決策類型"""
        question_lower = question.lower()
        
        for category, keywords in self.category_keywords.items():
            for keyword in keywords:
                if keyword in question_lower:
                    return category
        
        # 預設回傳空列表讓使用者回答
        return "一般"
    
    def get_questions(self, category: str, answers: dict) -> List[str]:
        """根據類型和已回答的問題，生成下一組問題"""
        
        if category in self.question_templates:
            base_questions = self.question_templates[category]
        else:
            base_questions = [
                "這個決定對您有多重要？（非常重要/普通/不重要）",
                "您有多少時間做這個決定？（很趕/充足/不急）",
                "您最在意這個決定的哪個面向？（時間/金錢/情感/發展）",
            ]
        
        # 過濾掉已回答的問題
        unanswered = []
        for q in base_questions:
            # 提取問題關鍵詞
            key = q.split("（")[0].strip()
            if key not in answers:
                unanswered.append(q)
        
        # 回傳最多3個問題
        return unanswered[:3]
    
    def analyze(self, question: str, answers: dict, category: str) -> Dict[str, Any]:
        """分析決策並生成建議"""
        
        # 計算分數
        pros = []
        cons = []
        score = 0
        
        for key, value in answers.items():
            # 根據問題類型給分數
            if "薪水" in key or "報酬" in key or "高多少" in key:
                try:
                    percent = int(''.join(filter(str.isdigit, str(value))) or 0
                    if percent > 20:
                        pros.append(f"{key}提升 {percent}%")
                        score += 3
                    elif percent > 0:
                        pros.append(f"{key}有提升")
                        score += 1
                    else:
                        cons.append(f"{key}沒有提升")
                        score -= 1
                except:
                    pass
            
            elif "興趣" in key or "喜歡" in key:
                if "是" in value or "喜歡" in value:
                    pros.append(f"{key}: 有興趣")
                    score += 2
                elif "普通" in value:
                    score += 0
                else:
                    cons.append(f"{key}: 沒興趣")
                    score -= 2
            
            elif "了解" in key or "熟悉" in key:
                if "了解" in value or "熟悉" in value:
                    pros.append(f"{key}")
                    score += 1
                else:
                    cons.append(f"{key}")
                    score -= 1
            
            elif "增加" in key or "變長" in key:
                if "增加" in value or "變長" in value:
                    cons.append("通勤/成本增加")
                    score -= 2
                elif "減少" in value or "變短" in value:
                    pros.append("通勤/成本減少")
                    score += 2
            
            elif "前景" in key or "發展" in key:
                if "很有" in value or "不錯" in value:
                    pros.append(f"{key}: 不錯")
                    score += 2
                elif "不明" in value or "沒有" in value:
                    cons.append(f"{key}: 不明")
                    score -= 1
            
            elif "時間" in key:
                if "有" in value or "充足" in value:
                    score += 1
                elif "沒有" in value:
                    score -= 1
            
            elif "承受" in key or "損失" in key:
                try:
                    percent = int(''.join(filter(str.isdigit, str(value))) or 0
                    if percent > 30:
                        score += 1
                except:
                    pass
        
        # 生成建議
        if score >= 3:
            recommendation = "積極考慮"
            recommendation_text = "根據您的回答，優點明顯，建議積極考慮這個決定。"
        elif score >= 0:
            recommendation = "可以考慮"
            recommendation_text = "根據您的回答，利弊參半，建議可以考慮但需更多信息。"
        else:
            recommendation = "建議謹慎"
            recommendation_text = "根據您的回答，缺點較多，建議謹慎考慮，多收集信息。"
        
        return {
            "category": category,
            "pros": pros,
            "cons": cons,
            "score": score,
            "recommendation": recommendation,
            "recommendation_text": recommendation_text,
        }
    
    def get_follow_up_questions(self, analysis: dict) -> List[str]:
        """根據分析結果生成跟進問題"""
        follow_ups = []
        
        if analysis["cons"]:
            worst_con = analysis["cons"][0]
            follow_ups.append(f"關於「{worst_con}」，您有辦法改善或接受嗎？")
        
        if analysis["score"] >= 0:
            follow_ups.append("這個決定有時間壓力嗎？還是可以再考慮一段時間？")
        
        return follow_ups[:2]
