(function () {
  const root = document.documentElement;
  const themeButtons = document.querySelectorAll("[data-theme-toggle]");
  let charts = [];
  const storedTheme = localStorage.getItem("tv-dashboard-theme");
  const preferredTheme =
    storedTheme ||
    (window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");

  function themePalette() {
    const styles = getComputedStyle(root);
    return {
      text: styles.getPropertyValue("--text").trim(),
      muted: styles.getPropertyValue("--muted").trim(),
      line: styles.getPropertyValue("--line").trim(),
      accent: styles.getPropertyValue("--accent").trim(),
      accent2: styles.getPropertyValue("--accent-2").trim(),
      success: styles.getPropertyValue("--success").trim(),
      danger: styles.getPropertyValue("--danger").trim(),
      warning: styles.getPropertyValue("--warning").trim(),
      blueSoft: styles.getPropertyValue("--blue-soft").trim(),
      greenSoft: styles.getPropertyValue("--green-soft").trim(),
      redSoft: styles.getPropertyValue("--red-soft").trim(),
      goldSoft: styles.getPropertyValue("--gold-soft").trim(),
    };
  }

  function chartColors() {
    const palette = themePalette();
    return [
      palette.accent,
      palette.accent2,
      palette.warning,
      palette.danger,
      "#8b5cf6",
      "#f97316",
    ];
  }

  function createChart(id, type, labels, values, options) {
    const element = document.getElementById(id);
    if (!element || !window.Chart) return;

    const palette = themePalette();
    const instance = new Chart(element, {
      type,
      data: {
        labels,
        datasets: [
          {
            data: values,
            label: options.label || "",
            backgroundColor: options.backgroundColor || chartColors(),
            borderColor: options.borderColor || palette.line,
            borderWidth: options.borderWidth || 1,
            tension: 0.36,
            fill: options.fill || false,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: {
          duration: 900,
          easing: "easeOutQuart",
        },
        plugins: {
          legend: {
            position: options.legendPosition || "bottom",
            labels: {
              color: palette.text,
              usePointStyle: true,
              padding: 18,
            },
          },
          tooltip: {
            backgroundColor: "rgba(15, 23, 42, 0.9)",
            titleColor: "#fff",
            bodyColor: "#fff",
            padding: 12,
            displayColors: true,
          },
        },
        scales:
          type === "bar"
            ? {
                x: {
                  ticks: { color: palette.muted },
                  grid: { display: false },
                },
                y: {
                  beginAtZero: true,
                  ticks: { color: palette.muted, precision: 0 },
                  grid: { color: palette.line },
                },
              }
            : undefined,
      },
    });

    charts.push(instance);
  }

  function renderCharts() {
    charts.forEach((chart) => chart.destroy());
    charts = [];

    const dataNode = document.getElementById("analytics-data");
    if (!dataNode) return;

    const analytics = JSON.parse(dataNode.textContent);
    const palette = themePalette();

    createChart(
      "statusChart",
      "doughnut",
      Object.keys(analytics.status),
      Object.values(analytics.status),
      {
        backgroundColor: [palette.success, palette.danger, palette.warning],
      }
    );

    createChart(
      "connectivityChart",
      "pie",
      Object.keys(analytics.connectivity),
      Object.values(analytics.connectivity),
      {
        backgroundColor: [palette.accent, palette.danger, palette.warning],
      }
    );

    createChart(
      "contentTypeChart",
      "doughnut",
      Object.keys(analytics.content_types),
      Object.values(analytics.content_types),
      {
        backgroundColor: chartColors(),
      }
    );

    createChart(
      "locationChart",
      "bar",
      Object.keys(analytics.locations),
      Object.values(analytics.locations),
      {
        label: "TVs by location",
        backgroundColor: palette.accent,
        borderColor: palette.accent,
      }
    );

    createChart(
      "layoutChart",
      "bar",
      Object.keys(analytics.layout_types),
      Object.values(analytics.layout_types),
      {
        label: "Layout composition",
        backgroundColor: palette.accent2,
        borderColor: palette.accent2,
      }
    );
  }

  function createStatusChip(label, variant, icon) {
    return `
      <span class="status-chip ${variant}">
        <span class="status-dot"></span>
        <i class="bi ${icon}"></i>
        ${label}
      </span>
    `;
  }

  function wireSpotlight() {
    const dataNode = document.getElementById("spotlight-data");
    const triggers = document.querySelectorAll("[data-spotlight-trigger]");
    if (!dataNode || !triggers.length) return;

    const records = JSON.parse(dataNode.textContent);
    const byId = new Map(records.map((record) => [String(record.id), record]));
    const refs = {
      screen: document.getElementById("tvSpotlightScreen"),
      tvId: document.getElementById("spotlightTvId"),
      contentType: document.getElementById("spotlightContentType"),
      location: document.getElementById("spotlightLocation"),
      statusWrap: document.getElementById("spotlightStatusWrap"),
      contentName: document.getElementById("spotlightContentName"),
      template: document.getElementById("spotlightTemplate"),
      layout: document.getElementById("spotlightLayout"),
      deploy: document.getElementById("spotlightDeploy"),
      ping: document.getElementById("spotlightPing"),
      lastPing: document.getElementById("spotlightLastPing"),
      statusText: document.getElementById("spotlightStatusText"),
      lastOnline: document.getElementById("spotlightLastOnline"),
      deployDate: document.getElementById("spotlightDeployDate"),
      deployTime: document.getElementById("spotlightDeployTime"),
      remarks: document.getElementById("spotlightRemarks"),
    };

    function setActive(recordId) {
      const record = byId.get(String(recordId));
      if (!record) return;

      if (refs.screen) {
        refs.screen.dataset.status = record.tv_status;
      }
      refs.tvId.textContent = record.tv_id;
      refs.contentType.textContent = record.content_type;
      refs.location.textContent = record.location;
      refs.statusWrap.innerHTML = createStatusChip(
        record.tv_status,
        record.tv_status.toLowerCase(),
        "bi-display"
      );
      refs.contentName.textContent = record.content_name;
      refs.template.textContent = record.template_type;
      refs.layout.textContent = record.layout_composition;
      refs.deploy.textContent = record.deployed_status;
      refs.ping.textContent = record.ping_status;
      refs.lastPing.textContent = record.last_ping_time;
      refs.statusText.textContent = record.tv_status;
      refs.lastOnline.textContent = `${record.last_online} last online state.`;
      refs.deployDate.textContent = record.deployed_date;
      refs.deployTime.textContent = `${record.deployed_time} deployment timestamp.`;
      refs.remarks.textContent = record.remarks;

      triggers.forEach((trigger) => {
        trigger.classList.toggle("active", trigger.dataset.recordId === String(recordId));
      });
    }

    triggers.forEach((trigger) => {
      trigger.addEventListener("click", () => setActive(trigger.dataset.recordId));
    });
  }

  function applyTheme(theme) {
    root.setAttribute("data-theme", theme);
    localStorage.setItem("tv-dashboard-theme", theme);
    requestAnimationFrame(renderCharts);
  }

  applyTheme(preferredTheme);

  themeButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const nextTheme = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
      applyTheme(nextTheme);
    });
  });

  const rows = document.querySelectorAll(".reveal-row");
  if ("IntersectionObserver" in window && rows.length) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.15 }
    );

    rows.forEach((row, index) => {
      row.style.animationDelay = `${index * 40}ms`;
      observer.observe(row);
    });
  } else {
    rows.forEach((row) => row.classList.add("is-visible"));
  }

  renderCharts();
  wireSpotlight();
})();
