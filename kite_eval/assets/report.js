(() => {
  'use strict';
  const cases = Array.from(document.querySelectorAll('.case'));
  const search = document.getElementById('search');
  const status = document.getElementById('status');
  const skill = document.getElementById('skill');
  const texts = new Map(cases.map(row => [row, row.textContent.toLowerCase()]));
  function filter() {
    const q = search.value.trim().toLowerCase();
    let count = 0;
    for (const row of cases) {
      row.hidden = !((status.value === 'all' || row.dataset.status === status.value) &&
        (skill.value === 'all' || row.dataset.skill === skill.value) && texts.get(row).includes(q));
      if (!row.hidden) count++;
    }
    document.getElementById('visible-count').textContent = `${count} of ${cases.length} cases`;
    document.getElementById('empty').hidden = count !== 0;
  }
  function reset() { search.value = ''; status.value = 'all'; skill.value = 'all'; filter(); }
  search.addEventListener('input', filter);
  status.addEventListener('change', filter);
  skill.addEventListener('change', filter);
  document.getElementById('reset').addEventListener('click', () => { reset(); search.focus(); });
  function openTarget() {
    const target = cases.find(row => '#' + row.id === location.hash);
    if (target) { reset(); target.open = true; target.scrollIntoView({block: 'start'}); }
  }
  document.querySelectorAll('.cell').forEach(cell => cell.addEventListener('click', () => {
    const target = document.getElementById(cell.hash.slice(1));
    reset(); if (target) target.open = true;
  }));
  window.addEventListener('hashchange', openTarget);
  window.addEventListener('beforeprint', () => cases.forEach(row => { row.dataset.wasOpen = String(row.open); row.open = true; }));
  window.addEventListener('afterprint', () => cases.forEach(row => { row.open = row.dataset.wasOpen === 'true'; }));
  openTarget();
})();
