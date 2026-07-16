export type ChatStage = "basic_info" | "self_intro" | "work_experience" | "skills" | "education" | "project_experience" | "awards" | "self_evaluation";
export type ChatRole = "assistant" | "user";

export type ChatMessage = { id: string; role: ChatRole; content: string };
export type ChatStartResponse = { session_id: string; reply: string; stage: ChatStage; stage_label: string; missing_info: string[]; should_summarize: boolean; summary_preview: string };
export type ChatMessageRequest = { session_id: string; message: string; stage: ChatStage };
export type ChatMessageResponse = { reply: string; stage: ChatStage; stage_label: string; missing_info: string[]; should_summarize: boolean; summary_preview: string };

export type CustomField = { key: string; value: string };

export type ProfileData = {
  basic_info: {
    name: string; job_intention: string; email: string; phone: string;
    birth_date: string; highest_degree: string; photo?: string;
    custom_fields?: CustomField[];
  };
  self_intro: string;
  work_experiences: Array<{ company_name: string; position_name: string; work_time: string; work_contents: string[] }>;
  skills: string[];
  education: Array<{ school_name: string; major: string; degree: string; school_time: string; main_courses: string[] }>;
  project_experiences: Array<{ project_name: string; project_time: string; project_role: string; technologies: string[]; project_description: string; personal_responsibilities: string[]; project_results: string[] }>;
  awards: string[];
  self_evaluation: string[];
};

export type ExtractValueResponse = { message: string; extracted_section: string; profile: ProfileData };
export type ProfileUpdateRequest = { field_path: string; value: string | string[] };

export type ResumeDraft = {
  summary: string; skills: string[];
  projects: Array<{ title: string; bullets: string[] }>;
  education: Array<{ title: string; bullets: string[] }>;
};

export type JobDescription = { id: string; title: string; company: string; location: string; salary: string; experience: string; education: string; job_type: string; industry: string; description: string; requirements: string; skills: string[]; responsibilities: string[] };
export type MatchResult = { jd_id: string; jd_title: string; jd_company: string; total_score: number; skill_score: number; experience_score: number; education_score: number; preference_score: number; strengths: string[]; weaknesses: string[]; suggestions: string[]; missing_skills?: string[] };
export type CustomResumeResponse = { jd_id: string; jd_title: string; content: string; modifications: string[] };
export type ResumeSection = { id: string; title: string; type: string; order: number; visible: boolean };
export type ResumeLayout = { sections: ResumeSection[] };
export type PolishResponse = { original: string; polished: string; changes: string[] };
export type JDParseResponse = { title: string; company: string; location: string; skills: string[]; description: string; requirements: string; responsibilities: string[] };

export type InterviewQuestion = { question: string; category: string; difficulty: string; suggested_answer: string };
export type InterviewCategory = { id: string; name: string; description: string };
export type InterviewGenerateResponse = { questions: InterviewQuestion[]; count: number };
export type InterviewCategoriesResponse = { categories: InterviewCategory[] };
// External Job Search
export interface ExternalJobItem {
  job_id: string;
  title: string;
  company: string;
  location: string;
  salary: string;
  experience: string;
  education: string;
  description: string;
  url: string;
}

export interface JobSearchResponse {
  items: ExternalJobItem[];
  total: number;
  page: number;
  page_size: number;
  source: string;
}
