(function () {
  'use strict';
  var $ = function (s, r) { return (r || document).querySelector(s); };
  var $$ = function (s, r) { return Array.prototype.slice.call((r || document).querySelectorAll(s)); };

  // мобильное меню
  var hdr = $('.hdr'), burger = $('.burger');
  if (burger) {
    burger.addEventListener('click', function () {
      var open = !hdr.classList.contains('open');
      hdr.classList.toggle('open', open);
      burger.setAttribute('aria-expanded', String(open));
      burger.setAttribute('aria-label', open ? 'Закрыть меню' : 'Открыть меню');
      document.body.style.overflow = open ? 'hidden' : '';
    });
  }

  // фильтры: .filters[data-target=".row"] > button[data-f]; элементы с data-tags="a b"
  $$('.filters').forEach(function (box) {
    var items = $$(box.getAttribute('data-target'));
    var count = $(box.getAttribute('data-count') || '#none');
    $$('button', box).forEach(function (btn) {
      btn.addEventListener('click', function () {
        var f = btn.getAttribute('data-f');
        $$('button', box).forEach(function (b) { b.classList.toggle('is-on', b === btn); });
        var n = 0;
        items.forEach(function (it) {
          var tags = (it.getAttribute('data-tags') || '').split(' ');
          var show = f === 'all' || tags.indexOf(f) !== -1;
          it.hidden = !show; if (show) n++;
        });
        if (count) count.textContent = n;
      });
    });
  });

  // галерея
  $$('.gal').forEach(function (g) {
    var main = $('.gal__main img', g);
    $$('.gal__thumbs button', g).forEach(function (b) {
      b.addEventListener('click', function () {
        main.src = b.getAttribute('data-src');
        $$('.gal__thumbs button', g).forEach(function (x) { x.classList.toggle('is-on', x === b); });
      });
    });
  });

  // калькулятор-ориентир: площадь × цена «от»
  function fmt(n) { return Math.round(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' '); }
  $$('[data-calc]').forEach(function (root) {
    var sys = $('[data-sys]', root), w = $('[data-w]', root), h = $('[data-h]', root);
    var wOut = $('[data-w-out]', root), hOut = $('[data-h-out]', root);
    var area = $('[data-area]', root), out = $('[data-out]', root), price = $('[data-price-out]', root);
    function update() {
      var p = Number(sys.options[sys.selectedIndex].getAttribute('data-price'));
      var W = Number(w.value), H = Number(h.value), S = W * H;
      wOut.textContent = W.toFixed(1).replace('.', ',') + ' м';
      hOut.textContent = H.toFixed(1).replace('.', ',') + ' м';
      area.textContent = S.toFixed(1).replace('.', ',') + ' м²';
      price.textContent = fmt(p) + ' ₽/м²';
      out.textContent = 'от ' + fmt(S * p) + ' ₽';
    }
    [sys, w, h].forEach(function (el) { el.addEventListener('input', update); });
    update();
  });

  function validPhone(v) { return String(v).replace(/\D/g, '').length >= 10; }

  // формы заявки (демо)
  $$('form[data-lead]').forEach(function (f) {
    var err = $('.err', f), done = $('.ok', f);
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var phone = f.elements.phone && f.elements.phone.value;
      if (!validPhone(phone)) { err.textContent = 'Укажите телефон, чтобы мы могли связаться'; err.hidden = false; return; }
      var c = $('input[type=checkbox]', f);
      if (c && !c.checked) { err.textContent = 'Нужно согласие на обработку персональных данных'; err.hidden = false; return; }
      err.hidden = true; done.hidden = false;
      $$('button[type=submit]', f).forEach(function (b) { b.disabled = true; });
    });
  });

  // квиз
  var quiz = $('#quiz');
  if (quiz) {
    var steps = $$('fieldset', quiz), cur = 0, total = steps.length;
    var bar = $('.quiz__bar span', quiz), label = $('.quiz__step', quiz), next = $('[data-next]', quiz), back = $('[data-back]', quiz), err = $('.err', quiz), done = $('.ok', quiz);
    var show = function (i) {
      cur = i;
      steps.forEach(function (s, k) { s.classList.toggle('is-on', k === i); });
      bar.style.width = ((i + 1) / total * 100) + '%';
      label.textContent = i === total - 1 ? 'Последний шаг' : 'Шаг ' + (i + 1) + ' из ' + (total - 1);
      back.hidden = i === 0; next.textContent = i === total - 1 ? 'Получить подбор' : 'Далее'; err.hidden = true;
    };
    next.addEventListener('click', function () {
      var s = steps[cur];
      if (cur < total - 1) {
        if (!$('input:checked', s)) { err.textContent = 'Выберите вариант, чтобы продолжить'; err.hidden = false; return; }
        show(cur + 1); return;
      }
      if (!validPhone($('input[type=tel]', s).value)) { err.textContent = 'Укажите телефон, чтобы мы могли связаться'; err.hidden = false; return; }
      if (!$('input[type=checkbox]', s).checked) { err.textContent = 'Нужно согласие на обработку персональных данных'; err.hidden = false; return; }
      err.hidden = true; next.hidden = true; back.hidden = true; done.hidden = false;
    });
    back.addEventListener('click', function () { if (cur > 0) show(cur - 1); });
    show(0);
  }
})();
