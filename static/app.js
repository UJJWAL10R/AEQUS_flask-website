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

    createChart(
      "deployStatusChart",
      "doughnut",
      Object.keys(analytics.deploy_status || {}),
      Object.values(analytics.deploy_status || {}),
      {
        backgroundColor: [palette.success, palette.warning, palette.danger, palette.accent],
      }
    );

    createChart(
      "reportCoverageChart",
      "pie",
      Object.keys(analytics.report_coverage || {}),
      Object.values(analytics.report_coverage || {}),
      {
        backgroundColor: [palette.accent, palette.danger],
      }
    );

    createChart(
      "reportVolumeChart",
      "bar",
      Object.keys(analytics.report_volume || {}),
      Object.values(analytics.report_volume || {}),
      {
        label: "Reports assigned",
        backgroundColor: palette.success,
        borderColor: palette.success,
      }
    );

    createChart(
      "contentNameChart",
      "bar",
      Object.keys(analytics.content_names || {}),
      Object.values(analytics.content_names || {}),
      {
        label: "Content count",
        backgroundColor: palette.warning,
        borderColor: palette.warning,
      }
    );
  }

  function initLiveBackground() {
    const canvas = document.getElementById("liveBackgroundCanvas");
    if (!canvas) return;

    const context = canvas.getContext("2d");
    if (!context) return;

    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const points = [];
    let width = 0;
    let height = 0;
    let animationId = null;

    function livePalette(palette) {
      return {
        primary: palette.accent,
        secondary: "#7aa2ff",
        tertiary: "#4f7cff",
        line: normalizeColor(palette.accent, 0.08),
      };
    }

    function buildPoints() {
      points.length = 0;
      const targetCount = prefersReducedMotion
        ? 0
        : Math.max(10, Math.min(22, Math.floor((width * height) / 90000)));

      for (let index = 0; index < targetCount; index += 1) {
        points.push({
          x: Math.random() * width,
          y: Math.random() * height,
          vx: (Math.random() - 0.5) * 0.12,
          vy: (Math.random() - 0.5) * 0.12,
          radius: 1 + Math.random() * 2.1,
          pulse: Math.random() * Math.PI * 2,
        });
      }
    }

    function resize() {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(height * dpr);
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      context.setTransform(dpr, 0, 0, dpr, 0, 0);
      buildPoints();
    }

    function drawConnections(colors) {
      for (let i = 0; i < points.length; i += 1) {
        for (let j = i + 1; j < points.length; j += 1) {
          const a = points[i];
          const b = points[j];
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          if (distance > 160) continue;
          const alpha = (1 - distance / 160) * 0.08;
          context.strokeStyle = normalizeColor(colors.primary, alpha);
          context.lineWidth = 1;
          context.beginPath();
          context.moveTo(a.x, a.y);
          context.lineTo(b.x, b.y);
          context.stroke();
        }
      }
    }

    function normalizeColor(color, alpha) {
      if (color.startsWith("rgba(")) {
        return color.replace(/rgba\(([^,]+),([^,]+),([^,]+),[^)]+\)/, `rgba($1,$2,$3,${alpha})`);
      }
      if (color.startsWith("rgb(")) {
        return color.replace("rgb(", "rgba(").replace(")", `, ${alpha})`);
      }
      return color;
    }

    function animate() {
      const palette = themePalette();
      const colors = livePalette(palette);
      context.clearRect(0, 0, width, height);

      const glowGradient = context.createLinearGradient(0, 0, width, height);
      glowGradient.addColorStop(0, normalizeColor(colors.primary, 0.08));
      glowGradient.addColorStop(0.5, normalizeColor(colors.secondary, 0.045));
      glowGradient.addColorStop(1, normalizeColor(colors.tertiary, 0.04));
      context.fillStyle = glowGradient;
      context.fillRect(0, 0, width, height);

      drawConnections(colors);

      points.forEach((point, index) => {
        point.x += point.vx;
        point.y += point.vy;
        point.pulse += 0.01 + index * 0.0002;

        if (point.x <= -20 || point.x >= width + 20) point.vx *= -1;
        if (point.y <= -20 || point.y >= height + 20) point.vy *= -1;

        const radius = point.radius + Math.sin(point.pulse) * 0.7;
        const halo = context.createRadialGradient(point.x, point.y, 0, point.x, point.y, radius * 8);
        halo.addColorStop(0, normalizeColor(index % 3 === 0 ? colors.primary : colors.secondary, 0.12));
        halo.addColorStop(1, "rgba(0, 0, 0, 0)");
        context.fillStyle = halo;
        context.beginPath();
        context.arc(point.x, point.y, radius * 8, 0, Math.PI * 2);
        context.fill();

        context.fillStyle = index % 2 === 0 ? colors.primary : colors.secondary;
        context.beginPath();
        context.arc(point.x, point.y, Math.max(1.2, radius), 0, Math.PI * 2);
        context.fill();
      });

      animationId = window.requestAnimationFrame(animate);
    }

    resize();
    if (!prefersReducedMotion) {
      animate();
    }

    window.addEventListener("resize", resize);
    window.addEventListener("beforeunload", () => {
      if (animationId) {
        window.cancelAnimationFrame(animationId);
      }
    });
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
      reports: document.getElementById("spotlightReports"),
    };

    function renderReports(record) {
      if (!refs.reports) return;
      const reports = Array.isArray(record.reports) ? record.reports : [];
      if (!reports.length) {
        refs.reports.innerHTML = `<p class="subtle-note">No report assigned to this TV yet.</p>`;
        return;
      }
      refs.reports.innerHTML = reports
        .map(
          (report) => `
            <a class="mini-report-link" href="/powerbi?tv=${record.id}&report=${report.id}">
              ${report.name}
              <small>${report.category}</small>
            </a>
          `
        )
        .join("");
    }

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
      renderReports(record);

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
  initLiveBackground();
})();
