'use strict';
const filenames = {breakdown:'视频拆解报告',compare:'视频差距表',script:'商品拍摄脚本'};
const commands = {
  claude: 'mkdir -p ~/.claude/skills\ngit clone https://github.com/guojunyu12/ecom-video-breakdown.git \\\n  ~/.claude/skills/ecom-video-breakdown',
  codex: 'mkdir -p ~/.agents/skills\ngit clone https://github.com/guojunyu12/ecom-video-breakdown.git \\\n  ~/.agents/skills/ecom-video-breakdown'
};
let selectedAgent = 'claude';
let toastTimer;
function selectTab(button,group){
  group.querySelectorAll('[role="tab"]').forEach(tab=>{
    const active=tab===button;
    tab.setAttribute('aria-selected',String(active));
    tab.tabIndex=active?0:-1;
  });
  if(button.dataset.output){
    const key=button.dataset.output;
    document.querySelectorAll('.output-panel').forEach(panel=>{panel.hidden=panel.id!==`output-${key}`;});
    document.getElementById('output-filename').textContent=filenames[key];
  }else{
    selectedAgent=button.dataset.agent;
    document.getElementById('install-command').textContent=commands[selectedAgent];
    document.getElementById('install-code').setAttribute('aria-labelledby',button.id);
    document.querySelector('#copy-install span').textContent='复制安装命令';
  }
}
document.querySelectorAll('[role="tablist"]').forEach(group=>{
  const tabs=Array.from(group.querySelectorAll('[role="tab"]'));
  tabs.forEach((button,index)=>{
    button.addEventListener('click',()=>selectTab(button,group));
    button.addEventListener('keydown',event=>{
      let next;
      if(event.key==='ArrowRight')next=(index+1)%tabs.length;
      if(event.key==='ArrowLeft')next=(index-1+tabs.length)%tabs.length;
      if(event.key==='Home')next=0;
      if(event.key==='End')next=tabs.length-1;
      if(next!==undefined){event.preventDefault();selectTab(tabs[next],group);tabs[next].focus();}
    });
  });
});
function toast(message){
  const element=document.getElementById('toast');
  element.textContent=message;element.classList.add('visible');
  clearTimeout(toastTimer);toastTimer=setTimeout(()=>element.classList.remove('visible'),3000);
}
document.getElementById('copy-install').addEventListener('click',async()=>{
  try{
    await navigator.clipboard.writeText(commands[selectedAgent]);
    document.querySelector('#copy-install span').textContent='已复制';
    toast('安装命令已复制，粘贴到终端即可。');
  }catch{
    const range=document.createRange();range.selectNodeContents(document.getElementById('install-command'));
    const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);
    toast('浏览器未允许自动复制，命令已选中，请按 Ctrl/Cmd + C。');
  }
});
