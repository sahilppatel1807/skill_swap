// ── Dummy Data ───────────────────────────────────────────────────
var skills = [
  { id: 1, name: 'React.js',    category: 'Programming', desc: 'Building web apps with React for 2 years. Can help with hooks, state management, and component patterns.' },
  { id: 2, name: 'JavaScript',  category: 'Programming', desc: 'Strong fundamentals in ES6+, async programming, and DOM manipulation.' },
  { id: 3, name: 'Python',      category: 'Programming', desc: 'Experience with scripting, data analysis, and building REST APIs with Flask.' },
  { id: 4, name: 'Node.js',     category: 'Programming', desc: 'Backend development with Express, REST APIs, and database integration.' },
];

var editingId = null;

// ── On page load ─────────────────────────────────────────────────
$(document).ready(function () {

  // Render skills from dummy data
  renderSkills();

  // Save skill button
  $('#save-skill-btn').on('click', function () {
    saveSkill();
  });

  // Delete skill — event delegation
  $(document).on('click', '.delete-btn', function () {
    var id = parseInt($(this).closest('.skill-card').data('skill-id'));
    deleteSkill(id);
  });

  // Edit skill — event delegation
  $(document).on('click', '.edit-btn', function () {
    var card = $(this).closest('.skill-card');
    var id   = parseInt(card.data('skill-id'));
    openEditModal(id);
  });
});

// ── Render all skills ─────────────────────────────────────────────
function renderSkills() {

  // ── REPLACE WITH AJAX WHEN BACKEND READY ────────────────────
  // $.ajax({
  //   url: '/profile/skills',
  //   method: 'GET',
  //   success: function(data) { buildSkillCards(data.skills); }
  // });
  // ────────────────────────────────────────────────────────────

  buildSkillCards(skills);
}

// ── Build skill cards from array ──────────────────────────────────
function buildSkillCards(data) {
  var list = $('#skills-list');
  list.empty();

  if (data.length === 0) {
    list.html('<p style="color:#aaa; font-size:14px;">No skills added yet.</p>');
    return;
  }

  $.each(data, function (i, skill) {
    list.append(makeSkillCard(skill));
  });
}

// ── Build a single skill card HTML ────────────────────────────────
function makeSkillCard(skill) {
  return $(
    '<div class="skill-card" data-skill-id="' + skill.id + '">' +
      '<div class="skill-card-body">' +
        '<div class="skill-card-top">' +
          '<div class="skill-left">' +
            '<span class="skill-name">' + escapeHtml(skill.name) + '</span>' +
            '<span class="skill-badge">' + escapeHtml(skill.category) + '</span>' +
          '</div>' +
          '<div class="skill-actions">' +
            '<button class="icon-btn edit-btn" title="Edit">' +
              '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>' +
            '</button>' +
            '<button class="icon-btn delete-btn" title="Delete">' +
              '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>' +
            '</button>' +
          '</div>' +
        '</div>' +
        '<p class="skill-desc">' + escapeHtml(skill.desc) + '</p>' +
      '</div>' +
    '</div>'
  );
}

// ── Save skill (add or edit) ──────────────────────────────────────
function saveSkill() {
  var name     = $('#skill-name').val().trim();
  var category = $('#skill-category').val();
  var desc     = $('#skill-desc').val().trim();

  if (name === '' || desc === '') {
    alert('Please fill in all fields.');
    return;
  }

  if (editingId !== null) {
    // Edit existing
    var skill = skills.find(function(s) { return s.id === editingId; });
    if (skill) {
      skill.name     = name;
      skill.category = category;
      skill.desc     = desc;
    }

    // ── REPLACE WITH AJAX WHEN BACKEND READY ──────────────────
    // $.ajax({
    //   url: '/profile/skills/edit/' + editingId,
    //   method: 'POST',
    //   contentType: 'application/json',
    //   data: JSON.stringify({ name, category, desc }),
    //   success: function() { renderSkills(); }
    // });
    // ──────────────────────────────────────────────────────────

    editingId = null;
    $('#addSkillModal .modal-title').text('Add New Skill');

  } else {
    // Add new
    var newSkill = {
      id:       skills.length + 1,
      name:     name,
      category: category,
      desc:     desc
    };
    skills.push(newSkill);

    // ── REPLACE WITH AJAX WHEN BACKEND READY ──────────────────
    // $.ajax({
    //   url: '/profile/skills/add',
    //   method: 'POST',
    //   contentType: 'application/json',
    //   data: JSON.stringify(newSkill),
    //   success: function() { renderSkills(); }
    // });
    // ──────────────────────────────────────────────────────────
  }

  // Clear form and close modal
  $('#skill-name').val('');
  $('#skill-category').val('Programming');
  $('#skill-desc').val('');
  $('#addSkillModal').modal('hide');

  renderSkills();
}

// ── Open modal in edit mode ───────────────────────────────────────
function openEditModal(id) {
  var skill = skills.find(function(s) { return s.id === id; });
  if (!skill) return;

  editingId = id;
  $('#skill-name').val(skill.name);
  $('#skill-category').val(skill.category);
  $('#skill-desc').val(skill.desc);
  $('#addSkillModal .modal-title').text('Edit Skill');
  $('#addSkillModal').modal('show');
}

// ── Delete a skill ────────────────────────────────────────────────
function deleteSkill(id) {
  if (!confirm('Delete this skill?')) return;

  skills = skills.filter(function(s) { return s.id !== id; });

  // ── REPLACE WITH AJAX WHEN BACKEND READY ──────────────────
  // $.ajax({
  //   url: '/profile/skills/delete/' + id,
  //   method: 'POST',
  //   success: function() { renderSkills(); }
  // });
  // ──────────────────────────────────────────────────────────

  renderSkills();
}

// ── Sanitize text ─────────────────────────────────────────────────
function escapeHtml(text) {
  return $('<div>').text(text).html();
}