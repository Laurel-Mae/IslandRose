(function(){
  const field=document.querySelector('.petal-field');
  if(field){
    for(let i=0;i<34;i++){
      const p=document.createElement('span'); p.className='petal';
      p.style.left=Math.random()*100+'%'; p.style.animationDelay=(-Math.random()*18)+'s';
      p.style.animationDuration=(12+Math.random()*12)+'s'; p.style.transform='rotate('+Math.random()*180+'deg)';
      p.style.opacity=(.25+Math.random()*.55).toFixed(2); p.style.width=(8+Math.random()*10)+'px'; p.style.height=(5+Math.random()*8)+'px';
      field.appendChild(p);
    }
  }
  setTimeout(()=>document.querySelectorAll('.flash').forEach(x=>x.classList.add('hide')),3500);
})();
