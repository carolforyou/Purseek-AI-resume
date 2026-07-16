import { useCallback, useState } from "react";
import Welcome from "./pages/Welcome";
import ChatPage from "./pages/Chat";
import ResumeBuilder from "./pages/ResumeBuilder";
import JDAnalysis from "./pages/JDAnalysis";
import KnowledgeBase from "./pages/KnowledgeBase";
import Interview from "./pages/Interview";

type PageKey = "welcome" | "chat" | "resume" | "jobs" | "knowledge" | "interview";

const NAV_ITEMS: { key: PageKey; label: string; icon: string }[] = [
  { key: "welcome", label: "个人资料", icon: "M15 9h6m-6 4h4m-4 4h5M5 9h.01M5 13h.01M5 17h.01M4 5h16a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V6a1 1 0 011-1z" },
  { key: "chat", label: "AI 对话", icon: "M8 12h8M8 8h8m-8 8h5M5 3h14a2 2 0 012 2v10a2 2 0 01-2 2h-4l-4 3-4-3H5a2 2 0 01-2-2V5a2 2 0 012-2z" },
  { key: "resume", label: "简历编辑", icon: "M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" },
  { key: "jobs", label: "岗位匹配", icon: "M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" },
  { key: "interview", label: "面试题", icon: "M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" },
  { key: "knowledge", label: "知识库", icon: "M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" },
];

export default function App() {
  const [activePage, setActivePage] = useState<PageKey>("welcome");
  const [welcomeDone, setWelcomeDone] = useState(false);
  const [resumeKey, setResumeKey] = useState(0);

  const navigate = useCallback((page: PageKey) => {
    setActivePage(page);
    if (page === "resume") setResumeKey(k => k + 1);
  }, []);

  const renderPage = () => {
    if (activePage === "welcome" && !welcomeDone) {
      return <Welcome onComplete={() => setWelcomeDone(true)} />;
    }
    switch (activePage) {
      case "welcome": return <Welcome onComplete={() => {}} />;
      case "chat": return <ChatPage />;
      case "resume": return <ResumeBuilder key={resumeKey} />;
      case "jobs": return <JDAnalysis />;
      case "interview": return <Interview />;
      case "knowledge": return <KnowledgeBase />;
      default: return null;
    }
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-logo">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
        </div>
        <nav className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <button
              key={item.key}
              className={`sidebar-item ${activePage === item.key ? "active" : ""}`}
              onClick={() => navigate(item.key)}
              title={item.label}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d={item.icon} />
              </svg>
            </button>
          ))}
        </nav>
        <div className="sidebar-footer">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3" />
            <line x1="12" y1="17" x2="12.01" y2="17" />
          </svg>
        </div>
      </aside>
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}
