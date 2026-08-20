/* ═══════════════════════════════════════════════════════════════════════
   UNIVENT — landing page chapter rail

   The only JavaScript the numbered sections need. Everything else on the
   page (headline masks, seams, the expanding Ruck panel, the drifting
   certificate strip) is CSS: .reveal from script.js, or a scroll-driven
   animation running off the main thread.

   This file does two things and no-ops everywhere the markup is absent:
     · marks the section you are currently reading in the right-hand rail,
     · flips the rail to its light palette over a dark chapter.
   ═══════════════════════════════════════════════════════════════════════ */

(function () {
  "use strict";

  var rail = document.getElementById("rail");
  if (!rail || !("IntersectionObserver" in window)) return;

  var sections = [].slice.call(document.querySelectorAll("[data-chapter]"));
  if (!sections.length) return;

  /* rail item, keyed by the id it points at */
  var items = {};
  [].forEach.call(rail.querySelectorAll(".rail-item"), function (a) {
    items[(a.getAttribute("href") || "").slice(1)] = a;
  });

  var current = null;

  var activate = function (section) {
    var item = items[section.id];
    if (!item || item === current) return;
    if (current) current.classList.remove("is-active");
    item.classList.add("is-active");
    current = item;
    rail.classList.toggle("on-dark", section.dataset.theme === "dark");
  };

  /* A section counts as "the one you're reading" while it crosses the middle
     band of the viewport. The band is deliberately thin, so the hand-over
     happens once per section rather than flickering between two. */
  var visible = [];

  var observer = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      var i = visible.indexOf(entry.target);
      if (entry.isIntersecting && i === -1) visible.push(entry.target);
      if (!entry.isIntersecting && i !== -1) visible.splice(i, 1);
    });

    if (!visible.length) return;   /* between two sections — hold the last one */

    /* the highest one in the band wins, so scrolling up hands back cleanly */
    var top = visible.reduce(function (best, el) {
      return el.getBoundingClientRect().top < best.getBoundingClientRect().top ? el : best;
    });
    activate(top);
  }, { rootMargin: "-45% 0px -45% 0px", threshold: 0 });

  sections.forEach(function (s) { observer.observe(s); });
})();
