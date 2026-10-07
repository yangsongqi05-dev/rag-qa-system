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
  var useAgent = document.getElementById('useAgent').checked;

  box.value = '';
  box.style.height = 'auto';

  addMsg('user', q);

  // 先放一条空的 AI 消息，里面显示"三个点"的等待动画
  var answerMsg = addMsg('bot', '');
  var body = answerMsg.querySelector('.body');
  body.innerHTML = '<span class="thinking"><i></i><i></i><i></i></span>';

  document.getElementById('send').disabled = true;

  // ---------- 路线零：Agent 模式（勾了就整条换掉，不走向下走） ----------
  if (useAgent) {
    askAgent(q, answerMsg, body);
    return;
  }

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

// ==================== Agent 模式 ====================

// 走 Agent 接口：由模型自己决定要不要查资料
function askAgent(q, answerMsg, body) {
  fetch('/agent?q=' + encodeURIComponent(q))
    .then(function (r) { return r.json(); })
    .then(function (d) {
      body.textContent = d.answer;
      showSteps(answerMsg, d.steps);
      document.getElementById('send').disabled = false;
      scrollBottom();
    })
    .catch(function () {
      body.textContent = '（Agent 接口连不上：确认 serve.py 已启动，并且 main.py 里加了 /agent）';
      document.getElementById('send').disabled = false;
    });
}

// 把 Agent 的执行过程画出来
function showSteps(answerMsg, steps) {
  if (!steps || steps.length === 0) return;

  // 整条轨迹里没有一次工具调用，说明 Agent 直接回答了，没什么可展示的
  var hasTool = false;
  for (var i = 0; i < steps.length; i++) {
    if (steps[i].type === 'tool_call') hasTool = true;
  }
  if (!hasTool) return;

  var wrap = document.createElement('div');
  wrap.className = 'steps';

  var title = document.createElement('div');
  title.className = 'steps-title';
  title.textContent = '▾ Agent 执行过程（' + steps.length + ' 步）';
  wrap.appendChild(title);

  for (var k = 0; k < steps.length; k++) {
    var s = steps[k];
    var row = document.createElement('div');
    row.className = 'step';

    var tag = document.createElement('span');
    tag.className = 'tag';
    tag.textContent = s.type === 'tool_call'   ? '调用工具'
                    : s.type === 'tool_result' ? '工具返回'
                    : '生成回答';
    row.appendChild(tag);

    var txt = document.createElement('span');
    if (s.type === 'tool_call') {
      txt.textContent = s.name + '（' + JSON.stringify(s.args) + '）';
    } else if (s.type === 'tool_result') {
      txt.textContent = s.text + ' …';
    } else {
      txt.textContent = '基于上面查到的资料作答';
    }
    row.appendChild(txt);

    wrap.appendChild(row);
  }

  answerMsg.querySelector('.bubble').appendChild(wrap);
}
