/* Notes are local, versioned and tied to source identities, never page pixels alone. */
(function(root,factory){const api=factory();if(typeof module==='object'&&module.exports)module.exports=api;else root.StudyStore=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const COLORS=['yellow','violet','green','pink'];
const bounded=(value,max=20000)=>typeof value==='string'?value.slice(0,max):'';
function rect(value){if(!value||['x','y','w','h'].some(k=>!Number.isFinite(value[k])))throw Error('Zona non valida');let x=Math.max(0,Math.min(1,value.x)),y=Math.max(0,Math.min(1,value.y));return{x,y,w:Math.max(0,Math.min(1-x,value.w)),h:Math.max(0,Math.min(1-y,value.h))};}
function validate(raw){
 if(!raw||typeof raw!=='object'||!raw.anchor||typeof raw.anchor!=='object')throw Error('Nota non valida');
 const a=raw.anchor;if(!['topic','block','slide','region','code','lesson'].includes(a.kind))throw Error('Tipo di riferimento non valido');
 if(typeof raw.lessonId!=='string'||!/^[a-z][a-z0-9_-]{0,79}$/.test(raw.lessonId))throw Error('Lezione non valida');
 if(typeof a.id!=='string'||!/^[\w:-]{1,180}$/.test(a.id))throw Error('Identificatore di riferimento non valido');
 const anchor={kind:a.kind,id:a.id,origin:['dispensa','slide','editorial','code','lesson'].includes(a.origin)?a.origin:'editorial',page:Number.isInteger(a.page)&&a.page>0?a.page:null,sectionId:bounded(a.sectionId,160),fingerprint:bounded(a.fingerprint,100),label:bounded(a.label,250)};
 if(a.quote?.exact?.length>8000)throw Error('Il passaggio selezionato supera 8000 caratteri');
 if(a.quote&&typeof a.quote.exact==='string')anchor.quote={exact:bounded(a.quote.exact,8000),prefix:bounded(a.quote.prefix,120),suffix:bounded(a.quote.suffix,120)};
 if(a.region)anchor.region=rect(a.region);
 if(a.kind==='region'&&(!anchor.region||anchor.region.w<.002||anchor.region.h<.002))throw Error('Seleziona una zona più grande');
 if(a.file)anchor.file=bounded(a.file,250);
 if(a.projectId)anchor.projectId=bounded(a.projectId,250);
 if(Number.isInteger(a.line)&&a.line>0)anchor.line=a.line;
 if(typeof raw.body==='string'&&raw.body.length>20000)throw Error('La nota supera 20000 caratteri');
 const now=new Date().toISOString();
 return{id:typeof raw.id==='string'&&/^[\w-]{1,100}$/.test(raw.id)?raw.id:crypto.randomUUID(),lessonId:raw.lessonId,anchor,body:bounded(raw.body),color:COLORS.includes(raw.color)?raw.color:'yellow',tags:[...new Set((Array.isArray(raw.tags)?raw.tags:[]).filter(t=>typeof t==='string').map(t=>t.trim().slice(0,60)).filter(Boolean))].slice(0,20),starred:raw.starred===true,trashed:raw.trashed===true,created:!Number.isNaN(Date.parse(raw.created))?raw.created:now,updated:!Number.isNaN(Date.parse(raw.updated))?raw.updated:now,courseRevision:bounded(raw.courseRevision,100)};
}
function resolveQuote(text,quote){
 if(!quote?.exact)return{status:'missing'};
 let hits=[],at=text.indexOf(quote.exact);
 while(at!==-1){let before=text.slice(0,at),after=text.slice(at+quote.exact.length);let score=0;if(quote.prefix&&before.endsWith(quote.prefix))score+=2;if(quote.suffix&&after.startsWith(quote.suffix))score+=2;hits.push({start:at,end:at+quote.exact.length,score});at=text.indexOf(quote.exact,at+1)}
 if(!hits.length)return{status:'missing'};
 hits.sort((a,b)=>b.score-a.score);if(hits.length>1&&hits[0].score===hits[1].score)return{status:'ambiguous'};
 return{status:hits.length===1?'exact':'context',start:hits[0].start,end:hits[0].end};
}
function importBundle(value,existing=[]){
 if(!value||value.format!=='cpp-studio-study'||value.version!==1||!Array.isArray(value.notes)||value.notes.length>10000)throw Error('Backup non riconosciuto o versione non supportata');
 const notes=value.notes.map(validate),result=new Map(existing.map(n=>[n.id,n]));let added=0,duplicates=0,conflicts=0;
 for(let note of notes){const prior=result.get(note.id);if(!prior){result.set(note.id,note);added++;continue}if(JSON.stringify({...prior,updated:''})===JSON.stringify({...note,updated:''})){duplicates++;continue}note={...note,id:crypto.randomUUID(),tags:[...new Set([...note.tags,'importata'])]};result.set(note.id,note);added++;conflicts++;}
 return{notes:[...result.values()],added,duplicates,conflicts};
}
function backup(notes,revision,extra={}){return{format:'cpp-studio-study',version:1,exportedAt:new Date().toISOString(),courseRevision:revision,notes:notes.map(validate),study:extra};}
const mdText=value=>String(value).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
function markdown(notes,titles={}){return'# Appunti del corso C++\n\n'+notes.filter(n=>!n.trashed).map(n=>{let a=n.anchor;return'## '+mdText(Object.hasOwn(titles,n.lessonId)?titles[n.lessonId]:n.lessonId)+' · '+mdText(a.label)+'\n\n'+(a.quote?.exact?'> '+mdText(a.quote.exact).replace(/\n/g,'\n> ')+'\n\n':'')+mdText(n.body||'_Evidenziazione senza nota testuale._')+'\n\nFonte: '+a.origin+(a.page?' · pagina '+a.page:'')+(a.file?' · '+mdText(a.file)+(a.line?':'+a.line:''):'')+(a.region?' · zona normalizzata '+JSON.stringify(a.region):'')+'\n\n'+(n.tags.length?'Tag: '+n.tags.map(mdText).join(', ')+'\n\n':'');}).join('---\n\n');}
class Repository{
 constructor(){this.db=null;}
 async open(){if(this.db)return this;this.db=await new Promise((resolve,reject)=>{const request=indexedDB.open('cpp-studio-study',1);request.onupgradeneeded=()=>{const db=request.result;if(!db.objectStoreNames.contains('notes')){let store=db.createObjectStore('notes',{keyPath:'id'});store.createIndex('lessonId','lessonId')}};request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(Error('Archivio appunti non disponibile: '+request.error?.message));request.onblocked=()=>reject(Error('Chiudi altre schede del corso per aggiornare l’archivio degli appunti.'));});this.db.onversionchange=()=>{this.db.close();this.db=null;};return this;}
 async transaction(mode,operation){await this.open();return new Promise((resolve,reject)=>{const tx=this.db.transaction('notes',mode);const request=operation(tx.objectStore('notes'));let value;request.onsuccess=()=>{value=request.result};tx.oncomplete=()=>resolve(value);tx.onerror=()=>reject(Error('Salvataggio non riuscito: '+tx.error?.message));tx.onabort=()=>reject(Error('Salvataggio annullato: '+tx.error?.message));});}
 async all(){return this.transaction('readonly',store=>store.getAll());}
 async put(note){let clean=validate(note);await this.transaction('readwrite',store=>store.put(clean));return clean;}
 async merge(notes){const validated=notes.map(validate);await this.open();return new Promise((resolve,reject)=>{const tx=this.db.transaction('notes','readwrite'),store=tx.objectStore('notes');for(const n of validated)store.put(n);tx.oncomplete=()=>resolve();tx.onerror=()=>reject(Error('Importazione non riuscita: '+tx.error?.message));tx.onabort=()=>reject(Error('Importazione annullata.'));});}
}
return{COLORS,rect,validate,resolveQuote,importBundle,backup,markdown,Repository};
});
