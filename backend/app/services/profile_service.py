import json, re
from pathlib import Path

from app.models.profile import ProfileData
from app.services.deepseek_service import DeepSeekService

DATA_DIR = Path(__file__).resolve().parents[3] / "data"
PROFILE_PATH = DATA_DIR / "profile.json"


class ProfileService:
    def __init__(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.deepseek_service = DeepSeekService()

    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        return self.deepseek_service.chat(system_prompt=system_prompt, user_prompt=user_prompt)

    def get_profile(self) -> ProfileData:
        if not PROFILE_PATH.exists():
            return ProfileData()
        try:
            return ProfileData(**json.loads(PROFILE_PATH.read_text(encoding="utf-8")))
        except Exception:
            return ProfileData()

    def save_profile(self, profile: ProfileData) -> None:
        PROFILE_PATH.write_text(profile.model_dump_json(indent=2, ensure_ascii=False), encoding="utf-8")

    def update_field(self, field_path: str, value) -> ProfileData:
        profile = self.get_profile()
        parts = field_path.split(".")
        current = profile
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                if hasattr(current, part):
                    setattr(current, part, value)
            else:
                if hasattr(current, part):
                    current = getattr(current, part)
        self.save_profile(profile)
        return profile

    def update_field_from_chat(self, stage: str, field_key: str, value: str) -> ProfileData:
        profile = self.get_profile()
        if stage == "basic_info":
            if hasattr(profile.basic_info, field_key):
                cur = getattr(profile.basic_info, field_key)
                if not cur or cur in ("", "None", "none"):
                    setattr(profile.basic_info, field_key, value)
        elif stage == "self_intro" and field_key == "self_intro":
            if not profile.self_intro:
                profile.self_intro = value
        elif stage == "skills":
            if value and value not in ("无", "没有", "None", "none", ""):
                if value not in profile.skills:
                    profile.skills.append(value)
        elif stage == "education":
            if not profile.education:
                profile.education.append(Education())
            cur = profile.education[-1]
            if hasattr(cur, field_key):
                cur_val = getattr(cur, field_key)
                if not cur_val or cur_val in ("", "None", "none"):
                    setattr(cur, field_key, value)
        elif stage == "project_experience":
            if not profile.project_experiences:
                profile.project_experiences.append(ProjectExperience())
            cur = profile.project_experiences[-1]
            if hasattr(cur, field_key):
                setattr(cur, field_key, value)
        elif stage == "work_experience":
            if not profile.work_experiences:
                profile.work_experiences.append(WorkExperience())
            cur = profile.work_experiences[-1]
            if hasattr(cur, field_key):
                setattr(cur, field_key, value)
        elif stage == "awards" and field_key == "awards":
            if value not in profile.awards:
                profile.awards.append(value)
        elif stage == "self_evaluation" and field_key == "self_evaluation":
            if value not in profile.self_evaluation:
                profile.self_evaluation.append(value)
        self.save_profile(profile)
        return profile

    def extract_from_conversation(self, stage: str, user_message: str, assistant_summary: str) -> ProfileData:
        system_prompt = (
            "Extract resume info from conversation. Output ONLY JSON with these keys:\n"
            "For stage 'basic_info': {\"name\":\"\",\"job_intention\":\"\",\"email\":\"\",\"phone\":\"\",\"birth_date\":\"\",\"highest_degree\":\"\"}\n"
            "For stage 'self_intro': {\"self_intro\":\"\"}\n"
            "For stage 'work_experience': {\"work_experiences\":[{\"company_name\":\"\",\"position_name\":\"\",\"work_time\":\"\",\"work_contents\":[]}]}\n"
            "For stage 'skills': {\"skills\":[]}\n"
            "For stage 'education': {\"education\":[{\"school_name\":\"\",\"major\":\"\",\"degree\":\"\",\"school_time\":\"\",\"main_courses\":[]}]}\n"
            "For stage 'project_experience': {\"project_experiences\":[{\"project_name\":\"\",\"project_time\":\"\",\"project_role\":\"\",\"technologies\":[],\"project_description\":\"\",\"personal_responsibilities\":[],\"project_results\":[]}]}\n"
            "For stage 'awards': {\"awards\":[]}\n"
            "For stage 'self_evaluation': {\"self_evaluation\":[]}\n"
            "Only extract explicitly stated info. Empty string/list if not found."
        )
        try:
            raw = self._call_llm(system_prompt, f"User: {user_message}\nSummary: {assistant_summary}\nStage: {stage}")
            raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
            raw = re.sub(r"\s*```$", "", raw).strip()
            extracted = json.loads(raw)
        except Exception:
            return self.get_profile()

        if not isinstance(extracted, dict):
            return self.get_profile()

        profile = self.get_profile()

        if stage == "basic_info":
            for f in ["name", "job_intention", "email", "phone", "birth_date", "highest_degree"]:
                v = extracted.get(f, "")
                if isinstance(v, str) and v.strip():
                    setattr(profile.basic_info, f, v.strip())
        elif stage == "self_intro":
            v = extracted.get("self_intro", "")
            if isinstance(v, str) and v.strip():
                profile.self_intro = v.strip()
        elif stage == "skills":
            s = extracted.get("skills", [])
            if isinstance(s, list) and s:
                profile.skills = [x for x in s if isinstance(x, str) and x.strip()]
        elif stage == "education":
            e = extracted.get("education", [])
            if isinstance(e, list) and e:
                from app.models.profile import Education
                profile.education = []
                for item in e:
                    if isinstance(item, dict) and any(v for v in item.values() if v):
                        profile.education.append(Education(**item))
        elif stage == "work_experience":
            exps = extracted.get("work_experiences", [])
            if isinstance(exps, list) and exps:
                from app.models.profile import WorkExperience
                valid = [WorkExperience(**x) for x in exps if isinstance(x, dict) and any(v for v in x.values() if v)]
                if valid:
                    profile.work_experiences = valid
        elif stage == "project_experience":
            projs = extracted.get("project_experiences", [])
            if isinstance(projs, list) and projs:
                from app.models.profile import ProjectExperience
                valid = [ProjectExperience(**x) for x in projs if isinstance(x, dict) and any(v for v in x.values() if v)]
                if valid:
                    profile.project_experiences = valid
        elif stage == "awards":
            a = extracted.get("awards", [])
            if isinstance(a, list) and a:
                profile.awards = [x.strip() for x in a if isinstance(x, str) and x.strip()]
        elif stage == "self_evaluation":
            se = extracted.get("self_evaluation", [])
            if isinstance(se, list) and se:
                profile.self_evaluation = [x.strip() for x in se if isinstance(x, str) and x.strip()]

        self.save_profile(profile)
        return profile
