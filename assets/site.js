/* SPDX-License-Identifier: MIT */
const root = document.documentElement;
root.classList.add('js');
const theme = document.querySelector('[data-theme-toggle]');
let preference = 'system';
try { preference = localStorage.getItem('impurifiers-theme') || 'system'; } catch {}
const applyTheme = () => {
  if (preference === 'system') delete root.dataset.theme;
  else root.dataset.theme = preference;
  if (theme) {
    theme.textContent = `Theme: ${preference}`;
    theme.setAttribute('aria-label', `Color theme: ${preference}. Activate to change.`);
  }
};
applyTheme();
theme?.addEventListener('click', () => {
  preference = {system:'light', light:'dark', dark:'system'}[preference] || 'system';
  try { localStorage.setItem('impurifiers-theme', preference); } catch {}
  applyTheme();
});
for (const [index, pre] of [...document.querySelectorAll('pre')].entries()) {
  const code = pre.querySelector('code') || pre;
  const wrapper = document.createElement('div');
  wrapper.className = 'code-block';
  pre.before(wrapper);
  wrapper.append(pre);
  const button = document.createElement('button');
  button.type = 'button'; button.className = 'copy-code'; button.textContent = 'Copy';
  button.setAttribute('aria-label', `Copy code example ${index + 1}`);
  const status = document.createElement('span');
  status.className = 'sr-only'; status.setAttribute('role', 'status');
  wrapper.append(button, status);
  let timer;
  button.addEventListener('click', async () => {
    clearTimeout(timer);
    try {
      await navigator.clipboard.writeText(code.textContent);
      button.textContent = 'Copied'; status.textContent = 'Code copied to clipboard.';
    } catch {
      const selection = window.getSelection(); const range = document.createRange();
      range.selectNodeContents(code); selection.removeAllRanges(); selection.addRange(range);
      button.textContent = 'Select & copy'; status.textContent = 'Code selected. Use your copy command.';
    }
    timer = setTimeout(() => { button.textContent = 'Copy'; status.textContent = ''; }, 2500);
  });
}
const search = document.querySelector('#project-search');
const filters = [...document.querySelectorAll('[data-filter]')];
const projects = [...document.querySelectorAll('[data-project]')];
let category = 'all';
function filterProjects() {
  const terms = (search?.value || '').toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
  let visible = 0;
  for (const row of projects) {
    const matches = (category === 'all' || row.dataset.category === category)
      && terms.every(term => row.dataset.search.includes(term));
    row.hidden = !matches; if (matches) visible++;
  }
  for (const group of document.querySelectorAll('.catalog-group')) {
    group.hidden = ![...group.querySelectorAll('[data-project]')].some(row => !row.hidden);
  }
  const count = document.querySelector('#project-count');
  if (count) count.textContent = `${visible} of ${projects.length} impurifiers`;
  const empty = document.querySelector('#no-projects'); if (empty) empty.hidden = visible > 0;
  for (const button of filters) button.setAttribute('aria-pressed', String(button.dataset.filter === category));
}
search?.addEventListener('input', filterProjects);
for (const button of filters) button.addEventListener('click', () => { category = button.dataset.filter; filterProjects(); });
document.querySelector('#reset-search')?.addEventListener('click', () => {
  search.value = ''; category = 'all'; filterProjects(); search.focus();
});
if (search) filterProjects();
const example = document.querySelector('#package-example');
for (const button of document.querySelectorAll('[data-example]')) {
  button.addEventListener('click', () => {
    const template = document.querySelector(`#example-${button.dataset.example}`);
    example.textContent = template.content.textContent.trim() + '\n';
    for (const tab of document.querySelectorAll('[data-example]')) tab.setAttribute('aria-pressed', String(tab === button));
    const link = document.querySelector('#example-docs');
    link.href = `/${button.dataset.example}-impurifier/`;
    link.textContent = `Read the ${button.dataset.example} guide →`;
  });
}
