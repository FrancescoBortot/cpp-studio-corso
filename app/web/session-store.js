(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.SessionStore=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const allowed=key=>/^(?:project-[a-z][a-z0-9_-]*\/.{1,300}|notebook-[a-z][a-z0-9_-]*|notes-[a-z][a-z0-9_-]*|course-location-[a-z][a-z0-9_-]*|cpp-state|course-read|course-font|course-density|course-view-preference|slide-code-comments)$/.test(key);
const plain=value=>value&&typeof value==='object'&&!Array.isArray(value);
function validateProject(project){
 if(!plain(project)||!plain(project.files)||!Object.keys(project.files).length)throw Error('Progetto senza file');
 if(Object.keys(project.files).length>500)throw Error('Troppi file nel progetto');
 for(const [name,body] of Object.entries(project.files))if(!/^[\w./-]+$/.test(name)||name.includes('..')||name.startsWith('/')||['__proto__','constructor','prototype'].includes(name)||typeof body!=='string'||body.length>8*1024*1024)throw Error('File della sessione non valido');
 if(!Array.isArray(project.sources)||project.sources.some(f=>typeof f!=='string'||!Object.hasOwn(project.files,f)))throw Error('Sorgenti della sessione non validi');
 if(project.standard&&!['c++98','c++03','c++11','c++14','c++17','c++20','c++23'].includes(project.standard))throw Error('Standard non valido');
 for(const field of ['stdin','args','defines','activeFile','title'])if(project[field]!==undefined&&typeof project[field]!=='string')throw Error('Opzione di progetto non valida');
 if(project.activeFile&&!Object.hasOwn(project.files,project.activeFile))throw Error('File attivo assente');
 for(const field of ['root','strict'])if(project[field]!==undefined&&typeof project[field]!=='boolean')throw Error('Opzione di compilazione non valida');
 return project;
}
function validate(value){
 if(!plain(value)||value.format!=='cpp-studio-session'||value.version!==1||!plain(value.storage)||!Array.isArray(value.notes)||value.notes.length>10000)throw Error('File sessione non riconosciuto');
 const storage=Object.create(null);if(Object.keys(value.storage).length>10000)throw Error('Sessione troppo grande');
 for(const [key,raw] of Object.entries(value.storage)){
  if(!allowed(key)||typeof raw!=='string')throw Error('Impostazione non riconosciuta: '+key);
  let parsed;try{parsed=JSON.parse(raw)}catch{throw Error('Dato sessione non valido: '+key)}
  if(key.startsWith('project-'))validateProject(parsed);
  else if(key.startsWith('notebook-')){if(!Array.isArray(parsed))throw Error('Celle personali non valide');for(const cell of parsed){if(!plain(cell)||typeof cell.id!=='string'||!/^scratch-\d+$/.test(cell.id)||typeof cell.title!=='string'||!plain(cell.files))throw Error('Cella personale non valida');validateProject({...cell,sources:Object.keys(cell.files).filter(f=>/\.(cc|cpp|c)$/.test(f))});}}
  else if(key==='cpp-state'){if(!plain(parsed)||!['done','saved'].every(k=>Array.isArray(parsed[k])&&parsed[k].every(id=>typeof id==='string'&&/^[a-z][a-z0-9_-]*$/.test(id))))throw Error('Avanzamento non valido')}
  else if(key==='course-read'){if(!plain(parsed)||Object.entries(parsed).some(([k,v])=>!/^[a-z][a-z0-9_-]*:(topics|slides):[\w.-]+$/.test(k)||typeof v!=='boolean'))throw Error('Stato di lettura non valido')}
  else if(key.startsWith('course-location-')){if(!plain(parsed)||!['topics','slides'].includes(parsed.mode)||typeof parsed.sectionId!=='string'||!Number.isInteger(parsed.page)||parsed.page<1)throw Error('Posizione non valida')}
  else if(key==='course-font'){if(!['15','17','19'].includes(String(parsed)))throw Error('Dimensione non valida')}
  else if(key==='course-view-preference'){if(!['topics','slides'].includes(parsed))throw Error('Vista non valida')}
  else if(key==='slide-code-comments'){if(typeof parsed!=='boolean')throw Error('Commenti codice non validi')}
  else if(key==='course-density'){if(!['normal','compact'].includes(parsed))throw Error('Densita non valida')}
  else if(typeof parsed!=='string')throw Error('Appunto precedente non valido');
  storage[key]=raw;
 }
 const context=value.context||{};if(!plain(context)||!['learn','examples','sources'].includes(context.tab)||typeof context.lessonId!=='string'||!/^[a-z][a-z0-9_-]*$/.test(context.lessonId)||context.projectId!==null&&context.projectId!==undefined&&typeof context.projectId!=='string')throw Error('Posizione della sessione non valida');
 return{format:value.format,version:1,name:typeof value.name==='string'?value.name.slice(0,100):'Sessione C++',created:value.created,storage,notes:value.notes,context:{lessonId:context.lessonId,tab:context.tab,projectId:context.projectId||null}};
}
function collect(storage){const result=Object.create(null);for(let i=0;i<storage.length;i++){const key=storage.key(i);if(allowed(key))result[key]=storage.getItem(key)}return result;}
function apply(storage,entries){const before=Object.fromEntries(Object.keys(entries).map(key=>[key,storage.getItem(key)]));const rollback=()=>{for(const key of Object.keys(before))storage.removeItem(key);for(const [key,value] of Object.entries(before))if(value!==null)storage.setItem(key,value)};try{for(const [key,value] of Object.entries(entries))storage.setItem(key,value)}catch(error){rollback();throw error}return rollback;}
return{allowed,validateProject,validate,collect,apply};
});
