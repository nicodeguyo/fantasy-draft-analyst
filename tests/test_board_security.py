"""Regression checks for the board's text, script, and CSS trust boundaries."""
import csv
import json
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / 'examples/sample-league'
RENDER = ROOT / 'skills/fantasy-draft-analyst/scripts/build_board.py'


class BoardSecurityTests(unittest.TestCase):
    def render(self, mutate):
        import yaml
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            cfg = yaml.safe_load((SAMPLE / 'league.yaml').read_text())
            notes = json.loads((SAMPLE / 'notes.json').read_text())
            with (SAMPLE / 'players.csv').open() as f:
                reader = csv.DictReader(f)
                fields, players = reader.fieldnames, list(reader)
            mutate(cfg, notes, players)
            (base / 'league.json').write_text(json.dumps(cfg))
            (base / 'notes.json').write_text(json.dumps(notes))
            with (base / 'players.csv').open('w') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(players)
            proc = subprocess.run([sys.executable, str(RENDER), '--league', str(base/'league.json'),
                '--sim', str(SAMPLE/'sim.json'), '--notes', str(base/'notes.json'),
                '--players', str(base/'players.csv'), '--out', str(base/'board.html')], capture_output=True, text=True)
            return proc, (base/'board.html').read_text() if (base/'board.html').exists() else ''

    def test_untrusted_text_cannot_create_html(self):
        payload = '<img src=x onerror=alert(1)>'
        def mutate(cfg, notes, players):
            notes['howto'] = [['Heading', payload]]
            notes['tiers'][payload] = {'bands': []}
        proc, page = self.render(mutate)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse(payload in page, "Untrusted HTML survived rendering")
        self.assertIn('&lt;img', page)

    def test_player_name_cannot_close_script(self):
        payload = '</script><script>alert(1)</script>'
        def mutate(cfg, notes, players):
            players.append(dict(players[0], name=payload))
        proc, page = self.render(mutate)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertFalse(payload in page, "Untrusted HTML survived rendering")
        self.assertEqual(page.count('</script>'), 1)

    def test_custom_colors_reject_css_and_html(self):
        for color in ('primary', 'secondary', 'accent'):
            with self.subTest(color=color):
                def mutate(cfg, notes, players):
                    cfg['theme'] = {'team': 'custom', 'custom': {color: '#123456;</style><script>alert(1)</script>'}}
                proc, page = self.render(mutate)
                self.assertNotEqual(proc.returncode, 0)
                self.assertEqual(page, '')

    def test_rich_text_fields_neutralize_active_and_malformed_markup(self):
        class FragmentElements(HTMLParser):
            def __init__(self):
                super().__init__()
                self.elements = []
            def handle_starttag(self, tag, attrs):
                self.elements.append((tag, attrs))
            def handle_startendtag(self, tag, attrs):
                self.handle_starttag(tag, attrs)

        payloads = [
            '<script>alert(1)</script><img src=x onerror=alert(1)>',
            '<svg><a xlink:href="javascript:alert(1)">click</a></svg>',
            '<b onclick="alert(1)" style="position:fixed">bold</b><br onmouseover="alert(1)">',
            '&lt;img src=x onerror=alert(1)&gt; &amp;lt;script&amp;gt;',
            '<b><i>nested</b> tail</i></li><script>alert(1)</script>',
            '<!-- hidden --><iframe srcdoc="<script>alert(1)</script>"></iframe>',
            '<math><mtext><table><mglyph><style><!--</style><img title="--><img src=x onerror=alert(1)>">',
            '<![CDATA[<script>alert(1)</script>]]> <b>okay</b>',
        ]
        for section, field in (('appendix', 'how_built'), ('appendix', 'assumptions'), ('headline_rule', 'paragraphs')):
            for payload in payloads:
                with self.subTest(field=field, payload=payload):
                    def mutate(cfg, notes, players):
                        notes.setdefault(section, {})[field] = ['RICHSTART' + payload + 'RICHEND']
                    proc, page = self.render(mutate)
                    self.assertEqual(proc.returncode, 0, proc.stderr)
                    fragment = page.split('RICHSTART', 1)[1].split('RICHEND', 1)[0]
                    parsed = FragmentElements()
                    parsed.feed(fragment)
                    self.assertTrue(all(tag in {'b', 'strong', 'em', 'i', 'br', 'code'} and not attrs
                                        for tag, attrs in parsed.elements), parsed.elements)
                    self.assertEqual(page.count('<script>'), 1)

    def test_rich_text_keeps_safe_formatting_and_balances_tags(self):
        def mutate(cfg, notes, players):
            notes['appendix']['how_built'] = ['<strong>Strong</strong><em>Em</em><i>I</i><code>Code</code><br><b>Open']
        proc, page = self.render(mutate)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn('<li><strong>Strong</strong><em>Em</em><i>I</i><code>Code</code><br><b>Open</b></li>', page)

    def test_documented_rich_text_is_preserved(self):
        def mutate(cfg, notes, players):
            notes['appendix']['how_built'] = ['<b>built</b>']
            notes['appendix']['assumptions'] = ['<b>assumed</b>']
            notes['headline_rule'] = {'paragraphs': ['<b>headline</b>']}
        proc, page = self.render(mutate)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        for text in ('built', 'assumed', 'headline'):
            self.assertIn('<b>' + text + '</b>', page)


if __name__ == '__main__':
    unittest.main()
