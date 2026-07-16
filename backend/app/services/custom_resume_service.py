from app.models.jd import CustomResumeResponse, JobDescription
from app.models.profile import ProfileData


class CustomResumeService:
    def __init__(self) -> None:
        self.jd_service = JDService()
        self.profile_service = ProfileService()

    def generate_custom_resume(self, jd_id: str) -> CustomResumeResponse | None:
        jd = self.jd_service.get_jd(jd_id)
        if not jd:
            return None

        profile = self.profile_service.get_profile()
        modifications = []

        skills_section = self._prioritize_skills(jd=jd, profile=profile, modifications=modifications)
        projects_section = self._reorder_projects(jd=jd, profile=profile, modifications=modifications)
        experience_section = self._highlight_experience(jd=jd, profile=profile, modifications=modifications)
        summary_section = self._rewrite_summary(jd=jd, profile=profile, modifications=modifications)

        return CustomResumeResponse(
            jd_id=jd.id,
            jd_title=jd.title,
            content=self._build_resume_content(
                jd=jd,
                profile=profile,
                summary=summary_section,
                skills=skills_section,
                experience=experience_section,
                projects=projects_section,
                modifications=modifications,
            ),
            modifications=modifications,
        )

    def _prioritize_skills(self, jd: JobDescription, profile: ProfileData, modifications: list[str]) -> str:
        jd_skills_lower = [s.lower() for s in jd.skills]
        matched_skills = []
        other_skills = []

        for skill in profile.skills:
            skill_lower = skill.lower()
            is_matched = any(jd_skill in skill_lower or skill_lower in jd_skill for jd_skill in jd_skills_lower)
            if is_matched:
                matched_skills.append(skill)
            else:
                other_skills.append(skill)

        if matched_skills:
            matched_display = ", ".join(matched_skills[:3])
            modifications.append(f"技能排序优化：将与{jd.title}相关的{matched_display}等技能放在前面")

        all_skills = matched_skills + other_skills
        return "、".join(all_skills[:10]) if all_skills else "暂无技能信息"

    def _reorder_projects(self, jd: JobDescription, profile: ProfileData, modifications: list[str]) -> str:
        if not profile.project_experiences:
            return "暂无项目经验"

        jd_text = (jd.description + jd.requirements).lower()
        scored_projects = []

        for project in profile.project_experiences:
            score = 0
            project_text = (project.project_description + " ".join(project.technologies)).lower()

            for jd_skill in jd.skills:
                if jd_skill.lower() in project_text:
                    score += 2

            for tech in project.technologies:
                if tech.lower() in jd_text:
                    score += 1

            scored_projects.append((project, score))

        scored_projects.sort(key=lambda x: x[1], reverse=True)
        ordered_projects = [p[0] for p in scored_projects]

        if len(scored_projects) > 1:
            top_project = ordered_projects[0]
            top_score = scored_projects[0][1]
            if top_score > 0:
                modifications.append(f"项目排序优化：将与{jd.title}最相关的「{top_project.project_name}」放在首位")
            else:
                modifications.append(f"项目排序优化：按默认顺序展示项目经验")

        lines = []
        for project in ordered_projects[:2]:
            desc = project.project_description[:60]
            if project.technologies:
                techs = "[" + ", ".join(project.technologies[:3]) + "]"
                lines.append(f"- {project.project_name} {techs}：{desc}")
            else:
                lines.append(f"- {project.project_name}：{desc}")
        return "\n".join(lines)

    def _highlight_experience(self, jd: JobDescription, profile: ProfileData, modifications: list[str]) -> str:
        if not profile.work_experiences:
            return "暂无工作经验"

        jd_text = (jd.description + jd.requirements).lower()
        lines = []
        found_highlight = False

        for exp in profile.work_experiences[:2]:
            highlighted_contents = []
            for content in exp.work_contents[:3]:
                if any(skill.lower() in content.lower() for skill in jd.skills):
                    highlighted_contents.append(content)

            if highlighted_contents:
                found_highlight = True
                lines.append(f"- {exp.company_name} {exp.position_name}：{'；'.join(highlighted_contents[:2])}")
            else:
                lines.append(f"- {exp.company_name} {exp.position_name}：{'；'.join(exp.work_contents[:2])}")

        if found_highlight:
            modifications.append(f"工作经验优化：突出与{jd.title}相关的工作内容")

        return "\n".join(lines)

    def _rewrite_summary(self, jd: JobDescription, profile: ProfileData, modifications: list[str]) -> str:
        target_role = profile.basic_info.job_intention or "软件工程师"
        location = profile.basic_info.custom_fields[0].value if profile.basic_info.custom_fields else "目标城市"

        matched_skills = []
        jd_skills_lower = [s.lower() for s in jd.skills]

        for skill in profile.skills[:6]:
            skill_lower = skill.lower()
            if any(jd_skill in skill_lower or skill_lower in jd_skill for jd_skill in jd_skills_lower):
                matched_skills.append(skill)

        if matched_skills:
            skill_text = "、".join(matched_skills[:4])
            modifications.append(f"自我介绍优化：针对{jd.title}需求，突出{skill_text}等核心技能")
        else:
            skill_text = "相关技术"
            modifications.append(f"自我介绍优化：针对{jd.title}需求重新撰写")

        project_count = len(profile.project_experiences)
        exp_count = len(profile.work_experiences)

        exp_text = f"{exp_count}年工作经验，" if exp_count > 0 else ""

        return f"{target_role}方向候选人，期望在{location}发展。{exp_text}熟练掌握{skill_text}，有{project_count}个项目经验，具备良好的团队协作能力和快速学习能力。"

    def _build_resume_content(self, jd: JobDescription, profile: ProfileData, summary: str, skills: str, experience: str, projects: str, modifications: list[str] = None) -> str:
        lines = []
        lines.append(f"# 定制简历 - {jd.title}")
        lines.append("")
        lines.append(f"## 应聘岗位：{jd.title}")
        lines.append(f"## 目标公司：{jd.company}")
        lines.append(f"## 工作地点：{jd.location}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## 基本信息")
        lines.append(f"- 姓名：{profile.basic_info.name or '待填写'}")
        lines.append(f"- 求职意向：{jd.title}")
        lines.append(f"- 邮箱：{profile.basic_info.email or '待填写'}")
        lines.append(f"- 电话：{profile.basic_info.phone or '待填写'}")
        lines.append("")
        lines.append("## 自我介绍")
        lines.append(summary)
        lines.append("")
        lines.append("## 核心技能")
        lines.append(skills)
        lines.append("")
        lines.append("## 工作经验")
        lines.append(experience)
        lines.append("")
        lines.append("## 项目经验")
        lines.append(projects)
        lines.append("")
        lines.append("## 教育背景")
        edu_info = "待填写"
        if profile.education:
            first = profile.education[0]
            parts = []
            if first.school_name: parts.append(first.school_name)
            if first.major: parts.append(first.major)
            if first.degree: parts.append(first.degree)
            if first.school_time: parts.append(f"时间：{first.school_time}")
            edu_info = " - ".join(parts) if parts else "待填写"
        lines.append(f"- {edu_info}")
        lines.append("")
        lines.append("---")
        lines.append("")
        if modifications:
            lines.append("## 修改说明")
            for i, mod in enumerate(modifications, 1):
                lines.append(f"{i}. {mod}")

        return "\n".join(lines)


from app.services.jd_service import JDService
from app.services.profile_service import ProfileService