"""Check source fidelity, anchored comments and the reviewed resource-management notes."""
import json,sys,unittest,re
from pathlib import Path
APP=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(APP/'tools'))
from slide_guidance import code_steps
class SlideGuides(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not (APP/'web/course-content.json').is_file() or not (APP/'web/catalog.json').is_file():raise unittest.SkipTest('Materiali locali non generati: consulta materiali/README.md e usa app/tools/build.py')
  cls.lessons=json.loads((APP/'web/course-content.json').read_text())['lessons']
 def test_every_slide_has_its_own_explanation(self):
  self.assertEqual(sum(len(l['slides']) for l in self.lessons),309)
  for lesson in self.lessons:
   for s in lesson['slides']:
    self.assertTrue(s.get('explanation') or any(b['kind']=='text' for b in s['guide']['blocks']),(lesson['id'],s['page']))
    self.assertTrue(all(b['page']==s['page'] for b in s['guide']['blocks']))
 def test_original_code_is_preserved_and_steps_reference_real_lines(self):
  for l in self.lessons:
   for s in l['slides']:
    native=[(b['id'],b['text']) for b in s['blocks'] if b['kind']=='code']
    self.assertTrue(set((b['id'],b['text']) for b in s['guide']['code'])<=set(native))
    for b in s['guide']['code']:
     for step in b['steps']:
      self.assertIn(step['code'],b['text'])
      self.assertTrue(1<=step['line']<=len(b['text'].splitlines()))
 def test_comment_regions_and_example_links_are_valid(self):
  for l in self.lessons:
   examples={e['id'] for original in json.loads((APP/'web/catalog.json').read_text())['lessons'] if original['id']==l['id'] for e in original['examples']}
   for s in l['slides']:
    self.assertTrue(set(s['examples'])<=examples)
    for c in s['guide']['comments']:
     r=c['region'];self.assertTrue(0<=r['x']<1 and 0<=r['y']<1);self.assertTrue(0<r['w']<=1 and 0<r['h']<=1)
     self.assertLessEqual(r['x']+r['w'],1.001);self.assertLessEqual(r['y']+r['h'],1.001)
     self.assertTrue(c['text']);self.assertTrue(c['code'])
 def test_floatarray_notes_cover_hidden_copy_and_move_source(self):
  slides=next(l['slides'] for l in self.lessons if l['id']=='objcopy')
  self.assertEqual(slides[12]['examples'],['dumb/testFloatArrayPrint.cc'])
  texts=lambda p:' '.join(step['text'] for b in slides[p-1]['guide']['code'] for step in b['steps'])
  self.assertIn('per valore',texts(11));self.assertIn('indefinito',texts(12))
  self.assertIn('lancia',texts(17));self.assertIn('un riferimento',texts(18));self.assertIn('sorgente',texts(21));self.assertIn('lvalue',texts(22))
 def test_const_return_on_a_separate_line_is_not_called_mutable(self):
  notes=code_steps('const\nfloat& operator[](unsigned int i) const;')
  self.assertEqual(notes[0]['title'],'Accesso in lettura')
if __name__=='__main__':unittest.main()
