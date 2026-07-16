import React, { useEffect, useRef, useState } from "react";
import html2canvas from "html2canvas";
import { fetchProfile, fetchResumeDraft, getResumeMarkdownExportUrl, getResumeTemplateDocxExportUrl, getResumePdfExportUrl, polishFullResume, polishResume, saveProfile, translateResumeToEnglish } from "../lib/api";
import type { CustomField, PolishResponse, ProfileData, ResumeDraft } from "../types/index";

type SectionDef = { id: string; title: string; order: number };

const DEFAULT_SECTIONS: SectionDef[] = [
  { id: "basic_info", title: "基本信息", order: 1 },
  { id: "education", title: "教育背景", order: 2 },
  { id: "work_experience", title: "工作经历", order: 3 },
  { id: "project_experience", title: "项目经验", order: 4 },
  { id: "skills", title: "个人技能", order: 5 },
  { id: "awards", title: "获奖证书", order: 6 },
];

function ExportDropdown({ label, previewRef }: { label: string; content?: string; previewRef: React.RefObject<HTMLDivElement | null> }) {
  const [open, setOpen] = useState(false);
  const [exporting, setExporting] = useState("");

  const doExport = async (format: string) => {
    setExporting(format);
    try {
      if (format === "pdf") {
        const resp = await fetch("/api/resume-export/html");
        const html = await resp.text();
        const win = window.open("", "_blank");
        if (win) { win.document.write(html); win.document.close(); win.focus(); setTimeout(function() { win.print(); }, 500); }
      } else if (format === "png") {
        if (previewRef.current) {
          const canvas = await html2canvas(previewRef.current, {
            scale: 2,
            useCORS: true,
            logging: false,
          });
          const link = document.createElement("a");
          link.download = "resume.png";
          link.href = canvas.toDataURL("image/png");
          link.click();
        }
      } else {
        const ep = format === "docx" ? "template-docx" : "markdown";
        const resp = await fetch("/api/resume-export/" + ep);
        const blob = await resp.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = "resume." + (format === "docx" ? "docx" : "md"); a.click();
        URL.revokeObjectURL(url);
      }
    } catch (e) {}
    setExporting("");
    setOpen(false);
  };

  return React.createElement("div", { className: "export-dropdown" },
    React.createElement("button", { className: "btn-export-dropdown", onClick: function() { setOpen(!open); } },
      exporting ? "..." : label,
      React.createElement("span", { className: "dropdown-arrow" }, open ? "▲" : "▼")
    ),
    open ? React.createElement("div", { className: "export-dropdown-menu" },
      React.createElement("button", { onClick: function() { doExport("md"); } }, "MD"),
      React.createElement("button", { onClick: function() { doExport("docx"); } }, "DOCX"),
      React.createElement("button", { onClick: function() { doExport("pdf"); } }, "PDF"),
      React.createElement("button", { onClick: function() { doExport("png"); } }, "PNG")
    ) : null
  );
}

export default function ResumeBuilder() {
  const [profile, setProfile] = useState<ProfileData | null>(null);
  const [draft, setDraft] = useState<ResumeDraft | null>(null);
  const [sections, setSections] = useState<SectionDef[]>([]);
  const [editingTitle, setEditingTitle] = useState<string | null>(null);
  const [dragIdx, setDragIdx] = useState<number | null>(null);
  const [polishing, setPolishing] = useState<string | null>(null);
  const [polishAll, setPolishAll] = useState(false);
  const [polishResult, setPolishResult] = useState<{ content: string; changes: string[] } | null>(null);
  const [translating, setTranslating] = useState(false);
  const [englishResume, setEnglishResume] = useState<{ content: string } | null>(null);
  const [previewMode, setPreviewMode] = useState(false);
  const [editingSection, setEditingSection] = useState<string | null>(null);
  const previewRef = useRef<HTMLDivElement>(null);

  useEffect(function() {
    (async function() {
      var _a = await Promise.all([fetchProfile(), fetchResumeDraft()]);
      setProfile(_a[0]); setDraft(_a[1]);
      setSections(DEFAULT_SECTIONS.map(function(s) { return Object.assign({}, s); }));
    })();
  }, []);

  const save = async function(p: ProfileData) { setProfile(p); try { await saveProfile(p); } catch (e) {} };
  const rename = function(id: string, t: string) { setSections(function(p) { return p.map(function(s) { return s.id === id ? Object.assign({}, s, { title: t }) : s; }); }); setEditingTitle(null); };
  const move = function(from: number, to: number) {
    if (from === to) return;
    setSections(function(p) { var c = p.slice(); var it = c.splice(from, 1)[0]; c.splice(to, 0, it); return c.map(function(s, i) { return Object.assign({}, s, { order: i + 1 }); }); });
  };
  const addSec = function() { var id = "custom_" + Date.now(); setSections(function(p) { return p.concat([{ id: id, title: "新板块", order: p.length + 1 }]); }); };
  const delSec = function(id: string) { setSections(function(p) { return p.filter(function(s) { return s.id !== id; }); }); };

  const polishSec = async function(sid: string, content: string) { setPolishing(sid); try { var r = await polishResume(sid, content); setSectionPolish(function(p) { p[sid] = r; return Object.assign({}, p); }); } catch (e) {} setPolishing(null); };
  const [sectionPolish, setSectionPolish] = useState<Record<string, PolishResponse>>({});

  const handlePolishAll = async function() { setPolishAll(true); try { setPolishResult(await polishFullResume()); } catch (e) {} setPolishAll(false); };
  const handleTranslate = async function() { setTranslating(true); try { setEnglishResume(await translateResumeToEnglish()); } catch (e) {} setTranslating(false); };

  const photoUpload = function() {
    var inp = document.createElement("input"); inp.type = "file"; inp.accept = "image/*";
    inp.onchange = function(e) { var f = (e.target as HTMLInputElement).files?.[0]; if (!f || !profile) return; var r = new FileReader(); r.onload = function() { var p = JSON.parse(JSON.stringify(profile)); p.basic_info.photo = r.result as string; save(p); }; r.readAsDataURL(f); };
    inp.click();
  };

  if (!profile || !draft) return <div className="loading">Loading...</div>;

  return (
    <div className="resume-builder">
      <div className="rb-header">
        <h2>Resume Editor</h2>
        <div className="rb-actions">
          <button className={"btn-mode" + (previewMode ? "" : " active")} onClick={function() { setPreviewMode(false); }}>Edit</button>
          <button className={"btn-mode" + (previewMode ? " active" : "")} onClick={function() { setPreviewMode(true); }}>Preview</button>
          <button className="btn-polish-all" onClick={handlePolishAll} disabled={polishAll}>{polishAll ? "..." : "AI Polish"}</button>
          <button className="btn-translate" onClick={handleTranslate} disabled={translating}>{translating ? "..." : "To EN"}</button>
          <ExportDropdown label="Export" previewRef={previewRef} />
        </div>
      </div>

      {englishResume && <Banner title="English" onCopy={function() { navigator.clipboard.writeText(englishResume.content); }}><pre className="polished-content">{englishResume.content}</pre></Banner>}
      {polishResult && <Banner title="AI Polish"><ul>{polishResult.changes.map(function(c, i) { return <li key={i}>{c}</li>; })}</ul><pre className="polished-content">{polishResult.content}</pre></Banner>}

      {previewMode ? (
        <Preview profile={profile!} draft={draft!} sections={sections} sp={sectionPolish} onEditSec={setEditingSection} editingSec={editingSection} ref={previewRef} />
      ) : (
        <div className="resume-sheet">
          {sections.map(function(s, i) {
            return (
              <div key={s.id} className="resume-block" draggable onDragStart={function() { setDragIdx(i); }} onDragOver={function(e) { e.preventDefault(); }} onDrop={function() { if (dragIdx !== null) move(dragIdx, i); setDragIdx(null); }}>
                <div className="block-header">
                  <span className="drag-handle">{String.fromCharCode(9776)}</span>
                  {editingTitle === s.id ? (
                    <input className="title-edit" defaultValue={s.title} onBlur={function(e) { rename(s.id, e.target.value); }} onKeyDown={function(e) { if (e.key === "Enter") rename(s.id, (e.target as HTMLInputElement).value); }} autoFocus />
                  ) : <h3 onClick={function() { setEditingTitle(s.id); }}>{s.title}</h3>}
                  <button className="btn-polish-sm" onClick={function() { polishSec(s.id, secContent(s.id, profile!, draft!)); }} disabled={polishing === s.id}>{polishing === s.id ? "..." : "AI"}</button>
                  <button className="btn-del-section" onClick={function() { delSec(s.id); }}>×</button>
                </div>
                <div className="block-content"><SectionEdit sectionId={s.id} profile={profile!} draft={draft!} polish={sectionPolish[s.id]} save={save} photoUpload={photoUpload} /></div>
              </div>
            );
          })}
          <button className="btn-add-section" onClick={addSec}>+</button>
        </div>
      )}
    </div>
  );
}

function secContent(sid: string, p: ProfileData, d: ResumeDraft): string {
  switch (sid) {
    case "basic_info": return (p.basic_info.name || "") + "\n" + (p.basic_info.job_intention || "");
    case "skills": return (p.skills || []).join("");
    case "work_experience": return p.work_experiences.map(function(e) { return e.company_name + " - " + e.position_name; }).join("\n");
    case "project_experience": return p.project_experiences.map(function(pr) { return pr.project_name + ": " + pr.project_description; }).join("\n");
    case "education": return (p.education || []).map(function(e) { return e.school_name + " - " + e.major; }).join("\n");
    case "awards": return p.awards.join("");
    default: return "";
  }
}

function Banner({ title, onCopy, children }: { title: string; onCopy?: () => void; children: React.ReactNode }) {
  return <div className="polish-result-banner en-banner"><div className="en-banner-header"><h4>{title}</h4>{onCopy && <button className="btn-copy" onClick={onCopy}>Copy</button>}</div>{children}</div>;
}

function SectionEdit({ sectionId, profile, draft, polish, save, photoUpload }: { sectionId: string; profile: ProfileData; draft: ResumeDraft; polish?: PolishResponse; save: (p: ProfileData) => void; photoUpload: () => void }) {
  var bi = profile.basic_info;
  switch (sectionId) {
    case "basic_info":
      return <div><PhotoField photo={bi.photo || ""} onUpload={photoUpload} onRemove={function() { var p = JSON.parse(JSON.stringify(profile)); p.basic_info.photo = ""; save(p); }} /><BasicFields bi={bi} onUpdate={function(k, v) { var p = JSON.parse(JSON.stringify(profile)); p.basic_info[k] = v; save(p); }} /><CustomFieldsEditor fields={bi.custom_fields || []} onChange={function(cf) { var p = JSON.parse(JSON.stringify(profile)); p.basic_info.custom_fields = cf; save(p); }} /></div>;
    case "skills": return <TagEditor tags={profile.skills || []} onChange={function(s) { var p = JSON.parse(JSON.stringify(profile)); p.skills = s; save(p); }} placeholder="Add skill..." />;
    case "work_experience": return <WorkExpEditor exps={profile.work_experiences} onChange={function(e) { var p = JSON.parse(JSON.stringify(profile)); p.work_experiences = e; save(p); }} />;
    case "project_experience": return <ProjEditor projs={profile.project_experiences} onChange={function(pr) { var p = JSON.parse(JSON.stringify(profile)); p.project_experiences = pr; save(p); }} />;
    case "education": return <EduEditor edus={profile.education || []} onChange={function(e) { var p = JSON.parse(JSON.stringify(profile)); p.education = e; save(p); }} />;
    case "awards": return <TagEditor tags={profile.awards} onChange={function(a) { var p = JSON.parse(JSON.stringify(profile)); p.awards = a; save(p); }} placeholder="Add award..." />;
    default: return <RichTextEditor value="" onChange={function() {}} placeholder="Content" />;
  }
}

function RichTextEditor({ value, onChange, placeholder }: { value: string; onChange: (v: string) => void; placeholder: string }) {
  const editorRef = useRef<HTMLDivElement>(null);
  useEffect(function() { if (editorRef.current && editorRef.current.innerHTML !== value) { editorRef.current.innerHTML = value || ""; } }, [value]);
  const handleInput = function() { if (editorRef.current) onChange(editorRef.current.innerHTML); };
  const execCmd = function(cmd: string, val?: string) { document.execCommand(cmd, false, val || ""); handleInput(); editorRef.current?.focus(); };
  return (
    <div>
      <div className="rte-toolbar">
        <button className="rte-btn" onClick={function() { execCmd("bold"); }}><b>B</b></button>
        <button className="rte-btn" onClick={function() { execCmd("underline"); }}><u>U</u></button>
        <button className="rte-btn" onClick={function() { execCmd("insertUnorderedList"); }}>•</button>
        <span className="rte-hint">Select text then click</span>
      </div>
      <div ref={editorRef} className="form-textarea content-editable" contentEditable suppressContentEditableWarning onInput={handleInput} data-placeholder={placeholder} style={{ minHeight: 100 }} />
    </div>
  );
}

function PhotoField({ photo, onUpload, onRemove }: { photo: string; onUpload: () => void; onRemove: () => void }) {
  return <div className="photo-area">{photo ? <div className="photo-preview-wrap"><img src={photo} className="photo-img" /><button className="btn-del-section photo-remove" onClick={onRemove}>×</button></div> : <div className="photo-placeholder" onClick={onUpload}><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#a0a0b8" strokeWidth="1.5"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg><span>Upload photo</span></div>}</div>;
}

const BI_FIELDS = [
  { key: "name", label: "Name" }, { key: "job_intention", label: "Title" },
  { key: "email", label: "Email" }, { key: "phone", label: "Phone" },
  { key: "birth_date", label: "DOB" }, { key: "highest_degree", label: "Degree" },
];

function BasicFields({ bi, onUpdate }: { bi: any; onUpdate: (k: string, v: string) => void }) {
  const [order, setOrder] = useState(BI_FIELDS.map(function(f) { return f.key; }));
  const [dragKey, setDragKey] = useState<string | null>(null);
  const moveField = function(from: number, to: number) { if (from === to) return; setOrder(function(p) { var c = p.slice(); var it = c.splice(from, 1)[0]; c.splice(to, 0, it); return c; }); };
  return (
    <div className="section-info-grid" style={{ marginTop: 12 }}>
      {order.map(function(key, i) {
        var f = BI_FIELDS.find(function(f) { return f.key === key; })!;
        return <div key={key} className="ef" draggable onDragStart={function() { setDragKey(key); }} onDragOver={function(e) { e.preventDefault(); }} onDrop={function() { if (dragKey) { var fi = order.indexOf(dragKey); moveField(fi, i); setDragKey(null); } }}><label style={{ cursor: "grab" }}>{f.label}</label><input className="ef-input" value={bi[key] || ""} onChange={function(e) { onUpdate(key, e.target.value); }} /></div>;
      })}
    </div>
  );
}

function CustomFieldsEditor({ fields, onChange }: { fields: CustomField[]; onChange: (f: CustomField[]) => void }) {
  const add = function() { onChange(fields.concat([{ key: "", value: "" }])); };
  const update = function(i: number, f: Partial<CustomField>) { var c = fields.slice(); c[i] = Object.assign({}, c[i], f); onChange(c); };
  const remove = function(i: number) { onChange(fields.filter(function(_, j) { return j !== i; })); };
  return (
    <div className="custom-fields-area">
      <div className="custom-fields-header"><span className="custom-fields-title">Custom</span><button className="btn-add-item" onClick={add}>+</button></div>
      {fields.map(function(f, i) {
        return <div key={i} className="custom-field-row"><input className="cf-key" placeholder="Key" value={f.key} onChange={function(e) { update(i, { key: e.target.value }); }} /><input className="cf-value" placeholder="Value" value={f.value} onChange={function(e) { update(i, { value: e.target.value }); }} /><button className="btn-del-section" onClick={function() { remove(i); }}>×</button></div>;
      })}
    </div>
  );
}

function TagEditor({ tags, onChange, placeholder }: { tags: string[]; onChange: (t: string[]) => void; placeholder: string }) {
  const [input, setInput] = useState("");
  const add = function() { if (input.trim()) { onChange(tags.concat([input.trim()])); setInput(""); } };
  const remove = function(i: number) { onChange(tags.filter(function(_, j) { return j !== i; })); };
  return <div>
    <div className="section-tags" style={{ marginBottom: 4 }}>{tags.map(function(t, i) { return <span key={i} className="tag tag-removable" onClick={function() { remove(i); }}>{t} ×</span>; })}</div>
    <div style={{ display: "flex", gap: 6 }}><input className="ef-input" style={{ flex: 1 }} value={input} onChange={function(e) { setInput(e.target.value); }} onKeyDown={function(e) { if (e.key === "Enter") add(); }} placeholder={placeholder} /><button className="btn-tool" onClick={add}>Add</button></div>
  </div>;
}

function WorkExpEditor({ exps, onChange }: { exps: any[]; onChange: (e: any[]) => void }) {
  const add = function() { onChange(exps.concat([{ company_name: "", position_name: "", work_time: "", work_contents: [] }])); };
  const update = function(i: number, e: any) { var c = exps.slice(); c[i] = Object.assign({}, c[i], e); onChange(c); };
  const remove = function(i: number) { onChange(exps.filter(function(_, j) { return j !== i; })); };
  return <div className="entries-editor">
    {exps.map(function(exp, i) { return (
      <div key={i} className="entry-card">
        <div className="entry-card-header"><span>Exp {i + 1}</span><button className="btn-del-section" onClick={function() { remove(i); }}>×</button></div>
        <div className="form-grid" style={{ marginBottom: 8 }}>
          <FieldRow label="Company" value={exp.company_name} onChange={function(v) { update(i, { company_name: v }); }} />
          <FieldRow label="Position" value={exp.position_name} onChange={function(v) { update(i, { position_name: v }); }} />
          <FieldRow label="Time" value={exp.work_time} onChange={function(v) { update(i, { work_time: v }); }} />
        </div>
        <TagEditor tags={exp.work_contents} onChange={function(items) { update(i, { work_contents: items }); }} placeholder="Content" />
      </div>
    ); })}
    <button className="btn-add-item" onClick={add}>+ Add</button>
  </div>;
}

function ProjEditor({ projs, onChange }: { projs: any[]; onChange: (p: any[]) => void }) {
  const add = function() { onChange(projs.concat([{ project_name: "", project_time: "", project_role: "", project_description: "" }])); };
  const update = function(i: number, p: any) { var c = projs.slice(); c[i] = Object.assign({}, c[i], p); onChange(c); };
  const remove = function(i: number) { onChange(projs.filter(function(_, j) { return j !== i; })); };
  return <div className="entries-editor">
    {projs.map(function(p, i) { return (
      <div key={i} className="entry-card">
        <div className="entry-card-header"><span>Proj {i + 1}</span><button className="btn-del-section" onClick={function() { remove(i); }}>×</button></div>
        <div className="form-grid">
          <FieldRow label="Name" value={p.project_name} onChange={function(v) { update(i, { project_name: v }); }} />
          <FieldRow label="Time" value={p.project_time} onChange={function(v) { update(i, { project_time: v }); }} />
          <FieldRow label="Role" value={p.project_role} onChange={function(v) { update(i, { project_role: v }); }} />
        </div>
        <RichTextEditor value={p.project_description} onChange={function(v) { update(i, { project_description: v }); }} placeholder="Description" />
      </div>
    ); })}
    <button className="btn-add-item" onClick={add}>+ Add</button>
  </div>;
}

function EduEditor({ edus, onChange }: { edus: any[]; onChange: (e: any[]) => void }) {
  const add = function() { onChange(edus.concat([{ school_name: "", major: "", degree: "", school_time: "", main_courses: [] }])); };
  const update = function(i: number, e: any) { var c = edus.slice(); c[i] = Object.assign({}, c[i], e); onChange(c); };
  const remove = function(i: number) { onChange(edus.filter(function(_, j) { return j !== i; })); };
  return <div className="entries-editor">
    {edus.map(function(edu, i) { return (
      <div key={i} className="entry-card">
        <div className="entry-card-header"><span>Edu {i + 1}</span><button className="btn-del-section" onClick={function() { remove(i); }}>×</button></div>
        <div className="form-grid">
          <FieldRow label="School" value={edu.school_name} onChange={function(v) { update(i, { school_name: v }); }} />
          <FieldRow label="Major" value={edu.major} onChange={function(v) { update(i, { major: v }); }} />
          <FieldRow label="Degree" value={edu.degree} onChange={function(v) { update(i, { degree: v }); }} />
          <FieldRow label="Time" value={edu.school_time} onChange={function(v) { update(i, { school_time: v }); }} />
        </div>
        <div style={{ marginTop: 8 }}><TagEditor tags={edu.main_courses} onChange={function(items) { update(i, { main_courses: items }); }} placeholder="Courses" /></div>
      </div>
    ); })}
    <button className="btn-add-item" onClick={add}>+ Add</button>
  </div>;
}

function FieldRow({ label, value, onChange }: { label: string; value: string; onChange: (v: string) => void }) {
  return <div className="ef"><label>{label}</label><input className="ef-input" value={value} onChange={function(e) { onChange(e.target.value); }} /></div>;
}

const Preview = React.forwardRef<HTMLDivElement, { profile: any; draft: any; sections: SectionDef[]; sp: any; onEditSec: (id: string) => void; editingSec: string | null }>(function({ profile, draft, sections, sp, onEditSec, editingSec }, ref) {
  var bi = profile.basic_info; var cf = bi.custom_fields || [];
  var allBasicFields = [
    { label: "求职意向", value: bi.job_intention },
    { label: "邮箱", value: bi.email },
    { label: "电话", value: bi.phone },
    { label: "出生年月", value: bi.birth_date },
    { label: "最高学历", value: bi.highest_degree },
  ].concat(cf.map(function(f: any) { return { label: f.key, value: f.value }; })).filter(function(f: any) { return f.value; });

  return (
    <div ref={ref} className="preview-doc">
      <div className="preview-header" onClick={function() { onEditSec("basic_info"); }} style={{ cursor: "pointer" }}>
        <div className="preview-basic-left">
          <h1 className="preview-name">{bi.name || "Name"}</h1>
          <div className="preview-meta-fields">{allBasicFields.map(function(f: any, i: number) { return <span key={i} className="preview-meta-field">{f.label}: {f.value}</span>; })}</div>
        </div>
        {bi.photo && <img src={bi.photo} className="preview-photo preview-photo-right" />}
      </div>
      {sections.map(function(s: SectionDef) {
        if (s.id === "basic_info") return null;
        return (
          <div key={s.id} className={"preview-section" + (editingSec === s.id ? " preview-section-active" : "")} onClick={function() { onEditSec(s.id); }}>
            <h3 className="preview-section-title">{s.title}</h3>
            <div className="preview-section-body">{prevSecBody(s.id, profile, draft, sp[s.id]?.polished)}</div>
          </div>
        );
      })}
    </div>
  );
});

function prevSecBody(sid: string, p: ProfileData, d: ResumeDraft, polished?: string) {
  switch (sid) {
    case "skills": return <div className="section-tags">{(p.skills?.length ? p.skills : ["None"]).map(function(s, i) { return <span key={i} className="tag">{s}</span>; })}</div>;
    case "work_experience": return p.work_experiences.length ? p.work_experiences.map(function(e, i) { return <div key={i} className="preview-entry"><div className="preview-entry-title"><span>{e.company_name} - {e.position_name}</span> <span className="preview-entry-time">{e.work_time}</span></div><ul className="preview-entry-ul">{e.work_contents.map(function(c: string, j: number) { return <li key={j}>{c}</li>; })}</ul></div>; }) : <p className="preview-empty">None</p>;
    case "project_experience": return p.project_experiences.length ? p.project_experiences.map(function(pr, i) { return <div key={i} className="preview-entry"><div className="preview-entry-title"><span>{pr.project_name}{pr.project_role ? " (" + pr.project_role + ")" : ""}</span> <span className="preview-entry-time">{pr.project_time}</span></div><div className="preview-text" style={{ whiteSpace: "pre-wrap" }} dangerouslySetInnerHTML={{ __html: pr.project_description || "None" }} /></div>; }) : <p className="preview-empty">None</p>;
    case "education": return (p.education || []).length ? p.education.map(function(e, i) { return <div key={i} className="preview-entry edu-entry"><div className="preview-entry-title edu-title-line"><span>{e.school_name}</span><span className="preview-entry-time">{e.school_time}</span></div><div className="edu-detail"><span className="edu-major">{e.major}</span>{e.degree ? <span className="edu-degree"> | {e.degree}</span> : ""}</div></div>; }) : <p className="preview-empty">None</p>;
    case "awards": return p.awards.length ? <ul className="preview-entry-ul">{p.awards.map(function(a, i) { return <li key={i}>{a}</li>; })}</ul> : <p className="preview-empty">None</p>;
    default: return <p className="preview-empty">Custom</p>;
  }
}
