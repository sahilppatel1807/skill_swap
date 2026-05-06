var currentUserId   = null;
var currentUserName = null;

// ── On page load ─────────────────────────────────────────────────
$(document).ready(function () {

  // Click a connection
  $('.connection-item').on('click', function () {
    $('.connection-item').removeClass('active');
    $(this).addClass('active');

    currentUserId   = $(this).data('user-id');
    currentUserName = $(this).data('name');
    var avatar      = $(this).data('avatar');

    // Update header
    $('#chat-header-name').text(currentUserName);
    $('#chat-avatar').text(avatar);

    // Load messages from Flask
    loadMessages(currentUserId);
  });

  // Send button
  $('#send-btn').on('click', function () {
    sendMessage();
  });

  // Enter key
  $('#message-input').on('keypress', function (e) {
    if (e.which === 13) sendMessage();
  });

  // Auto load first connection on page load
  var first = $('.connection-item').first();
  if (first.length) {
    currentUserId   = first.data('user-id');
    currentUserName = first.data('name');
    loadMessages(currentUserId);
  }
});

// ── Fetch messages from Flask ─────────────────────────────────────
function loadMessages(userId) {
  $.ajax({
    url: '/chat/messages/' + userId,
    method: 'GET',
    success: function (data) {
      renderMessages(data.messages);
    },
    error: function () {
      $('#chat-messages').html('<p style="color:#aaa; padding:20px;">Could not load messages.</p>');
    }
  });
}

// ── Render messages into the chat window ──────────────────────────
function renderMessages(messages) {
  $('#chat-messages').empty();

  $.each(messages, function (i, msg) {
    var bubble = $(
      '<div class="message ' + msg.type + '">' +
        '<div class="bubble">' + escapeHtml(msg.text) + '</div>' +
      '</div>'
    );
    $('#chat-messages').append(bubble);
  });

  scrollToBottom();
}

// ── Send message to Flask ─────────────────────────────────────────
function sendMessage() {
  var input = $('#message-input');
  var text  = input.val().trim();

  if (text === '' || !currentUserId) return;

  // Show bubble immediately
  var bubble = $(
    '<div class="message sent">' +
      '<div class="bubble">' + escapeHtml(text) + '</div>' +
    '</div>'
  );
  $('#chat-messages').append(bubble);
  input.val('');
  scrollToBottom();

  // Send to Flask
  $.ajax({
    url: '/chat/send',
    method: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
      user_id: currentUserId,
      message: text
    }),
    error: function () {
      console.log('Failed to send message to server.');
    }
  });
}

// ── Scroll to bottom ──────────────────────────────────────────────
function scrollToBottom() {
  var el = $('#chat-messages');
  el.scrollTop(el[0].scrollHeight);
}

// ── Sanitize text before inserting into DOM ───────────────────────
function escapeHtml(text) {
  return $('<div>').text(text).html();
}