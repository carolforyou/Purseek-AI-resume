import { useEffect, useRef, useState } from "react";
import { exportProfile, fetchProfile, saveProfile } from "../lib/api";
import type { ProfileData } from "../types/index";

const DEGREE_OPTIONS = ["", "高中", "大专", "本科", "硕士", "博士"];

export default function Welcome({ onComplete }: { onComplete: () => void }) {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [status, setStatus] = useState("");
  const autoSaveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    fetchProfile().then(setProfile).catch(() => setProfile(null));
  }, []);

  const update = (path: string, value: string) => {
    setProfile(p => {
      if (!p) return p;
      const parts = path.split(".");
      const copy = JSON.parse(JSON.stringify(p));
      let cur = copy;
      for (let i = 0; i < parts.length - 1; i++) cur = cur[parts[i]];
      cur[parts[parts.length - 1]] = value;
      // Auto-save after 2s of no typing
      if (autoSaveTimer.current) clearTimeout(autoSaveTimer.current);
      autoSaveTimer.current = setTimeout(async () => {
        try { await saveProfile(copy); setStatus("已自动保存"); setTimeout(() => setStatus(""), 2000); } catch {}
      }, 2000);
      return copy;
    });
  };

  const handleSave = async () => {
    if (!profile) return;
    setSaving(true);
    try {
      await saveProfile(profile);
      setSaved(true);
      setStatus("保存成功");
      setTimeout(onComplete, 800);
    } catch { setSaving(false); }
    setSaving(false);
  };

  const handleExport = async () => {
    try {
      const result = await exportProfile();
      const blob = new Blob([JSON.stringify(result.content, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = result.filename; a.click();
      URL.revokeObjectURL(url);
      setStatus("导出成功");
    } catch { setStatus("导出失败"); }
    setTimeout(() => setStatus(""), 2000);
  };

  const handleImport = () => {
    const input = document.createElement("input");
    input.type = "file"; input.accept = ".json";
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (!file) return;
      try {
        const text = await file.text();
        const data = JSON.parse(text);
        await saveProfile(data as ProfileData);
        setProfile(data as ProfileData);
        setStatus("导入成功");
      } catch { setStatus("导入失败，请检查文件格式"); }
      setTimeout(() => setStatus(""), 2000);
    };
    input.click();
  };

  if (!profile) return <div className="loading">加载中...</div>;

  const bi = profile.basic_info;
  const ed = profile.education;

  return (
    <div className="welcome-page">
      <div className="welcome-card">
        <div className="welcome-header">
          <h1>欢迎使用 AI 求职助手</h1>
          <p>先来填写您的基本信息吧，这将作为母简历的初稿。所有修改会自动保存。</p>
        </div>

        <div className="welcome-toolbar">
          <div className="toolbar-left">
            <button className="btn-tool" onClick={handleExport} title="导出为 JSON 文件">导出 JSON</button>
            <button className="btn-tool" onClick={handleImport} title="从 JSON 文件导入">导入 JSON</button>
          </div>
          {status && <span className="status-msg">{status}</span>}
        </div>

        <div className="welcome-form">
          <div className="form-section">
            <h3>基本信息</h3>
            <div className="form-grid">
              <div className="form-field">
                <label>姓名 *</label>
                <input value={bi.name} onChange={e => update("basic_info.name", e.target.value)} placeholder="请输入您的姓名" />
              </div>
              <div className="form-field">
                <label>求职意向 *</label>
                <input value={bi.job_intention} onChange={e => update("basic_info.job_intention", e.target.value)} placeholder="如：前端开发工程师" />
              </div>
              <div className="form-field">
                <label>电子邮箱</label>
                <input value={bi.email} onChange={e => update("basic_info.email", e.target.value)} placeholder="your@email.com" />
              </div>
              <div className="form-field">
                <label>手机号码</label>
                <input value={bi.phone} onChange={e => update("basic_info.phone", e.target.value)} placeholder="+86 13800000000" />
              </div>
              <div className="form-field">
                <label>出生年月</label>
                <input value={bi.birth_date} onChange={e => update("basic_info.birth_date", e.target.value)} placeholder="1995-06" />
              </div>
              <div className="form-field">
                <label>最高学历</label>
                <select value={bi.highest_degree} onChange={e => update("basic_info.highest_degree", e.target.value)}>
                  {DEGREE_OPTIONS.map(d => <option key={d} value={d}>{d || "-- 请选择 --"}</option>)}
                </select>
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>教育背景</h3>
            <div className="form-grid">
              <div className="form-field">
                <label>学校名称</label>
                <input value={ed[0]?.school_name || ""} onChange={e => update("education.0.school_name", e.target.value)} placeholder="请输入毕业院校" />
              </div>
              <div className="form-field">
                <label>专业</label>
                <input value={ed[0]?.major || ""} onChange={e => update("education.0.major", e.target.value)} placeholder="所学专业" />
              </div>
              <div className="form-field">
                <label>学位</label>
                <input value={ed[0]?.degree || ""} onChange={e => update("education.0.degree", e.target.value)} placeholder="如：工学学士" />
              </div>
              <div className="form-field">
                <label>在校时间</label>
                <input value={ed[0]?.school_time || ""} onChange={e => update("education.0.school_time", e.target.value)} placeholder="如：2014-2018" />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>自我介绍</h3>
            <textarea
              className="form-textarea"
              value={profile.self_intro}
              onChange={e => update("self_intro", e.target.value)}
              placeholder="简要介绍您的专业背景、核心优势、职业目标..."
              rows={5}
            />
          </div>

          <div className="form-actions">
            <button className="btn-primary" onClick={handleSave} disabled={saving}>
              {saving ? "保存中..." : saved ? "已保存，继续 " : "保存并继续"}
            </button>
            <button className="btn-secondary" onClick={onComplete}>暂时跳过</button>
          </div>
        </div>
      </div>
    </div>
  );
}
