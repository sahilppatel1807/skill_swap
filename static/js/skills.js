$(document).ready(function () {

  $.ajaxSetup({
    headers: {
      'X-CSRFToken': $('meta[name="csrf-token"]').attr('content')
    }
  });

  $(document).on('click', '.request-btn', function () {

    const btn = $(this);
    const skillId = btn.data('skill-id');

    $.ajax({
      url: '/request_skill',
      type: 'POST',
      data: { skill_id: skillId },

      success: function () {
        btn.text('✓ Requested!');
        btn.prop('disabled', true);
        btn.addClass('requested');
      },

      error: function (xhr) {
        alert(xhr.responseJSON?.message || 'Request failed');
      }
    });

  });

});