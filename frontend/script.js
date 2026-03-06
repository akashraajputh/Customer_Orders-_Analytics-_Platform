const API_BASE = "https://customer-orders-analytics-platform.onrender.com/";

let revenueData = [];
let customersData = [];

const revenueStatus = document.getElementById("revenueStatus");
const customersStatus = document.getElementById("customersStatus");
const categoryStatus = document.getElementById("categoryStatus");
const regionsStatus = document.getElementById("regionsStatus");

let revenueChart;
let categoryChart;

function setStatus(el, message, isError = false) {
  if (!el) return;
  el.textContent = message;
  el.style.color = isError ? "#fca5a5" : "#9ca3af";
}

async function fetchJson(path, statusEl) {
  setStatus(statusEl, "Loading...");
  try {
    const res = await fetch(`${API_BASE}${path}`);
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    const data = await res.json();
    setStatus(statusEl, "");
    return data;
  } catch (err) {
    setStatus(statusEl, `Failed to load data: ${err.message}`, true);
    return [];
  }
}

function renderRevenueChart(data) {
  const ctx = document.getElementById("revenueChart").getContext("2d");
  const labels = data.map((d) => d.order_year_month);
  const values = data.map((d) => d.total_revenue);

  if (revenueChart) {
    revenueChart.destroy();
  }

  revenueChart = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: [
        {
          label: "Total Revenue",
          data: values,
          borderColor: "#60a5fa",
          backgroundColor: "rgba(37, 99, 235, 0.3)",
          fill: true,
          tension: 0.3,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: "#e5e7eb",
          },
        },
      },
      scales: {
        x: {
          ticks: { color: "#9ca3af" },
          grid: { color: "#1f2937" },
        },
        y: {
          ticks: { color: "#9ca3af" },
          grid: { color: "#1f2937" },
        },
      },
    },
  });
}

function filterRevenueByMonth(startMonth, endMonth) {
  if (!startMonth && !endMonth) {
    return revenueData;
  }
  return revenueData.filter((d) => {
    const m = d.order_year_month;
    if (startMonth && m < startMonth) return false;
    if (endMonth && m > endMonth) return false;
    return true;
  });
}

function renderCustomersTable(data) {
  const tbody = document.querySelector("#customersTable tbody");
  tbody.innerHTML = "";
  data.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.name ?? ""}</td>
      <td>${row.region ?? ""}</td>
      <td>${Number(row.total_spend).toFixed(2)}</td>
      <td>${row.churned ? "Yes" : "No"}</td>
    `;
    tbody.appendChild(tr);
  });
}

function renderCategoryChart(data) {
  const ctx = document.getElementById("categoryChart").getContext("2d");
  const labels = data.map((d) => d.category);
  const values = data.map((d) => d.total_revenue);

  if (categoryChart) {
    categoryChart.destroy();
  }

  categoryChart = new Chart(ctx, {
    type: "bar",
    data: {
      labels,
      datasets: [
        {
          label: "Revenue",
          data: values,
          backgroundColor: ["#34d399", "#60a5fa", "#fbbf24", "#f97316", "#a855f7"],
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: "#e5e7eb",
          },
        },
      },
      scales: {
        x: {
          ticks: { color: "#9ca3af" },
          grid: { color: "#1f2937" },
        },
        y: {
          ticks: { color: "#9ca3af" },
          grid: { color: "#1f2937" },
        },
      },
    },
  });
}

function renderRegionsTable(data) {
  const tbody = document.querySelector("#regionsTable tbody");
  tbody.innerHTML = "";
  data.forEach((row) => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${row.region ?? ""}</td>
      <td>${row.num_customers ?? 0}</td>
      <td>${row.num_orders ?? 0}</td>
      <td>${Number(row.total_revenue ?? 0).toFixed(2)}</td>
      <td>${Number(row.avg_revenue_per_customer ?? 0).toFixed(2)}</td>
    `;
    tbody.appendChild(tr);
  });
}

function attachTopCustomerInteractions() {
  const searchInput = document.getElementById("customerSearch");
  searchInput.addEventListener("input", () => {
    const term = searchInput.value.toLowerCase();
    const filtered = customersData.filter(
      (c) =>
        (c.name && c.name.toLowerCase().includes(term)) ||
        (c.region && c.region.toLowerCase().includes(term))
    );
    renderCustomersTable(filtered);
  });

  const headers = document.querySelectorAll("#customersTable th[data-sort]");
  let currentSort = { key: null, asc: true };

  headers.forEach((th) => {
    th.addEventListener("click", () => {
      const key = th.getAttribute("data-sort");
      if (currentSort.key === key) {
        currentSort.asc = !currentSort.asc;
      } else {
        currentSort.key = key;
        currentSort.asc = true;
      }
      const sorted = [...customersData].sort((a, b) => {
        const va = a[key];
        const vb = b[key];
        if (typeof va === "number" && typeof vb === "number") {
          return currentSort.asc ? va - vb : vb - va;
        }
        return currentSort.asc
          ? String(va).localeCompare(String(vb))
          : String(vb).localeCompare(String(va));
      });
      renderCustomersTable(sorted);
    });
  });
}

function attachRevenueFilter() {
  const btn = document.getElementById("applyDateFilter");
  const startInput = document.getElementById("startMonth");
  const endInput = document.getElementById("endMonth");
  btn.addEventListener("click", () => {
    const filtered = filterRevenueByMonth(startInput.value, endInput.value);
    renderRevenueChart(filtered);
  });
}

async function init() {
  revenueData = await fetchJson("/api/revenue", revenueStatus);
  customersData = await fetchJson("/api/top-customers", customersStatus);
  const categoryData = await fetchJson("/api/categories", categoryStatus);
  const regionsData = await fetchJson("/api/regions", regionsStatus);

  renderRevenueChart(revenueData);
  renderCustomersTable(customersData);
  renderCategoryChart(categoryData);
  renderRegionsTable(regionsData);

  attachTopCustomerInteractions();
  attachRevenueFilter();
}

document.addEventListener("DOMContentLoaded", init);

