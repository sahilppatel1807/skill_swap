// ── Filter logic ──────────────────────────────────────────────────
$(document).ready(function () {

  // Filter pill click
  $('.filter-btn').on('click', function () {
    var filter = $(this).data('filter');

    // Update active pill
    $('.filter-btn').removeClass('active');
    $(this).addClass('active');

    // Show/hide cards
    $('.skill-card').each(function () {
      var category = $(this).data('category');

      if (filter === 'all' || category === filter) {
        $(this).removeClass('hidden');
      } else {
        $(this).addClass('hidden');
      }
    });
  });

  // Request button click
  $(document).on('click', '.request-btn', function () {
    var card     = $(this).closest('.skill-card');
    var skillId  = card.data('skill-id');
    var skillName = card.find('.skill-name').text();
    var btn = $(this);

    $.ajax({
      url: '/requests/send/' + skillId,
      method: 'POST',
      success: function () {
        btn.text('✓ Requested!');
        btn.css('background', '#2d6a4f');
        btn.prop('disabled', true);
      },
      error: function (err) {
        var errorMsg = 'Unable to request';
        try {
          var resp = JSON.parse(err.responseText);
          errorMsg = resp.message || errorMsg;
        } catch (e) {}
        btn.text(errorMsg);
        btn.css('background', '#dc2626');
        setTimeout(function () {
          btn.text('Request');
          btn.css('background', '');
        }, 3000);
      }
    });
  });

});