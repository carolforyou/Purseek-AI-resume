from pydantic import BaseModel


class CustomField(BaseModel):
    key: str = ""
    value: str = ""


class BasicInfo(BaseModel):
    name: str = ""
    job_intention: str = ""
    email: str = ""
    phone: str = ""
    birth_date: str = ""
    highest_degree: str = ""
    photo: str = ""
    custom_fields: list[CustomField] = []


class WorkExperience(BaseModel):
    company_name: str = ""
    position_name: str = ""
    work_time: str = ""
    work_contents: list[str] = []


class Education(BaseModel):
    school_name: str = ""
    major: str = ""
    degree: str = ""
    school_time: str = ""
    main_courses: list[str] = []


class ProjectExperience(BaseModel):
    project_name: str = ""
    project_time: str = ""
    project_role: str = ""
    technologies: list[str] = []
    project_description: str = ""
    personal_responsibilities: list[str] = []
    project_results: list[str] = []


class ProfileData(BaseModel):
    basic_info: BasicInfo = BasicInfo()
    self_intro: str = ""
    work_experiences: list[WorkExperience] = []
    skills: list[str] = []
    education: list[Education] = []
    project_experiences: list[ProjectExperience] = []
    awards: list[str] = []
    self_evaluation: list[str] = []


class ExtractValueRequest(BaseModel):
    session_id: str
    stage: str
    user_message: str
    assistant_summary: str


class ExtractValueResponse(BaseModel):
    message: str
    extracted_section: str
    profile: ProfileData


class ProfileUpdateRequest(BaseModel):
    field_path: str
    value: str | list[str]
