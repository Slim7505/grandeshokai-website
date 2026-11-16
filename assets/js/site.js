(function () {
  "use strict";
  var doc = document.documentElement;
  doc.classList.add("js");

  // Sticky header shadow
  var header = document.querySelector("[data-header]");
  function onScroll() { if (header) header.classList.toggle("is-scrolled", window.scrollY > 8); }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  // Mobile menu
  var btn = document.querySelector("[data-menu]");
  var nav = document.querySelector("[data-nav]");
  function setMenu(open) {
    if (!btn || !nav) return;
    btn.setAttribute("aria-expanded", String(open));
    nav.classList.toggle("is-open", open);
  }
  if (btn && nav) {
    btn.addEventListener("click", function () { setMenu(btn.getAttribute("aria-expanded") !== "true"); });
    nav.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") setMenu(false); });
    window.matchMedia("(min-width: 981px)").addEventListener("change", function () { setMenu(false); });
  }

  // Reveal on scroll
  var items = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.06 });
    items.forEach(function (el) { io.observe(el); });
  } else {
    items.forEach(function (el) { el.classList.add("is-in"); });
  }

  // Products: highlight the category in view
  var jumpLinks = document.querySelectorAll(".jump a");
  if (jumpLinks.length && "IntersectionObserver" in window) {
    var map = {};
    jumpLinks.forEach(function (a) { map[a.getAttribute("href").slice(1)] = a; });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting && map[en.target.id]) {
          jumpLinks.forEach(function (a) { a.classList.remove("is-active"); });
          map[en.target.id].classList.add("is-active");
          var a = map[en.target.id], bar = a.closest(".jump-inner");
          if (bar) bar.scrollTo({ left: a.offsetLeft - 80, behavior: "smooth" });
        }
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    Object.keys(map).forEach(function (id) { var s = document.getElementById(id); if (s) spy.observe(s); });
  }

  // Contact: compose an email (no data leaves the browser except via the visitor's own mail app)
  var form = document.querySelector("form[data-mailto]");
  if (form) {
    var q = new URLSearchParams(location.search).get("topic");
    if (q !== null) {
      var r = form.querySelector('input[name="topic"][data-i="' + q + '"]');
      if (r) r.checked = true;
    }
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      var f = form.elements, ok = true;
      ["name", "email", "message"].forEach(function (n) {
        var el = f[n], bad = !el.value.trim() || (n === "email" && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(el.value.trim()));
        el.setAttribute("aria-invalid", bad ? "true" : "false");
        if (bad && ok) { el.focus(); ok = false; }
      });
      form.querySelector(".form-error").hidden = ok;
      if (!ok) return;
      var topic = (form.querySelector('input[name="topic"]:checked') || {}).value || "";
      var lines = [
        f.l_topic.value + ": " + topic,
        f.l_name.value + ": " + f.name.value.trim(),
        f.company.value.trim() ? f.l_company.value + ": " + f.company.value.trim() : "",
        f.l_email.value + ": " + f.email.value.trim(),
        f.phone.value.trim() ? f.l_phone.value + ": " + f.phone.value.trim() : "",
        f.product && f.product.value.trim() ? f.l_product.value + ": " + f.product.value.trim() : "",
        "",
        f.message.value.trim()
      ].filter(function (l, i) { return l !== "" || i === 6; });
      var subject = form.dataset.subject + " — " + topic + " / " + f.name.value.trim();
      location.href = "mailto:" + form.dataset.mailto + "?subject=" + encodeURIComponent(subject) + "&body=" + encodeURIComponent(lines.join("\n"));
    });
  }
})();
