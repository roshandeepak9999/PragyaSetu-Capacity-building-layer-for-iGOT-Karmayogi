const CATEGORY_COLOR = { Domain: "#2C3E63", Functional: "#C9862B", Behavioural: "#A6432F" };

const SAMPLE_MATERIAL = `Stratified random sampling divides the population into distinct, non-overlapping subgroups called strata before sampling. Each stratum should be internally homogeneous with respect to the characteristic being studied, while strata should differ from one another. Within each stratum, units are then selected using simple random sampling or systematic sampling.

In official surveys such as those conducted by the National Sample Survey Office, stratification is often done by geographic region (state, district) and by sector (rural/urban), since these strata tend to have meaningfully different socio-economic characteristics. Proportionate allocation assigns sample size to each stratum in proportion to the stratum's share of the population, while disproportionate (optimum) allocation may over-sample smaller strata with higher internal variance to control the overall margin of error.

A key advantage of stratified sampling over simple random sampling is a reduction in sampling error when strata are well-chosen, because variability within each stratum is lower than variability in the population as a whole. A common pitfall is choosing strata that do not differ meaningfully on the variable of interest, in which case stratification adds administrative cost without a corresponding precision gain.`;

let OFFICERS = [];
let currentOfficerId = null;
let currentTab = "overview";

// Quiz state
let quizQuestions = [];
let quizAnswers = {};
let quizChecked = false;

async function init() {
  const res = await fetch("/api/officers");
  OFFICERS = await res.json();
  currentOfficerId = OFFICERS[0].id;
  renderSidebar();
  renderHeader();
  renderTab();

  document.querySelectorAll(".ss-tab").forEach((btn) => {
    btn.addEventListener("click", () => {
      currentTab = btn.dataset.tab;
      document.querySelectorAll(".ss-tab").forEach((b) => b.classList.toggle("is-active", b === btn));
      document.querySelectorAll(".ss-panel").forEach((p) => (p.hidden = p.id !== `tab-${currentTab}`));
      renderTab();
    });
  });
}

function currentOfficer() {
  return OFFICERS.find((o) => o.id === currentOfficerId);
}

function renderHeader() {
  const o = currentOfficer();
  document.getElementById("current-officer-name").textContent = o.name;
  document.getElementById("current-officer-role").textContent = `${o.role}, ${o.org}`;
}

function renderSidebar() {
  const list = document.getElementById("officer-list");
  list.innerHTML = "";
  OFFICERS.forEach((o) => {
    const li = document.createElement("li");
    const btn = document.createElement("button");
    btn.className = "ss-officer-item" + (o.id === currentOfficerId ? " is-active" : "");
    btn.innerHTML = `<span class="ss-officer-item-name">${o.name}</span><span class="ss-officer-item-role">${o.role}</span>`;
    btn.addEventListener("click", () => {
      currentOfficerId = o.id;
      quizQuestions = [];
      quizAnswers = {};
      quizChecked = false;
      renderSidebar();
      renderHeader();
      renderTab();
    });
    li.appendChild(btn);
    list.appendChild(li);
  });
}

function renderTab() {
  if (currentTab === "overview") renderOverview();
  if (currentTab === "learning") renderLearning();
  if (currentTab === "quiz") renderQuiz();
}

// ---------------------------------------------------------------------------

function renderOverview() {
  const o = currentOfficer();
  const total = o.competencies.length;
  const closed = o.competencies.filter((c) => c.acquired >= c.required).length;
  const readiness = Math.round((closed / total) * 100);

  const rows = o.competencies.map((c) => {
    const gap = c.required - c.acquired;
    return `
      <tr>
        <td class="ss-ledger-name">${c.name}</td>
        <td><span class="ss-category-dot" style="background:${CATEGORY_COLOR[c.category]}"></span>${c.category}</td>
        <td class="ss-num">${c.required}</td>
        <td class="ss-num">${c.acquired}</td>
        <td>
          <div class="ss-gap-track">
            <div class="ss-gap-fill ${gap > 0 ? "is-open" : "is-closed"}" style="width:${(c.acquired / 5) * 100}%"></div>
            <div class="ss-gap-req" style="left:${(c.required / 5) * 100}%"></div>
          </div>
        </td>
      </tr>`;
  }).join("");

  document.getElementById("tab-overview").innerHTML = `
    <div class="ss-readiness">
      <div class="ss-readiness-figure">${readiness}%</div>
      <div>
        <div class="ss-readiness-label">Role readiness</div>
        <div class="ss-readiness-detail">${closed} of ${total} FRAC competencies at or above the required level for ${o.role}</div>
      </div>
    </div>
    <table class="ss-ledger">
      <thead><tr><th>Competency</th><th>Category</th><th>Required</th><th>Acquired</th><th>Gap</th></tr></thead>
      <tbody>${rows}</tbody>
    </table>
    <p class="ss-footnote">Bar shows acquired proficiency (1–5 FRAC scale); the vertical mark is the required level for this role.</p>
  `;
}

function renderLearning() {
  const o = currentOfficer();
  const gaps = o.competencies
    .filter((c) => c.required - c.acquired > 0)
    .sort((a, b) => (b.required - b.acquired) - (a.required - a.acquired));

  const panel = document.getElementById("tab-learning");

  if (gaps.length === 0) {
    panel.innerHTML = `<p class="ss-empty">No open gaps for ${o.name} right now — every competency meets the required level.</p>`;
    return;
  }

  const items = gaps.map((c) => {
    if (!c.course) return "";
    return `
      <li class="ss-course">
        <div>
          <div class="ss-course-title">${c.course.title}</div>
          <div class="ss-course-meta">${c.course.code} · ${c.course.duration}</div>
        </div>
        <div class="ss-course-side">
          <span class="ss-course-tag">Closes: ${c.name} (gap ${c.required - c.acquired})</span>
          <a class="ss-btn" href="https://igotkarmayogi.gov.in" target="_blank" rel="noopener">Open in iGOT Karmayogi</a>
        </div>
      </li>`;
  }).join("");

  panel.innerHTML = `
    <p class="ss-section-intro">Courses pulled from the iGOT Karmayogi catalogue, ranked by the size of ${o.name.split(" ")[0]}'s gap.</p>
    <ul class="ss-course-list">${items}</ul>
  `;
}

// ---------------------------------------------------------------------------

function renderQuiz() {
  const o = currentOfficer();
  const panel = document.getElementById("tab-quiz");

  const options = o.competencies.map((c) => `<option value="${c.name}">${c.name}</option>`).join("");

  panel.innerHTML = `
    <p class="ss-section-intro">Paste or upload departmental training material — SOPs, methodology notes, circulars — and generate a tagged MCQ set. Results roll back into the competency ledger.</p>
    <div class="ss-quiz-form">
      <textarea id="quiz-material" class="ss-textarea" rows="8" placeholder="Paste training material here…"></textarea>
      <div class="ss-quiz-controls">
        <label class="ss-upload">
          Upload .txt file
          <input type="file" id="quiz-upload" accept=".txt,.md" hidden />
        </label>
        <button class="ss-btn ss-btn-quiet" id="quiz-sample">Use sample material</button>
        <select id="quiz-tag" class="ss-select">${options}</select>
        <select id="quiz-count" class="ss-select">
          <option value="3">3 questions</option>
          <option value="5" selected>5 questions</option>
          <option value="8">8 questions</option>
        </select>
        <button class="ss-btn ss-btn-primary" id="quiz-generate">Generate quiz</button>
      </div>
      <div id="quiz-error" class="ss-alert"></div>
    </div>
    <div id="quiz-results"></div>
  `;

  document.getElementById("quiz-sample").addEventListener("click", () => {
    document.getElementById("quiz-material").value = SAMPLE_MATERIAL;
  });

  document.getElementById("quiz-upload").addEventListener("change", (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => (document.getElementById("quiz-material").value = reader.result);
    reader.readAsText(file);
  });

  document.getElementById("quiz-generate").addEventListener("click", generateQuiz);

  renderQuizResults();
}

async function generateQuiz() {
  const material = document.getElementById("quiz-material").value.trim();
  const tag = document.getElementById("quiz-tag").value;
  const count = document.getElementById("quiz-count").value;
  const errorBox = document.getElementById("quiz-error");
  const btn = document.getElementById("quiz-generate");

  errorBox.textContent = "";
  if (!material) {
    errorBox.textContent = "Paste or upload some training material first.";
    return;
  }

  btn.disabled = true;
  btn.textContent = "Drafting questions…";

  try {
    const res = await fetch("/api/generate-quiz", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ material, tag, count }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Request failed");

    quizQuestions = data.questions;
    quizAnswers = {};
    quizChecked = false;
    renderQuizResults();
  } catch (err) {
    errorBox.textContent = err.message || "Something went wrong generating the quiz.";
  } finally {
    btn.disabled = false;
    btn.textContent = "Generate quiz";
  }
}

function renderQuizResults() {
  const container = document.getElementById("quiz-results");
  if (!container) return;

  if (quizQuestions.length === 0) {
    container.innerHTML = "";
    return;
  }

  const score = quizQuestions.reduce((s, q, i) => s + (quizAnswers[i] === q.correctIndex ? 1 : 0), 0);
  const allAnswered = Object.keys(quizAnswers).length === quizQuestions.length;

  const questionsHtml = quizQuestions.map((q, qi) => {
    const optionsHtml = q.options.map((opt, oi) => {
      const selected = quizAnswers[qi] === oi;
      const isCorrect = oi === q.correctIndex;
      let cls = "";
      if (quizChecked) {
        if (isCorrect) cls = "is-correct";
        else if (selected) cls = "is-wrong";
      } else if (selected) {
        cls = "is-selected";
      }
      return `<button class="ss-option ${cls}" data-qi="${qi}" data-oi="${oi}">${opt}</button>`;
    }).join("");

    return `
      <div class="ss-question">
        <div class="ss-question-head">
          <span class="ss-question-num">Q${qi + 1}</span>
        </div>
        <div class="ss-question-text">${q.question}</div>
        <div class="ss-options">${optionsHtml}</div>
        ${quizChecked ? `<div class="ss-explanation">${q.explanation || ""}</div>` : ""}
      </div>`;
  }).join("");

  container.innerHTML = `
    <div class="ss-quiz-results">
      <div class="ss-quiz-results-head">
        <span>${quizQuestions.length} questions</span>
        ${quizChecked ? `<span class="ss-score">${score} / ${quizQuestions.length} correct</span>` : ""}
      </div>
      ${questionsHtml}
      ${!quizChecked ? `<button class="ss-btn ss-btn-primary" id="quiz-check" ${allAnswered ? "" : "disabled"}>Check answers</button>` : ""}
    </div>
  `;

  container.querySelectorAll(".ss-option").forEach((btn) => {
    btn.addEventListener("click", () => {
      if (quizChecked) return;
      quizAnswers[btn.dataset.qi] = Number(btn.dataset.oi);
      renderQuizResults();
    });
  });

  const checkBtn = document.getElementById("quiz-check");
  if (checkBtn) checkBtn.addEventListener("click", () => { quizChecked = true; renderQuizResults(); });
}

init();