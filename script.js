/* Univent site — header state, mobile nav, scroll reveal, product filter.
   Loaded by every page; each block no-ops where its markup is absent. */

(function () {
  "use strict";

  /* ── Header shadow on scroll ── */
  var header = document.getElementById("header");
  var onScroll = function () {
    header.classList.toggle("scrolled", window.scrollY > 10);
  };
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* ── Mobile nav ── */
  var burger = document.getElementById("burger");
  var nav = document.getElementById("nav");

  var setNav = function (open) {
    nav.classList.toggle("open", open);
    burger.setAttribute("aria-expanded", String(open));
  };

  burger.addEventListener("click", function () {
    setNav(burger.getAttribute("aria-expanded") !== "true");
  });

  nav.addEventListener("click", function (e) {
    if (e.target.tagName === "A") setNav(false);
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") setNav(false);
  });

  window.addEventListener("resize", function () {
    if (window.innerWidth > 900) setNav(false);
  });

  /* ── Scroll reveal ── */
  var items = Array.prototype.slice.call(document.querySelectorAll(".reveal"));

  var show = function (el) {
    el.classList.add("in");
  };

  if (!("IntersectionObserver" in window)) {
    items.forEach(show);
  } else {
    /* Stagger siblings inside a grid so cards cascade in */
    var counts = {};
    items.forEach(function (el) {
      var key = el.parentElement.className || "root";
      counts[key] = (counts[key] || 0) + 1;
      el.style.transitionDelay = Math.min(counts[key] - 1, 7) * 60 + "ms";
    });

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        show(entry.target);
        observer.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });

    items.forEach(function (el) { observer.observe(el); });

    /* Safety net: an element that has scrolled into view must never stay
       hidden, whatever the observer does. Cheap — the list only shrinks. */
    var pending = items;
    var sweep = function () {
      if (!pending.length) return;
      var vh = window.innerHeight;
      pending = pending.filter(function (el) {
        var r = el.getBoundingClientRect();
        if (r.top < vh * 0.95 && r.bottom > 0) { show(el); return false; }
        return true;
      });
    };
    window.addEventListener("scroll", sweep, { passive: true });
    window.addEventListener("resize", sweep);
    window.addEventListener("load", sweep);
    sweep();
  }

  /* ── Product category filter (products.html only) ── */
  var filters = Array.prototype.slice.call(document.querySelectorAll(".filter"));
  var grid = document.getElementById("product-grid");

  if (filters.length && grid) {
    var cards = grid.querySelectorAll(".product-card");
    var empty = document.getElementById("grid-empty");

    var applyFilter = function (want) {
      var shown = 0;

      filters.forEach(function (b) {
        var on = b.dataset.filter === want;
        b.classList.toggle("is-active", on);
        b.setAttribute("aria-selected", String(on));
      });

      cards.forEach(function (card) {
        var match = want === "all" || card.dataset.cat === want;
        card.hidden = !match;
        if (match) { shown++; show(card); }   /* may never have crossed the observer */
      });

      if (empty) empty.hidden = shown > 0;
    };

    filters.forEach(function (btn) {
      btn.addEventListener("click", function () {
        applyFilter(btn.dataset.filter);
        history.replaceState(null, "",
          btn.dataset.filter === "all" ? location.pathname
                                       : location.pathname + "?cat=" + btn.dataset.filter);
      });
    });

    /* Deep link: products.html?cat=smoke opens on that category. Links from the
       other pages point here, so an unknown slug must fall back to All. */
    var wanted = (location.search.match(/[?&]cat=([\w-]+)/) || [])[1];
    if (wanted && filters.some(function (b) { return b.dataset.filter === wanted; })) {
      applyFilter(wanted);
      /* land on the filter bar, not mid-grid — scroll-padding-top clears the header */
      (document.getElementById("products") || grid).scrollIntoView({ block: "start" });
    }
  }

  /* ── Scroll-expanding panel (fallback only) ──
     Browsers with animation-timeline: view() do this in CSS, off the main
     thread. This drives the same two properties for everyone else. */
  if (!(window.CSS && CSS.supports && CSS.supports("animation-timeline", "view()"))) {
    var panels = document.querySelectorAll("[data-expand]");

    var expand = function () {
      var vh = window.innerHeight;
      panels.forEach(function (panel) {
        var r = panel.getBoundingClientRect();
        /* 0 when the panel's top edge is one viewport down, 1 once it has
           travelled 55% of the viewport upward from there */
        var p = (vh - r.top) / (vh * 0.55);
        p = p < 0 ? 0 : p > 1 ? 1 : p;
        var eased = p * p * (3 - 2 * p);
        panel.style.setProperty("--panel-inset",
          "calc(clamp(16px, 4.5vw, 80px) * " + (1 - eased).toFixed(4) + ")");
        panel.style.setProperty("--panel-radius", (40 * (1 - eased)).toFixed(1) + "px");
      });
    };

    if (panels.length) {
      var queued = false;
      var onExpandScroll = function () {
        if (queued) return;
        queued = true;
        requestAnimationFrame(function () { expand(); queued = false; });
      };
      window.addEventListener("scroll", onExpandScroll, { passive: true });
      window.addEventListener("resize", onExpandScroll);
      expand();
    }
  }

  /* ── Quote form → WhatsApp (contact.html only) ──
     There is no back end. The form composes a plain-text message out of the
     fields and hands it to wa.me, which opens WhatsApp with the text already
     written; the enquiry is only actually sent when the person presses send
     there. The same body is kept on the mailto link as a fallback for anyone
     without WhatsApp. */
  var waForm = document.getElementById("wa-form");

  if (waForm) {
    var WA_NUMBER = "201006063909";           /* +20 100 606 3909, digits only */
    var MAIL_TO = "ehab@univent.com.eg";
    var status = document.getElementById("wa-status");
    var mailLink = document.getElementById("wa-email");

    var val = function (name) {
      var el = waForm.elements[name];
      return el && el.value ? el.value.trim() : "";
    };

    var buildMessage = function () {
      var lines = ["Quote request — Univent", ""];
      var add = function (label, value) { if (value) lines.push(label + ": " + value); };

      add("Name", val("name"));
      add("Company", val("company"));
      add("Contact", val("contact"));
      add("Application", val("application"));

      /* a number is meaningless without its unit, so they travel together */
      if (val("airflow")) add("Airflow", val("airflow") + " " + val("airflowUnit"));
      if (val("pressure")) add("Static pressure", val("pressure") + " " + val("pressureUnit"));

      add("Model", val("model"));
      add("Quantity", val("quantity"));

      if (val("message")) lines.push("", val("message"));
      lines.push("", "Sent from the Univent website");

      return lines.join("\n");
    };

    /* keep the email fallback carrying whatever has been typed so far */
    var syncMail = function () {
      if (!mailLink) return;
      mailLink.href = "mailto:" + MAIL_TO +
        "?subject=" + encodeURIComponent("Quote request — Univent") +
        "&body=" + encodeURIComponent(buildMessage());
    };
    waForm.addEventListener("input", syncMail);
    waForm.addEventListener("change", syncMail);
    syncMail();

    waForm.addEventListener("submit", function (e) {
      e.preventDefault();

      var name = waForm.elements.name;
      if (!name.value.trim()) {
        name.focus();
        waForm.classList.add("is-invalid");
        if (status) status.textContent = "Please add your name so we know who we're quoting for.";
        return;
      }
      waForm.classList.remove("is-invalid");

      var url = "https://wa.me/" + WA_NUMBER + "?text=" + encodeURIComponent(buildMessage());
      var win = window.open(url, "_blank", "noopener");

      /* popup blocked (or an in-app browser that refuses window.open) */
      if (!win) { window.location.href = url; return; }

      if (status) status.textContent = "Opening WhatsApp with your details — press send there to deliver it.";
    });
  }

  /* ── Footer year ── */
  document.getElementById("year").textContent = new Date().getFullYear();
})();
