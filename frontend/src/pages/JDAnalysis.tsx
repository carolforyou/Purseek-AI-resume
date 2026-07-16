import React, { useEffect, useState } from "react";
import { createJd, deleteJd, generateCustomResume, getAllJds, getMatchResult, importExternalJob, parseJdText, searchExternalJobs } from "../lib/api";
import type { CustomResumeResponse, ExternalJobItem, JDParseResponse, JobDescription, JobSearchResponse, MatchResult } from "../types/index";

function ExportDropdown({ label, content }: { label: string; content: string }) {
  const [open, setOpen] = useState(false);
  const [exporting, setExporting] = useState("");

  const doExport = async (format: string) => {
    setExporting(format);
    try {
      if (format === "md") {
        const blob = new Blob([content], { type: "text/plain;charset=utf-8" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = "custom-resume.md"; a.click();
        URL.revokeObjectURL(url);
      } else if (format === "png" || format === "pdf") {
        const win = window.open("", "_blank");
        if (win) {
          win.document.write(content);
          win.document.close(); win.focus();
          if (format === "pdf") setTimeout(function() { win.print(); }, 500);
        }
      } else {
        const endpoint = format === "docx" ? "template-docx" : "markdown";
        const resp = await fetch("/api/resume-export/" + endpoint);
        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = "custom-resume." + (format === "docx" ? "docx" : "md"); a.click();
        URL.revokeObjectURL(url);
      }
    } catch (e: any) {}
    setExporting("");
    setOpen(false);
  };

  return (
    <div className="export-dropdown">
      <button className="btn-export-dropdown" onClick={function() { setOpen(!open); }}>
        {exporting ? "..." : label} <span className="dropdown-arrow">{open ? "^" : "v"}</span>
      </button>
      {open && (
        <div className="export-dropdown-menu">
          <button onClick={function() { doExport("md"); }}>MD</button>
          <button onClick={function() { doExport("docx"); }}>DOCX</button>
          <button onClick={function() { doExport("pdf"); }}>PDF</button>
          <button onClick={function() { doExport("png"); }}>PNG</button>
        </div>
      )}
    </div>
  );
}

function OriginalResumePreview() {
  const [origContent, setOrigContent] = useState("");
  const [loading, setLoading] = useState(true);
  useEffect(function() {
    fetch("/api/resume-export/html")
      .then(function(r) { return r.text(); })
      .then(function(t) { setOrigContent(t); setLoading(false); })
      .catch(function() { setLoading(false); });
  }, []);
  if (loading) return <div style={{ padding: 20, color: "#a0a0b8", fontSize: 12 }}>Loading...</div>;
  return <div className="orig-resume-preview" dangerouslySetInnerHTML={{ __html: origContent }} />;
}

function ScoreBar({ label, score }: { label: string; score: number }) {
  return (
    <div className="score-bar-wrap">
      <span className="score-bar-label">{label}</span>
      <div className="score-bar-track"><div className="score-bar-fill" style={{ width: score + "%" }} /></div>
      <span className="score-bar-val">{score}</span>
    </div>
  );
}

type InputMode = "paste" | "search";

export default function JDAnalysis() {
  const [jds, setJds] = useState<JobDescription[]>([]);
  const [selectedJd, setSelectedJd] = useState<JobDescription | null>(null);
  const [matchResult, setMatchResult] = useState<MatchResult | null>(null);
  const [customResume, setCustomResume] = useState<CustomResumeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [showCustomModal, setShowCustomModal] = useState(false);
  const [editedCustom, setEditedCustom] = useState("");

  // Paste mode state
  const [pasteText, setPasteText] = useState("");
  const [parsing, setParsing] = useState(false);
  const [parsedJd, setParsedJd] = useState<JDParseResponse | null>(null);
  const [parseError, setParseError] = useState("");

  // Search mode state
  const [inputMode, setInputMode] = useState<InputMode>("paste");
  const [searchKeyword, setSearchKeyword] = useState("");
  const [searchResults, setSearchResults] = useState<ExternalJobItem[]>([]);
  const [searchPage, setSearchPage] = useState(1);
  const [searchTotal, setSearchTotal] = useState(0);
  const [searching, setSearching] = useState(false);
  const [searchSource, setSearchSource] = useState("");
  const [importingId, setImportingId] = useState<string | null>(null);

  useEffect(function() { getAllJds().then(setJds).catch(function() {}); }, []);

  // ===== Paste mode =====
  const handleParseJD = async function() {
    if (!pasteText.trim()) return;
    setParsing(true); setParseError("");
    try { setParsedJd(await parseJdText(pasteText.trim())); }
    catch (e: any) { setParseError(e?.message || "Network error"); }
    setParsing(false);
  };

  const handleSaveParsedJd = async function() {
    if (!parsedJd) return;
    try {
      const jd = await createJd({
        title: parsedJd.title, company: parsedJd.company, location: parsedJd.location,
        salary: "", experience: "", education: "", job_type: "", industry: "",
        description: parsedJd.description, requirements: parsedJd.requirements,
        skills: parsedJd.skills, responsibilities: parsedJd.responsibilities,
      });
      setJds(function(prev) { return prev.concat([jd]); });
      setSelectedJd(jd); setParsedJd(null); setPasteText(""); setParseError("");
    } catch (e) {}
  };

  // ===== Search mode =====
  const handleSearch = async function(page: number = 1) {
    if (!searchKeyword.trim()) return;
    setSearching(true);
    try {
      const res: JobSearchResponse = await searchExternalJobs(searchKeyword.trim(), page);
      setSearchResults(res.items);
      setSearchPage(res.page);
      setSearchTotal(res.total);
      setSearchSource(res.source);
    } catch (e: any) {
      console.error("Search failed:", e);
    }
    setSearching(false);
  };

  const handleImportExternal = async function(job: ExternalJobItem) {
    setImportingId(job.job_id);
    try {
      const saved = await importExternalJob({
        job_id: job.job_id,
        title: job.title,
        company: job.company,
        location: job.location,
        salary: job.salary,
        description: job.description,
        experience: job.experience,
        education: job.education,
      });
      setJds(function(prev) { return prev.concat([saved]); });
      setSelectedJd(saved);
      setMatchResult(null);
      setCustomResume(null);
    } catch (e) {
      console.error("Import failed:", e);
    }
    setImportingId(null);
  };

  // ===== Analysis =====
  const handleMatch = async function() {
    if (!selectedJd) return; setLoading(true);
    try { setMatchResult(await getMatchResult(selectedJd.id)); } catch (e) {}
    setLoading(false);
  };

  const handleCustomResume = async function() {
    if (!selectedJd) return; setLoading(true);
    try {
      const result = await generateCustomResume(selectedJd.id);
      setCustomResume(result); setEditedCustom(result.content); setShowCustomModal(true);
    } catch (e) {}
    setLoading(false);
  };

  const handleDelete = async function(id: string) {
    await deleteJd(id);
    setJds(function(prev) { return prev.filter(function(j) { return j.id !== id; }); });
    if (selectedJd?.id === id) { setSelectedJd(null); setMatchResult(null); setCustomResume(null); }
  };

  return (
    <div className="jd-page">
      {/* ===== Left Panel: Input ===== */}
      <div className="jd-paste-panel">
        <div className="jd-input-tabs">
          <button
            className={`jd-input-tab ${inputMode === "paste" ? "active" : ""}`}
            onClick={() => setInputMode("paste")}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
              <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/>
            </svg>
            粘贴 JD
          </button>
          <button
            className={`jd-input-tab ${inputMode === "search" ? "active" : ""}`}
            onClick={() => setInputMode("search")}
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0 }}>
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            搜索职位
          </button>
        </div>

        {inputMode === "paste" ? (
          <>
            <textarea className="jd-paste-ta" value={pasteText} onChange={function(e) { setPasteText(e.target.value); }} placeholder="粘贴完整的职位描述文本..." rows={6} />
            <button className="btn-primary" onClick={handleParseJD} disabled={parsing || !pasteText.trim()}>
              {parsing ? "解析中..." : "解析 JD"}
            </button>
            {parseError && <div className="parsed-jd" style={{ borderColor: "#fecaca", background: "#fef2f2" }}><p style={{ color: "#e44", fontSize: 12, margin: 0 }}>{parseError}</p></div>}
            {parsedJd && (
              <div className="parsed-jd">
                <h4>解析结果</h4>
                <div><strong>职位:</strong> {parsedJd.title}</div>
                <div><strong>公司:</strong> {parsedJd.company}</div>
                <div><strong>地点:</strong> {parsedJd.location}</div>
                <div><strong>技能:</strong> {parsedJd.skills.join(", ")}</div>
                <button className="btn-primary" onClick={handleSaveParsedJd}>保存并分析</button>
              </div>
            )}
          </>
        ) : (
          <>
            <div className="jd-search-input-wrap">
              <input
                className="jd-search-input"
                value={searchKeyword}
                onChange={e => setSearchKeyword(e.target.value)}
                onKeyDown={e => e.key === "Enter" && handleSearch(1)}
                placeholder="输入关键词搜索职位..."
              />
              <button className="btn-primary" onClick={() => handleSearch(1)} disabled={searching || !searchKeyword.trim()}>
                {searching ? "搜索中..." : "搜索"}
              </button>
            </div>
            {searchSource && (
              <div className="jd-search-source">
                数据来源: {searchSource === "liepin_mcp" ? "猎聘 MCP" : "模拟数据"}
              </div>
            )}
            {searching && <div className="empty-hint">搜索中...</div>}
            {!searching && searchResults.length > 0 && (
              <div className="jd-search-results">
                <div className="jd-search-count">找到 {searchTotal || searchResults.length} 个职位</div>
                {searchResults.map((job) => (
                  <div key={job.job_id} className="jd-search-card">
                    <div className="jd-search-card-body">
                      <div className="jd-search-card-title">{job.title}</div>
                      <div className="jd-search-card-company">{job.company}</div>
                      <div className="jd-search-card-meta">
                        <span>{job.location}</span>
                        <span className="jd-search-card-salary">{job.salary}</span>
                      </div>
                      {job.experience && <div className="jd-search-card-exp">{job.experience} · {job.education}</div>}
                      <div className="jd-search-card-desc">{job.description}</div>
                    </div>
                    <button
                      className="btn-tool jd-search-card-import"
                      onClick={() => handleImportExternal(job)}
                      disabled={importingId === job.job_id}
                    >
                      {importingId === job.job_id ? "..." : "+ 导入"}
                    </button>
                  </div>
                ))}
              </div>
            )}
            {!searching && searchKeyword && searchResults.length === 0 && (
              <div className="empty-hint">未找到匹配职位</div>
            )}
          </>
        )}
      </div>

      {/* ===== Middle Panel: Saved Positions ===== */}
      <div className="jd-list-panel">
        <h3>已保存岗位</h3>
        <div className="jd-list">
          {jds.length ? jds.map(function(jd) { return (
            <div key={jd.id} className={"jd-card" + (selectedJd?.id === jd.id ? " sel" : "")} onClick={function() { setSelectedJd(jd); setMatchResult(null); setCustomResume(null); }}>
              <div className="jd-card-top">
                <strong>{jd.title}</strong>
                <button className="jd-del" onClick={function(e: React.MouseEvent) { e.stopPropagation(); handleDelete(jd.id); }}>x</button>
              </div>
              <div className="jd-card-sub">{jd.company} · {jd.location}</div>
            </div>
          ); }) : <div className="empty-hint">暂无已保存岗位</div>}
        </div>
      </div>

      {/* ===== Right Panel: Analysis Results ===== */}
      <div className="jd-result-panel">
        {selectedJd ? (
          <>
            <div className="jd-result-header">
              <h3>{selectedJd.title} @ {selectedJd.company}</h3>
              <div className="jd-result-actions">
                <button onClick={handleMatch} disabled={loading} className="btn-primary">{loading ? "分析中..." : "匹配分析"}</button>
                <button onClick={handleCustomResume} disabled={loading} className="btn-secondary">{loading ? "生成中..." : "定制简历"}</button>
              </div>
            </div>
            {matchResult && (
              <div className="match-box">
                <div className="match-score-row">
                  <div className="match-big-score"><span className="score-num">{matchResult.total_score}</span><span className="score-sub">Match</span></div>
                  <div className="score-bars">
                    <ScoreBar label="Skills" score={matchResult.skill_score} />
                    <ScoreBar label="Experience" score={matchResult.experience_score} />
                    <ScoreBar label="Education" score={matchResult.education_score} />
                    <ScoreBar label="Preference" score={matchResult.preference_score} />
                  </div>
                </div>
                <div className="match-details-grid">
                  <div><h4>Strengths</h4><ul>{matchResult.strengths.map(function(s, i) { return <li key={i}>+ {s}</li>; })}</ul></div>
                  <div><h4>Weaknesses</h4><ul>{matchResult.weaknesses.map(function(w, i) { return <li key={i}>- {w}</li>; })}</ul></div>
                  <div><h4>Suggestions</h4><ul>{matchResult.suggestions.map(function(s, i) { return <li key={i}>Tip: {s}</li>; })}</ul></div>
                </div>
                {matchResult.missing_skills && matchResult.missing_skills.length > 0 && (
                  <div className="missing-skills"><h4>Skills to Learn</h4><div className="section-tags">{matchResult.missing_skills.map(function(s, i) { return <span key={i} className="tag tag-miss">{s}</span>; })}</div></div>
                )}
              </div>
            )}
            {customResume && (
              <div className="custom-resume-box">
                <h4>定制简历已就绪</h4>
                <button className="btn-primary" onClick={function() { setShowCustomModal(true); setEditedCustom(customResume.content); }}>预览与编辑</button>
                <div className="mods" style={{ marginTop: 8 }}><h5>改动项</h5><ul>{customResume.modifications.map(function(m, i) { return <li key={i}>{m}</li>; })}</ul></div>
              </div>
            )}
          </>
        ) : (
          <div className="empty-hint">选择一个岗位进行分析</div>
        )}
      </div>

      {/* ===== Custom Resume Modal ===== */}
      {showCustomModal && customResume && (
        <div className="modal-overlay" onClick={function() { setShowCustomModal(false); }}>
          <div className="modal-content custom-resume-modal" onClick={function(e: React.MouseEvent) { e.stopPropagation(); }}>
            <div className="modal-header">
              <h3>定制简历 - {customResume.jd_title}</h3>
              <button className="modal-close" onClick={function() { setShowCustomModal(false); }}>x</button>
            </div>
            <div className="modal-body">
              <div className="compare-panels">
                <div className="compare-panel">
                  <h4>原始简历</h4>
                  <div className="panel-content-wrapper">
                    <OriginalResumePreview />
                  </div>
                </div>
                <div className="compare-panel">
                  <h4>定制版（可编辑）</h4>
                  <div className="panel-content-wrapper">
                    <textarea className="form-textarea compare-textarea" value={editedCustom} onChange={function(e) { setEditedCustom(e.target.value); }} />
                  </div>
                </div>
              </div>
              <div className="modifications-list"><h4>改动项</h4><ul>{customResume.modifications.map(function(m, i) { return <li key={i}>{m}</li>; })}</ul></div>
            </div>
            <div className="modal-footer">
              <button className="btn-secondary" onClick={function() { setShowCustomModal(false); }}>关闭</button>
              <ExportDropdown label="导出" content={editedCustom} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
