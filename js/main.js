/* Pessic website: download links, system detection, screen tabs, zoomed screenshots and the mobile menu. */

/**
 * The installers. When a release is published, fill in each `href` (a relative path such as
 * "downloads/Pessic-1.0.0.msi" or a full URL). Empty links show "Aviat disponible".
 * `label` is a key of i18n/<language>.json.
 */
const RELEASE = {
  version: "1.0.0",
  downloads: {
    windows: [{ label: "js.msi", href: "" }],
    mac: [
      { label: "js.dmgArm", href: "" },
      { label: "js.dmgIntel", href: "" },
    ],
    linux: [
      { label: "js.deb", href: "" },
      { label: "js.rpm", href: "" },
    ],
  },
};

/** Texts for this script, embedded in each page by tools/build.py from i18n/<language>.json. */
const STRINGS = (() => {
  try {
    return JSON.parse(document.getElementById("i18n-strings").textContent);
  } catch {
    return {};
  }
})();

/** The text for `key`, with {name} placeholders replaced from `values`. */
function t(key, values = {}) {
  let text = STRINGS[key] ?? key;
  for (const [name, value] of Object.entries(values)) text = text.replaceAll(`{${name}}`, value);
  return text;
}

const PLATFORM_NAMES = { windows: "Windows", mac: "macOS", linux: "Linux" };

/** "windows", "mac", "linux", or null on phones and unknown systems. */
function detectPlatform() {
  const ua = navigator.userAgent || "";
  const platform = (navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || "";
  if (/android|iphone|ipad|ipod/i.test(ua)) return null;
  if (/win/i.test(platform) || /windows/i.test(ua)) return "windows";
  if (/mac/i.test(platform) || /mac os x/i.test(ua)) return "mac";
  if (/linux|x11|cros/i.test(platform) || /linux/i.test(ua)) return "linux";
  return null;
}

function linkButton(item, primary) {
  const a = document.createElement("a");
  a.className = primary ? "button" : "button button-ghost";
  a.textContent = t(item.label);
  if (item.href) {
    a.href = item.href;
    a.setAttribute("download", "");
  } else {
    a.textContent = t("js.soon");
    a.setAttribute("aria-disabled", "true");
    a.setAttribute("role", "link");
    a.addEventListener("click", (e) => e.preventDefault());
  }
  return a;
}

function setUpDownloads() {
  const current = detectPlatform();
  const anyPublished = Object.values(RELEASE.downloads).some((list) => list.some((d) => d.href));

  document.querySelectorAll("[data-platform]").forEach((card) => {
    const key = card.dataset.platform;
    const slot = card.querySelector("[data-links]");
    const links = RELEASE.downloads[key] || [];
    const seen = new Set();
    links.forEach((item, i) => {
      if (!item.href && seen.has("soon")) return; // a single "Aviat disponible" per card
      if (!item.href) seen.add("soon");
      slot.appendChild(linkButton(item, i === 0));
    });
    if (key === current) {
      card.classList.add("is-current");
      const badge = document.createElement("span");
      badge.className = "platform-badge";
      badge.textContent = t("js.yourSystem");
      card.appendChild(badge);
    }
  });

  const status = document.querySelector('[data-download="status"]');
  if (status) {
    status.textContent = anyPublished
      ? t("js.statusPublished", { version: RELEASE.version })
      : t("js.statusSoon");
  }

  // the hero button downloads directly for the visitor's system when that installer exists
  const hero = document.querySelector('[data-download="primary"]');
  if (hero && current) {
    const first = (RELEASE.downloads[current] || [])[0];
    if (first && first.href) {
      hero.href = first.href;
      hero.setAttribute("download", "");
      hero.textContent = t("js.downloadFor", { system: PLATFORM_NAMES[current] });
      const note = document.querySelector('[data-download="note"]');
      if (note) note.innerHTML = t("js.heroNote", { version: RELEASE.version });
    }
  }
}

/* ---------------------------------------------------------------- tabs (WAI-ARIA tabs pattern) */
function setUpTabs() {
  document.querySelectorAll("[data-tabs]").forEach((root) => {
    const tabs = Array.from(root.querySelectorAll('[role="tab"]'));
    const select = (tab, focus) => {
      tabs.forEach((t) => {
        const on = t === tab;
        t.setAttribute("aria-selected", String(on));
        t.tabIndex = on ? 0 : -1;
        document.getElementById(t.getAttribute("aria-controls")).hidden = !on;
      });
      if (focus) tab.focus();
      tab.scrollIntoView({ block: "nearest", inline: "nearest" });
    };
    tabs.forEach((tab, i) => {
      tab.addEventListener("click", () => select(tab, false));
      tab.addEventListener("keydown", (e) => {
        const moves = { ArrowRight: i + 1, ArrowLeft: i - 1, Home: 0, End: tabs.length - 1 };
        if (!(e.key in moves)) return;
        e.preventDefault();
        select(tabs[(moves[e.key] + tabs.length) % tabs.length], true);
      });
    });
  });
}

/* ---------------------------------------------------------------- zoomed screenshots */
function setUpLightbox() {
  const dialog = document.querySelector(".lightbox");
  if (!dialog || typeof dialog.showModal !== "function") return;
  const big = dialog.querySelector("img");
  document.querySelectorAll("[data-zoom]").forEach((button) => {
    button.addEventListener("click", () => {
      const img = button.querySelector("img");
      big.src = img.currentSrc || img.src;
      big.alt = img.alt;
      dialog.showModal();
    });
  });
  dialog.querySelector(".lightbox-close").addEventListener("click", () => dialog.close());
  dialog.addEventListener("click", (e) => { if (e.target === dialog) dialog.close(); });
}

/* ---------------------------------------------------------------- mobile menu */
function setUpMenu() {
  const toggle = document.querySelector(".menu-toggle");
  const menu = document.getElementById("menu");
  if (!toggle || !menu) return;
  const set = (open) => {
    menu.classList.toggle("open", open);
    toggle.setAttribute("aria-expanded", String(open));
  };
  toggle.addEventListener("click", () => set(!menu.classList.contains("open")));
  menu.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => set(false)));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") set(false); });
}

document.addEventListener("DOMContentLoaded", () => {
  setUpDownloads();
  setUpTabs();
  setUpLightbox();
  setUpMenu();
  document.querySelectorAll("[data-year]").forEach((el) => { el.textContent = new Date().getFullYear(); });
});
