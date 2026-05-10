$(document).ready(function () {
  var modalElement = document.getElementById('addSkillModal');
  var skillModal = bootstrap.Modal.getOrCreateInstance(modalElement);
  var addAction = '/profile/skills/add';

  function setAddMode() {
    $('#skill-form').attr('action', addAction);
    $('#addSkillModal .modal-title').text('Add New Skill');
    $('#skill-submit-btn').text('Add Skill');
    $('#skill-form')[0].reset();
  }

  $('.add-skill-btn').on('click', function () {
    setAddMode();
  });

  $(document).on('click', '.edit-btn', function () {
    var button = $(this);
    var skillId = button.data('skill-id');

    $('#skill-form').attr('action', '/profile/skills/edit/' + skillId);
    $('#skill-name').val(button.data('skill-name') || '');
    $('#skill-category').val(button.data('skill-category') || '');
    $('#skill-level').val(button.data('skill-level') || '');
    $('#skill-description').val(button.data('skill-desc') || '');
    $('#addSkillModal .modal-title').text('Edit Skill');
    $('#skill-submit-btn').text('Save Changes');

    skillModal.show();
  });

  modalElement.addEventListener('hidden.bs.modal', setAddMode);
});
