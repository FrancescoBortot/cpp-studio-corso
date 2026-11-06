"""Independent inventory checks against the complete extracted source catalog."""
import hashlib,json,re,unittest
from pathlib import Path
WEB=Path(__file__).resolve().parents[1]/'web'
class Coverage(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  if not all((WEB/name).is_file() for name in ('catalog.json','course-content.json')):raise unittest.SkipTest('Materiali locali non generati: consulta materiali/README.md e usa app/tools/build.py')
  cls.catalog=json.loads((WEB/'catalog.json').read_text())['lessons']
  cls.course=json.loads((WEB/'course-content.json').read_text())['lessons']
 def test_handout_is_an_exact_partition(self):
  for original,course in zip(self.catalog,self.course):
   source={f'd-{p["page"]}-{i}':b for p in original['dispensa'] for i,b in enumerate(p['blocks'])}
   core={b['id']:b for s in course['sections'] for b in s['blocks'] if b['origin']=='dispensa'}
   excluded=set(course['excludedBlockIds'])
   self.assertEqual(set(source),set(core)|excluded)
   self.assertFalse(set(core)&excluded)
   for bid,b in core.items():self.assertEqual(b['text'],source[bid]['text'])
   for b in core.values():self.assertFalse(re.match(r'^Approfondimento\b',b['text'],re.I))
 def test_every_slide_body_and_image_is_present(self):
  self.assertEqual(sum(len(l['slides']) for l in self.course),309)
  for original,course in zip(self.catalog,self.course):
   self.assertEqual(len(original['slides']),len(course['slides']))
   sections={s['id'] for s in course['sections']}
   for source,slide in zip(original['slides'],course['slides']):
    self.assertEqual(source['page'],slide['page']);self.assertTrue(slide['sectionIds']);self.assertTrue(set(slide['sectionIds'])<=sections)
    expected=[]
    for i,b in enumerate(source['blocks']):
     normalize=lambda t:re.sub(r'\s+',' ',t.replace('ﬁ','fi').replace('ﬂ','fl')).strip()
     if i==0 and normalize(b['text'])==normalize(original['slides'][0]['blocks'][0]['text']):continue
     body='\n'.join(line for line in b['text'].splitlines() if not normalize(line).startswith('ObjectorientedprogrammingandC++')).strip()
     if body:expected.append(body)
    self.assertEqual(expected,[b['text'] for b in slide['blocks']])
    self.assertEqual(slide['imageFingerprint'],hashlib.sha256((WEB/slide['image']).read_bytes()).hexdigest()[:20])
 def test_extra_decks_have_individual_explanations(self):
  for lesson in self.course:
   if lesson['id'] in ('rvalue','thread'):
    for slide in lesson['slides']:self.assertGreater(len(slide['explanation']),120)
 def test_anchor_identities_are_unique(self):
  for l in self.course:
   ids=[b['id'] for s in l['sections'] for b in s['blocks']]+[b['id'] for s in l['slides'] for b in s['blocks']]
   self.assertEqual(len(ids),len(set(ids)))
if __name__=='__main__':unittest.main()
