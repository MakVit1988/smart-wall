// Ориентировочный калькулятор для макетов: площадь × цена «от» из каталога.
// Это не КП: точный расчёт делает менеджер после замера.
(function () {
  'use strict';
  function fmt(n) {
    return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ');
  }
  document.querySelectorAll('[data-calc]').forEach(function (root) {
    var sys = root.querySelector('[data-sys]');
    var w = root.querySelector('[data-w]');
    var h = root.querySelector('[data-h]');
    var wOut = root.querySelector('[data-w-out]');
    var hOut = root.querySelector('[data-h-out]');
    var area = root.querySelector('[data-area]');
    var out = root.querySelector('[data-out]');
    var price = root.querySelector('[data-price-out]');
    function update() {
      var p = Number(sys.options[sys.selectedIndex].getAttribute('data-price'));
      var W = Number(w.value), H = Number(h.value);
      var S = W * H;
      wOut.textContent = W.toFixed(1).replace('.', ',') + ' м';
      hOut.textContent = H.toFixed(1).replace('.', ',') + ' м';
      area.textContent = S.toFixed(1).replace('.', ',') + ' м²';
      price.textContent = fmt(p) + ' ₽/м²';
      out.textContent = 'от ' + fmt(S * p) + ' ₽';
    }
    [sys, w, h].forEach(function (el) { el.addEventListener('input', update); });
    update();
  });
})();
