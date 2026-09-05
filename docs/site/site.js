'use strict';
// The demo uses saved, reproducible sample data. No live draft or account access.
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
const dataElement = document.getElementById('comparison-data');
if (dataElement) {
  const data = JSON.parse(dataElement.textContent);
  const buttons = document.getElementById('candidate-buttons');
  const rows = document.getElementById('lineup-rows');
  const total = document.getElementById('lineup-total');
  const status = document.getElementById('lineup-status');
  let selected = new URL(location.href).searchParams.get('pick') === 'wr' ? 'wr' : 'rb';
  const number = value => new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(value);
  function render(id, animate) {
    selected = id;
    const branch = data.branches.find(b => b.id === id);
    const other = data.branches.find(b => b.id !== id);
    const otherNames = new Set(other.starting_lineup.map(p => p.name));
    buttons.querySelectorAll('button').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.pick === id)));
    rows.replaceChildren();
    branch.starting_lineup.forEach((player, index) => {
      const row = document.createElement('div');
      row.className = 'lineup-row' + (otherNames.has(player.name) ? '' : ' changed');
      const slot = document.createElement('span'); slot.className = 'slot'; slot.textContent = player.slot;
      const name = document.createElement('span'); name.className = 'player-name'; name.textContent = player.name;
      const points = document.createElement('span'); points.className = 'player-points'; points.textContent = number(player.projected_points);
      if (!otherNames.has(player.name)) { const tag = document.createElement('small'); tag.textContent = 'DIFFERENT PLAYER'; name.append(tag); }
      row.append(slot, name, points); rows.append(row);
      if (animate && !reduceMotion.matches && row.animate) row.animate([{opacity:.45, transform:'translateY(5px)'},{opacity:1,transform:'translateY(0)'}], {duration:220,delay:index*18,easing:'ease-out'});
    });
    total.textContent = number(branch.projected_lineup_points);
    const diff = branch.projected_lineup_points - other.projected_lineup_points;
    status.textContent = `${branch.candidate.name}: ${number(branch.projected_lineup_points)} projected points. ${number(Math.abs(diff))} ${diff > 0 ? 'more' : 'fewer'} than the other branch in this one example.`;
    document.getElementById('result-name').textContent = `Start with ${branch.candidate.name}`;
    document.getElementById('result-points').textContent = number(branch.projected_lineup_points);
    document.getElementById('result-difference').textContent = diff === 0 ? 'Same total in this example' : `${number(Math.abs(diff))} ${diff > 0 ? 'more' : 'fewer'} than the other branch`;
    const later = branch.draft_picks.find(p => p.round > data.method.round && !other.draft_picks.some(q => q.overall === p.overall && q.name === p.name));
    document.getElementById('branch-explanation').textContent = later
      ? `After ${branch.candidate.name}, this continuation takes ${later.name} in round ${later.round}. Explore the resulting lineup; other simulated drafts can unfold differently.`
      : 'The later picks match in this example. Other simulated drafts can unfold differently.';
  }
  data.branches.forEach(branch => {
    const button = document.createElement('button'); button.type = 'button'; button.dataset.pick = branch.id;
    const position = document.createElement('span'); position.textContent = branch.candidate.position;
    const name = document.createElement('strong'); name.textContent = branch.candidate.name;
    button.append(position,name); button.addEventListener('click', () => render(branch.id, true)); buttons.append(button);
  });
  render(selected, false);
  document.getElementById('comparison-workspace').hidden = false;
  document.querySelector('.saved-lineups').open = false;
  document.getElementById('share-example').addEventListener('click', async () => {
    const url = new URL('https://nicodeguyo.github.io/fantasy-draft-analyst/');
    url.searchParams.set('pick', selected); url.hash = 'compare';
    try { await navigator.clipboard.writeText(url.href); document.getElementById('share-status').textContent = 'Link copied. It opens this saved example.'; }
    catch { document.getElementById('share-status').textContent = `Copy this link: ${url.href}`; }
  });
}
const copyButton = document.getElementById('copy-prompt');
if (copyButton) {
  copyButton.hidden = false;
  copyButton.addEventListener('click', async () => {
    const prompt = document.getElementById('league-prompt');
    try { await navigator.clipboard.writeText(prompt.value); document.getElementById('copy-status').textContent = 'Copied. Paste it into your assistant.'; }
    catch { prompt.focus(); prompt.select(); document.getElementById('copy-status').textContent = 'Text selected. Use your device’s Copy command.'; }
  });
}
// Enhancement only: essential text and controls never depend on scroll progress.
if (window.ScrollCraft) window.ScrollCraft.mount();
