const form = document.querySelector("#research-form");
const message = document.querySelector("#form-message");
const reportPreview = document.querySelector("#report-preview");
const reportPath = document.querySelector("#report-path");
const reviewStatus = document.querySelector("#review-status");
const nodes = Array.from(document.querySelectorAll("#pipeline span"));
const submitButton = form.querySelector("button[type='submit']");

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

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(form);
  const topic = String(formData.get("topic") || "").trim();
  if (!topic) {
    message.textContent = "请输入研究主题。";
    return;
  }

  submitButton.disabled = true;
  message.textContent = "正在生成报告，请稍候...";
  reportPath.textContent = "生成中";
  reviewStatus.textContent = "运行中";
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
    reportPath.textContent = payload.report_path;
    reviewStatus.textContent = payload.review.passed ? "通过" : "需检查";
    reportPreview.innerHTML = markdownToHtml(payload.markdown);
    message.textContent = "报告生成完成。";
  } catch (error) {
    setPipeline(-1);
    reviewStatus.textContent = "失败";
    reportPath.textContent = "未生成";
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
