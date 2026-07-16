import json
from pathlib import Path
from uuid import uuid4

from app.models.jd import JobDescription, MatchResult
from app.models.profile import ProfileData
from app.services.profile_service import ProfileService

DATA_DIR = Path(__file__).resolve().parents[3] / "data"
JD_FILE = DATA_DIR / "jds.json"


class JDService:
    def __init__(self) -> None:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.profile_service = ProfileService()

    def get_all_jds(self) -> list[JobDescription]:
        if not JD_FILE.exists():
            return []
        try:
            content = JD_FILE.read_text(encoding="utf-8")
            data = json.loads(content)
            return [JobDescription(**item) for item in data]
        except (json.JSONDecodeError, Exception):
            return []

    def get_jd(self, jd_id: str) -> JobDescription | None:
        jds = self.get_all_jds()
        return next((jd for jd in jds if jd.id == jd_id), None)

    def save_jd(self, jd: JobDescription) -> JobDescription:
        jds = self.get_all_jds()
        if jd.id:
            idx = next((i for i, existing in enumerate(jds) if existing.id == jd.id), -1)
            if idx >= 0:
                jds[idx] = jd
            else:
                jds.append(jd)
        else:
            jd.id = f"jd_{uuid4().hex[:8]}"
            jds.append(jd)

        JD_FILE.write_text(json.dumps([item.model_dump() for item in jds], indent=2, ensure_ascii=False), encoding="utf-8")
        return jd

    def delete_jd(self, jd_id: str) -> bool:
        jds = self.get_all_jds()
        new_jds = [jd for jd in jds if jd.id != jd_id]
        if len(new_jds) != len(jds):
            JD_FILE.write_text(json.dumps([item.model_dump() for item in new_jds], indent=2, ensure_ascii=False), encoding="utf-8")
            return True
        return False

    def match_analysis(self, jd_id: str) -> MatchResult | None:
        jd = self.get_jd(jd_id)
        if not jd:
            return None

        profile = self.profile_service.get_profile()
        skill_score = self._calculate_skill_score(jd=jd, profile=profile)
        experience_score = self._calculate_experience_score(jd=jd, profile=profile)
        education_score = self._calculate_education_score(jd=jd, profile=profile)
        preference_score = self._calculate_preference_score(jd=jd, profile=profile)

        total_score = (skill_score * 0.4) + (experience_score * 0.3) + (education_score * 0.2) + (preference_score * 0.1)

        strengths, weaknesses, suggestions = self._generate_analysis(jd=jd, profile=profile)

        return MatchResult(
            jd_id=jd.id,
            jd_title=jd.title,
            jd_company=jd.company,
            total_score=round(total_score, 1),
            skill_score=round(skill_score, 1),
            experience_score=round(experience_score, 1),
            education_score=round(education_score, 1),
            preference_score=round(preference_score, 1),
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
        )

    def _calculate_skill_score(self, jd: JobDescription, profile: ProfileData) -> float:
        jd_skills_lower = [s.lower() for s in jd.skills]
        if not jd_skills_lower:
            return 50.0

        profile_skills = []
        profile_skills.extend(profile.skills)
        profile_skills_lower = [s.lower() for s in profile_skills]

        matched = 0
        for jd_skill in jd_skills_lower:
            for profile_skill in profile_skills_lower:
                # Try exact word match first, then substring
                if jd_skill in profile_skill.split() or profile_skill in jd_skill.split():
                    matched += 1
                    break
                elif jd_skill in profile_skill or profile_skill in jd_skill:
                    matched += 0.5
                    break

        return min(100.0, (matched / len(jd_skills_lower)) * 100)

    def _calculate_experience_score(self, jd: JobDescription, profile: ProfileData) -> float:
        has_projects = len(profile.project_experiences) > 0
        has_work = len(profile.work_experiences) > 0
        
        # Check experience field first, then fall back to JD description
        exp_text = jd.experience or jd.description or ""
        exp_text_lower = exp_text.lower()
        
        # Count work experiences as a base
        work_count = len(profile.work_experiences)
        project_count = len(profile.project_experiences)
        
        if "\u5e94\u5c4a" in exp_text or "\u4e0d\u9650" in exp_text or "intern" in exp_text_lower or "fresh" in exp_text_lower:
            return 75.0 if has_projects else 50.0
        
        # Try to find required years of experience
        years = 0
        import re
        m = re.search(r"(\d+)[\s-]*\u5e74", exp_text)
        if m:
            years = int(m.group(1))
        
        if years <= 1:
            if has_work or has_projects:
                return 90.0
            return 50.0
        elif years <= 3:
            if work_count >= 2:
                return 85.0
            elif work_count >= 1 or project_count >= 2:
                return 65.0
            return 45.0
        elif years <= 5:
            if work_count >= 3:
                return 85.0
            elif work_count >= 1:
                return 60.0
            return 40.0
        elif years > 5:
            if work_count >= 4:
                return 85.0
            elif work_count >= 2:
                return 55.0
            return 35.0
        
        # If no year info, estimate from skills match
        jd_skills_lower = [s.lower() for s in jd.skills]
        profile_skills_lower = [s.lower() for s in profile.skills]
        matched = sum(1 for js in jd_skills_lower for ps in profile_skills_lower if js in ps or ps in js)
        
        if has_work:
            return 55.0 + min(30.0, matched * 5.0)
        elif has_projects:
            return 45.0 + min(25.0, matched * 5.0)
        return 35.0 + min(15.0, matched * 5.0)

    def _calculate_education_score(self, jd: JobDescription, profile: ProfileData) -> float:
        edu_text = jd.education or jd.description or ""
        user_degree = profile.basic_info.highest_degree or (profile.education[0].degree if profile.education else "")

        degree_map = {"\u5927\u4e13": 1, "\u672c\u79d1": 2, "\u7855\u58eb": 3, "\u535a\u58eb": 4}
        user_level = degree_map.get(user_degree, 2)

        # Find required degree from JD
        required_level = 0
        if "\u535a\u58eb" in edu_text:
            required_level = 4
        elif "\u7855\u58eb" in edu_text:
            required_level = 3
        elif "\u672c\u79d1" in edu_text:
            required_level = 2
        elif "\u5927\u4e13" in edu_text:
            required_level = 1
        
        if required_level == 0:
            # No degree specified - check if user has any education
            return 80.0 if user_level >= 2 else 60.0
        
        if user_level >= required_level + 1:
            return 95.0
        elif user_level >= required_level:
            return 85.0
        elif user_level >= required_level - 1:
            return 60.0
        else:
            return 35.0

    def _calculate_preference_score(self, jd: JobDescription, profile: ProfileData) -> float:
        score = 50.0

        # Match job_intention with JD title
        job_intention = profile.basic_info.job_intention or ""
        if job_intention and jd.title:
            if job_intention.lower() in jd.title.lower() or jd.title.lower() in job_intention.lower():
                score += 20.0

        # Match skills with JD requirements
        jd_skills_lower = [s.lower() for s in jd.skills]
        profile_skills_lower = [s.lower() for s in profile.skills]
        matched = sum(1 for js in jd_skills_lower for ps in profile_skills_lower if js in ps or ps in js)
        if matched > 0:
            score += min(30.0, matched * 10.0)

        return min(100.0, score)

    def _generate_analysis(self, jd: JobDescription, profile: ProfileData) -> tuple[list[str], list[str], list[str]]:
        strengths: list[str] = []
        weaknesses: list[str] = []
        suggestions: list[str] = []

        jd_skills_lower = [s.lower() for s in jd.skills]
        profile_skills = []
        profile_skills.extend(profile.skills)
        profile_skills_lower = [s.lower() for s in profile_skills]

        matched_skills = []
        missing_skills = []

        for jd_skill in jd_skills_lower:
            found = False
            for profile_skill in profile_skills_lower:
                if jd_skill in profile_skill or profile_skill in jd_skill:
                    matched_skills.append(jd_skill)
                    found = True
                    break
            if not found:
                missing_skills.append(jd_skill)

        if matched_skills:
            strengths.append(f"\u6280\u80fd\u5339\u914d\uff1a\u4f60\u5df2\u638c\u63e1{', '.join(matched_skills[:3])}\u7b49\u5173\u952e\u6280\u672f")
        else:
            weaknesses.append(f"\u6280\u80fd\u4e0d\u5339\u914d\uff1a\u672a\u627e\u5230\u4e0e\u8be5\u5c97\u4f4d\u5339\u914d\u7684\u6280\u80fd")

        if missing_skills:
            weaknesses.append(f"\u7f3a\u5c11\u6280\u80fd\uff1a\u5c97\u4f4d\u8981\u6c42{', '.join(missing_skills[:3])}")
            suggestions.append(f"\u5efa\u8bae\u5b66\u4e60\u6216\u8865\u5145{', '.join(missing_skills[:2])}\u76f8\u5173\u6280\u80fd")

        if not profile.project_experiences:
            weaknesses.append("\u9879\u76ee\u7ecf\u9a8c\u4e0d\u8db3")
            suggestions.append("\u8865\u5145\u81f3\u5c111-2\u4e2a\u5b8c\u6574\u9879\u76ee\u7ecf\u9a8c")

        if not profile.work_experiences and not jd.experience:
            suggestions.append("\u5efa\u8bae\u8865\u5145\u5b9e\u4e60\u6216\u5de5\u4f5c\u7ecf\u5386")

        job_intention = profile.basic_info.job_intention or ""
        if job_intention and jd.title:
            if job_intention.lower() in jd.title.lower() or jd.title.lower() in job_intention.lower():
                strengths.append(f"\u5c97\u4f4d\u5339\u914d\uff1a\u6c42\u804c\u610f\u5411{job_intention}\u4e0e\u8be5\u804c\u4f4d\u76f8\u7b26")

        if jd.location and job_intention:
            strengths.append("\u6c42\u804c\u610f\u5411\u660e\u786e\uff0c\u5173\u6ce8\u76ee\u6807\u5c97\u4f4d")

        if not strengths:
            strengths.append("\u7b80\u5386\u57fa\u672c\u5b8c\u6574\uff0c\u7ee7\u7eed\u5b8c\u5584\u9879\u76ee\u7ec6\u8282")

        if not weaknesses:
            weaknesses.append("\u6682\u65e0\u660e\u663e\u77ed\u677f")

        if not suggestions:
            suggestions.append("\u4fdd\u6301\u5f53\u524d\u7b80\u5386\u7ed3\u6784\uff0c\u91cd\u70b9\u4f18\u5316\u9879\u76ee\u63cf\u8ff0")

        return strengths, weaknesses, suggestions

    def parse_jd_text(self, text: str) -> dict:
        system_prompt = (
            "You are a job description parser. Extract structured information from the JD text.\n"
            "Output ONLY a JSON object with these fields:\n"
            "  title: job title (string)\n"
            "  company: company name (string, empty if not found)\n"
            "  location: work location (string, empty if not found)\n"
            "  skills: list of required skills/technologies (array of strings)\n"
            "  description: summary of the role (string)\n"
            "  requirements: job requirements/qualifications (string)\n"
            "  responsibilities: list of key responsibilities (array of strings)\n"
            "Rules: only extract what is explicitly stated. Empty string/list if not found."
        )
        try:
            import re
            from app.services.groq_service import GroqService
            from app.services.deepseek_service import DeepSeekService
            
            groq_service = GroqService()
            if groq_service.is_configured():
                raw = groq_service.chat(system_prompt=system_prompt, user_prompt=text)
            else:
                raw = DeepSeekService().chat(system_prompt=system_prompt, user_prompt=text)
            
            raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
            raw = re.sub(r"\s*```$", "", raw).strip()
            result = json.loads(raw)
            return {
                "title": result.get("title", ""),
                "company": result.get("company", ""),
                "location": result.get("location", ""),
                "skills": result.get("skills", []),
                "description": result.get("description", ""),
                "requirements": result.get("requirements", ""),
                "responsibilities": result.get("responsibilities", []),
            }
        except Exception:
            return {
                "title": "Unknown Position",
                "company": "",
                "location": "",
                "skills": [],
                "description": text[:200],
                "requirements": "",
                "responsibilities": [],
            }
