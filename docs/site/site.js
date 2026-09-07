'use strict';
// Two frozen outputs from the shipped v3 engine. No simulation or account access here.
const stageButtons = document.querySelectorAll('[data-stage]');
function showStage(stage) {
  if (!['before', 'after'].includes(stage)) stage = 'after';
  for (const button of stageButtons) button.setAttribute('aria-pressed', String(button.dataset.stage === stage));
  for (const name of ['before', 'after']) document.getElementById('stage-' + name).hidden = name !== stage;
  document.getElementById('demo-status').textContent = stage === 'before'
    ? 'Pick 19: preview only. Another manager picks before your turn.'
    : 'Pick 20: your turn. George Pickens is off the board.';
}
for (const button of stageButtons) button.addEventListener('click', () => showStage(button.dataset.stage));
const copyButton = document.getElementById('copy-prompt');
if (copyButton) {
  copyButton.hidden = false;
  copyButton.addEventListener('click', async () => {
    const prompt = document.getElementById('league-prompt');
    try { await navigator.clipboard.writeText(prompt.value); document.getElementById('copy-status').textContent = 'Copied. Paste it into your assistant after installing the skill.'; }
    catch { prompt.focus(); prompt.select(); document.getElementById('copy-status').textContent = 'Text selected. Use your device’s Copy command.'; }
  });
}
