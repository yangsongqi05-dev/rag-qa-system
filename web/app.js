// 会话编号存在浏览器里，刷新页面也保持不变
var THREAD_ID = localStorage.getItem('rag_thread_id');
if (!THREAD_ID) {
  THREAD_ID = 'th-' + Date.now() + '-' + Math.random().toString(36).slice(2, 8);
  localStorage.setItem('rag_thread_id', THREAD_ID);
}
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
      '<div class="body md"></div>' +
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
  var accText = '';       // 攒下来的答案原文（模型是一段一段吐的）

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
      if (!started) { started = true; body.innerHTML = ''; }   // 第一段来了，把「三个点」清掉
      accText += d.text;
      body.innerHTML = mdToHtml(accText);   // 每来一段就整体重画一次，这样 Markdown 才是完整的
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
        body.innerHTML = mdToHtml(data.answer);
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

// 走 Agent 流式接口：工具调用、工具返回、答案文字，都是一条条推过来的
function askAgent(q, answerMsg, body) {
  var bubble = answerMsg.querySelector('.bubble');

  var stepsWrap = null;   // 「Agent 执行过程」那个框，等真有事件了才建
  var accText = '';       // 攒下来的答案原文
  var finished = false;   // 正常收到 done 了没有

  // 建步骤框（只建一次），把它插在正文上面 —— 先看过程，再看答案
  function stepBox() {
    if (!stepsWrap) {
      stepsWrap = document.createElement('div');
      stepsWrap.className = 'steps';
      var t = document.createElement('div');
      t.className = 'steps-title';
      t.textContent = '▾ Agent 执行过程';
      stepsWrap.appendChild(t);
      bubble.insertBefore(stepsWrap, body);
    }
    return stepsWrap;
  }

  // 往步骤框里加一行：左边是标签，右边是内容
  function addStep(tag, text) {
    var row = document.createElement('div');
    row.className = 'step';

    var t = document.createElement('span');
    t.className = 'tag';
    t.textContent = tag;

    var s = document.createElement('span');
    s.textContent = text;

    row.appendChild(t);
    row.appendChild(s);
    stepBox().appendChild(row);
    scrollBottom();
  }

  // Agent 要执行 SQL 时，先弹个框问用户
  function showConfirm(sql) {
    var box = document.createElement('div');
    box.className = 'confirm';

    var title = document.createElement('div');
    title.className = 'confirm-title';
    title.textContent = '⚠️ 这条 SQL 要执行吗？';
    box.appendChild(title);

    var pre = document.createElement('pre');
    pre.className = 'confirm-sql';
    pre.textContent = sql;
    box.appendChild(pre);

    var okBtn = document.createElement('button');
    okBtn.textContent = '确认执行';
    okBtn.onclick = function () {
      box.remove();
      connect('/agent_resume?ok=1&thread=' + encodeURIComponent(THREAD_ID), null);
    };

    var noBtn = document.createElement('button');
    noBtn.textContent = '取消';
    noBtn.onclick = function () {
      box.remove();
      connect('/agent_resume?ok=0&thread=' + encodeURIComponent(THREAD_ID), null);
    };

    box.appendChild(okBtn);
    box.appendChild(noBtn);
    bubble.appendChild(box);
    scrollBottom();
  }

  // 连一个 SSE 流并处理事件 —— 提问和恢复两条路都走这里
  function connect(url, fallbackQ) {
    var es = new EventSource(url);

    es.onmessage = function (e) {
      var d = JSON.parse(e.data);

      if (d.type === 'tool_call') {
        addStep('调用工具', d.name);

      } else if (d.type === 'tool_result') {
        addStep('工具返回', d.text + ' …');

      } else if (d.type === 'text') {
        if (accText === '') body.innerHTML = '';   // 第一段文字来了，清掉「三个点」
        accText += d.text;
        body.innerHTML = mdToHtml(accText);
        scrollBottom();

      } else if (d.type === 'interrupt') {
        showConfirm(d.sql);                        // 后端停下来等确认了

      } else if (d.type === 'done') {
        finished = true;
        es.close();
        document.getElementById('send').disabled = false;
        scrollBottom();
      }
    };

    // 连不上（比如后端还没加 /agent_stream），就退回一次性返回的 /agent
    // 恢复那条路不降级（fallbackQ 是 null），否则会把问题重问一遍
    es.onerror = function () {
      es.close();
      if (finished) return;
      if (!fallbackQ) {
        document.getElementById('send').disabled = false;
        return;
      }

      fetch('/agent?q=' + encodeURIComponent(fallbackQ) + '&thread=' + encodeURIComponent(THREAD_ID))
        .then(function (r) { return r.json(); })
        .then(function (d) {
          body.innerHTML = mdToHtml(d.answer);
          showSteps(answerMsg, d.steps);
          document.getElementById('send').disabled = false;
          scrollBottom();
        })
        .catch(function () {
          body.textContent = '（Agent 接口连不上：确认 serve.py 已启动，并且 main.py 里加了 /agent）';
          document.getElementById('send').disabled = false;
        });
    };
  }

  // 第一次连接
  connect('/agent_stream?q=' + encodeURIComponent(q) + '&thread=' + encodeURIComponent(THREAD_ID), q);
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

  // 和流式那条路一样，把过程框插在正文上面
  var bubble = answerMsg.querySelector('.bubble');
  bubble.insertBefore(wrap, bubble.querySelector('.body'));
}
