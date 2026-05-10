$(document).ready(function () {
  var modalElement = document.getElementById('addSkillModal');
  var skillModal = bootstrap.Modal.getOrCreateInstance(modalElement);
  var addAction = '/profile/skills/add';
  var avatarManuallyEdited = false;

  function initialsFromName(name) {
    var parts = (name || '').replace(/[^a-z0-9\s]/gi, ' ').trim().split(/\s+/).filter(Boolean);

    if (parts.length >= 2) {
      return (parts[0][0] + parts[1][0]).toUpperCase();
    }

    if (parts.length === 1) {
      return parts[0].slice(0, 2).toUpperCase().padEnd(2, parts[0][0].toUpperCase());
    }

    return 'US';
  }

  function updateAvatarPreview(value) {
    $('#profile-avatar-preview').text((value || 'US').toUpperCase());
  }

  $('#profile-avatar-input').on('input', function () {
    avatarManuallyEdited = true;
    var value = $(this).val().replace(/[^a-z0-9]/gi, '').slice(0, 2).toUpperCase();
    $(this).val(value);
    updateAvatarPreview(value);
  });

  $('#profile-name-input').on('input', function () {
    if (!avatarManuallyEdited) {
      var initials = initialsFromName($(this).val());
      $('#profile-avatar-input').val(initials);
      updateAvatarPreview(initials);
    }
  });

  $('#editProfileModal').on('hidden.bs.modal', function () {
    avatarManuallyEdited = false;
    $(this).find('form')[0].reset();
    updateAvatarPreview($('#profile-avatar-input').val());
  });

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
