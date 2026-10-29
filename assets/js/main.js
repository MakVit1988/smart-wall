(function () {
  'use strict';

  // mobile menu
  var burger = document.getElementById('burger');
  var nav = document.getElementById('nav');
  function setMenu(open) {
    nav.classList.toggle('is-open', open);
    burger.setAttribute('aria-expanded', String(open));
  }
  burger.addEventListener('click', function () { setMenu(!nav.classList.contains('is-open')); });
  nav.addEventListener('click', function (e) { if (e.target.tagName === 'A') setMenu(false); });

  // catalog filter
  var chips = document.querySelectorAll('.chip');
  var cards = document.querySelectorAll('#cards .card');
  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      var f = chip.getAttribute('data-filter');
      chips.forEach(function (c) { c.classList.toggle('is-active', c === chip); });
      cards.forEach(function (card) {
        var tags = card.getAttribute('data-tags').split(' ');
        card.hidden = !(f === 'all' || tags.indexOf(f) !== -1);
      });
    });
  });

  // remember chosen product for the lead form
  var product = document.getElementById('leadProduct');
  document.querySelectorAll('[data-product]').forEach(function (a) {
    a.addEventListener('click', function () { product.value = a.getAttribute('data-product'); });
  });

  function validPhone(v) { return v.replace(/\D/g, '').length >= 10; }

  // quiz
  var form = document.getElementById('quizForm');
  var steps = form.querySelectorAll('.q');
  var total = steps.length;
  var current = 0;
  var next = document.getElementById('quizNext');
  var back = document.getElementById('quizBack');
  var bar = document.getElementById('quizBar');
  var label = document.getElementById('quizStepLabel');
  var err = document.getElementById('quizError');

  function showStep(i) {
    current = i;
    steps.forEach(function (s, idx) { s.classList.toggle('is-active', idx === i); });
    bar.style.width = ((i + 1) / total * 100) + '%';
    label.textContent = i === total - 1 ? 'Последний шаг' : 'Шаг ' + (i + 1) + ' из ' + (total - 1);
    back.hidden = i === 0;
    next.textContent = i === total - 1 ? 'Получить подбор' : 'Далее';
    err.hidden = true;
  }
  function fail(msg) { err.textContent = msg; err.hidden = false; }

  next.addEventListener('click', function () {
    var step = steps[current];
    if (current < total - 1) {
      if (!step.querySelector('input:checked')) { fail('Выберите вариант, чтобы продолжить'); return; }
      showStep(current + 1);
      return;
    }
    var phone = step.querySelector('input[type="tel"]').value;
    if (!validPhone(phone)) { fail('Укажите телефон, чтобы мы могли связаться'); return; }
    if (!step.querySelector('input[type="checkbox"]').checked) { fail('Нужно согласие на обработку персональных данных'); return; }
    err.hidden = true;
    next.hidden = true; back.hidden = true;
    document.getElementById('quizDone').hidden = false;
  });
  back.addEventListener('click', function () { if (current > 0) showStep(current - 1); });
  showStep(0);

  // lead form
  var lead = document.getElementById('leadForm');
  var leadErr = document.getElementById('leadError');
  var file = lead.querySelector('input[type="file"]');
  file.addEventListener('change', function () {
    document.getElementById('fileName').textContent = file.files.length ? file.files[0].name : 'Прикрепить планировку или ТЗ';
  });
  lead.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!validPhone(lead.elements.phone.value)) { leadErr.textContent = 'Укажите телефон, чтобы мы могли связаться'; leadErr.hidden = false; return; }
    if (!lead.querySelector('input[type="checkbox"]').checked) { leadErr.textContent = 'Нужно согласие на обработку персональных данных'; leadErr.hidden = false; return; }
    leadErr.hidden = true;
    document.getElementById('leadDone').hidden = false;
  });
})();
