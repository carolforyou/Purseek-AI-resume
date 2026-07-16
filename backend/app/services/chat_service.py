import json, os
from pathlib import Path
from typing import Literal

from app.models.chat import ChatMessageResponse, ChatStage, ChatStartResponse
from app.prompts.onboarding import (
    FIELD_LABELS,
    ONBOARDING_STAGE_PROMPTS,
    STAGE_QUESTION_BANK,
    STAGE_REQUIRED_FIELDS,
)
from app.services.deepseek_service import DeepSeekService
from app.services.groq_service import GroqService
from app.services.profile_service import ProfileService

ChatStage = Literal[
    "basic_info",
    "self_intro",
    "work_experience",
    "skills",
    "education",
    "project_experience",
    "awards",
    "self_evaluation",
]

_STAGE_LABELS: dict[ChatStage, str] = {
    "basic_info": "基本信息",
    "self_intro": "自我介绍",
    "work_experience": "工作经历",
    "skills": "个人技能",
    "education": "教育背景",
    "project_experience": "项目经验",
    "awards": "获奖情况",
    "self_evaluation": "自我评价",
}

_STAGE_SEQUENCE: list[ChatStage] = [
    "basic_info",
    "self_intro",
    "work_experience",
    "skills",
    "education",
    "project_experience",
    "awards",
    "self_evaluation",
]

_FIELD_QUESTIONS: dict[str, str] = {
    "name": "请问你的姓名是什么？",
    "job_intention": "请问你的求职意向是什么？",
    "email": "方便提供你的电子邮箱吗？",
    "phone": "方便提供你的联系方式吗？",
    "birth_date": "你的出生年月是？",
    "highest_degree": "你的最高学历是？",
    "self_intro": "请简单介绍一下你自己。",
    "company_name": "请介绍你的工作经历，公司名称是？",
    "position_name": "你的职位名称是？",
    "work_time": "工作时间是？",
    "work_contents": "主要负负责哪些工作内容？",
    "backend": "你掌握哪些后端技术？",
    "framework": "熟悉哪些框架？",
    "database": "了解哪些数据库技术？",
    "middleware": "熟悉哪些中间件？",
    "frontend": "掌握哪些前端技术？",
    "tools": "常用哪些开发工具？",
    "description": "可以描述一下你的技术能力吗？",
    "school_name": "你的学校名称是？",
    "major": "所学专业是？",
    "degree": "学历是？",
    "school_time": "在校时间是？",
    "main_courses": "主修过哪些课程？",
    "project_name": "项目名称是？",
    "project_time": "项目时间是？",
    "project_role": "你在项目中担任什么角色？",
    "technologies": "使用了哪些技术栈？",
    "project_description": "项目描述是？",
    "personal_responsibilities": "你的个人职责是什么？",
    "project_results": "项目取得了哪些成果？",
    "awards": "获得过哪些奖项或证书？",
    "self_evaluation": "请做一个简单的自我评价。",
}

SESSIONS_DIR = Path(__file__).resolve().parents[3] / "data" / "sessions"


class ChatService:
    def __init__(self) -> None:
        SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
        self.groq_service = GroqService()
        self.deepseek_service = DeepSeekService()
        self.profile_service = ProfileService()
        self.sessions: dict[str, dict] = {}

    def _save_session(self, session_id: str) -> None:
        if session_id in self.sessions:
            data = self.sessions[session_id].copy()
            data["completed_fields"] = list(data.get("completed_fields", set()))
            session_file = SESSIONS_DIR / f"{session_id}.json"
            session_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def _load_session(self, session_id: str) -> dict | None:
        session_file = SESSIONS_DIR / f"{session_id}.json"
        if session_file.exists():
            try:
                data = json.loads(session_file.read_text(encoding="utf-8"))
                data["completed_fields"] = set(data.get("completed_fields", []))
                self.sessions[session_id] = data
                return data
            except Exception:
                return None
        return None

    def delete_session(self, session_id: str) -> bool:
        session_file = SESSIONS_DIR / f"{session_id}.json"
        if session_file.exists():
            session_file.unlink()
            self.sessions.pop(session_id, None)
            return True
        return False

    def get_all_sessions(self) -> list[dict]:
        sessions = []
        for f in sorted(SESSIONS_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                sessions.append({
                    "session_id": f.stem,
                    "current_stage": data.get("current_stage", "basic_info"),
                    "stage_label": data.get("stage_label", ""),
                    "preview": data.get("preview", ""),
                    "message_count": data.get("message_count", 0),
                    "updated_at": data.get("updated_at", ""),
                })
            except Exception:
                pass
        return sessions

    def resume_session(self, session_id: str) -> ChatStartResponse | None:
        data = self._load_session(session_id)
        if not data:
            return None
        stage = data.get("current_stage", "basic_info")
        history = data.get("message_history", [])
        preview = history[-1]["content"][:80] + "..." if history else ""
        return ChatStartResponse(
            session_id=session_id,
            reply=f"欢迎回来！我们上次进行到「{_STAGE_LABELS.get(stage, stage)}」，要继续完善吗？",
            stage=stage,
            stage_label=_STAGE_LABELS.get(stage, stage),
            missing_info=self._get_missing_fields_for_stage(stage),
            should_summarize=False,
            summary_preview=preview,
        )

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        if self.groq_service.is_configured():
            return self.groq_service.chat(system_prompt=system_prompt, user_prompt=user_prompt)
        return self.deepseek_service.chat(system_prompt=system_prompt, user_prompt=user_prompt)

    def start_chat(self) -> ChatStartResponse:
        import uuid, datetime
        session_id = f"session_{uuid.uuid4().hex[:12]}"
        self.sessions[session_id] = {
            "completed_fields": set(),
            "current_stage": "basic_info",
            "stage_label": "基本信息",
            "message_count": 0,
            "message_history": [],
            "preview": "",
            "created_at": datetime.datetime.now().isoformat(),
            "updated_at": datetime.datetime.now().isoformat(),
        }
        self._save_session(session_id)
        opening_stage: ChatStage = "basic_info"
        return ChatStartResponse(
            session_id=session_id,
            reply="你好，我会帮你一步一步整理简历。先从基本信息开始，你的姓名和求职意向是什么？",
            stage=opening_stage,
            stage_label=_STAGE_LABELS[opening_stage],
            missing_info=self._get_missing_fields_for_stage(opening_stage),
            should_summarize=False,
            summary_preview="",
        )

    def _format_history(self, history: list[dict]) -> str:
        lines = []
        for msg in history[-10:]:
            role = "用户" if msg["role"] == "user" else "助手"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)

    def _ai_analyze_message(
        self,
        stage: ChatStage,
        message: str,
        completed_fields: set[str],
        message_history: list[dict],
    ) -> dict:
        required_fields = STAGE_REQUIRED_FIELDS.get(stage, [])
        field_labels = {f: FIELD_LABELS.get(f, f) for f in required_fields}
        history_text = self._format_history(message_history)

        system_prompt = (
            "你是一个简历信息分析专家。请分析用户输入，识别其中包含的简历字段信息。\n"
            "你有完整的对话历史作为上下文，请利用历史信息来更好地理解用户意图。\n"
            "请严格按照JSON格式输出分析结果。\n\n"
            "输出格式要求：\n"
            "{\n"
            '  "identified_fields": ["字段名", "字段名"],\n'
            '  "can_advance": true或false,\n'
            '  "next_field_to_ask": "下一个应该询问的字段名",\n'
            '  "extracted_values": {"字段名": "提取的值", ...}\n'
            "}\n\n"
            "字段名必须从以下列表中选择：\n"
            f"{required_fields}\n\n"
            "字段名对应标签：\n"
            f"{field_labels}\n\n"
            "分析规则：\n"
            "1. identified_fields：列出用户输入中明确包含的字段，不需要完全匹配关键字\n"
            "2. extracted_values：提取每个字段的具体值，用于后续写入简历\n"
            "3. can_advance：如果用户已经提供了当前阶段大部分必要信息（至少70%），则为true\n"
            "4. next_field_to_ask：选择用户还没有提供的、最重要的字段\n"
            "5. 如果用户直接说'下一个'、'够了'等，can_advance应该为true\n"
            "6. 注意：用户说'没有'、'无'等表示该字段为空，但不代表整个项目不存在\n"
            "7. 使用对话历史来理解上下文，比如用户之前提到的项目名称等\n"
        )

        user_prompt = (
            f"当前阶段：{_STAGE_LABELS[stage]}\n"
            f"阶段说明：{ONBOARDING_STAGE_PROMPTS[stage]}\n"
            f"已完成字段：{list(completed_fields) if completed_fields else []}\n"
            f"对话历史：\n{history_text}\n\n"
            f"最新用户输入：{message}\n"
            "请分析并输出JSON格式结果。"
        )

        try:
            result = self._call_llm(system_prompt=system_prompt, user_prompt=user_prompt)
            import json
            return json.loads(result)
        except Exception:
            return {"identified_fields": [], "can_advance": False, "next_field_to_ask": "", "extracted_values": {}}

    def _ai_generate_reply(
        self,
        current_stage: ChatStage,
        next_stage: ChatStage,
        message: str,
        identified_fields: list[str],
        missing_info: list[str],
        completed_fields: set[str],
        message_history: list[dict],
    ) -> str:
        identified_labels = [FIELD_LABELS.get(f, f) for f in identified_fields]
        history_text = self._format_history(message_history)

        system_prompt = (
            "你是AI求职助手的聊天机器人，正在帮用户完成简历信息建档。\n"
            "你的任务是：在对话中收集用户简历信息，用友好、自然的中文回复。\n\n"
            "回复规则：\n"
            "1. 对用户提供的信息给予肯定确认，然后自然地问下一个问题\n"
            "2. 用口语化的中文，不要用'好的，我已记录'这种机械回复\n"
            "3. 如果用户已经给出了当前阶段需要的信息，自然过渡到下一阶段\n"
            "4. 回复控制在50-120字，简洁自然\n"
            "5. 直接给出最终回复，不要包含思考过程\n"
            "6. 使用对话历史来保持回复的连贯性，记住用户之前说过的话\n"
            "7. 如果用户说某项技术没有，不要因此否定整个项目，继续询问其他信息\n"
        )

        user_prompt = (
            f"当前阶段：{_STAGE_LABELS[current_stage]}\n"
            f"下一阶段：{_STAGE_LABELS[next_stage]}\n"
            f"对话历史：\n{history_text}\n\n"
            f"最新用户消息：{message}\n"
            f"已识别字段：{', '.join(identified_labels) if identified_labels else '无'}\n"
            f"仍待补充：{', '.join(missing_info) if missing_info else '无'}\n"
            f"已完成字段：{list(completed_fields)}\n"
            f"当前阶段策略：{ONBOARDING_STAGE_PROMPTS[current_stage]}\n"
            f"候选问题：{' | '.join(STAGE_QUESTION_BANK[current_stage])}\n"
            "请直接给出最终回复。"
        )

        return self._call_llm(system_prompt=system_prompt, user_prompt=user_prompt)

    def reply_to_message(self, session_id: str, stage: ChatStage, message: str) -> ChatMessageResponse:
        import datetime
        normalized_message = message.strip()

        if session_id not in self.sessions:
            self._load_session(session_id)
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "completed_fields": set(),
                "current_stage": stage,
                "message_count": 0,
                "message_history": [],
                "created_at": datetime.datetime.now().isoformat(),
            }

        session_data = self.sessions[session_id]
        session_data["current_stage"] = stage
        session_data["message_count"] = session_data.get("message_count", 0) + 1
        session_data["stage_label"] = _STAGE_LABELS.get(stage, stage)

        session_data["message_history"].append({"role": "user", "content": normalized_message})

        ai_result = self._ai_analyze_message(
            stage=stage,
            message=normalized_message,
            completed_fields=session_data["completed_fields"],
            message_history=session_data["message_history"],
        )

        identified_fields = ai_result.get("identified_fields", [])
        extracted_values = ai_result.get("extracted_values", {})
        can_advance = ai_result.get("can_advance", False)
        next_field_to_ask = ai_result.get("next_field_to_ask", "")

        session_data["completed_fields"].update(identified_fields)

        if extracted_values:
            for field_key, value in extracted_values.items():
                if value and value not in ("无", "没有", "None", "none", ""):
                    self.profile_service.update_field_from_chat(stage, field_key, value)

        missing_info = self._get_missing_fields_after_match(
            stage=stage, completed_fields=session_data["completed_fields"]
        )

        next_stage = self._resolve_next_stage(
            stage=stage,
            missing_info=missing_info,
            message=normalized_message,
            can_advance=can_advance,
        )

        should_summarize = self._should_summarize(
            stage=stage,
            missing_info=missing_info,
            matched_fields=identified_fields,
            message_count=session_data.get("message_count", 0),
        )
        summary_preview = ""

        if should_summarize:
            summary_preview = self._build_summary_preview(
                stage=stage, matched_fields=identified_fields, message=normalized_message
            )

        if next_stage != stage:
            session_data["current_stage"] = next_stage
            session_data["completed_fields"] = set()
            session_data["message_count"] = 0

        reply = self._build_reply(
            current_stage=stage,
            next_stage=next_stage,
            message=normalized_message,
            matched_fields=identified_fields,
            missing_info=missing_info,
            completed_fields=session_data["completed_fields"],
            next_field_to_ask=next_field_to_ask,
            message_history=session_data["message_history"],
        )

        session_data["message_history"].append({"role": "assistant", "content": reply})
        session_data["preview"] = normalized_message[:60]
        session_data["updated_at"] = datetime.datetime.now().isoformat()
        self._save_session(session_id)

        return ChatMessageResponse(
            reply=reply,
            stage=next_stage,
            stage_label=_STAGE_LABELS[next_stage],
            missing_info=self._get_missing_fields_for_stage(next_stage),
            should_summarize=should_summarize,
            summary_preview=summary_preview,
        )

    def _get_missing_fields_for_stage(self, stage: ChatStage) -> list[str]:
        required = STAGE_REQUIRED_FIELDS.get(stage, [])
        return [FIELD_LABELS.get(f, f) for f in required]

    def _get_missing_fields_after_match(
        self, stage: ChatStage, completed_fields: set[str]
    ) -> list[str]:
        required = STAGE_REQUIRED_FIELDS.get(stage, [])
        missing = [f for f in required if f not in completed_fields]
        return [FIELD_LABELS.get(f, f) for f in missing]

    def _resolve_next_stage(
        self,
        stage: ChatStage,
        missing_info: list[str],
        message: str,
        can_advance: bool = False,
    ) -> ChatStage:
        if not missing_info or can_advance:
            idx = _STAGE_SEQUENCE.index(stage)
            if idx < len(_STAGE_SEQUENCE) - 1:
                return _STAGE_SEQUENCE[idx + 1]
            return stage

        force_next_keywords = ["下一阶段", "下一页", "下一个", "够了", "没有其他", "没有了", "没有别的"]
        message_lower = message.lower()
        for kw in force_next_keywords:
            if kw in message_lower:
                idx = _STAGE_SEQUENCE.index(stage)
                if idx < len(_STAGE_SEQUENCE) - 1:
                    return _STAGE_SEQUENCE[idx + 1]
                return stage

        return stage

    def _should_summarize(
        self,
        stage: ChatStage,
        missing_info: list[str],
        matched_fields: list[str],
        message_count: int,
    ) -> bool:
        if not missing_info:
            return True
        if len(matched_fields) > 0:
            return True
        if message_count >= 2:
            return True
        return False

    def _build_summary_preview(
        self, stage: ChatStage, matched_fields: list[str], message: str
    ) -> str:
        labels = [FIELD_LABELS.get(f, f) for f in matched_fields]
        return f"用户提供了{'、'.join(labels)}等信息"

    def _build_reply(
        self,
        current_stage: ChatStage,
        next_stage: ChatStage,
        message: str,
        matched_fields: list[str],
        missing_info: list[str],
        completed_fields: set[str],
        next_field_to_ask: str = "",
        message_history: list[dict] = None,
    ) -> str:
        try:
            return self._ai_generate_reply(
                current_stage=current_stage,
                next_stage=next_stage,
                message=message,
                identified_fields=matched_fields,
                missing_info=missing_info,
                completed_fields=completed_fields,
                message_history=message_history or [],
            )
        except Exception:
            pass

        return self._build_rule_based_reply(
            current_stage=current_stage,
            next_stage=next_stage,
            message=message,
            matched_fields=matched_fields,
            missing_info=missing_info,
            completed_fields=completed_fields,
            next_field_to_ask=next_field_to_ask,
        )

    def _build_rule_based_reply(
        self,
        current_stage: ChatStage,
        next_stage: ChatStage,
        message: str,
        matched_fields: list[str],
        missing_info: list[str],
        completed_fields: set[str],
        next_field_to_ask: str = "",
    ) -> str:
        if next_stage != current_stage:
            transition_line = self._build_transition_line(
                current_stage=current_stage, next_stage=next_stage
            )
            next_question = STAGE_QUESTION_BANK[next_stage][0]
            return f"{transition_line}{next_question}"

        if matched_fields:
            matched_labels = [FIELD_LABELS.get(f, f) for f in matched_fields]
            confirmed_text = "、".join(matched_labels)
            if missing_info:
                next_field_name = missing_info[0]
                next_field_key = self._get_field_key_by_label(next_field_name, current_stage)
                next_question = _FIELD_QUESTIONS.get(
                    next_field_key, STAGE_QUESTION_BANK[current_stage][0]
                )
                return f"我已记录你的{confirmed_text}。接下来补充{next_field_name}：{next_question}"
            return (
                f"我已记录你的{confirmed_text}，这一阶段信息已够。"
                f"{self._build_transition_line(current_stage=current_stage, next_stage=next_stage)}"
                f"{STAGE_QUESTION_BANK[next_stage][0]}"
            )

        if missing_info:
            next_field_name = missing_info[0]
            next_field_key = self._get_field_key_by_label(next_field_name, current_stage)
            next_question = _FIELD_QUESTIONS.get(
                next_field_key, STAGE_QUESTION_BANK[current_stage][0]
            )
            return f"我需要先了解你的{next_field_name}。{next_question}"

        return self._pick_follow_up_question(current_stage=current_stage, message=message)

    def _get_field_key_by_label(self, label: str, stage: ChatStage) -> str:
        for field_key, field_label in FIELD_LABELS.items():
            if field_label == label:
                return field_key
        required_fields = STAGE_REQUIRED_FIELDS.get(stage, [])
        return required_fields[0] if required_fields else ""

    def _build_transition_line(
        self, current_stage: ChatStage, next_stage: ChatStage
    ) -> str:
        transitions = {
            "basic_info": "基本信息我记下了。",
            "self_intro": "自我介绍很清晰。",
            "work_experience": "工作经历已记录。",
            "skills": "技能栈我记住了。",
            "education": "教育背景已记录。",
            "project_experience": "项目经验涵盖了关键要素。",
            "awards": "获奖情况已记录。",
            "self_evaluation": "自我评价已完成。",
        }
        return transitions.get(current_stage, "这一阶段信息已够。")

    def _pick_follow_up_question(self, current_stage: ChatStage, message: str) -> str:
        questions = STAGE_QUESTION_BANK[current_stage]
        if len(message) >= 80 and len(questions) > 1:
            return questions[1]
        return questions[0]

    def get_all_sessions(self) -> list[dict]:
        return [
            {
                "session_id": session_id,
                "current_stage": data["current_stage"],
                "message_count": data.get("message_count", 0),
            }
            for session_id, data in self.sessions.items()
        ]

    def resume_session(self, session_id: str) -> ChatStartResponse | None:
        if session_id not in self.sessions:
            return None
        data = self.sessions[session_id]
        stage = data["current_stage"]
        return ChatStartResponse(
            session_id=session_id,
            reply="会话已恢复，请继续提供简历信息。",
            stage=stage,
            stage_label=_STAGE_LABELS[stage],
            missing_info=self._get_missing_fields_for_stage(stage),
            should_summarize=False,
            summary_preview="",
        )

    def delete_session(self, session_id: str) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
