#!/usr/bin/env node
// Optional media build dependency: Playwright Chromium + ffmpeg. Not needed to use the skill.
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { execFileSync } = require('node:child_process');
const { chromium } = require('playwright');
const root = path.resolve(__dirname, '..');
const out = path.join(root, 'docs/media');
const temp = fs.mkdtempSync(path.join(require('node:os').tmpdir(), 'fantasy-v3-media-'));
const css = fs.readFileSync(path.join(root, 'docs/site/site.css'),'utf8') + fs.readFileSync(path.join(root, 'docs/site/v3.css'),'utf8');
const esc = text => String(text).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
(async () => {
 const browser = await chromium.launch({headless:true});
 try {
  const page = await browser.newPage({viewport:{width:1100,height:780},deviceScaleFactor:1});
  await page.goto(pathToFileURL(path.join(root,'index.html')).href);
  const before = await page.locator('#stage-before .draft-cards').evaluate(e=>e.outerHTML);
  const after = await page.locator('#stage-after .draft-cards').evaluate(e=>e.outerHTML);
  const data = JSON.parse(fs.readFileSync(path.join(root,'docs/site/v3-demo.json'),'utf8'));
  const leader = data.after.candidates[0];
  const sourceRows = leader.evidence.accepted.map(s=>`<tr><th>${esc(s.source.toUpperCase())}</th><td>${s.league_points.toFixed(1)} points</td></tr>`).join('');
  const frames = [
   ['BEFORE PICK 19 · PREVIEW ONLY','Your target is still on the board.',before,'Another manager picks before you. This preview can change.'],
   ['PICKENS RECORDED AT 19 · YOUR TURN AT 20','Your shortlist updates.',after,'Walker now leads. Rice and Olave are alternatives.'],
   ['INSPECT THE REASONING','What could change the call?',`<div class="proof"><h3>${esc(leader.name)} · ${leader.projection.toFixed(1)} blended points</h3><table>${sourceRows}</table><p>${esc(leader.sensitivity)}</p><p>Source disagreement measures differences between forecasts. It is not a confidence interval.</p></div>`,'Limited evidence: provider update times are unverified; scoring approximations apply.'],
   ['FANTASY DRAFT ANALYST · V3','Your league. Your roster. Your next pick.',`<div class="proof"><h3>Choose your setup</h3><p><b>Prepare:</b> researched targets and a saved board. Use an assistant with code execution.</p><p><b>Draft live:</b> record picks and recalculate advice. Requires local Python.</p><p>No automatic platform sync. Free and open source.</p><p><b>nicodeguyo.github.io/fantasy-draft-analyst</b></p></div>`,'Make your next pick with the evidence and the tradeoffs in view.']
  ];
  for (let i=0;i<frames.length;i++) {
   const [label,title,body,caption]=frames[i];
   await page.setContent(`<html><head><meta charset="utf-8"><style>${css}
    body{background:#f5f7fa;color:#101c33;padding:32px 34px;height:780px;overflow:hidden}.eyebrow{color:#326714;margin-bottom:12px}h2{font-size:40px;margin-bottom:22px}.draft-card{padding:20px}.draft-card.preferred{padding-top:16px}.draft-card h3{font-size:22px}.draft-card details{display:none}.card-number{margin:20px 0}.proof{padding:22px 28px;background:white;border:1px solid #c5d0da;border-radius:7px;max-width:900px}.proof h3{font-size:26px}.proof p{font-size:21px}.proof table{font-size:21px}.caption-bar{position:absolute;bottom:34px;left:34px;right:34px;background:#0b1b33;color:white;border-radius:6px;padding:17px 20px;font-size:20px;font-weight:600}.foot{position:absolute;bottom:7px;left:34px;font-size:11px;color:#52627a}</style></head><body><p class="eyebrow">${esc(label)}</p><h2>${esc(title)}</h2>${body}<div class="caption-bar">${esc(caption)}</div><p class="foot">Saved v3 engine output · Fictional 12-team half-PPR draft · Public projections fetched September 7, 2026 UTC · Not current advice</p></body></html>`);
   await page.screenshot({path:path.join(temp,`frame-${i}.png`)});
   if(i===1) await page.screenshot({path:path.join(out,'v3-decision.png')});
  }
  await page.setViewportSize({width:1280,height:640});
  await page.setContent(`<html><head><style>${css}body{padding:55px 65px;width:1280px;height:640px;overflow:hidden}.eyebrow{font-size:17px;margin-bottom:25px}h1{font-size:81px;line-height:1.02}.social-row{position:absolute;right:65px;top:172px;width:350px;border-top:3px solid #8edb4b;padding-top:20px}.social-row p{font-size:26px;border-bottom:1px solid #43596f;padding-bottom:19px;margin-top:0}.social-footer{position:absolute;bottom:37px;font-size:19px;color:#bccbdd}.social-footer b{color:#8edb4b}</style></head><body><p class="eyebrow">Fantasy Draft Analyst · Free &amp; open source</p><h1>Your league.<br>Your roster.<br><span>Your next pick.</span></h1><div class="social-row"><p>Compare sources.</p><p>See roster tradeoffs.</p><p>Inspect alternatives.</p></div><p class="social-footer"><b>V3</b> · Prepare your plan or run local live advice · nicodeguyo.github.io/fantasy-draft-analyst</p></body></html>`);
  await page.screenshot({path:path.join(out,'social-preview-v3.png')});
 } finally { await browser.close(); }
 execFileSync('ffmpeg',['-y','-framerate','1/6','-i',path.join(temp,'frame-%d.png'),'-c:v','libx264','-r','25','-pix_fmt','yuv420p','-movflags','+faststart',path.join(out,'v3-walkthrough.mp4')],{stdio:'pipe'});
 fs.writeFileSync(path.join(out,'v3-walkthrough.vtt'),`WEBVTT\n\n00:00.000 --> 00:06.000\nBefore pick 19: Pickens leads the preview. Another manager picks before you.\n\n00:06.000 --> 00:12.000\nAfter Pickens is recorded: Walker leads, with Rice and Olave as alternatives.\n\n00:12.000 --> 00:18.000\nInspect the sources: lowering Walker by observed source disagreement puts Rice first. This is not a confidence interval.\n\n00:18.000 --> 00:24.000\nChoose preparation with an assistant or live advice with local Python. Free and open source. No automatic platform sync.\n`);
 const files=['v3-decision.png','social-preview-v3.png','v3-walkthrough.mp4','v3-walkthrough.vtt'];
 const crypto = require('node:crypto');
 fs.writeFileSync(path.join(out,'v3-manifest.json'),JSON.stringify({description:'Captioned editorial walkthrough of reproduced v3 outputs. Silent, four six-second frames. No private league data.',files:Object.fromEntries(files.map(f=>[f,{bytes:fs.statSync(path.join(out,f)).size,sha256:crypto.createHash('sha256').update(fs.readFileSync(path.join(out,f))).digest('hex')}]))},null,2)+'\n');
 fs.rmSync(temp,{recursive:true,force:true});
 console.log('Created v3 screenshot, social preview, and 24-second captioned walkthrough.');
})().catch(e=>{console.error(e);process.exitCode=1});
