import { useEffect, useRef, useState } from "react";
import { deleteSession, extractValue, fetchProfile, fetchResumeDraft, listSessions, resumeSession, sendChatMessage, startChat } from "../lib/api";
import type { ChatMessage, ChatStage, ProfileData, ResumeDraft } from "../types/index";

const STAGE_LABELS: Record<ChatStage, string> = {
  basic_info: "基本信息",
  self_intro: "自我介绍",
  work_experience: "工作经历",
  skills: "个人技能",
  education: "教育背景",
  project_experience: "项目经验",
  awards: "获奖情况",
  self_evaluation: "自我评价",
};

const STAGE_ORDER = Object.keys(STAGE_LABELS) as ChatStage[];

type SessionInfo = { session_id: string; current_stage: string; stage_label: string; preview: string; message_count: number; updated_at: string };

export default function ChatPage() {
  const [sessionId, setSessionId] = useState("");
  const [stage, setStage] = useState<ChatStage>("basic_info");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [extracting, setExtracting] = useState(false);
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [resumeDraft, setResumeDraft] = useState<ResumeDraft | null>(null);
  const [summary, setSummary] = useState("");
  const [sessions, setSessions] = useState<SessionInfo[]>([]);
  const [showHistory, setShowHistory] = useState(false);
  const msgEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const [chat, p, r, sess] = await Promise.all([
          startChat(), fetchProfile(), fetchResumeDraft(), listSessions().catch(() => [] as SessionInfo[])
        ]);
        setSessionId(chat.session_id);
        setStage(chat.stage);
        setSummary(chat.summary_preview);
        setMessages([{ id: crypto.randomUUID(), role: "assistant", content: chat.reply }]);
        setProfile(p);
        setResumeDraft(r);
        setSessions(sess);
      } catch {
        setMessages([{ id: crypto.randomUUID(), role: "assistant", content: "无法连接到后端服务，请检查服务器是否启动。" }]);
      }
      setLoading(false);
    })();
  }, []);

  useEffect(() => { msgEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || !sessionId || loading) return;
    setMessages(c => [...c, { id: crypto.randomUUID(), role: "user", content: text }]);
    setInput("");
    setLoading(true);
    try {
      const result = await sendChatMessage({ session_id: sessionId, message: text, stage });
      setStage(result.stage);
      setSummary(result.summary_preview);
      setMessages(c => [...c, { id: crypto.randomUUID(), role: "assistant", content: result.reply }]);
      if (result.should_summarize) {
        setExtracting(true);
        try {
          const ext = await extractValue({ session_id: sessionId, stage, user_message: text, assistant_summary: result.summary_preview });
          setProfile(ext.profile);
        } catch {}
        setExtracting(false);
      }
      listSessions().then(setSessions).catch(() => {});
    } catch {
      setMessages(c => [...c, { id: crypto.randomUUID(), role: "assistant", content: "发送失败，请稍后重试。" }]);
    }
    setLoading(false);
  };

  const handleNewChat = async () => {
    setLoading(true);
    try {
      const [chat, sess] = await Promise.all([startChat(), listSessions().catch(() => [] as SessionInfo[])]);
      setSessionId(chat.session_id);
      setStage(chat.stage);
      setSummary(chat.summary_preview);
      setMessages([{ id: crypto.randomUUID(), role: "assistant", content: chat.reply }]);
      setSessions(sess);
      setShowHistory(false);
    } catch {}
    setLoading(false);
  };

  const handleDeleteSession = async (sid: string, e: React.MouseEvent) => {
    e.stopPropagation();
    try {
      await deleteSession(sid);
      setSessions(s => s.filter(x => x.session_id !== sid));
    } catch {}
  };

  const handleResumeSession = async (sid: string) => {
    setLoading(true);
    try {
      const result = await resumeSession(sid);
      setSessionId(result.session_id);
      setStage(result.stage);
      setSummary(result.summary_preview);
      setMessages([{ id: crypto.randomUUID(), role: "assistant", content: result.reply }]);
      setShowHistory(false);
    } catch {
      setMessages([{ id: crypto.randomUUID(), role: "assistant", content: "无法恢复该会话。" }]);
    }
    setLoading(false);
  };

  const handleJumpStage = async (targetStage: ChatStage) => {
    if (targetStage === stage) return;
    setStage(targetStage);
    setMessages(c => [...c, { id: crypto.randomUUID(), role: "assistant", content: `已跳转到「${STAGE_LABELS[targetStage]}」阶段。你可以直接描述这个阶段的信息。` }]);
  };

  return (
    <div className="chat-page">
      <div className="chat-main-area">
        <div className="chat-header-bar">
          <h2>AI 简历对话</h2>
          <span className="badge">{STAGE_LABELS[stage]}</span>
          <div style={{ marginLeft: "auto", display: "flex", gap: 8 }}>
            <button className="btn-tool" onClick={handleNewChat} title="新建对话">新建对话</button>
            <button className="btn-tool" onClick={() => setShowHistory(!showHistory)} title="历史会话">
              历史{showHistory ? " ▲" : " ▼"}
            </button>
          </div>
        </div>
        {showHistory && sessions.length > 0 && (
          <div className="history-dropdown">
            {sessions.slice(0, 10).map(s => (
              <div key={s.session_id} className="history-item" onClick={() => handleResumeSession(s.session_id)}>
                <div className="history-item-top">
                  <span className="history-stage">{s.stage_label || s.current_stage}</span>
                  <span className="history-count">{s.message_count} 条消息</span>
                </div>
                <div className="history-preview">{s.preview || "空会话"}</div>
                <button className="history-del-btn" onClick={(e) => handleDeleteSession(s.session_id, e)} title="删除">×</button>
              </div>
            ))}
          </div>
        )}
        <div className="chat-msgs">
          {messages.map(m => (
            <div key={m.id} className={`msg msg-${m.role}`}>{m.content}</div>
          ))}
          {loading && <div className="msg msg-assistant typing">AI 正在输入...</div>}
          {extracting && <div className="msg msg-assistant">正在提取信息到简历库...</div>}
          <div ref={msgEndRef} />
        </div>
        <div className="chat-input-area">
          <textarea value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); } }} placeholder="描述您的工作经历、技能、教育背景.." rows={2} disabled={loading} />
          <button onClick={handleSend} disabled={loading || !sessionId} className="btn-send">{loading ? "发送中..." : "发送"}</button>
        </div>
      </div>
      <div className="chat-side-panel">
        <div className="panel-box">
          <h3>阶段进度</h3>
          <div className="stage-list">
            {STAGE_ORDER.map((s, i) => (
              <div key={s} className={`stage-item ${s === stage ? "active" : ""}`} onClick={() => handleJumpStage(s)} style={{cursor:"pointer"}}>
                <span className="stage-num">{i + 1}</span>
                <span>{STAGE_LABELS[s]}</span>
                {s === stage && <span className="curr">当前</span>}
              </div>
            ))}
          </div>
        </div>
        {summary && <div className="panel-box"><h3>最新摘要</h3><div className="summary-txt">{summary}</div></div>}
      </div>
    </div>
  );
}
