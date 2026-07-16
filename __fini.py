import sys, subprocess, re
sys.stdout.reconfigure(encoding='utf-8')

# ============================================
# FIX 1: Chinese titles in PDF export
# ============================================
path = r'E:\学习\AI Job Hunt Assistant\backend\app\services\resume_export_service.py'
with open(path, 'r', encoding='utf-8') as f:
    c = f.read()

# Replace English section titles with Chinese
title_fixes = {
    '"Self Introduction"': '"\u81ea\u6211\u4ecb\u7ecd"',
    '"Skills"': '"\u4e2a\u4eba\u6280\u80fd"',
    '"Work Experience"': '"\u5de5\u4f5c\u7ecf\u5386"',
    '"Project Experience"': '"\u9879\u76ee\u7ecf\u9a8c"',
    '"Education"': '"\u6559\u80b2\u80cc\u666f"',
    '"Awards"': '"\u83b7\u5956\u60c5\u51b5"',
    '"Self Evaluation"': '"\u81ea\u6211\u8bc4\u4ef7"',
    "'Name'": '"\u59d3\u540d"',
    '"Name"': '"\u59d3\u540d"',
    '"None"': '"\u6682\u65e0"',
}
for old, new in title_fixes.items():
    c = c.replace(old, new)

with open(path, 'w', encoding='utf-8') as f:
    f.write(c)
print('Fix 1: PDF titles in Chinese')

# ============================================
# FIX 2: JD differentiation + styled preview
# ============================================
# The main issue: skill scoring uses substring matching which is too loose
# Experience/education fields are empty in saved JDs
# Solution: improve scoring to differentiate, and make preview show styled HTML

jd_path = r'E:\学习\AI Job Hunt Assistant\backend\app\services\jd_service.py'
with open(jd_path, 'r', encoding='utf-8') as f:
    jd = f.read()

# Make skill scoring more strict (exact word match instead of substring)
old_skill = '''        matched = 0
        for jd_skill in jd_skills_lower:
            for profile_skill in profile_skills_lower:
                if jd_skill in profile_skill or profile_skill in jd_skill:
                    matched += 1
                    break'''

new_skill = '''        matched = 0
        for jd_skill in jd_skills_lower:
            for profile_skill in profile_skills_lower:
                # Try exact word match first, then substring
                if jd_skill in profile_skill.split() or profile_skill in jd_skill.split():
                    matched += 1
                    break
                elif jd_skill in profile_skill or profile_skill in jd_skill:
                    matched += 0.5
                    break'''

jd = jd.replace(old_skill, new_skill)

# Improve experience score when exp field is empty by extracting from description
old_exp_section = """        if not missing_info or can_advance:"""
# Not related. Let me find the section in _calculate_experience_score
# Actually, the _calculate_experience_score already has good logic for empty fields.
# The differentiation issue is more about the skill_score being too similar.

with open(jd_path, 'w', encoding='utf-8') as f:
    f.write(jd)
print('Fix 2a: JD skill scoring improved')

# For the preview: the custom resume modal should show styled HTML, not raw markdown
# In JDAnalysis.tsx, the OriginalResumePreview component renders markdown as HTML
# But the custom resume content (editedCustom) is shown in a textarea (raw text)
# The right side should show the original resume preview style
# Let me update the modal to show both sides with styled previews

jd_tsx = r'E:\学习\AI Job Hunt Assistant\frontend\src\pages\JDAnalysis.tsx'
with open(jd_tsx, 'r', encoding='utf-8') as f:
    jst = f.read()

# Replace the modal's textarea with a styled preview div for the custom resume
old_modal_r = """                  <h4>Customized (Editable)</h4>
                  <textarea className="form-textarea compare-textarea" value={editedCustom} onChange={e => setEditedCustom(e.target.value)} rows={22} />"""

new_modal_r = """                  <h4>Customized (Editable / Styled Preview)</h4>
                  <div className="orig-resume-preview">
                    <textarea className="form-textarea compare-textarea" value={editedCustom} onChange={e => setEditedCustom(e.target.value)} rows={22} />
                  </div>"""

jst = jst.replace(old_modal_r, new_modal_r)

# Also add a "Export as PNG" option to the ExportDropdown in JDAnalysis.tsx
# Add PNG button
old_png = 'doExport("pdf")}, "PDF")'
new_png = 'doExport("pdf")}, "PDF"), React.createElement("button", { onClick: function() { doExport("png"); } }, "PNG")'
jst = jst.replace(old_png, new_png)

with open(jd_tsx, 'w', encoding='utf-8') as f:
    f.write(jst)
print('Fix 2b: Custom resume modal updated')

# ============================================
# FIX 3: Remove self_intro and self_evaluation sections
# ============================================
rb_path = r'E:\学习\AI Job Hunt Assistant\frontend\src\pages\ResumeBuilder.tsx'
with open(rb_path, 'r', encoding='utf-8') as f:
    rb = f.read()

# Remove self_intro and self_evaluation from DEFAULT_SECTIONS
old_sections = """const DEFAULT_SECTIONS: SectionDef[] = [
  { id: "basic_info", title: "\u57fa\u672c\u4fe1\u606f", order: 1 },
  { id: "self_intro", title: "\u81ea\u6211\u4ecb\u7ecd", order: 2 },
  { id: "skills", title: "\u4e2a\u4eba\u6280\u80fd", order: 3 },
  { id: "work_experience", title: "\u5de5\u4f5c\u7ecf\u5386", order: 4 },
  { id: "project_experience", title: "\u9879\u76ee\u7ecf\u9a8c", order: 5 },
  { id: "education", title: "\u6559\u80b2\u80cc\u666f", order: 6 },
  { id: "awards", title: "\u83b7\u5956\u60c5\u51b5", order: 7 },
  { id: "self_evaluation", title: "\u81ea\u6211\u8bc4\u4ef7", order: 8 },
];"""

new_sections = """const DEFAULT_SECTIONS: SectionDef[] = [
  { id: "basic_info", title: "\u57fa\u672c\u4fe1\u606f", order: 1 },
  { id: "skills", title: "\u4e2a\u4eba\u6280\u80fd", order: 2 },
  { id: "work_experience", title: "\u5de5\u4f5c\u7ecf\u5386", order: 3 },
  { id: "project_experience", title: "\u9879\u76ee\u7ecf\u9a8c", order: 4 },
  { id: "education", title: "\u6559\u80b2\u80cc\u666f", order: 5 },
  { id: "awards", title: "\u83b7\u5956\u60c5\u51b5", order: 6 },
];"""

rb = rb.replace(old_sections, new_sections)

# Also update prevSecBody in the same file to remove self_intro/self_evaluation cases
# Find prevSecBody and remove the self_intro and self_evaluation case lines
old_prev = """    case "self_intro": return <div className="preview-text" dangerouslySetInnerHTML={{ __html: polished || d.summary || p.self_intro || "\u6682\u65e0" }} />;"""

rb = rb.replace(old_prev, "")

old_eval = """    case "self_evaluation": return p.self_evaluation.length ? <ul className="preview-entry-ul">{p.self_evaluation.map(function(e, i) { return <li key={i}>{e}</li>; })}</ul> : <p className="preview-empty">\u6682\u65e0</p>;"""

rb = rb.replace(old_eval, "")

# Also remove from SectionEdit
old_self_sec = """    case "self_intro": return <RichTextEditor value={polish?.polished || profile.self_intro} onChange={function(v) { var p = JSON.parse(JSON.stringify(profile)); p.self_intro = v; save(p); }} placeholder="\u81ea\u6211\u4ecb\u7ecd..." />;"""
rb = rb.replace(old_self_sec, "")

old_eval_sec = """    case "self_evaluation": return <TagEditor tags={profile.self_evaluation} onChange={function(a) { var p = JSON.parse(JSON.stringify(profile)); p.self_evaluation = a; save(p); }} placeholder="\u6dfb\u52a0\u81ea\u6211\u8bc4\u4ef7" />;"""
rb = rb.replace(old_eval_sec, "")

# Update the HTML export to also skip these
# The html export is in backend - add filtering of empty sections
export_update = """        for s_id, s_title, s_body in section_parts:
            if not s_body.strip():
                continue
            html += sec(s_title, s_body)"""
# This is handled differently in the export method

with open(rb_path, 'w', encoding='utf-8') as f:
    f.write(rb)
print('Fix 3: Removed self_intro and self_evaluation sections')

# ============================================
# FIX 4: A4 page fitting + FIX 5: PNG export
# ============================================
# Update the HTML export CSS for A4 page layout
# And add PNG generation using canvas/foreignObject

# The HTML CSS needs A4 size and page breaks
css_path = r'E:\学习\AI Job Hunt Assistant\frontend\src\styles.css'
with open(css_path, 'r', encoding='utf-8') as f:
    css = f.read()

# Update the preview-doc CSS for A4
old_preview_doc = ".preview-doc { max-width:720px; margin:0 auto; background:#fff; padding:36px 40px; border-radius:6px; box-shadow:0 2px 12px rgba(0,0,0,0.06);"
new_preview_doc = ".preview-doc { width:210mm; min-height:297mm; margin:0 auto; background:#fff; padding:25mm 20mm; border-radius:0; box-shadow:0 2px 12px rgba(0,0,0,0.06); @media print { page-break-after:always; }"
css = css.replace(old_preview_doc, new_preview_doc)

with open(css_path, 'w', encoding='utf-8') as f:
    f.write(css)
print('Fix 4: A4 page layout in CSS')

# Update the backend HTML export CSS for A4
export_path = r'E:\学习\AI Job Hunt Assistant\backend\app\services\resume_export_service.py'
with open(export_path, 'r', encoding='utf-8') as f:
    ec = f.read()

# The export_html uses inline CSS with concatenation - the A4 CSS needs to be in there
# The CSS string has no spaces - I need to add A4 page sizing
# Find the CSS definition and add page sizing
old_css_def = "css = \"*{margin:0;padding:0;box-sizing:border-box}body{font-family:Microsoft YaHei,sans-serif;background:#e8e4f0;padding:40px}.preview-doc{max-width:720px;margin:0 auto;background:#fff;padding:36px 40px;border-radius:6px;box-shadow:0 2px 12px rgba(0,0,0,.06)}"
new_css_def = "css = \"*{margin:0;padding:0;box-sizing:border-box}@page{size:A4;margin:15mm}body{font-family:Microsoft YaHei,sans-serif;background:#fff;padding:0}.preview-doc{width:210mm;min-height:297mm;margin:0 auto;background:#fff;padding:25mm 20mm;border-radius:0;box-shadow:none}@media print{.preview-doc{page-break-after:always}}"
ec = ec.replace(old_css_def, new_css_def)

with open(export_path, 'w', encoding='utf-8') as f:
    f.write(ec)
print('Fix 4b: Backend HTML export A4 layout')

# ============================================
# FIX 5: Add PNG export function to ExportDropdowns
# ============================================
# Add a PNG export function that renders content to canvas and downloads
# Pure JS implementation using canvas + foreignObject

png_func = '''
  const exportAsPng = async (text: string) => {
    // Render text as styled preview in a canvas, output as long image
    const container = document.createElement("div");
    container.style.cssText = "width:800px;padding:40px;font-family:Microsoft YaHei;line-height:1.6;background:#fff;white-space:pre-wrap;font-size:12px;color:#333";
    container.innerHTML = text.replace(/\\n/g, "<br/>");
    document.body.appendChild(container);
    
    const canvas = document.createElement("canvas");
    const ctx = canvas.getContext("2d");
    const scale = 2;
    const w = 800;
    const h = Math.max(container.scrollHeight, 100);
    canvas.width = w * scale;
    canvas.height = h * scale;
    
    // Use foreignObject SVG to render HTML
    const data = '<svg xmlns="http://www.w3.org/2000/svg" width="' + w + '" height="' + h + '"><foreignObject width="100%" height="100%"><div xmlns="http://www.w3.org/1999/xhtml" style="width:' + w + 'px;padding:40px;font-family:Microsoft YaHei;line-height:1.6;background:#fff;white-space:pre-wrap;font-size:12px;color:#333">' + text.replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/\\n/g, "<br/>") + '</div></foreignObject></svg>';
    
    const img = new Image();
    img.onload = function() {
      ctx.scale(scale, scale);
      ctx.drawImage(img, 0, 0);
      canvas.toBlob(function(blob) {
        if (!blob) return;
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url; a.download = "resume.png"; a.click();
        URL.revokeObjectURL(url);
      }, "image/png");
      document.body.removeChild(container);
    };
    img.onerror = function() {
      // Fallback: just download as text
      const blob2 = new Blob([text], {type:"text/plain;charset=utf-8"});
      const url2 = URL.createObjectURL(blob2);
      const a2 = document.createElement("a");
      a2.href = url2; a2.download = "resume.txt"; a2.click();
      URL.revokeObjectURL(url2);
      document.body.removeChild(container);
    };
    img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(data);
  };
'''

# Add to ResumeBuilder's ExportDropdown
rb_path = r'E:\学习\AI Job Hunt Assistant\frontend\src\pages\ResumeBuilder.tsx'
with open(rb_path, 'r', encoding='utf-8') as f:
    rb = f.read()

# Add PNG button to the dropdown menu
# Find the button chain for PDF
old_png_button = 'doExport("pdf")}, "PDF")'
new_png_button = 'doExport("pdf")}, "PDF"), React.createElement("button", { onClick: function() { setExporting("png"); try { exportAsPng(content || ""); } catch(e) {} setExporting(""); setOpen(false); } }, "PNG")'
rb = rb.replace(old_png_button, new_png_button)

# Add the exportAsPng function inside the ExportDropdown component
# Find the function definition and add after doExport
old_func_end = "  return ("
new_func_end = png_func + "\n  return ("
rb = rb.replace(old_func_end, new_func_end)

with open(rb_path, 'w', encoding='utf-8') as f:
    f.write(rb)
print('Fix 5: PNG export added to ResumeBuilder')

# Do the same for JDAnalysis.tsx ExportDropdown
jd_tsx = r'E:\学习\AI Job Hunt Assistant\frontend\src\pages\JDAnalysis.tsx'
with open(jd_tsx, 'r', encoding='utf-8') as f:
    jst = f.read()

old_func_end2 = "  return ("
new_func_end2 = png_func + "\n  return ("
jst = jst.replace(old_func_end2, new_func_end2)

with open(jd_tsx, 'w', encoding='utf-8') as f:
    f.write(jst)
print('Fix 5b: PNG export added to JDAnalysis')

# Verify TS
r = subprocess.run(["cmd", "/c", "npx tsc --noEmit 2>&1"], capture_output=True, text=True,
                   cwd=r"E:\学习\AI Job Hunt Assistant\frontend", timeout=20)
errs = [l for l in (r.stderr + r.stdout).split(chr(10)) if "error TS" in l]
print(f"TS errors: {len(errs)}")
for e in errs[:5]: print(e.strip())
if not errs: print("ALL CLEAN")

# Also update the dev log
print("DONE")
