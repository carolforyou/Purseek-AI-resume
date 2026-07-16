import  json
from typing import List, Dict, Any, Optional
from pathlib import Path

from app.services.groq_service import GroqService
from app.services.deepseek_service import DeepSeekService
from app.services.profile_service import ProfileService
from app.services.jd_service import JDService


class InterviewQuestion:
    def __init__(self, question: str, category: str, difficulty: str, suggested_answer: str = ""):
        self.question = question
        self.category = category
        self.difficulty = difficulty
        self.suggested_answer = suggested_answer

    def to_dict(self) -> Dict[str, str]:
        return {
            "question": self.question,
            "category": self.category,
            "difficulty": self.difficulty,
            "suggested_answer": self.suggested_answer,
        }


class InterviewService:
    def __init__(self):
        self.groq_service = GroqService()
        self.deepseek_service = DeepSeekService()
        self.profile_service = ProfileService()
        self.jd_service = JDService()

    def generate_questions(
        self,
        jd_id: Optional[str] = None,
        count: int = 15,
        categories: Optional[List[str]] = None,
    ) -> List[InterviewQuestion]:
        profile = self.profile_service.get_profile()
        
        jd = None
        jd_text = ""
        if jd_id:
            jd = self.jd_service.get_jd(jd_id)
            if jd:
                jd_text = f"""
岗位信息：
标题：{jd.title}
公司：{jd.company}
描述：{jd.description}
要求：{jd.requirements}
技能：{', '.join(jd.skills)}
"""

        profile_text = self._format_profile_for_prompt(profile)
        
        prompt = self._build_prompt(profile_text, jd_text, count, categories)
        
        try:
            response = self.groq_service.generate(prompt)
            return self._parse_response(response)
        except Exception:
            try:
                response = self.deepseek_service.generate(prompt)
                return self._parse_response(response)
            except Exception as e:
                return self._generate_fallback_questions(profile, jd)

    def _format_profile_for_prompt(self, profile) -> str:
        sections = []
        
        if profile.basic_info:
            sections.append(f"""基本信息：
姓名：{profile.basic_info.name or ''}
求职意向：{profile.basic_info.job_intention or ''}
学历：{profile.basic_info.highest_degree or ''}
""")
        
        if profile.project_experiences:
            projects_text = "\n".join([
                f"""项目{idx+1}：{p.project_name}
时间：{p.project_time}
角色：{p.project_role}
技术栈：{', '.join(p.technologies)}
描述：{p.project_description}
职责：{'; '.join(p.personal_responsibilities)}
成果：{'; '.join(p.project_results)}"""
                for idx, p in enumerate(profile.project_experiences[:3])
            ])
            sections.append(f"项目经验：\n{projects_text}\n")
        
        if profile.work_experiences:
            work_text = "\n".join([
                f"""公司：{w.company_name}
职位：{w.position_name}
时间：{w.work_time}
工作内容：{'; '.join(w.work_contents)}"""
                for w in profile.work_experiences[:2]
            ])
            sections.append(f"工作经历：\n{work_text}\n")
        
        if profile.skills:
            sections.append(f"技能：{', '.join(profile.skills)}\n")
        
        if profile.education:
            edu_text = "\n".join([
                f"""学校：{e.school_name}
专业：{e.major}
学历：{e.degree}
时间：{e.school_time}"""
                for e in profile.education[:2]
            ])
            sections.append(f"教育背景：\n{edu_text}\n")
        
        return "\n".join(sections)

    def _build_prompt(
        self,
        profile_text: str,
        jd_text: str,
        count: int,
        categories: Optional[List[str]],
    ) -> str:
        category_list = categories or ["行为面试", "技术面试", "项目深挖", "综合能力"]
        categories_text = ", ".join(category_list)
        
        prompt = f"""你是一位专业的技术面试官。请根据以下候选人的简历信息和目标岗位，生成{count}个高质量的面试问题。

【候选人简历】
{profile_text}

【目标岗位信息】
{jd_text if jd_text else '未提供具体岗位，根据简历内容生成通用问题'}

【要求】
1. 问题类型：{categories_text}
2. 难度分布：简单30%、中等50%、困难20%
3. 每个问题必须附一个简短的参考答案思路
4. 问题要针对性强，深入挖掘候选人的真实能力
5. 输出格式必须是JSON数组，每个元素包含：question(问题), category(类型), difficulty(难度), suggested_answer(参考思路)

【JSON格式示例】
[
  {{
    "question": "请描述你在XX项目中遇到的最大挑战是什么？",
    "category": "行为面试",
    "difficulty": "中等",
    "suggested_answer": "使用STAR法则回答，重点说明如何分析问题、采取的行动和最终结果"
  }}
]

请直接输出JSON，不要包含其他文字。"""
        
        return prompt

    def _parse_response(self, response: str) -> List[InterviewQuestion]:
        try:
            start_idx = response.find("[")
            end_idx = response.rfind("]") + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                data = json.loads(json_str)
                questions = []
                for item in data[:20]:
                    questions.append(InterviewQuestion(
                        question=item.get("question", ""),
                        category=item.get("category", "综合能力"),
                        difficulty=item.get("difficulty", "中等"),
                        suggested_answer=item.get("suggested_answer", ""),
                    ))
                return questions
        except (json.JSONDecodeError, Exception):
            pass
        return []

    def _generate_fallback_questions(self, profile, jd) -> List[InterviewQuestion]:
        questions = []
        
        if profile.project_experiences:
            p = profile.project_experiences[0]
            questions.extend([
                InterviewQuestion(
                    question=f"请详细介绍你在「{p.project_name}」项目中的主要职责和贡献",
                    category="项目深挖",
                    difficulty="中等",
                    suggested_answer="重点说明个人负责的模块、技术选型理由和取得的成果"
                ),
                InterviewQuestion(
                    question=f"在「{p.project_name}」项目中，你遇到的最大技术挑战是什么？如何解决的？",
                    category="技术面试",
                    difficulty="困难",
                    suggested_answer="描述问题背景、尝试过的方案、最终解决方案及其效果"
                ),
            ])
        
        questions.extend([
            InterviewQuestion(
                question="请介绍一个你最有成就感的项目，并说明为什么",
                category="行为面试",
                difficulty="简单",
                suggested_answer="突出个人贡献和量化成果"
            ),
            InterviewQuestion(
                question="你在团队中通常扮演什么角色？举例说明你如何与团队协作",
                category="综合能力",
                difficulty="简单",
                suggested_answer="说明团队角色定位，举具体协作案例"
            ),
            InterviewQuestion(
                question="你最近学习了什么新技术？如何应用到实际项目中的？",
                category="技术面试",
                difficulty="中等",
                suggested_answer="说明学习的技术、学习途径和实际应用案例"
            ),
            InterviewQuestion(
                question="描述一次你犯过的技术错误，以及你从中学到了什么",
                category="行为面试",
                difficulty="中等",
                suggested_answer="诚实描述错误，重点说明反思和改进措施"
            ),
            InterviewQuestion(
                question="如何处理需求变更频繁的项目？你有什么方法论？",
                category="综合能力",
                difficulty="困难",
                suggested_answer="说明需求管理策略、沟通方式和变更控制流程"
            ),
        ])
        
        return questions[:15]