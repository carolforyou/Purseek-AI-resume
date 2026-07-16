from app.models.profile import ProfileData
from app.models.resume import ResumeDraftResponse, ResumeEducationDraft, ResumeMarkdownResponse, ResumeProjectDraft
from app.services.profile_service import ProfileService


class ResumeService:
    def __init__(self) -> None:
        self.profile_service = ProfileService()

    def generate_draft(self) -> ResumeDraftResponse:
        profile = self.profile_service.get_profile()
        return ResumeDraftResponse(
            summary=profile.self_intro or "Please fill in your self-introduction first",
            skills=profile.skills or [],
            projects=self._build_projects(profile),
            education=self._build_education(profile),
        )

    def generate_markdown(self) -> ResumeMarkdownResponse:
        profile = self.profile_service.get_profile()
        lines: list[str] = []
        lines.append("# Personal Resume")
        lines.append("")
        lines.append("## Basic Information")
        lines.append(f"- Name: {profile.basic_info.name or 'N/A'}")
        lines.append(f"- Job Intention: {profile.basic_info.job_intention or 'N/A'}")
        lines.append(f"- Email: {profile.basic_info.email or 'N/A'}")
        lines.append(f"- Phone: {profile.basic_info.phone or 'N/A'}")
        lines.append("")
        lines.append("## Self Introduction")
        lines.append(profile.self_intro or "")
        lines.append("")
        lines.append("## Skills")
        lines.append(", ".join(profile.skills) if profile.skills else "N/A")
        lines.append("")
        lines.append("## Work Experience")
        for exp in profile.work_experiences:
            lines.append(f"- {exp.company_name} - {exp.position_name} ({exp.work_time})")
            for c in exp.work_contents:
                lines.append(f"  * {c}")
        lines.append("")
        lines.append("## Education")
        for edu in profile.education:
            lines.append(f"- {edu.school_name} - {edu.major} ({edu.degree}, {edu.school_time})")
        lines.append("")
        lines.append("## Project Experience")
        for proj in profile.project_experiences:
            lines.append(f"- {proj.project_name} ({proj.project_role}, {proj.project_time})")
            lines.append(f"  {proj.project_description}")
        lines.append("")
        lines.append("## Awards")
        for a in profile.awards:
            lines.append(f"- {a}")
        lines.append("")
        lines.append("## Self Evaluation")
        for e in profile.self_evaluation:
            lines.append(f"- {e}")

        return ResumeMarkdownResponse(content="\n".join(lines).strip())

    def _build_projects(self, profile: ProfileData) -> list[ResumeProjectDraft]:
        if not profile.project_experiences:
            return [ResumeProjectDraft(title="Project Experience (to be filled)", bullets=["Please fill in via AI Chat."])]
        drafts: list[ResumeProjectDraft] = []
        for project in profile.project_experiences[:3]:
            bullets = [project.project_description] if project.project_description else []
            if project.project_role:
                bullets.append(f"Role: {project.project_role}")
            if project.technologies:
                bullets.append(f"Tech: {' / '.join(project.technologies)}")
            drafts.append(ResumeProjectDraft(title=project.project_name or "Project", bullets=bullets))
        return drafts

    def _build_education(self, profile: ProfileData) -> list[ResumeEducationDraft]:
        if not profile.education:
            return [ResumeEducationDraft(title="Education (to be filled)", bullets=["Please fill in via AI Chat."])]
        drafts: list[ResumeEducationDraft] = []
        for edu in profile.education[:2]:
            title = " ".join(p for p in [edu.degree, edu.major, edu.school_name] if p) or "Education"
            bullets = [f"School: {edu.school_name}"] if edu.school_name else []
            if edu.main_courses:
                bullets.append(f"Main Courses: {' / '.join(edu.main_courses[:3])}")
            drafts.append(ResumeEducationDraft(title=title, bullets=bullets))
        return drafts

    def polish_section(self, section_id: str, content: str) -> dict:
        if not content.strip():
            return {"original": content, "polished": content, "changes": []}
        system_prompt = (
            "You are a professional resume writing expert. Polish the given resume section.\n"
            "Rules: 1. Keep original language. 2. Use strong action verbs and quantifiable results.\n"
            "3. Keep same information but more professional and impactful.\n"
            "4. Output ONLY a JSON object: {\"polished\": \"...\", \"changes\": [\"what was improved\"]}"
        )
        try:
            import json, re
            from app.services.deepseek_service import DeepSeekService
            raw = DeepSeekService().chat(system_prompt=system_prompt, user_prompt=f"Section: {section_id}\nContent:\n{content}")
            raw = re.sub(r'^```(?:json)?\s*', '', raw.strip())
            raw = re.sub(r'\s*```$', '', raw).strip()
            result = json.loads(raw)
            return {"original": content, "polished": result.get("polished", content), "changes": result.get("changes", [])}
        except Exception:
            return {"original": content, "polished": content, "changes": []}

    def polish_full(self) -> dict:
        raw = self.generate_markdown()
        system_prompt = (
            "You are a professional resume writing expert. Polish and improve this resume.\n"
            "Rules: 1. Keep original language. 2. Use strong action verbs and quantifiable results.\n"
            "3. Output ONLY JSON: {\"content\": \"polished markdown\", \"changes\": [\"improvements\"]}"
        )
        try:
            import json, re
            from app.services.deepseek_service import DeepSeekService
            result_raw = DeepSeekService().chat(system_prompt=system_prompt, user_prompt=raw.content)
            result_raw = re.sub(r'^```(?:json)?\s*', '', result_raw.strip())
            result_raw = re.sub(r'\s*```$', '', result_raw).strip()
            result = json.loads(result_raw)
            return {"content": result.get("content", raw.content), "changes": result.get("changes", [])}
        except Exception:
            return {"content": raw.content, "changes": []}

    def translate_to_english(self) -> dict:
        raw = self.generate_markdown()
        if not raw.content.strip():
            return {"content": ""}
        system_prompt = "You are a professional resume translator. Translate the following resume from Chinese to English.\nRules: 1. Translate ALL Chinese to natural, professional English.\n2. Keep markdown structure.\n3. Use professional vocabulary and strong action verbs.\n4. Keep proper nouns as-is.\n5. Output ONLY the translated markdown, no extra text."
        try:
            from app.services.deepseek_service import DeepSeekService
            return {"content": DeepSeekService().chat(system_prompt=system_prompt, user_prompt=raw.content).strip()}
        except Exception:
            return {"content": raw.content}

    def get_layout(self) -> dict:
        import json
        from pathlib import Path
        layout_path = Path(__file__).resolve().parents[3] / "data" / "resume_layout.json"
        default = {"sections": [
            {"id": "basic_info", "title": "Basic Information", "type": "basic_info", "order": 1, "visible": True},
            {"id": "self_intro", "title": "Self Introduction", "type": "self_intro", "order": 2, "visible": True},
            {"id": "skills", "title": "Skills", "type": "skills", "order": 3, "visible": True},
            {"id": "work_experience", "title": "Work Experience", "type": "work_experience", "order": 4, "visible": True},
            {"id": "project_experience", "title": "Project Experience", "type": "project_experience", "order": 5, "visible": True},
            {"id": "education", "title": "Education", "type": "education", "order": 6, "visible": True},
            {"id": "awards", "title": "Awards", "type": "awards", "order": 7, "visible": True},
            {"id": "self_evaluation", "title": "Self Evaluation", "type": "self_evaluation", "order": 8, "visible": True},
        ]}
        if layout_path.exists():
            try:
                return json.loads(layout_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return default

    def update_layout(self, data: dict) -> dict:
        import json
        from pathlib import Path
        layout_path = Path(__file__).resolve().parents[3] / "data" / "resume_layout.json"
        layout_path.parent.mkdir(parents=True, exist_ok=True)
        layout_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return data

