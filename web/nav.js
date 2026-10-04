// 顶部导航栏：所有页面共用，避免每个页面抄一遍
var PAGES = [
  ['/web/home.html', '首页'],
  ['/', '智能问答'],
  ['/web/history.html', '历史记录'],
  ['/web/kb.html', '知识库'],
  ['/web/eval.html', '实验数据'],
  ['/web/about.html', '系统说明']
];

(function () {
  var here = location.pathname;
  if (here === '' || here === '/web/index.html') here = '/';

  var html = '<div class="nav-brand">🤖 数据库课程智能问答助手</div><nav class="nav-links">';
  for (var i = 0; i < PAGES.length; i++) {
    var cls = (PAGES[i][0] === here) ? ' class="active"' : '';
    html += '<a href="' + PAGES[i][0] + '"' + cls + '>' + PAGES[i][1] + '</a>';
  }
  html += '</nav>';

  var box = document.getElementById('nav');
  if (box) box.innerHTML = html;
})();
