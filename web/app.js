// ==================== 消息列表操作 ====================

// 往聊天区追加一条消息，返回这条消息的 DOM 节点
function addMsg(role, text) {
  var chat = document.getElementById('chat');

  // 第一条消息来了，就把欢迎页去掉
  var welcome = document.getElementById('welcome');
  if (welcome) welcome.remove();

  var div = document.createElement('div');
  div.className = 'msg ' + role;

  var avatar = role === 'user' ? '🙋' : '🤖';
  var who = role === 'user' ? '你' : '数据库课程助手';

  div.innerHTML =
    '<div class="avatar">' + avatar + '</div>' +
    '<div class="bubble">' +
      '<div class="who">' + who + '</div>' +
      '<div class="body"></div>' +
    '</div>';

  chat.appendChild(div);
  div.querySelector('.body').textContent = text;
  scrollBottom();
  return div;
}

// 滚到最底下
function scrollBottom() {
  var chat = document.getElementById('chat');
  chat.scrollTop = chat.scrollHeight;
}

// 回车发送，Shift+回车换行
function onKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    ask();
  }
}

// 把「依据的资料」插进某条消息下面
function showSources(answerMsg, sources) {
  var html = '<div class="srcs"><div class="srcs-title">▾ 依据的资料 ' + sources.length + ' 条</div>';
  for (var i = 0; i < sources.length; i++) {
    html += '<div class="src-item">' +
              '<span class="score">' + sources[i].score + '</span>' +
              '<span>' + sources[i].text + '</span>' +
            '</div>';
  }
  html += '</div>';
  answerMsg.querySelector('.bubble').insertAdjacentHTML('beforeend', html);
}

// ==================== 提问主流程 ====================

function ask() {
  var box = document.getElementById('q');
  var q = box.value.trim();
  if (q === '') return;

  var topk = document.getElementById('topk').value;
  var useRerank = document.getElementById('rerank').checked;

  box.value = '';
  box.style.height = 'auto';

  addMsg('user', q);

  // 先放一条空的 AI 消息，里面显示"三个点"的等待动画
  var answerMsg = addMsg('bot', '');
  var body = answerMsg.querySelector('.body');
  body.innerHTML = '<span class="thinking"><i></i><i></i><i></i></span>';

  document.getElementById('send').disabled = true;

  var params = '&top_k=' + topk + '&use_rerank=' + useRerank;
  var started = false;    // 第一段文字到了没有
  var finished = false;   // 整个流程结束了没有（防止重复请求）
  var srcHtml = '';

  // ---------- 路线一：流式（后端有 /ask_stream 时走这条） ----------
  var es = new EventSource('/ask_stream?q=' + encodeURIComponent(q) + params);

  es.onmessage = function (e) {
    var d = JSON.parse(e.data);

    if (d.type === 'sources') {
      // 最先到：检索到的几段依据，先攒着
      srcHtml = '<div class="srcs"><div class="srcs-title">▾ 依据的资料 ' + d.sources.length + ' 条</div>';
      for (var i = 0; i < d.sources.length; i++) {
        srcHtml += '<div class="src-item">' +
                     '<span class="score">' + d.sources[i].score + '</span>' +
                     '<span>' + d.sources[i].text + '</span>' +
                   '</div>';
      }
      srcHtml += '</div>';

    } else if (d.type === 'text') {
      if (!started) { body.textContent = ''; started = true; }
      body.textContent += d.text;
      scrollBottom();

    } else if (d.type === 'done') {
      finished = true;
      if (srcHtml) answerMsg.querySelector('.bubble').insertAdjacentHTML('beforeend', srcHtml);
      es.close();
      document.getElementById('send').disabled = false;
      scrollBottom();
    }
  };

  es.onerror = function () {
    es.close();
    if (finished) return;      // 已经正常结束了，不是错误
    finished = true;

    // ---------- 路线二：降级到普通接口（后端还没有 /ask_stream 时走这条） ----------
    fetch('/ask?q=' + encodeURIComponent(q) + params)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        body.textContent = data.answer;
        showSources(answerMsg, data.sources);
        document.getElementById('send').disabled = false;
        scrollBottom();
      })
      .catch(function () {
        body.textContent = '（连不上服务，请确认 serve.py 已经启动）';
        document.getElementById('send').disabled = false;
      });
  };
}

// ==================== 输入框自动长高 ====================

var ta = document.getElementById('q');
ta.addEventListener('input', function () {
  ta.style.height = 'auto';
  ta.style.height = Math.min(ta.scrollHeight, 140) + 'px';
});
