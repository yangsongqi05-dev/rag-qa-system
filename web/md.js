// ==================== 极简 Markdown 渲染 ====================
// 模型返回的答案里带 ** 粗体 ** 、### 小标题、- 列表这些语法，
// 如果直接塞进页面就会看到一堆星号和井号。
// 这里手写一个最小的渲染器：只认这几种语法，够用就行，不引第三方库。

// 第一步：把 & < > 换成 HTML 实体
// 为什么必须先做：答案是模型生成的，里面可能出现 < 或 >，
// 浏览器会把它们当成标签的开头，直接把页面结构搞坏（这就是 XSS 漏洞的原理）
function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');
}

// 第二步：处理「行内」语法 —— **粗体** 和 `代码`
// 为什么叫行内：它们出现在一句话里面，不单独占一行
function mdInline(s) {
  return s
    .replace(/\*\*(.+?)\*\*/g, '<b>$1</b>')
    .replace(/`([^`]+)`/g, '<code>$1</code>');
}

// 第三步：一行一行地判断，拼成 HTML
function mdToHtml(text) {
  var lines = escapeHtml(text).split('\n');
  var html = '';
  var inList = false;   // 记录现在是不是「正在一个列表里面」

  for (var i = 0; i < lines.length; i++) {
    var line = lines[i];

    // 列表项：- xxx  或者  1. xxx（前面有空格说明是子项）
    var lm = line.match(/^(\s*)(?:[-*]|\d+\.)\s+(.*)$/);
    if (lm) {
      if (!inList) { html += '<ul>'; inList = true; }   // 列表刚开头，补一个 <ul>
      var sub = lm[1].length >= 2 ? ' class="sub"' : '';
      html += '<li' + sub + '>' + mdInline(lm[2]) + '</li>';
      continue;
    }

    // 走到这里说明列表结束了，补上 </ul>
    if (inList) { html += '</ul>'; inList = false; }

    // 小标题：### xxx（模型爱用 ###，标题级别统一按 h4 画）
    var hm = line.match(/^#{1,6}\s+(.*)$/);
    if (hm) { html += '<h4>' + mdInline(hm[1]) + '</h4>'; continue; }

    if (line.trim() === '') continue;   // 空行只用来分段，不输出

    html += '<p>' + mdInline(line) + '</p>';
  }

  if (inList) html += '</ul>';   // 最后一行还是列表项的话，收个尾

  return html;
}
