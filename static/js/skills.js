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
    var skillName = card.find('.skill-name').text();
    var author    = card.find('.skill-author').text();

    // ── REPLACE WITH AJAX WHEN BACKEND READY ────────────────
    // $.ajax({
    //   url: '/requests/send',
    //   method: 'POST',
    //   contentType: 'application/json',
    //   data: JSON.stringify({ skill: skillName }),
    //   success: function () {
    //     showConfirmation(skillName);
    //   }
    // });
    // 

    // Temporary feedback
    var btn = $(this);
    btn.text('Requested!');
    btn.css('background', '#2d6a4f');
    btn.prop('disabled', true);
  });

});