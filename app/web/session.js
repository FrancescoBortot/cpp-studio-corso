'use strict';
(()=>{
 let incoming=null;
 const dialog=$('#session-dialog'),message=text=>{$('#session-message').textContent=text};
 $('#open-session').onclick=()=>{message('');$('#session-preview').hidden=true;dialog.showModal()};
 $('#close-session').onclick=()=>dialog.close();
 async function snapshot(){if(project)save();const notes=await StudyAnnotations.exportNotes();return{format:'cpp-studio-session',version:1,name:$('#session-name').value.trim()||'Sessione C++',created:new Date().toISOString(),courseRevision:courseContent.revision,storage:{...SessionStore.collect(localStorage),...(project?{['project-'+project.key]:JSON.stringify({activeFile,title:project.title,files:project.files,sources:[...sources],standard:$('#standard').value,stdin:$('#stdin').value,args:$('#args').value,defines:$('#defines').value,root:project.root,strict:$('#strict').checked})}:{})},notes,context:{lessonId:lesson.id,tab,projectId:!$('#lab').hidden&&project?project.id:null}};}
 $('#save-session').onclick=async()=>{try{const value=await snapshot();SessionStore.validate(value);downloadBytes('cpp-studio-sessione.json',new TextEncoder().encode(JSON.stringify(value,null,2)));message('Sessione salvata nel file scaricato. Contiene '+Object.keys(value.storage).filter(k=>k.startsWith('project-')).length+' progetti e '+value.notes.length+' appunti.')}catch(error){message('Salvataggio non riuscito: '+error.message)}};
 $('#load-session').onclick=()=>$('#session-file').click();
 $('#session-file').onchange=async event=>{try{const file=event.target.files[0];if(!file)return;if(file.size>50*1024*1024)throw Error('Dimensione massima: 50 MiB.');incoming=SessionStore.validate(JSON.parse(await file.text()));incoming.notes=incoming.notes.map(StudyStore.validate);if(!catalog.lessons.some(l=>l.id===incoming.context.lessonId))throw Error('La lezione della sessione non esiste in questo corso.');$('#session-summary').textContent=incoming.name+' · '+Object.keys(incoming.storage).filter(k=>k.startsWith('project-')).length+' progetti · '+incoming.notes.length+' appunti';$('#session-preview').hidden=false;message('Controlla il riepilogo, poi ripristina quando sei pronto.')}catch(error){incoming=null;$('#session-preview').hidden=true;message('Caricamento non riuscito: '+error.message)}finally{event.target.value=''}};
 $('#restore-session').onclick=async()=>{
  if(!incoming)return;if(busy){message('Arresta prima il programma in esecuzione.');return}
  const button=$('#restore-session');button.disabled=true;let rollback;
  try{
   if(project)save();await StudyAnnotations.exportNotes();
   rollback=SessionStore.apply(localStorage,incoming.storage);
   await StudyAnnotations.mergeNotes(incoming.notes);
   const loaded=read('cpp-state',{done:[],saved:[]});state.done=loaded.done;state.saved=loaded.saved;
   const context=incoming.context;$('#lab-home').append($('#lab'));project=null;tab=context.tab;$('#lab').hidden=true;closeProgramView();
   history.replaceState(null,'','#'+context.lessonId);load();
   if(context.projectId){const example=lesson.examples.find(e=>e.id===context.projectId),saved=read('project-'+lesson.id+'/'+context.projectId,null),personal=read('notebook-'+lesson.id,[]).find(c=>c.id===context.projectId);if(example)openExample(example);else if(personal)openProject(personal.id,personal.title,personal.files,personal.root,personal.note,personal.recipe);else if(saved)openProject(context.projectId,saved.title||context.projectId,saved.files,saved.root,'Progetto ripristinato dalla sessione.',{sources:saved.sources,standard:saved.standard});}
   incoming=null;dialog.close();
  }catch(error){if(rollback)rollback();message('Ripristino non riuscito: '+error.message)}finally{button.disabled=false}
 };
})();
