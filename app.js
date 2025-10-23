const projects = [
  {
    projectId: "proj-001",
    name: "智慧製造平台整合",
    health: "green",
    status: "整體進度正常，近期完成資料匯流模組。",
    lastUpdated: "2023-09-12",
  },
  {
    projectId: "proj-002",
    name: "AI 檢測系統升級",
    health: "yellow",
    status: "測試環境穩定度待提升，與供應商協調中。",
    lastUpdated: "2023-09-08",
  },
  {
    projectId: "proj-003",
    name: "供應鏈追蹤平台",
    health: "red",
    status: "核心 API 延遲過高，本週安排重構。",
    lastUpdated: "2023-09-05",
  },
];

const projectList = document.getElementById("project-list");
const healthFilter = document.getElementById("health-filter");
const addProjectBtn = document.getElementById("add-project-btn");
const sortUpdatedBtn = document.getElementById("sort-updated-btn");
const modal = document.getElementById("project-modal");
const modalCloseBtn = document.getElementById("modal-close-btn");
const modalCancelBtn = document.getElementById("modal-cancel-btn");
const projectForm = document.getElementById("project-form");
const projectNameInput = document.getElementById("project-name");
const projectHealthSelect = document.getElementById("project-health");
const projectUpdatedInput = document.getElementById("project-updated");
const projectStatusTextarea = document.getElementById("project-status");

let lastFocusedElement = null;
let closeTimeoutId = null;
let sortOrder = "desc";

function generateProjectId() {
  if (window.crypto && typeof window.crypto.randomUUID === "function") {
    return window.crypto.randomUUID();
  }
  return `proj-${Date.now()}-${Math.random().toString(16).slice(2, 8)}`;
}

function formatDate(value) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleDateString("zh-TW", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  });
}

function renderProjects() {
  const filter = healthFilter.value;
  projectList.innerHTML = "";

  const filteredProjects = projects.filter((project) => {
    if (filter === "all") return true;
    return project.health === filter;
  });

  const sortedProjects = [...filteredProjects].sort((a, b) => {
    const aTime = new Date(a.lastUpdated).getTime();
    const bTime = new Date(b.lastUpdated).getTime();
    if (Number.isNaN(aTime) && Number.isNaN(bTime)) {
      return 0;
    }
    if (Number.isNaN(aTime)) {
      return sortOrder === "desc" ? 1 : -1;
    }
    if (Number.isNaN(bTime)) {
      return sortOrder === "desc" ? -1 : 1;
    }
    return sortOrder === "desc" ? bTime - aTime : aTime - bTime;
  });

  if (sortedProjects.length === 0) {
    const emptyState = document.createElement("li");
    emptyState.className = "project-card";
    emptyState.textContent = "目前沒有符合條件的專案。";
    projectList.appendChild(emptyState);
    return;
  }

  sortedProjects.forEach((project) => {
    const item = document.createElement("li");
    item.className = "project-card";
    item.dataset.projectId = project.projectId;

    const title = document.createElement("h2");
    title.textContent = project.name;

    const statusIndicator = document.createElement("span");
    statusIndicator.className = "status-indicator";

    const light = document.createElement("span");
    light.className = `status-light ${project.health}`;
    light.setAttribute("aria-hidden", "true");

    const statusText = document.createElement("span");
    statusText.textContent =
      project.health === "green"
        ? "綠燈"
        : project.health === "yellow"
        ? "黃燈"
        : "紅燈";

    statusIndicator.append(light, statusText);
    title.append(statusIndicator);

    const statusDescription = document.createElement("p");
    statusDescription.textContent = project.status;

    const updatedInfo = document.createElement("p");
    updatedInfo.className = "project-updated";
    updatedInfo.textContent = "上次更新：";

    const updatedTime = document.createElement("time");
    updatedTime.dateTime = project.lastUpdated;
    updatedTime.textContent = formatDate(project.lastUpdated);
    updatedInfo.append(updatedTime);

    item.append(title, statusDescription, updatedInfo);
    projectList.appendChild(item);
  });
}

function openModal() {
  if (closeTimeoutId) {
    window.clearTimeout(closeTimeoutId);
    closeTimeoutId = null;
  }
  lastFocusedElement = document.activeElement;
  modal.removeAttribute("hidden");
  modal.removeAttribute("inert");
  modal.classList.add("open");
  modal.setAttribute("aria-hidden", "false");
  projectForm.reset();
  const today = new Date().toISOString().slice(0, 10);
  projectUpdatedInput.value = today;
  projectUpdatedInput.max = today;
  projectNameInput.focus();
}

function closeModal() {
  modal.classList.remove("open");
  modal.setAttribute("aria-hidden", "true");
  modal.setAttribute("inert", "");
  const handleTransitionEnd = (event) => {
    if (event.target === modal && !modal.classList.contains("open")) {
      modal.setAttribute("hidden", "");
      closeTimeoutId = null;
    }
  };
  modal.addEventListener("transitionend", handleTransitionEnd, { once: true });

  closeTimeoutId = window.setTimeout(() => {
    if (!modal.classList.contains("open")) {
      modal.setAttribute("hidden", "");
    }
    closeTimeoutId = null;
  }, 250);
  if (lastFocusedElement) {
    lastFocusedElement.focus();
  }
}

function handleFormSubmit(event) {
  event.preventDefault();
  const name = projectNameInput.value.trim();
  const health = projectHealthSelect.value;
  const lastUpdated = projectUpdatedInput.value;
  const status = projectStatusTextarea.value.trim();

  if (!name || !status || !lastUpdated) {
    return;
  }

  projects.unshift({
    projectId: generateProjectId(),
    name,
    health,
    status,
    lastUpdated,
  });
  healthFilter.value = "all";
  closeModal();
  renderProjects();
}

function updateSortButtonLabel() {
  if (!sortUpdatedBtn) return;
  sortUpdatedBtn.textContent =
    sortOrder === "desc" ? "更新日期排序：新 → 舊" : "更新日期排序：舊 → 新";
  sortUpdatedBtn.setAttribute("aria-pressed", sortOrder === "desc" ? "true" : "false");
}

function toggleSortOrder() {
  sortOrder = sortOrder === "desc" ? "asc" : "desc";
  updateSortButtonLabel();
  renderProjects();
}

function handleKeyDown(event) {
  if (event.key === "Escape" && modal.classList.contains("open")) {
    closeModal();
  }
}

healthFilter.addEventListener("change", renderProjects);
addProjectBtn.addEventListener("click", openModal);
sortUpdatedBtn.addEventListener("click", toggleSortOrder);
modalCloseBtn.addEventListener("click", closeModal);
modalCancelBtn.addEventListener("click", closeModal);
modal.addEventListener("click", (event) => {
  if (event.target === modal) {
    closeModal();
  }
});
projectForm.addEventListener("submit", handleFormSubmit);
document.addEventListener("keydown", handleKeyDown);

updateSortButtonLabel();

renderProjects();
