import { useState, useEffect } from "react";
import type { InterviewQuestion, InterviewCategory, JobDescription } from "../types/index";
import { generateInterviewQuestions, getInterviewCategories, getAllJds } from "../lib/api";

export default function Interview() {
  const [questions, setQuestions] = useState<InterviewQuestion[]>([]);
  const [categories, setCategories] = useState<InterviewCategory[]>([]);
  const [jds, setJds] = useState<JobDescription[]>([]);
  const [selectedJdId, setSelectedJdId] = useState<string>("");
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [questionCount, setQuestionCount] = useState(15);
  const [isGenerating, setIsGenerating] = useState(false);
  const [expandedQuestion, setExpandedQuestion] = useState<number | null>(null);
  const [filterCategory, setFilterCategory] = useState<string>("");

  useEffect(() => {
    getInterviewCategories().then(res => setCategories(res.categories));
    getAllJds().then(setJds);
  }, []);

  const handleGenerate = async () => {
    setIsGenerating(true);
    try {
      const res = await generateInterviewQuestions(
        selectedJdId || undefined,
        questionCount,
        selectedCategories.length > 0 ? selectedCategories : undefined
      );
      setQuestions(res.questions);
    } catch (err) {
      console.error("Failed to generate questions:", err);
    } finally {
      setIsGenerating(false);
    }
  };

  const toggleCategory = (catId: string) => {
    setSelectedCategories(prev =>
      prev.includes(catId)
        ? prev.filter(c => c !== catId)
        : [...prev, catId]
    );
  };

  const toggleQuestion = (index: number) => {
    setExpandedQuestion(expandedQuestion === index ? null : index);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case "简单": return "#059669";
      case "中等": return "#d97706";
      case "困难": return "#dc2626";
      default: return "#6c6c8a";
    }
  };

  const filteredQuestions = filterCategory
    ? questions.filter(q => q.category === filterCategory)
    : questions;

  const categoryCounts = questions.reduce((acc, q) => {
    acc[q.category] = (acc[q.category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="interview-page">
      <div className="interview-header">
        <h2>面试题生成器</h2>
      </div>

      <div className="interview-panel">
        <div className="interview-panel-header">
          <h3>生成设置</h3>
        </div>

        <div className="form-grid" style={{ gridTemplateColumns: "1fr" }}>
          <div className="form-field">
            <label>目标职位（可选）</label>
            <select
              value={selectedJdId}
              onChange={(e) => setSelectedJdId(e.target.value)}
              className="form-input"
            >
              <option value="">选择目标职位（不选则生成通用问题）</option>
              {jds.map(jd => (
                <option key={jd.id} value={jd.id}>
                  {jd.title} - {jd.company}
                </option>
              ))}
            </select>
          </div>

          <div className="form-field">
            <label>问题数量</label>
            <input
              type="number"
              min="5"
              max="30"
              value={questionCount}
              onChange={(e) => setQuestionCount(parseInt(e.target.value) || 15)}
              className="form-input"
            />
          </div>

          <div className="form-field">
            <label>问题类型（多选）</label>
            <div className="interview-category-tags">
              {categories.map(cat => (
                <button
                  key={cat.id}
                  onClick={() => toggleCategory(cat.name)}
                  className={`interview-category-tag ${selectedCategories.includes(cat.name) ? "active" : ""}`}
                >
                  {cat.name}
                </button>
              ))}
            </div>
          </div>
        </div>

        <div className="knowledge-upload-actions" style={{ marginTop: "16px" }}>
          <button
            onClick={handleGenerate}
            disabled={isGenerating}
            className="btn-primary"
          >
            {isGenerating ? "生成中..." : "生成面试题"}
          </button>
        </div>
      </div>

      {questions.length > 0 && (
        <div className="interview-panel">
          <div className="interview-panel-header">
            <h3>面试题列表</h3>
            <span className="badge">{filteredQuestions.length} 题</span>
          </div>

          <div className="interview-filter-bar">
            <button
              onClick={() => setFilterCategory("")}
              className={`interview-filter-btn ${!filterCategory ? "active" : ""}`}
            >
              全部
            </button>
            {Object.entries(categoryCounts).map(([cat, count]) => (
              <button
                key={cat}
                onClick={() => setFilterCategory(filterCategory === cat ? "" : cat)}
                className={`interview-filter-btn ${filterCategory === cat ? "active" : ""}`}
              >
                {cat} ({count})
              </button>
            ))}
          </div>

          <div className="interview-questions-list">
            {filteredQuestions.map((q, index) => (
              <div
                key={index}
                className="interview-question-card"
                onClick={() => toggleQuestion(index)}
              >
                <div className="interview-question-header">
                  <span className="interview-question-number">{index + 1}</span>
                  <span className="interview-question-category">{q.category}</span>
                  <span
                    className="interview-question-difficulty"
                    style={{ backgroundColor: `${getDifficultyColor(q.difficulty)}20`, color: getDifficultyColor(q.difficulty) }}
                  >
                    {q.difficulty}
                  </span>
                  <svg
                    className={`interview-expand-icon ${expandedQuestion === index ? "rotated" : ""}`}
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                  >
                    <path d="M6 9l6 6 6-6" />
                  </svg>
                </div>
                <div className="interview-question-body">
                  <p>{q.question}</p>
                </div>
                {expandedQuestion === index && q.suggested_answer && (
                  <div className="interview-suggested-answer">
                    <h4>参考思路</h4>
                    <p>{q.suggested_answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {questions.length === 0 && !isGenerating && (
        <div className="interview-panel">
          <div className="interview-empty">
            <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#c0bcd0" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: 12 }}>
              <circle cx="12" cy="12" r="10" />
              <path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3" />
              <line x1="12" y1="17" x2="12.01" y2="17" />
            </svg>
            <h3>开始生成面试题</h3>
            <p>选择目标职位和问题类型，AI 将为你生成针对性的面试问题</p>
          </div>
        </div>
      )}
    </div>
  );
}
