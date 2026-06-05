const form = document.querySelector("#research-form");
const message = document.querySelector("#form-message");
const reportPreview = document.querySelector("#report-preview");
const reportPath = document.querySelector("#report-path");
const reviewStatus = document.querySelector("#review-status");
const sectionsCount = document.querySelector("#sections-count");
const sourcesCount = document.querySelector("#sources-count");
const nodes = Array.from(document.querySelectorAll("#pipeline span"));
const submitButton = form.querySelector("button[type='submit']");
const copyButton = document.querySelector("#copy-report");
const downloadButton = document.querySelector("#download-report");
const topicField = document.querySelector("#topic");
let latestMarkdown = "";
let latestTopic = "";

function setPipeline(active) {
  nodes.forEach((node, index) => {
    node.classList.toggle("active", index <= active);
  });
}

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function markdownToHtml(markdown) {
  const lines = markdown.split("\n");
  const html = [];
  let inList = false;

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line) {
      if (inList) {
        html.push("</ul>");
        inList = false;
      }
      continue;
    }

    if (line.startsWith("# ")) {
      if (inList) html.push("</ul>");
      inList = false;
      html.push(`<h1>${escapeHtml(line.slice(2))}</h1>`);
    } else if (line.startsWith("## ")) {
      if (inList) html.push("</ul>");
      inList = false;
      html.push(`<h2>${escapeHtml(line.slice(3))}</h2>`);
    } else if (line.startsWith("- ")) {
      if (!inList) {
        html.push("<ul>");
        inList = true;
      }
      html.push(`<li>${escapeHtml(line.slice(2))}</li>`);
    } else if (/^\d+\.\s/.test(line)) {
      if (!inList) {
        html.push("<ul>");
        inList = true;
      }
      html.push(`<li>${escapeHtml(line.replace(/^\d+\.\s/, ""))}</li>`);
    } else {
      if (inList) {
        html.push("</ul>");
        inList = false;
      }
      html.push(`<p>${escapeHtml(line)}</p>`);
    }
  }

  if (inList) html.push("</ul>");
  return html.join("");
}

function setReportActions(enabled) {
  copyButton.disabled = !enabled;
  downloadButton.disabled = !enabled;
}

function downloadMarkdown() {
  if (!latestMarkdown) return;
  const blob = new Blob([latestMarkdown], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `${latestTopic || "research-report"}.md`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function copyMarkdown() {
  if (!latestMarkdown) return;
  const fallbackCopy = () => {
    const textArea = document.createElement("textarea");
    textArea.value = latestMarkdown;
    textArea.setAttribute("readonly", "readonly");
    textArea.style.position = "fixed";
    textArea.style.left = "-9999px";
    document.body.appendChild(textArea);
    textArea.select();
    const copied = document.execCommand("copy");
    textArea.remove();
    return copied;
  };

  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(latestMarkdown);
    } else if (!fallbackCopy()) {
      throw new Error("fallback copy failed");
    }
    message.textContent = "报告已复制到剪贴板。";
  } catch (error) {
    if (fallbackCopy()) {
      message.textContent = "报告已复制到剪贴板。";
    } else {
      message.textContent = "复制失败，请直接在预览区选择文本复制。";
    }
  }
}

document.querySelectorAll("[data-topic]").forEach((button) => {
  button.addEventListener("click", () => {
    topicField.value = button.dataset.topic;
    topicField.focus();
  });
});

copyButton.addEventListener("click", copyMarkdown);
downloadButton.addEventListener("click", downloadMarkdown);

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(form);
  const topic = String(formData.get("topic") || "").trim();
  if (!topic) {
    message.textContent = "请输入研究主题。";
    return;
  }

  submitButton.disabled = true;
  setReportActions(false);
  latestMarkdown = "";
  latestTopic = "";
  message.textContent = "正在生成报告，请稍候...";
  reportPath.textContent = "生成中";
  reviewStatus.textContent = "运行中";
  sectionsCount.textContent = "0";
  sourcesCount.textContent = "0";
  setPipeline(1);

  try {
    const response = await fetch('/api/research', {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        topic,
        provider: String(formData.get("provider") || "demo"),
        demo: document.querySelector("#demo").checked,
        output_dir: String(formData.get("output_dir") || "outputs"),
      }),
    });

    if (!response.ok) {
      throw new Error(`请求失败：${response.status}`);
    }

    setPipeline(4);
    const payload = await response.json();
    latestMarkdown = payload.markdown;
    latestTopic = payload.topic;
    reportPath.textContent = payload.report_path;
    reviewStatus.textContent = payload.review.passed ? "通过" : "需检查";
    sectionsCount.textContent = String(payload.sections_count || 0);
    sourcesCount.textContent = String(payload.sources_count || 0);
    reportPreview.innerHTML = markdownToHtml(payload.markdown);
    setReportActions(true);
    message.textContent = "报告生成完成。";
  } catch (error) {
    setPipeline(-1);
    reviewStatus.textContent = "失败";
    reportPath.textContent = "未生成";
    sectionsCount.textContent = "0";
    sourcesCount.textContent = "0";
    reportPreview.innerHTML = `
      <div class="empty-state">
        <h3>生成失败</h3>
        <p>${escapeHtml(error.message)}</p>
      </div>
    `;
    message.textContent = "生成失败，请检查服务状态或输入参数。";
  } finally {
    submitButton.disabled = false;
  }
});
