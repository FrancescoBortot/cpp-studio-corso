'use strict';
let courseContent=null;
let studyView={mode:'slides',sectionId:null,page:1};
let pendingStudyTarget=null;
function currentCourse(){return courseContent.lessons.find(l=>l.id===lesson.id);}
function anchorAttrs(a){return `id="study-${esc(a.id.replaceAll(':','-'))}" data-study-anchor="${esc(a.id)}" data-study-kind="${esc(a.kind)}" data-study-origin="${esc(a.origin)}" data-study-page="${a.page||''}" data-study-section="${esc(a.sectionId||'')}" data-study-fingerprint="${esc(a.fingerprint||'')}" data-study-label="${esc(a.label||'')}"`;}
function courseBlock(block){
 const a={id:lesson.id+':'+block.id,kind:'block',origin:block.origin,page:block.page,sectionId:block.sectionId,fingerprint:block.fingerprint,label:block.label||((block.origin==='dispensa'?'Dispensa':'Slide')+' · '+block.page)};
 if(block.kind==='inline-code')return `<p class="guide-inline-code" ${anchorAttrs(a)}><code>${esc(block.text)}</code></p>`;
 if(block.kind==='code')return `<div class="course-code"><pre class="snippet" ${anchorAttrs(a)}>${esc(block.text)}</pre><div class="code-block-actions"><button data-code="${esc(encodeURIComponent(block.text))}" data-origin="${block.origin}" data-page="${block.page}" onclick="tryBlock(this)">▶ Modifica e prova</button><button data-annotate-anchor="${esc(a.id)}">✎ Annota codice</button><span class="tag">${snippetBadge(block.text,block.origin,block.page)}</span></div></div>`;
 if(block.kind==='heading')return `<h3 class="course-subheading" ${anchorAttrs(a)}>${esc(block.text.replace(/\n/g,' '))}</h3>`;
 let text=block.text.replace(/-\n(?=[a-zà-ú])/g,'');
 let html;if(text.split('\n').filter(l=>/^\s*[•●]/.test(l)).length>1){let parts=text.split(/\n(?=\s*[•●])/);html=parts.map(p=>/^\s*[•●]/.test(p)?`<li>${sourceReferences(p.replace(/^\s*[•●]\s*/, '').replace(/\n/g,' '))}</li>`:`<p>${sourceReferences(p.replace(/\n/g,' '))}</p>`).join('');html='<div class="course-list">'+html.replace(/(<li>[\s\S]*)/,'<ul>$1</ul>')+'</div>';}else html=sourceReferences(text.replace(/\n/g,' '));
 return `<div class="course-paragraph" ${anchorAttrs(a)}>${html}</div>`;
}
function sectionBody(section){return `<div class="topic-body" ${anchorAttrs({id:lesson.id+':topic:'+section.id,kind:'topic',origin:section.blocks[0]?.origin||'dispensa',page:section.pages[0]||section.blocks[0]?.page,sectionId:section.id,fingerprint:section.fingerprint,label:section.title})}>${section.blocks.map((b,i)=>b.kind==='heading'&&b.text.replace(/\s+/g,' ').trim()===section.title.replace(/\s+/g,' ').trim()?`<span class="source-heading-anchor" ${anchorAttrs({id:lesson.id+':'+b.id,kind:'block',origin:b.origin,page:b.page,sectionId:b.sectionId,fingerprint:b.fingerprint,label:section.title})}>${esc(b.text)}</span>`:courseBlock(b)).join('')}</div>`;}
function slideFigure(slide){let id=lesson.id+':figure:'+slide.page;return `<figure class="study-slide"><div class="slide-tools"><span>Slide ${slide.page} · ${esc(slide.title)}</span><div><button data-note-slide="${slide.page}">✎ Nota sulla slide</button><button data-region-slide="${slide.page}" aria-pressed="false">▧ Annota zona</button></div></div><div class="slide-image-box" ${anchorAttrs({id,kind:'slide',origin:'slide',page:slide.page,sectionId:slide.sectionIds[0],fingerprint:slide.imageFingerprint,label:'Slide '+slide.page+' · '+slide.title})}><img loading="lazy" width="1200" height="900" src="${esc(slide.image)}" alt="Slide ${slide.page}: ${esc(slide.title)}" draggable="false">${codeCommentLayer(slide)}<div class="region-layer"></div><div class="region-draft" hidden></div></div><figcaption>Seleziona il testo della spiegazione per evidenziare o annotare. Per la figura usa «Annota zona».</figcaption></figure>`;}
function relatedExamples(slides){let ids=[...new Set(slides.flatMap(s=>s.examples))];return ids.length?`<section class="related-examples"><h3>Dal concetto al programma</h3><div>${ids.map(id=>`<button data-course-example="${esc(id)}">${esc(id)} ↗</button>`).join('')}</div></section>`:'';}
function rememberView(){write('course-location-'+lesson.id,studyView);}
let courseObserver=null;
function stopCourseTracking(){courseObserver?.disconnect();courseObserver=null;}
function readingTarget(view=studyView){return view.mode==='slides'?'course-slide-'+view.page:'course-section-'+view.sectionId;}
function scrollCourse(id,behavior='smooth'){
 const el=document.getElementById(id);if(!el)return;
 document.querySelector('#lesson-outline')?.classList.remove('outline-open');
 document.querySelector('#toggle-outline')?.setAttribute('aria-expanded','false');
 el.scrollIntoView({block:'start',behavior});
}
function trackCoursePosition(){
 stopCourseTracking();let visible=new Set();
 courseObserver=new IntersectionObserver(entries=>{
  for(const entry of entries)if(entry.isIntersecting)visible.add(entry.target);else visible.delete(entry.target);
  const first=[...visible].sort((a,b)=>a.getBoundingClientRect().top-b.getBoundingClientRect().top)[0];if(!first)return;
  if(first.dataset.courseSection)studyView.sectionId=first.dataset.courseSection;
  if(first.dataset.coursePage)studyView.page=Number(first.dataset.coursePage);
  rememberView();
  document.querySelectorAll('[data-outline-target]').forEach(link=>{if(link.dataset.outlineTarget===first.id){link.setAttribute('aria-current','location')}else link.removeAttribute('aria-current')});
 },{rootMargin:'-130px 0px -45% 0px',threshold:0});
 document.querySelectorAll('.continuous-topic,.continuous-slide').forEach(el=>courseObserver.observe(el));
}
function readCheck(mode,value){const key=lesson.id+':'+mode+':'+value;return `<label class="section-read"><input type="checkbox" data-reading-key="${esc(key)}" ${read('course-read',{})[key]?'checked':''}> Letto</label>`;}
function renderCourseLesson(){
 stopCourseTracking();
 const material=currentCourse(),saved=read('course-location-'+lesson.id,{});
 studyView={mode:read('course-view-preference','slides')==='topics'?'topics':'slides',sectionId:saved.sectionId||material.sections[0].id,page:Math.max(1,Math.min(material.slides.length,saved.page||1))};
 const pending=pendingStudyTarget?.lessonId===lesson.id?pendingStudyTarget:null;
 if(pending)studyView={...studyView,...pending.view};
 if(!material.sections.some(s=>s.id===studyView.sectionId))studyView.sectionId=material.sections[0].id;
 const outline=studyView.mode==='topics'?material.sections.map(s=>({id:'course-section-'+s.id,title:s.title})):material.slides.map(s=>({id:'course-slide-'+s.page,title:s.page+'. '+s.title}));
 $('#content').innerHTML=`<div class="study-controls"><div class="view-switch" aria-label="Modalità di studio"><button data-study-mode="slides" aria-pressed="${studyView.mode==='slides'}">Slide e spiegazioni</button><button data-study-mode="topics" aria-pressed="${studyView.mode==='topics'}">Lezione continua</button></div><div class="study-reading-tools"><button id="note-lesson">✎ Appunto</button><div class="font-controls" aria-label="Dimensione del testo"><button id="reader-smaller" aria-label="Riduci dimensione del testo">A−</button><button id="reader-larger" aria-label="Aumenta dimensione del testo">A+</button></div><button id="density-reader" aria-pressed="${read('course-density','normal')==='compact'}">Vista compatta</button><button id="focus-reader" aria-pressed="${document.body.classList.contains('focus-reading')}">Concentrazione</button></div></div><p class="course-help">Tutta la lezione in una pagina. Scorri per leggere, seleziona per annotare, usa l’indice per raggiungere un punto.</p><div id="inline-lab-slot"></div><div class="continuous-layout"><div id="study-reading" class="continuous-paper"></div><aside id="lesson-outline" aria-label="Indice della lezione"><div class="outline-heading"><strong>IN QUESTA LEZIONE</strong><button id="close-outline" aria-label="Chiudi indice">×</button></div><nav class="outline-links" aria-label="Argomenti della lezione">${outline.map(o=>`<a href="#${lesson.id}" data-outline-target="${esc(o.id)}">${esc(o.title)}</a>`).join('')}</nav><button id="resume-reading">Riprendi la lettura ↗</button></aside></div><div id="personal-cells"></div>`;
 if(studyView.mode==='topics'){
  const assigned=new Set();
  $('#study-reading').innerHTML=material.sections.map(section=>{
   const linked=material.slides.filter(s=>s.sectionIds.includes(section.id)&&!assigned.has(s.page));linked.forEach(s=>assigned.add(s.page));
   const depth=(section.title.match(/^\d+(\.\d+)+/)?.[0].match(/\./g)||[]).length;
   return `<section id="course-section-${esc(section.id)}" class="continuous-topic ${depth>1?'topic-subsection':''}" data-course-section="${esc(section.id)}"><div class="article-heading"><h2>${esc(section.title)}</h2><button data-annotate-anchor="${esc(lesson.id+':topic:'+section.id)}" aria-label="Annota ${esc(section.title)}">✎ Annota</button></div>${sectionBody(section)}${relatedExamples(linked)}<div class="section-end">${section.pages.length?`<div class="handout-links"><span>Dispensa</span>${section.pages.map(p=>`<a href="${sourceLink('dispensa',p)}" target="_blank" rel="noopener">p. ${p} ↗</a>`).join('')}</div>`:''}${linked.length?`<div class="inline-slide-links"><span>Slide di riferimento</span>${linked.map(s=>`<button data-follow-slide="${s.page}">${s.page}</button>`).join('')}</div>`:'<span></span>'}${readCheck('topics',section.id)}</div></section>`;
  }).join('');
 }else{
  $('#study-reading').innerHTML=material.slides.map(slide=>{
   const guide=slide.guide||{blocks:[],code:[],comments:[],sourcePages:[]};
   const explanation=slide.explanation?`<div class="course-paragraph" ${anchorAttrs({id:lesson.id+':explanation:'+slide.page,kind:'block',origin:'slide',page:slide.page,sectionId:slide.sectionIds[0],fingerprint:slide.fingerprint,label:'Spiegazione slide '+slide.page})}>${esc(slide.explanation)}</div>`:guide.blocks.map(courseBlock).join('');
   const code=guide.code.map(block=>`<section class="code-walkthrough"><h3>Come funziona il codice</h3>${courseBlock(block)}${block.steps.length?`<ol class="code-reading-steps">${block.steps.map(step=>`<li><strong>${esc(step.title)}</strong><code>${esc(step.code)}</code><p>${esc(step.text)}</p></li>`).join('')}</ol>`:''}</section>`).join('');
   const handout=guide.sourcePages.length?`<div class="guide-sources">Dalla dispensa ${guide.sourcePages.map(p=>`<a target="_blank" rel="noopener" href="${sourceLink('dispensa',p)}">p. ${p} ↗</a>`).join(' · ')}</div>`:'';
   return `<section id="course-slide-${slide.page}" class="continuous-slide" data-course-page="${slide.page}"><h2><span class="slide-number">${slide.page}</span>${esc(slide.title)}</h2><div class="slide-study-pair">${slideFigure(slide)}<div class="slide-explanation"><p class="eyebrow">CAPIRE QUESTA SLIDE</p>${explanation}${code}${handout}</div></div><div class="section-end"><span></span>${readCheck('slides',slide.page)}</div>${exampleBridge(slide)}</section>`;
  }).join('');

 }
 document.querySelectorAll('[data-study-mode]').forEach(b=>b.onclick=()=>{write('course-view-preference',b.dataset.studyMode);changeStudy({mode:b.dataset.studyMode})});
 document.querySelectorAll('[data-follow-slide]').forEach(b=>b.onclick=()=>changeStudy({mode:'slides',page:Number(b.dataset.followSlide)}));
 document.querySelectorAll('[data-course-example]').forEach(b=>b.onclick=()=>{const example=lesson.examples.find(e=>e.id===b.dataset.courseExample);if(example&&openExample(example)&&b.closest('.example-bridge')){b.closest('.example-bridge').append($('#lab'));$('#lab').scrollIntoView({block:'start',behavior:'instant'})}});
 document.querySelectorAll('[data-jump-explanation]').forEach(b=>b.onclick=e=>{e.preventDefault();scrollCourse('explanation-'+b.dataset.jumpExplanation)});
 document.querySelectorAll('[data-outline-target]').forEach(b=>b.onclick=e=>{e.preventDefault();const id=b.dataset.outlineTarget;if(id.startsWith('course-slide-'))studyView.page=Number(id.slice(13));else studyView.sectionId=id.slice(15);rememberView();scrollCourse(id)});
 document.querySelectorAll('[data-reading-key]').forEach(box=>box.onchange=()=>{const values=read('course-read',{});values[box.dataset.readingKey]=box.checked;write('course-read',values)});
 $('#toggle-code-comments').hidden=studyView.mode!=='slides';document.body.classList.toggle('code-comments-on',read('slide-code-comments',false)===true);$('#toggle-code-comments').setAttribute('aria-pressed',String(read('slide-code-comments',false)===true));$('#toggle-code-comments').onclick=()=>{const enabled=document.body.classList.toggle('code-comments-on');write('slide-code-comments',enabled);$('#toggle-code-comments').setAttribute('aria-pressed',String(enabled))};
 $('#note-lesson').onclick=()=>StudyAnnotations.create({kind:'lesson',id:lesson.id+':lesson',origin:'lesson',sectionId:studyView.sectionId,fingerprint:'',label:lesson.title});
 let size=Number(read('course-font','17'));if(![15,17,19].includes(size))size=17;
 const font=()=>{document.documentElement.style.setProperty('--course-font',size+'px');$('#reader-smaller').disabled=size===15;$('#reader-larger').disabled=size===19;write('course-font',String(size))};font();
 $('#reader-smaller').onclick=()=>{size=Math.max(15,size-2);font()};$('#reader-larger').onclick=()=>{size=Math.min(19,size+2);font()};
 document.body.classList.toggle('compact-reading',read('course-density','normal')==='compact');document.body.classList.toggle('slides-reading',studyView.mode==='slides');$('#density-reader').onclick=()=>{const compact=document.body.classList.toggle('compact-reading');write('course-density',compact?'compact':'normal');$('#density-reader').setAttribute('aria-pressed',String(compact))};
 $('#focus-reader').onclick=()=>{document.body.classList.toggle('focus-reading');$('#focus-reader').setAttribute('aria-pressed',String(document.body.classList.contains('focus-reading')))};
 $('#toggle-outline').onclick=()=>{const open=$('#lesson-outline').classList.toggle('outline-open');$('#toggle-outline').setAttribute('aria-expanded',String(open));if(open)$('#lesson-outline a')?.focus({preventScroll:true})};
 $('#close-outline').onclick=()=>{$('#lesson-outline').classList.remove('outline-open');$('#toggle-outline').setAttribute('aria-expanded','false');$('#toggle-outline').focus()};
 $('#resume-reading').onclick=()=>scrollCourse(readingTarget());
 const destination=(pending?.view||saved.sectionId||saved.mode)?readingTarget():null;
 rememberView();renderPersonalCells();StudyAnnotations.decorate();
 requestAnimationFrame(()=>{if(destination&&!pending?.noteId&&!pending?.exampleId)scrollCourse(destination,'instant');StudyAnnotations.finishNavigation();trackCoursePosition()});
}
function changeStudy(update){
 const switched=update.mode&&update.mode!==studyView.mode;
 if(switched&&!('page' in update)&&update.mode==='slides'){const slide=currentCourse().slides.find(s=>s.sectionIds.includes(studyView.sectionId));if(slide)update={...update,page:slide.page}}
 if(switched&&!('sectionId' in update)&&update.mode==='topics'){const slide=currentCourse().slides.find(s=>s.page===studyView.page);if(slide)update={...update,sectionId:slide.sectionIds[0]}}
 studyView={...studyView,...update};rememberView();
 pendingStudyTarget={lessonId:lesson.id,view:{...studyView}};render();
}

function navigateStudy(lessonId,view,exampleId){pendingStudyTarget={lessonId,view,exampleId};tab='learn';if(lesson.id===lessonId)render();else location.hash=lessonId;}
function showCourseSearch(query){let host=document.querySelector('#course-search-results');if(!host){host=document.createElement('div');host.id='course-search-results';host.setAttribute('aria-label','Risultati della ricerca');document.querySelector('#sidebar .search').after(host)}if(!courseContent||query.length<2){host.hidden=true;return}const q=query.toLocaleLowerCase('it'),results=[];for(const l of courseContent.lessons){for(const section of l.sections){const body=section.blocks.map(b=>b.text).join(' ');if((section.title+' '+body).toLocaleLowerCase('it').includes(q))results.push({lessonId:l.id,title:section.title,type:'Argomento',view:{mode:'topics',sectionId:section.id},score:section.title.toLocaleLowerCase('it').includes(q)?5:1})}for(const slide of l.slides){if(slide.title.toLocaleLowerCase('it').includes(q))results.push({lessonId:l.id,title:slide.title,type:'Slide '+slide.page,view:{mode:'slides',page:slide.page},score:3})}const examples=catalog.lessons.find(x=>x.id===l.id).examples;for(const e of examples){if(e.title.toLocaleLowerCase('it').includes(q))results.push({lessonId:l.id,title:e.title,type:'Esempio',exampleId:e.id,view:{mode:'topics'},score:6})}}results.sort((a,b)=>b.score-a.score);host.hidden=false;host.innerHTML=`<p>${results.length} risultati · primi ${Math.min(12,results.length)}</p>`+results.slice(0,12).map((r,i)=>`<button data-search-result="${i}"><small>${esc(r.type)} · ${esc(r.lessonId)}</small><span>${esc(r.title.slice(0,110))}</span></button>`).join('');if(!results.length)host.innerHTML='<p>Nessun risultato. Prova un altro termine.</p>';host.querySelectorAll('[data-search-result]').forEach(b=>b.onclick=()=>{const r=results[Number(b.dataset.searchResult)];host.hidden=true;navigateStudy(r.lessonId,r.view,r.exampleId)});}

document.addEventListener('keydown',event=>{if(event.key==='Escape'&&document.querySelector('#lesson-outline.outline-open')){document.querySelector('#lesson-outline').classList.remove('outline-open');document.querySelector('#toggle-outline').setAttribute('aria-expanded','false');document.querySelector('#toggle-outline').focus()}});

function codeCommentLayer(slide){const comments=slide.guide?.comments||[];if(!comments.length)return '';return `<div class="code-guide-layer" aria-label="Commenti al codice della slide ${slide.page}">${comments.map((c,i)=>{const r=c.region;return `${c.inlineLabel?`<span class="code-guide-label" style="left:${Math.max(.6,r.x+r.w+.025)*100}%;top:${(r.y+r.h/2)*100}%">${esc(c.title)}</span>`:''}<div class="code-guide-region" style="left:${r.x*100}%;top:${r.y*100}%;width:${r.w*100}%;height:${r.h*100}%"></div><div class="code-guide-pin ${r.y>.65?'comment-up':''}" style="left:${Math.max(.006,r.x-.04)*100}%;top:${(r.y+r.h/2)*100}%"><button data-code-comment="${esc(c.id)}" aria-expanded="false" aria-label="Commento ${i+1}: ${esc(c.title)}">${i+1}</button><div class="code-guide-bubble" style="left:${(Math.min(.28,Math.max(.02,r.x-.1))-Math.max(.006,r.x-.04))*100}cqw" role="note"><strong>${esc(c.title)}</strong><p>${esc(c.text)}</p></div></div>`}).join('')}</div>`}
function exampleBridge(slide){const examples=slide.examples.map(id=>lesson.examples.find(e=>e.id===id)).filter(Boolean);if(!examples.length)return '';return `<section class="example-bridge" aria-label="Esempi dopo la slide ${slide.page}"><div class="bridge-heading"><span class="bridge-icon">⌘</span><div><p class="eyebrow">ORA PROVALO NEL CODICE</p><h3>Dalla slide ${slide.page} all’esempio del docente</h3><p>Apri il programma, segui i file e modifica il codice per verificare il comportamento.</p></div></div><div class="bridge-examples">${examples.map(e=>`<button data-course-example="${esc(e.id)}"><span><strong>${esc(e.title)}</strong><small>${e.expectedError?'Errore didattico atteso':e.root?'Esempio con ROOT':e.files.length+' file del progetto'}</small></span><span>Apri il codice →</span></button>`).join('')}</div></section>`}
document.addEventListener('click',event=>{const button=event.target.closest('[data-code-comment]');if(!button)return;const pin=button.closest('.code-guide-pin'),open=pin.classList.toggle('comment-expanded');button.setAttribute('aria-expanded',String(open))});
document.addEventListener('keydown',event=>{if(event.key==='Escape')document.querySelectorAll('.code-guide-pin.comment-expanded').forEach(pin=>{pin.classList.remove('comment-expanded');pin.querySelector('button').setAttribute('aria-expanded','false')})});
