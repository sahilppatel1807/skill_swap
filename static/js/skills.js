$(document).ready(function () {

  // 全局 CSRF（一次就够）
  $.ajaxSetup({
    headers: {
      'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
    }
  });

  // request button
  $(document).on('click', '.request-btn', function () {

    var btn = $(this);
    var skillId = btn.data('skill-id');

    $.ajax({
      url: `/request_skill`,
      type: 'POST',
      data: { skill_id: skillId },

      success: function () {
        btn.text('✓ Requested!');
        btn.prop('disabled', true);
        btn.css('background', '#2d6a4f');
      },

      error: function (xhr) {
        alert(xhr.responseJSON?.message || 'Request failed');
      }
    });

  });

});