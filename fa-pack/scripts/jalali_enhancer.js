(function(){
"use strict";
if(window.__faJalaliEnhancer) return; window.__faJalaliEnhancer=true;
var M=["\u0641\u0631\u0648\u0631\u062f\u06cc\u0646","\u0627\u0631\u062f\u06cc\u0628\u0647\u0634\u062a","\u062e\u0631\u062f\u0627\u062f","\u062a\u06cc\u0631","\u0645\u0631\u062f\u0627\u062f","\u0634\u0647\u0631\u06cc\u0648\u0631","\u0645\u0647\u0631","\u0622\u0628\u0627\u0646","\u0622\u0630\u0631","\u062f\u06cc","\u0628\u0647\u0645\u0646","\u0627\u0633\u0641\u0646\u062f"];
var W=["\u0634","\u06cc","\u062f","\u0633","\u0686","\u067e","\u062c"];
var BR=[-61,9,38,199,426,686,756,818,1111,1181,1210,1635,2060,2097,2192,2262,2324,2394,2456,3178];
function dv(a,b){return Math.trunc(a/b)}function md(a,b){return a-Math.trunc(a/b)*b}
function jalCal(jy){var bl=BR.length,gy=jy+621,lj=-14,jp=BR[0],jm=0,jump=0,i,n,lg,mrch,lp;
if(jy<jp||jy>=BR[bl-1])throw new Error("bad jy");
for(i=1;i<bl;i++){jm=BR[i];jump=jm-jp;if(jy<jm)break;lj=lj+dv(jump,33)*8+dv(md(jump,33),4);jp=jm}
n=jy-jp;lj=lj+dv(n,33)*8+dv(md(n,33)+3,4);if(md(jump,33)===4&&jump-n===4)lj+=1;
lg=dv(gy,4)-dv((dv(gy,100)+1)*3,4)-150;mrch=20+lj-lg;
if(jump-n<6)n=n-jump+dv(jump+4,33)*33;lp=md(md(n+1,33)-1,4);if(lp===-1)lp=4;
return{leap:lp,gy:gy,march:mrch}}
function g2d(gy,gm,gd){var d=dv((gy+dv(gm-8,6)+100100)*1461,4)+dv(153*md(gm+9,12)+2,5)+gd-34840408;
d=d-dv(dv(gy+100100+dv(gm-8,6),100)*3,4)+752;return d}
function d2g(j){var i,gd,gm,gy;j=4*j+139361631;j=j+dv(dv(4*(j-139361631)/4+183187720,146097)*3,4)*4-3908;
i=dv(md(j,1461),4)*5+308;gd=dv(md(i,153),5)+1;gm=md(dv(i,153),12)+1;gy=dv(j,1461)-100100+dv(8-gm,6);
return{gy:gy,gm:gm,gd:gd}}
function j2d(jy,jm,jd){var r=jalCal(jy);return g2d(r.gy,3,r.march)+(jm-1)*31-dv(jm,7)*(jm-7)+jd-1}
function d2j(jdn){var gy=d2g(jdn).gy,jy=gy-621,r=jalCal(jy),j1=g2d(gy,3,r.march),k=jdn-j1,jm,jd;
if(k>=0){if(k<=185){jm=1+dv(k,31);jd=md(k,31)+1;return{jy:jy,jm:jm,jd:jd}}k-=186}
else{jy-=1;k+=179;if(r.leap===1)k+=1}
jm=7+dv(k,30);jd=md(k,30)+1;return{jy:jy,jm:jm,jd:jd}}
var fmt;try{fmt=new Intl.DateTimeFormat("en-u-ca-persian-nu-latn",{year:"numeric",month:"numeric",day:"numeric",timeZone:"UTC"})}catch(e){fmt=null}
function intlJ(gy,gm,gd){if(!fmt)return null;var p=fmt.formatToParts(new Date(Date.UTC(gy,gm-1,gd,12))),o={};
p.forEach(function(x){if(x.type!=="literal")o[x.type]=Number(String(x.value).replace(/[^0-9]/g,""))});
return o.year?{jy:o.year,jm:o.month,jd:o.day}:null}
function toJ(gy,gm,gd){var j=d2j(g2d(gy,gm,gd)),w=intlJ(gy,gm,gd);
if(!w||w.jy>3178||w.jy<-61)return j;
for(var i=0;i<3;i++){if(j.jy===w.jy&&j.jm===w.jm&&j.jd===w.jd)break;
var step=j2d(w.jy,w.jm,w.jd)-j2d(j.jy,j.jm,j.jd);var g=d2g(g2d(gy,gm,gd)+step);j=d2j(g2d(g.gy,g.gm,g.gd))}
return j}
function toG(jy,jm,jd){var g=d2g(j2d(jy,jm,jd)),w=intlJ(g.gy,g.gm,g.gd);
if(w&&w.jy===jy&&w.jm===jm&&w.jd===jd)return g;
var lo=j2d(jy,jm,jd)-40,hi=j2d(jy,jm,jd)+40;
if(!fmt)return g;
while(lo<hi){var mid=(lo+hi)>>1,o=intlJ(d2g(mid).gy,d2g(mid).gm,d2g(mid).gd);
if(!o||j2d(o.jy,o.jm,o.jd)<j2d(jy,jm,jd))lo=mid+1;else hi=mid}
var hit=intlJ(d2g(lo).gy,d2g(lo).gm,d2g(lo).gd);
if(hit&&hit.jy===jy&&hit.jm===jm&&hit.jd===jd)return d2g(lo);return g}
function isoToJ(s){var m=/^(\d{4})-(\d{2})-(\d{2})/.exec(s||"");if(!m)return null;return toJ(+m[1],+m[2],+m[3])}
function jToIso(jy,jm,jd){var g=toG(jy,jm,jd);function p(n){return String(n).padStart(2,"0")}return g.gy+"-"+p(g.gm)+"-"+p(g.gd)}
function mLen(jy,jm){var ny=jm===12?jy+1:jy,nm=jm===12?1:jm+1;return j2d(ny,nm,1)-j2d(jy,jm,1)}
function wd(jy,jm,jd){var g=toG(jy,jm,jd);return (new Date(Date.UTC(g.gy,g.gm-1,g.gd,12)).getUTCDay()+1)%7}
function fmtJ(iso){var j=isoToJ(iso);return j?j.jd+" "+M[j.jm-1]+" "+j.jy:""}
function pd(x){return String(x).replace(/[0-9]/g,function(d){return "\u06f0\u06f1\u06f2\u06f3\u06f4\u06f5\u06f6\u06f7\u06f8\u06f9"[d]})}
var pop=null,cur=null,cleanups=[];
function cleanup(f){cleanups.push(f)}
function close(){if(pop){pop.remove();pop=null;cur=null;cleanups.forEach(function(f){f()});cleanups.length=0}}
function build(input){
close();cur=input;
var val=input.value||"";var sel=isoToJ(val)||isoToJ(new Date().toISOString().slice(0,10))||{jy:1404,jm:1,jd:1};
var view={jy:sel.jy,jm:sel.jm};
var r=input.getBoundingClientRect();var Wd=272;
var left=Math.min(Math.max(8,r.left),window.innerWidth-Wd-8);
var top=r.bottom+6; if(top+330>window.innerHeight) top=Math.max(8,r.top-336);
pop=document.createElement("div");
pop.dir="rtl";
pop.style.cssText="position:fixed;z-index:99999;width:"+Wd+"px;border-radius:12px;border:1px solid var(--border);background:var(--popover);color:var(--popover-foreground);padding:8px;font-size:13px;box-shadow:0 10px 30px rgba(0,0,0,.18);font-family:inherit";
function render(){
var fw=wd(view.jy,view.jm,1),len=mLen(view.jy,view.jm),html="";
html+='<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px">';
html+='<button type="button" data-a="prev" style="all:unset;cursor:pointer;padding:2px 8px;border-radius:6px">&#8250;</button>';
html+='<span style="font-weight:600">'+M[view.jm-1]+" "+pd(view.jy)+"</span>";
html+='<button type="button" data-a="next" style="all:unset;cursor:pointer;padding:2px 8px;border-radius:6px">&#8249;</button>';
html+="</div>";
html+='<div style="display:grid;grid-template-columns:repeat(7,1fr);text-align:center;font-size:11px;opacity:.6">';
for(var i=0;i<7;i++)html+="<span>"+W[i]+"</span>";html+="</div>";
html+='<div style="display:grid;grid-template-columns:repeat(7,1fr);text-align:center;row-gap:2px">';
for(var k=0;k<fw;k++)html+="<span></span>";
var todayIso=new Date().toISOString().slice(0,10);
for(var d=1;d<=len;d++){var iso=jToIso(view.jy,view.jm,d);
var selStyle=(iso===val)?"background:var(--primary);color:var(--primary-foreground);":"";
html+='<button type="button" data-d="'+iso+'" style="all:unset;cursor:pointer;'+selStyle+'display:inline-block;width:28px;height:28px;line-height:28px;border-radius:8px;text-align:center">'+pd(d)+"</button>"}
html+="</div>";
html+='<div style="display:flex;justify-content:space-between;border-top:1px solid var(--border);margin-top:4px;padding-top:4px;font-size:12px;opacity:.8">';
html+='<button type="button" data-a="today" style="all:unset;cursor:pointer;padding:2px 6px;border-radius:6px">\u0627\u0645\u0631\u0648\u0632</button>';
html+='<button type="button" data-a="clear" style="all:unset;cursor:pointer;padding:2px 6px;border-radius:6px">\u067e\u0627\u06a9 \u06a9\u0631\u062f\u0646</button>';
html+="</div>";
pop.innerHTML=html}
render();
pop.addEventListener("click",function(e){
var b=e.target.closest("button");if(!b)return;
var a=b.getAttribute("data-a"),d=b.getAttribute("data-d");
if(a==="prev"){view.jm--;if(view.jm<1){view.jm=12;view.jy--}render();return}
if(a==="next"){view.jm++;if(view.jm>12){view.jm=1;view.jy++}render();return}
if(a==="today"){set(new Date().toISOString().slice(0,10));return}
if(a==="clear"){set("");return}
if(d)set(d)});
function set(iso){
var proto=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,"value");
if(proto&&proto.set)proto.set.call(input,iso);else input.value=iso;
input.dispatchEvent(new Event("input",{bubbles:true}));
input.dispatchEvent(new Event("change",{bubbles:true}));
close()}
document.body.appendChild(pop);
document.addEventListener("mousedown",outside,true);
document.addEventListener("keydown",esc,true);
cleanup(function(){document.removeEventListener("mousedown",outside,true);document.removeEventListener("keydown",esc,true)});
function outside(e){if(pop&&!pop.contains(e.target)&&e.target!==input)close()}
function esc(e){if(e.key==="Escape")close()}
var obs=new MutationObserver(function(){if(!document.contains(pop)){obs.disconnect();document.removeEventListener("mousedown",outside,true);document.removeEventListener("keydown",esc,true);cleanups.forEach(function(f){f()});cleanups.length=0}});
obs.observe(document.body,{childList:true,subtree:true});
}
function active(){return document.documentElement.lang==="fa"}
document.addEventListener("click",function(e){
if(!active())return;
var t=e.target;
if(!(t&&t.tagName==="INPUT"&&t.type==="date"))return;
if(t.readOnly||t.disabled)return;
e.preventDefault();
build(t)},true);
document.addEventListener("keydown",function(e){
if(!active())return;
var t=e.target;
if(!(t&&t.tagName==="INPUT"&&t.type==="date"))return;
if(t.readOnly||t.disabled)return;
if(e.key===" "||e.key==="Enter"){e.preventDefault();build(t)}},true);
})();