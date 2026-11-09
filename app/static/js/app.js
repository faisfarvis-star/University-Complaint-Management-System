/* CampusFlow – shell behaviour. Progressive enhancement: pages work without it. */
(function () {
  "use strict";
  var root = document.documentElement, body = document.body;
  var store = {
    get: function (k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set: function (k, v) { try { localStorage.setItem(k, v); } catch (e) { /* private mode */ } }
  };
  var mqMobile = window.matchMedia("(max-width: 767.98px)");
  var mqDesktop = window.matchMedia("(min-width: 1024px)");

  /* ── Theme (initial value is applied by an inline script in <head>) ── */
  function applyTheme(t, persist) {
    root.setAttribute("data-theme", t);
    root.setAttribute("data-bs-theme", t);
    if (persist) store.set("campusflow-theme", t);
    document.querySelectorAll("[data-theme-toggle]").forEach(function (b) {
      b.setAttribute("aria-pressed", String(t === "dark"));
      b.setAttribute("aria-label", t === "dark" ? "Switch to light mode" : "Switch to dark mode");
    });
    document.dispatchEvent(new CustomEvent("cf:theme", { detail: t }));
  }
  window.CampusFlow = { theme: function () { return root.getAttribute("data-theme") || "light"; } };
  applyTheme(window.CampusFlow.theme(), false);

  /* ── Sidebar: collapsed (desktop), compact (tablet, CSS), off-canvas (mobile) ── */
  var sidebar = document.getElementById("sidebar");
  var lastToggle = null;
  function syncSidebarInert() {
    if (!sidebar) return;
    var hidden = mqMobile.matches && !body.classList.contains("sidebar-open");
    if (hidden) sidebar.setAttribute("inert", ""); else sidebar.removeAttribute("inert");
  }
  function setOpen(open) {
    body.classList.toggle("sidebar-open", open);
    document.querySelectorAll("[data-sidebar-toggle]").forEach(function (b) { b.setAttribute("aria-expanded", String(open)); });
    syncSidebarInert();
    if (open && sidebar) { var first = sidebar.querySelector("a,button"); if (first) first.focus(); }
    if (!open && lastToggle) { lastToggle.focus(); lastToggle = null; }
  }
  function setCollapsed(c, persist) {
    body.classList.toggle("sidebar-collapsed", c);
    if (persist) store.set("campusflow-sidebar", c ? "collapsed" : "expanded");
    document.querySelectorAll("[data-sidebar-collapse]").forEach(function (b) { b.setAttribute("aria-expanded", String(!c)); });
  }
  if (store.get("campusflow-sidebar") === "collapsed" && mqDesktop.matches) setCollapsed(true, false);
  syncSidebarInert();
  (mqMobile.addEventListener ? mqMobile.addEventListener.bind(mqMobile, "change") : mqMobile.addListener.bind(mqMobile))(function () {
    body.classList.remove("sidebar-open"); syncSidebarInert();
  });

  /* ── Menus (profile dropdown) ── */
  function closeMenus(except) {
    document.querySelectorAll("[data-menu].open").forEach(function (m) {
      if (m === except) return;
      m.classList.remove("open");
      var b = m.querySelector("[data-menu-btn]"); if (b) b.setAttribute("aria-expanded", "false");
    });
  }

  /* ── Confirmation dialog (native <dialog>; falls back to window.confirm) ── */
  var dialog;
  function askConfirm(message, okLabel, onOk) {
    if (typeof HTMLDialogElement === "undefined") { if (window.confirm(message)) onOk(); return; }
    if (!dialog) {
      dialog = document.createElement("dialog");
      dialog.className = "cf-dialog";
      dialog.setAttribute("aria-labelledby", "cf-dlg-title");
      dialog.innerHTML = '<h2 id="cf-dlg-title">Please confirm</h2><p class="mb-0" id="cf-dlg-msg"></p>' +
        '<div class="dialog-actions"><button type="button" class="btn btn-soft" data-dlg="cancel">Cancel</button>' +
        '<button type="button" class="btn btn-primary" data-dlg="ok"></button></div>';
      document.body.appendChild(dialog);
      dialog.addEventListener("click", function (e) {
        if (e.target === dialog || (e.target.dataset && e.target.dataset.dlg === "cancel")) dialog.close("cancel");
        else if (e.target.dataset && e.target.dataset.dlg === "ok") dialog.close("ok");
      });
    }
    dialog.querySelector("#cf-dlg-msg").textContent = message;
    dialog.querySelector('[data-dlg="ok"]').textContent = okLabel || "Confirm";
    dialog.onclose = function () { if (dialog.returnValue === "ok") onOk(); dialog.returnValue = ""; };
    dialog.showModal();
    dialog.querySelector('[data-dlg="cancel"]').focus();
  }

  /* ── Delegated clicks ── */
  document.addEventListener("click", function (e) {
    var t = e.target;
    var toggle = t.closest("[data-sidebar-toggle]");
    if (toggle) {
      if (mqMobile.matches) { lastToggle = toggle; setOpen(!body.classList.contains("sidebar-open")); }
      else setCollapsed(!body.classList.contains("sidebar-collapsed"), true);
      return;
    }
    if (t.closest("[data-sidebar-collapse]")) { setCollapsed(!body.classList.contains("sidebar-collapsed"), true); return; }
    if (t.closest("[data-sidebar-close]")) { setOpen(false); return; }
    if (t.closest("[data-theme-toggle]")) { applyTheme(window.CampusFlow.theme() === "dark" ? "light" : "dark", true); return; }

    var mb = t.closest("[data-menu-btn]");
    if (mb) {
      var menu = mb.closest("[data-menu]"); closeMenus(menu);
      var open = menu.classList.toggle("open"); mb.setAttribute("aria-expanded", String(open));
      return;
    }
    if (!t.closest("[data-menu]")) closeMenus();

    var pw = t.closest("[data-pw-toggle]");
    if (pw) {
      var input = document.getElementById(pw.dataset.pwToggle);
      if (input) {
        var show = input.type === "password"; input.type = show ? "text" : "password";
        pw.setAttribute("aria-pressed", String(show));
        pw.setAttribute("aria-label", show ? "Hide password" : "Show password");
        var ic = pw.querySelector("[data-lucide],svg");
        if (ic && window.lucide) { pw.innerHTML = '<i data-lucide="' + (show ? "eye-off" : "eye") + '" aria-hidden="true"></i>'; window.lucide.createIcons(); }
      }
      return;
    }
    var tc = t.closest(".toast-n button");
    if (tc) { dismissToast(tc.closest(".toast-n")); return; }

    var c = t.closest("[data-confirm]");
    if (c && !c.dataset.confirmed) {
      e.preventDefault();
      var form = c.closest("form");
      askConfirm(c.dataset.confirm, c.dataset.confirmLabel, function () {
        if (form) { c.dataset.confirmed = "1"; if (form.requestSubmit) form.requestSubmit(c); else form.submit(); }
        else if (c.href) window.location.href = c.href;
      });
    }
  });
  document.addEventListener("keydown", function (e) {
    if (e.key !== "Escape") return;
    if (body.classList.contains("sidebar-open")) setOpen(false);
    var openMenu = document.querySelector("[data-menu].open");
    if (openMenu) { closeMenus(); var b = openMenu.querySelector("[data-menu-btn]"); if (b) b.focus(); }
  });

  /* ── Toasts (server flash messages are rendered into .toast-region) ── */
  function dismissToast(el) {
    if (!el) return; el.classList.add("leaving"); setTimeout(function () { el.remove(); }, 260);
  }
  document.querySelectorAll(".toast-n").forEach(function (el) {
    if (!el.classList.contains("danger")) setTimeout(function () { dismissToast(el); }, 6500);
  });

  /* ── Submit feedback: spinner on the submit button (never disables the form) ── */
  document.addEventListener("submit", function (e) {
    var f = e.target; if (e.defaultPrevented || f.dataset.noLoading !== undefined) return;
    var b = e.submitter || f.querySelector('button[type="submit"]');
    if (!b || b.dataset.confirm && !b.dataset.confirmed) return;
    if (f.dataset.submitting) { e.preventDefault(); return; }
    f.dataset.submitting = "1"; b.classList.add("is-loading"); b.setAttribute("aria-busy", "true");
    setTimeout(function () { delete f.dataset.submitting; b.classList.remove("is-loading"); b.removeAttribute("aria-busy"); }, 8000);
  });

  /* ── File inputs: show chosen file names ── */
  document.querySelectorAll('input[type="file"]').forEach(function (inp) {
    var list = document.createElement("ul"); list.className = "file-list"; list.setAttribute("aria-live", "polite");
    inp.insertAdjacentElement("afterend", list);
    inp.addEventListener("change", function () {
      list.innerHTML = "";
      Array.prototype.forEach.call(inp.files, function (f) {
        var li = document.createElement("li"); li.textContent = f.name + " (" + Math.max(1, Math.round(f.size / 1024)) + " KB)"; list.appendChild(li);
      });
    });
  });

  /* ── Client-side paging for long tables: <div data-paginate="10"> wrapping a table ── */
  document.querySelectorAll("[data-paginate]").forEach(function (box) {
    var size = parseInt(box.dataset.paginate, 10) || 10;
    var rows = Array.prototype.slice.call(box.querySelectorAll("tbody tr[data-row]"));
    if (rows.length <= size) return;
    var pages = Math.ceil(rows.length / size), cur = 1;
    var nav = document.createElement("nav"); nav.className = "pager"; nav.setAttribute("aria-label", "Table pages");
    box.insertAdjacentElement("afterend", nav);
    function render() {
      rows.forEach(function (r, i) { r.hidden = !(i >= (cur - 1) * size && i < cur * size); });
      var from = (cur - 1) * size + 1, to = Math.min(cur * size, rows.length);
      nav.innerHTML = '<span>Showing ' + from + '–' + to + ' of ' + rows.length + '</span><div class="pages">' +
        '<button type="button" data-p="' + (cur - 1) + '" aria-label="Previous page"' + (cur === 1 ? " disabled" : "") + '>‹</button>' +
        Array.apply(null, Array(pages)).map(function (_, i) {
          return '<button type="button" data-p="' + (i + 1) + '"' + (i + 1 === cur ? ' aria-current="page"' : "") + ' aria-label="Page ' + (i + 1) + '">' + (i + 1) + "</button>";
        }).join("") +
        '<button type="button" data-p="' + (cur + 1) + '" aria-label="Next page"' + (cur === pages ? " disabled" : "") + '>›</button></div>';
    }
    nav.addEventListener("click", function (e) {
      var b = e.target.closest("button[data-p]"); if (!b || b.disabled) return;
      cur = parseInt(b.dataset.p, 10); render();
      var again = nav.querySelector('[aria-current="page"]'); if (again) again.focus();
    });
    render();
  });

  if (window.lucide) window.lucide.createIcons();
})();
