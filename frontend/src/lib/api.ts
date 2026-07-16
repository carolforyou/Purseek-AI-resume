import type {
  ChatMessageRequest,
  ChatMessageResponse,
  ChatStartResponse,
  CustomResumeResponse,
  ExtractValueResponse,
  InterviewCategoriesResponse,
  InterviewGenerateResponse,
  JDParseResponse,
  JobDescription,
  MatchResult,
  PolishResponse,
  ProfileData,
  ProfileUpdateRequest,
  ResumeDraft,
  ResumeLayout,
} from "../types/index";

const API_BASE = "/api";

// Chat
export async function startChat(): Promise<ChatStartResponse> {
  const r = await fetch(`${API_BASE}/chat/start`, { method: "POST", headers: { "Content-Type": "application/json" } });
  if (!r.ok) throw new Error("Start chat failed");
  return r.json();
}

export async function sendChatMessage(payload: ChatMessageRequest): Promise<ChatMessageResponse> {
  const r = await fetch(`${API_BASE}/chat/message`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!r.ok) throw new Error("Send message failed");
  return r.json();
}

export async function extractValue(payload: { session_id: string; stage: string; user_message: string; assistant_summary: string }): Promise<ExtractValueResponse> {
  const r = await fetch(`${API_BASE}/profile/extract`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!r.ok) throw new Error("Extract failed");
  return r.json();
}

// Profile
export async function fetchProfile(): Promise<ProfileData> {
  const r = await fetch(`${API_BASE}/profile`);
  if (!r.ok) throw new Error("Fetch profile failed");
  return r.json();
}

export async function updateProfile(payload: ProfileUpdateRequest): Promise<ProfileData> {
  const r = await fetch(`${API_BASE}/profile`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
  if (!r.ok) throw new Error("Update profile failed");
  return r.json();
}

export async function saveProfile(profile: ProfileData): Promise<ProfileData> {
  const r = await fetch(`${API_BASE}/profile/save`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(profile) });
  if (!r.ok) throw new Error("Save profile failed");
  return r.json();
}

// Resume
export async function fetchResumeDraft(): Promise<ResumeDraft> {
  const r = await fetch(`${API_BASE}/resume/draft`);
  if (!r.ok) throw new Error("Fetch resume draft failed");
  return r.json();
}

export async function polishResume(sectionId: string, content: string): Promise<PolishResponse> {
  const r = await fetch(`${API_BASE}/resume/polish`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ section_id: sectionId, content }) });
  if (!r.ok) throw new Error("Polish failed");
  return r.json();
}

export async function polishFullResume(): Promise<{ content: string; changes: string[] }> {
  const r = await fetch(`${API_BASE}/resume/polish-full`, { method: "POST" });
  if (!r.ok) throw new Error("Polish full resume failed");
  return r.json();
}

export function getResumeMarkdownExportUrl(): string { return `${API_BASE}/resume-export/markdown`; }
export function getResumeTemplateDocxExportUrl(): string { return `${API_BASE}/resume-export/template-docx`; }
export function getResumePdfExportUrl(): string { return `${API_BASE}/resume-export/pdf`; }

// JD
export async function getAllJds(): Promise<JobDescription[]> {
  const r = await fetch(`${API_BASE}/jd`);
  if (!r.ok) throw new Error("Get JDs failed");
  return r.json();
}

export async function createJd(jd: Omit<JobDescription, "id">): Promise<JobDescription> {
  const r = await fetch(`${API_BASE}/jd`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(jd) });
  if (!r.ok) throw new Error("Create JD failed");
  return r.json();
}

export async function deleteJd(jdId: string): Promise<void> {
  await fetch(`${API_BASE}/jd/${jdId}`, { method: "DELETE" });
}

export async function parseJdText(text: string): Promise<JDParseResponse> {
  const r = await fetch(`${API_BASE}/jd/parse`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text }) });
  if (!r.ok) throw new Error("Parse JD failed");
  return r.json();
}

export async function getMatchResult(jdId: string): Promise<MatchResult> {
  const r = await fetch(`${API_BASE}/jd/${jdId}/match`);
  if (!r.ok) throw new Error("Match analysis failed");
  return r.json();
}

export async function generateCustomResume(jdId: string): Promise<CustomResumeResponse> {
  const r = await fetch(`${API_BASE}/custom-resume`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ jd_id: jdId }) });
  if (!r.ok) throw new Error("Generate custom resume failed");
  return r.json();
}

// Resume Layout
export async function getResumeLayout(): Promise<ResumeLayout> {
  const r = await fetch(`${API_BASE}/resume/layout`);
  if (!r.ok) throw new Error("Get layout failed");
  return r.json();
}

export async function updateResumeLayout(layout: ResumeLayout): Promise<ResumeLayout> {
  const r = await fetch(`${API_BASE}/resume/layout`, { method: "PUT", headers: { "Content-Type": "application/json" }, body: JSON.stringify(layout) });
  if (!r.ok) throw new Error("Update layout failed");
  return r.json();
}

export async function translateResumeToEnglish(): Promise<{ content: string }> {
  const r = await fetch(`${API_BASE}/resume/translate-to-english`, { method: "POST" });
  if (!r.ok) throw new Error("Translate failed");
  return r.json();
}

// Sessions
export async function listSessions(): Promise<Array<{ session_id: string; current_stage: string; stage_label: string; preview: string; message_count: number; updated_at: string }>> {
  const r = await fetch(`${API_BASE}/chat/sessions`);
  if (!r.ok) throw new Error("List sessions failed");
  return r.json();
}

export async function resumeSession(sessionId: string): Promise<any> {
  const r = await fetch(`${API_BASE}/chat/session/${sessionId}/resume`, { method: "POST" });
  if (!r.ok) throw new Error("Resume session failed");
  return r.json();
}

export async function deleteSession(sessionId: string): Promise<void> {
  const r = await fetch(`${API_BASE}/chat/session/${sessionId}`, { method: "DELETE" });
  if (!r.ok) throw new Error("Delete session failed");
}

// Profile Export
export async function exportProfile(): Promise<{ filename: string; content: any }> {
  const r = await fetch(`${API_BASE}/profile/export`);
  if (!r.ok) throw new Error("Export profile failed");
  return r.json();
}

// Knowledge Base
export async function uploadKnowledge(formData: FormData): Promise<any> {
  const r = await fetch(`${API_BASE}/knowledge/upload`, { method: "POST", body: formData });
  if (!r.ok) throw new Error("Upload knowledge failed");
  return r.json();
}

export async function queryKnowledge(question: string): Promise<any> {
  const r = await fetch(`${API_BASE}/knowledge/query`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question }) });
  if (!r.ok) throw new Error("Query knowledge failed");
  return r.json();
}

export async function getKnowledgeStats(): Promise<any> {
  const r = await fetch(`${API_BASE}/knowledge/stats`);
  if (!r.ok) throw new Error("Get knowledge stats failed");
  return r.json();
}

// Interview

// ===== External Job Search (Liepin MCP) =====

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

export async function searchExternalJobs(keyword: string, page: number = 1): Promise<JobSearchResponse> {
  const r = await fetch(`${API_BASE}/jobs/search?keyword=${encodeURIComponent(keyword)}&page=${page}`);
  if (!r.ok) throw new Error("Search external jobs failed");
  return r.json();
}

export async function importExternalJob(job: {
  job_id: string; title: string; company: string; location?: string;
  salary?: string; description?: string; requirements?: string;
  skills?: string[]; responsibilities?: string[];
  experience?: string; education?: string; industry?: string;
}): Promise<JobDescription> {
  const r = await fetch(`${API_BASE}/jobs/import`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(job),
  });
  if (!r.ok) throw new Error("Import job failed");
  return r.json();
}

export async function getExternalJobDetail(jobId: string): Promise<any> {
  const r = await fetch(`${API_BASE}/jobs/external/${jobId}`);
  if (!r.ok) throw new Error("Get job detail failed");
  return r.json();
}

export async function checkExternalJobStatus(): Promise<{ available: boolean; source: string; note: string }> {
  const r = await fetch(`${API_BASE}/jobs/external/status`);
  if (!r.ok) return { available: false, source: "unknown", note: "" };
  return r.json();
}

export async function generateInterviewQuestions(jdId?: string, count: number = 15, categories?: string[]): Promise<InterviewGenerateResponse> {
  const params = new URLSearchParams();
  if (jdId) params.append("jd_id", jdId);
  params.append("count", count.toString());
  if (categories) params.append("categories", JSON.stringify(categories));
  const r = await fetch(`${API_BASE}/interview/generate?${params}`, { method: "POST" });
  if (!r.ok) throw new Error("Generate interview questions failed");
  return r.json();
}

export async function getInterviewCategories(): Promise<InterviewCategoriesResponse> {
  const r = await fetch(`${API_BASE}/interview/categories`);
  if (!r.ok) throw new Error("Get interview categories failed");
  return r.json();
}
