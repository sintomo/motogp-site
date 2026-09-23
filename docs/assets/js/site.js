/* site.js ― 全ページ共通の小さな動き（絞り込みボタン・検索・現在メニューの表示位置） */
(function () {
  "use strict";
  /* 絞り込み：<div data-filter="対象ID"> のボタン → 対象内の [data-cat] を表示切替 */
  document.querySelectorAll("[data-filter]").forEach(function (group) {
    var target = document.getElementById(group.getAttribute("data-filter"));
    if (!target) return;
    function apply(v) {
      target.querySelectorAll("[data-cat]").forEach(function (el) {
        el.hidden = v !== "" && el.getAttribute("data-cat") !== v;
      });
    }
    group.querySelectorAll("button").forEach(function (b) {
      b.addEventListener("click", function () {
        group.querySelectorAll("button").forEach(function (x) { x.setAttribute("aria-pressed", "false"); });
        b.setAttribute("aria-pressed", "true");
        apply(b.getAttribute("data-value"));
      });
    });
    var cur = group.querySelector('[aria-pressed="true"]');
    if (cur) apply(cur.getAttribute("data-value"));
  });
  /* 検索：<input data-search="対象ID"> → 対象内の [data-text] を文字で絞り込み */
  document.querySelectorAll("[data-search]").forEach(function (input) {
    var target = document.getElementById(input.getAttribute("data-search"));
    if (!target) return;
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      target.querySelectorAll("[data-text]").forEach(function (el) {
        el.hidden = q !== "" && el.getAttribute("data-text").toLowerCase().indexOf(q) < 0;
      });
    });
  });
  /* 現在のメニューを横スクロール内で見える位置へ */
  var cur = document.querySelector('nav.tabs [aria-current="page"]');
  if (cur && cur.scrollIntoView) { try { cur.scrollIntoView({ block: "nearest", inline: "center" }); } catch (e) {} }
})();
