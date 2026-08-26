const STORAGE_KEY = "travelBudgetRecords";
const TOTAL_DAYS = 28;

const mappingData = [
  { t1: "Corporate", t2: "Finance", t3: "Budget" },
  { t1: "Corporate", t2: "Finance", t3: "Compliance" },
  { t1: "Corporate", t2: "HR", t3: "Recruiting" },
  { t1: "Corporate", t2: "HR", t3: "People Ops" },
  { t1: "Engineering", t2: "Platform", t3: "Core" },
  { t1: "Engineering", t2: "Platform", t3: "Infrastructure" },
  { t1: "Engineering", t2: "Product", t3: "Frontend" },
  { t1: "Engineering", t2: "Product", t3: "Backend" },
  { t1: "Sales", t2: "APAC", t3: "Taiwan" },
  { t1: "Sales", t2: "APAC", t3: "Japan" },
  { t1: "Sales", t2: "EMEA", t3: "Germany" },
  { t1: "Sales", t2: "EMEA", t3: "France" },
];

const dom = {
  totalDays: document.getElementById("totalDays"),
  usedDays: document.getElementById("usedDays"),
  remainingDays: document.getElementById("remainingDays"),
  remainingDaysWrap: document.getElementById("remainingDaysWrap"),
  lastUpdated: document.getElementById("lastUpdated"),
  summaryMessage: document.getElementById("summaryMessage"),
  form: document.getElementById("recordForm"),
  formError: document.getElementById("formError"),
  applicant: document.getElementById("applicant"),
  location: document.getElementById("location"),
  days: document.getElementById("days"),
  t1: document.getElementById("t1"),
  t2: document.getElementById("t2"),
  t3: document.getElementById("t3"),
  daysMinus: document.getElementById("daysMinus"),
  daysPlus: document.getElementById("daysPlus"),
  applicantError: document.getElementById("applicantError"),
  locationError: document.getElementById("locationError"),
  daysError: document.getElementById("daysError"),
  t1Error: document.getElementById("t1Error"),
  recordsBody: document.getElementById("recordsBody"),
  emptyState: document.getElementById("emptyState"),
  copyAllBtn: document.getElementById("copyAllBtn"),
  toast: document.getElementById("toast"),
  loadExcelBtn: document.getElementById("loadExcelBtn"),
};

let records = [];

const showToast = (message) => {
  dom.toast.textContent = message;
  dom.toast.classList.add("show");
  window.setTimeout(() => dom.toast.classList.remove("show"), 2500);
};

const getNowIso = () => new Date().toISOString();

const sortRecords = (list) =>
  [...list].sort((a, b) => {
    if (a.submitted_at === b.submitted_at) {
      return a.applicant.localeCompare(b.applicant, "zh-Hant");
    }
    return b.submitted_at.localeCompare(a.submitted_at);
  });

const persistRecords = () => {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
};

const loadRecords = () => {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored) {
    try {
      records = JSON.parse(stored);
    } catch (error) {
      records = [];
    }
  }
};

const updateSummary = () => {
  const usedDays = records.reduce((sum, item) => sum + Number(item.days || 0), 0);
  const remaining = Math.max(TOTAL_DAYS - usedDays, 0);
  const lastUpdated = records.length
    ? sortRecords(records)[0].submitted_at
    : "-";

  dom.totalDays.textContent = TOTAL_DAYS;
  dom.usedDays.textContent = usedDays;
  dom.remainingDays.textContent = remaining;
  dom.remainingDaysWrap.classList.toggle("warning", remaining === 0);
  dom.lastUpdated.textContent = lastUpdated;
  dom.summaryMessage.textContent = records.length
    ? ""
    : "尚未有任何申請，可直接在下方表單新增。";
};

const buildOptions = (select, values, placeholder) => {
  select.innerHTML = "";
  if (placeholder !== null) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = placeholder;
    select.appendChild(option);
  }
  values.forEach((value) => {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  });
};

const updateT1Options = () => {
  const t1Values = [...new Set(mappingData.map((item) => item.t1))];
  buildOptions(dom.t1, t1Values, "請選擇");
};

const updateT2Options = (t1Value) => {
  const t2Values = mappingData
    .filter((item) => item.t1 === t1Value)
    .map((item) => item.t2)
    .filter((value) => value);
  const unique = [...new Set(t2Values)];
  buildOptions(dom.t2, unique, "（空白 / HQ）");
  dom.t2.value = "";
  updateT3Options("", "");
};

const updateT3Options = (t1Value, t2Value) => {
  const t3Values = mappingData
    .filter((item) => item.t1 === t1Value && item.t2 === t2Value)
    .map((item) => item.t3)
    .filter((value) => value);
  const unique = [...new Set(t3Values)];
  dom.t3.disabled = !t2Value;
  const placeholder = t2Value ? "請選擇" : "請先選擇 T2";
  buildOptions(dom.t3, unique, placeholder);
  dom.t3.value = "";
};

const renderRecords = () => {
  const sorted = sortRecords(records);
  dom.recordsBody.innerHTML = "";
  if (!sorted.length) {
    dom.emptyState.style.display = "block";
    return;
  }
  dom.emptyState.style.display = "none";
  sorted.forEach((record) => {
    const row = document.createElement("tr");
    [
      record.applicant,
      record.location,
      record.days,
      record.t1,
      record.t2,
      record.t3,
      record.submitted_at,
      record.status,
    ].forEach((value) => {
      const cell = document.createElement("td");
      cell.textContent = value || "";
      row.appendChild(cell);
    });
    dom.recordsBody.appendChild(row);
  });
};

const resetErrors = () => {
  dom.formError.textContent = "";
  dom.applicantError.textContent = "";
  dom.locationError.textContent = "";
  dom.daysError.textContent = "";
  dom.t1Error.textContent = "";
};

const resetForm = () => {
  dom.applicant.value = "";
  dom.location.value = "";
  dom.days.value = "1";
  dom.t1.value = "";
  updateT2Options("");
};

const validateDays = (value) => {
  const numberValue = Number(value);
  if (!Number.isInteger(numberValue) || numberValue < 1) {
    return "天數必須為大於等於 1 的整數";
  }
  return "";
};

const validateForm = () => {
  resetErrors();
  let hasError = false;

  if (!dom.applicant.value.trim()) {
    dom.applicantError.textContent = "此欄位必填";
    hasError = true;
  }

  if (!dom.location.value.trim()) {
    dom.locationError.textContent = "此欄位必填";
    hasError = true;
  }

  if (!dom.t1.value) {
    dom.t1Error.textContent = "請選擇一級組織";
    hasError = true;
  }

  const daysError = validateDays(dom.days.value);
  if (daysError) {
    dom.daysError.textContent = daysError;
    hasError = true;
  }

  if (hasError) {
    dom.formError.textContent = "請修正欄位錯誤後再送出";
  }

  return !hasError;
};

const isOverBudget = (newDays) => {
  const usedDays = records.reduce((sum, item) => sum + Number(item.days || 0), 0);
  return usedDays + newDays > TOTAL_DAYS;
};

const addRecord = () => {
  const record = {
    applicant: dom.applicant.value.trim(),
    location: dom.location.value.trim(),
    days: Number(dom.days.value),
    t1: dom.t1.value,
    t2: dom.t2.value,
    t3: dom.t3.value,
    submitted_at: getNowIso(),
    status: "",
  };

  records.push(record);
  persistRecords();
  updateSummary();
  renderRecords();
  resetForm();
  showToast("新增成功");
};

const handleSubmit = (event) => {
  event.preventDefault();
  if (!validateForm()) {
    return;
  }

  const dayValue = Number(dom.days.value);
  if (isOverBudget(dayValue)) {
    dom.formError.textContent =
      "剩餘天數不足，無法送出（將超出總預算天數）";
    return;
  }

  addRecord();
};

const handleCopyAll = async () => {
  const headers = [
    "applicant",
    "location",
    "days",
    "t1",
    "t2",
    "t3",
    "submitted_at",
    "status",
  ];
  const sorted = sortRecords(records);
  const rows = sorted.map((record) =>
    headers.map((header) => record[header] || "").join("\t")
  );
  const content = [headers.join("\t"), ...rows].join("\n");

  try {
    await navigator.clipboard.writeText(content);
    showToast("已複製到剪貼簿");
  } catch (error) {
    showToast("複製失敗，請重試");
  }
};

const applyExcelRecords = (items, sourceMessage) => {
  records = items.map((item) => ({
    applicant: item.applicant || "",
    location: item.location || "",
    days: Number(item.days) || 0,
    t1: item.t1 || "",
    t2: item.t2 || "",
    t3: item.t3 || "",
    submitted_at: item.submitted_at || getNowIso(),
    status: item.status || "",
  }));
  persistRecords();
  updateSummary();
  renderRecords();
  showToast(sourceMessage);
};

const loadFromSharePointExcel = async () => {
  if (!window.msal || !window.sharePointConfig) {
    showToast("SharePoint Excel 未設定或授權");
    return;
  }

  const config = window.sharePointConfig;
  const msalInstance = new msal.PublicClientApplication({
    auth: {
      clientId: config.clientId,
      authority: `https://login.microsoftonline.com/${config.tenantId}`,
      redirectUri: config.redirectUri || window.location.origin,
    },
  });

  const loginResponse = await msalInstance.loginPopup({
    scopes: ["User.Read", "Sites.Read.All"],
  });

  const tokenResponse = await msalInstance.acquireTokenSilent({
    scopes: ["Sites.Read.All"],
    account: loginResponse.account,
  });

  const tableEndpoint = `https://graph.microsoft.com/v1.0/sites/${config.siteId}/drive/root:/${config.excelPath}:/workbook/tables/${config.tableName}/rows`;
  const response = await fetch(tableEndpoint, {
    headers: {
      Authorization: `Bearer ${tokenResponse.accessToken}`,
    },
  });

  if (!response.ok) {
    throw new Error("Unable to load SharePoint Excel");
  }

  const payload = await response.json();
  const rows = payload.value || [];
  const items = rows.map((row) => {
    const [
      applicant,
      location,
      days,
      t1,
      t2,
      t3,
      submitted_at,
      status,
    ] = row.values[0];
    return {
      applicant,
      location,
      days,
      t1,
      t2,
      t3,
      submitted_at,
      status,
    };
  });

  applyExcelRecords(items, `已從 SharePoint Excel 載入 ${items.length} 筆紀錄`);
};

const handleLoadExcel = async () => {
  try {
    await loadFromSharePointExcel();
  } catch (error) {
    showToast("SharePoint Excel 載入失敗，請重試");
  }
};

const bindEvents = () => {
  dom.form.addEventListener("submit", handleSubmit);
  dom.daysMinus.addEventListener("click", () => {
    const value = Math.max(Number(dom.days.value) - 1, 1);
    dom.days.value = String(value);
  });
  dom.daysPlus.addEventListener("click", () => {
    const value = Number(dom.days.value) + 1;
    dom.days.value = String(value);
  });
  dom.t1.addEventListener("change", (event) => {
    updateT2Options(event.target.value);
  });
  dom.t2.addEventListener("change", (event) => {
    updateT3Options(dom.t1.value, event.target.value);
  });
  dom.copyAllBtn.addEventListener("click", handleCopyAll);
  dom.loadExcelBtn.addEventListener("click", handleLoadExcel);
};

const init = () => {
  updateT1Options();
  updateT2Options("");
  loadRecords();
  updateSummary();
  renderRecords();
  bindEvents();
};

init();
