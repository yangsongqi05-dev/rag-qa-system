// ==================== 历史记录页 ====================

// 把 "2026-10-04 14:38:10" 裁成 "10-04 14:38"
function shortTime(s) {
  if (!s) return '';
  return s.slice(5, 16);
}

// 把一条记录画成一张卡片
function renderItem(item) {
  var card = document.createElement('div');
  card.className = 'card';

  // 头部：编号 + 时间
  var head = document.createElement('div');
  head.className = 'card-head';
  head.innerHTML = '<span class="tag">#' + item.id + '</span>' +
                   '<span class="muted">' + shortTime(item.created_at) + '</span>';
  card.appendChild(head);

  // 问题
  var q = document.createElement('div');
  q.className = 'q-line';
  q.textContent = 'Q：' + item.question;
  card.appendChild(q);

  // 回答
  var a = document.createElement('div');
  a.className = 'answer md';
  a.innerHTML = mdToHtml(item.answer || '（没有存到回答）');
  card.appendChild(a);

  // 依据的资料，默认收起来，点一下展开
  var sources = [];
  try {
    sources = JSON.parse(item.sources || '[]');
  } catch (e) {
    sources = [];
  }

  if (sources.length > 0) {
    var box = document.createElement('details');
    box.className = 'srcs-box';

    var sum = document.createElement('summary');
    sum.textContent = '▸ 依据的资料 ' + sources.length + ' 条';
    box.appendChild(sum);

    for (var i = 0; i < sources.length; i++) {
      var row = document.createElement('div');
      row.className = 'src';

      var txt = document.createElement('div');
      txt.className = 'pre';
      txt.textContent = sources[i];

      row.appendChild(txt);
      box.appendChild(row);
    }
    card.appendChild(box);
  }

  return card;
}

// 主流程：去后端要数据，然后画出来
function loadHistory() {
  var list = document.getElementById('list');
  var count = document.getElementById('count');

  count.textContent = '加载中…';
  list.innerHTML = '';

  fetch('/history?limit=20')
    .then(function (r) { return r.json(); })
    .then(function (data) {
      var items = data.items || [];

      if (items.length === 0) {
        count.textContent = '还没有任何记录';
        list.innerHTML = '<div class="note">数据库里还是空的。' +
          '去「智能问答」页面问一个问题，再回来点刷新就能看到了。</div>';
        return;
      }

      count.textContent = '共 ' + items.length + ' 条（最新的在最上面）';
      for (var i = 0; i < items.length; i++) {
        list.appendChild(renderItem(items[i]));
      }
    })
    .catch(function () {
      count.textContent = '';
      list.innerHTML = '<div class="note">读不到历史记录。' +
        '请确认后端服务已经启动（serve.py）。</div>';
    });
}

// 页面一打开就加载
loadHistory();
