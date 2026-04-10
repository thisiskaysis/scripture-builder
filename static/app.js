const scriptures = [];
let dragSrcIndex = null;

// --- DOM refs ---
const addBtn = document.getElementById('add-btn');
const generateBtn = document.getElementById('generate-btn');
const clearBtn = document.getElementById('clear-btn');
const list = document.getElementById('scripture-list');
const emptyMsg = document.getElementById('empty-msg');
const countBadge = document.getElementById('scripture-count');
const darkToggle = document.getElementById('dark-mode-toggle');
const uploadArea = document.getElementById('upload-area');
const docUpload = document.getElementById('doc-upload');
const uploadStatus = document.getElementById('upload-status');

// --- Dark mode ---
if (localStorage.getItem('darkMode') === 'true') {
  document.body.classList.add('dark');
  darkToggle.textContent = '☀️';
}

darkToggle.addEventListener('click', () => {
  document.body.classList.toggle('dark');
  const isDark = document.body.classList.contains('dark');
  darkToggle.textContent = isDark ? '☀️' : '🌙';
  localStorage.setItem('darkMode', isDark);
});

// --- Persist list across refresh ---
function saveToStorage() {
  localStorage.setItem('scriptures', JSON.stringify(scriptures));
}

function loadFromStorage() {
  const saved = localStorage.getItem('scriptures');
  if (saved) {
    const parsed = JSON.parse(saved);
    parsed.forEach(s => scriptures.push(s));
    renderList();
  }
}

// --- Add scripture ---
addBtn.addEventListener('click', addScripture);

document.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && document.activeElement !== document.getElementById('verse-text')) {
    addScripture();
  }
});

function addScripture() {
  const ref = document.getElementById('verse-ref').value.trim();
  const text = document.getElementById('verse-text').value.trim();
  const screens = [...document.querySelectorAll('.checkboxes input:checked')]
    .map(cb => cb.value);

  if (!ref || !text) {
    alert('Please enter both a verse reference and the scripture text.');
    return;
  }

  if (screens.length === 0) {
    alert('Please select at least one screen.');
    return;
  }

  scriptures.push({ ref, text, screens });
  saveToStorage();
  renderList();
  clearForm();
}

// --- Clear all ---
clearBtn.addEventListener('click', () => {
  if (confirm('Clear all scriptures? This cannot be undone.')) {
    scriptures.length = 0;
    saveToStorage();
    renderList();
  }
});

// --- Render list ---
function renderList() {
  emptyMsg.style.display = scriptures.length === 0 ? 'block' : 'none';
  clearBtn.style.display = scriptures.length === 0 ? 'none' : 'inline-block';
  countBadge.style.display = scriptures.length === 0 ? 'none' : 'inline-block';
  countBadge.textContent = scriptures.length;

  list.innerHTML = '';

  scriptures.forEach((s, i) => {
    const mainChecked = s.screens.includes('main') ? 'checked' : '';
    const leftChecked = s.screens.includes('left_pillar') ? 'checked' : '';
    const rightChecked = s.screens.includes('right_pillar') ? 'checked' : '';
    const bannerChecked = s.screens.includes('banner') ? 'checked' : '';

    const li = document.createElement('li');
    li.className = 'scripture-item';
    li.id = `item-${i}`;
    li.draggable = true;

    li.innerHTML = `
      <div class="item-view" id="view-${i}">
        <div class="item-content">
          <div class="ref">${s.ref}</div>
          <div class="item-text">${s.text}</div>
          <div class="screens">Screens: ${s.screens.join(', ')}</div>
        </div>
        <div class="item-actions">
          <button class="edit-btn" onclick="startEdit(${i})">Edit</button>
          <button class="duplicate-btn" onclick="duplicateEntry(${i})">Duplicate</button>
          <button class="remove" onclick="removeEntry(${i})">Remove</button>
        </div>
      </div>

      <div class="item-edit" id="edit-${i}" style="display:none;">
        <div class="field">
          <label>Verse reference</label>
          <input type="text" id="edit-ref-${i}" value="${s.ref}">
        </div>
        <div class="field">
          <label>Scripture text</label>
          <textarea id="edit-text-${i}" rows="4">${s.text}</textarea>
        </div>
        <div class="field">
          <label>Display on screens</label>
          <div class="checkboxes">
            <label><input type="checkbox" value="main" ${mainChecked}> Main</label>
            <label><input type="checkbox" value="left_pillar" ${leftChecked}> Left Pillar</label>
            <label><input type="checkbox" value="right_pillar" ${rightChecked}> Right Pillar</label>
            <label><input type="checkbox" value="banner" ${bannerChecked}> Banner</label>
          </div>
        </div>
        <div class="edit-actions">
          <button class="save-btn" onclick="saveEdit(${i})">Save</button>
          <button class="cancel-btn" onclick="cancelEdit(${i})">Cancel</button>
        </div>
      </div>
    `;

    // Drag and drop events
    li.addEventListener('dragstart', () => {
      dragSrcIndex = i;
      setTimeout(() => li.classList.add('dragging'), 0);
    });

    li.addEventListener('dragend', () => {
      li.classList.remove('dragging');
      document.querySelectorAll('.scripture-item').forEach(el => el.classList.remove('drag-over'));
    });

    li.addEventListener('dragover', (e) => {
      e.preventDefault();
      li.classList.add('drag-over');
    });

    li.addEventListener('dragleave', () => {
      li.classList.remove('drag-over');
    });

    li.addEventListener('drop', (e) => {
      e.preventDefault();
      li.classList.remove('drag-over');
      if (dragSrcIndex === null || dragSrcIndex === i) return;
      const moved = scriptures.splice(dragSrcIndex, 1)[0];
      scriptures.splice(i, 0, moved);
      dragSrcIndex = null;
      saveToStorage();
      renderList();
    });

    list.appendChild(li);
  });
}

// --- Edit ---
function startEdit(index) {
  document.getElementById(`view-${index}`).style.display = 'none';
  document.getElementById(`edit-${index}`).style.display = 'block';
}

function cancelEdit(index) {
  document.getElementById(`view-${index}`).style.display = 'flex';
  document.getElementById(`edit-${index}`).style.display = 'none';
}

function saveEdit(index) {
  const ref = document.getElementById(`edit-ref-${index}`).value.trim();
  const text = document.getElementById(`edit-text-${index}`).value.trim();
  const screens = [...document.querySelectorAll(`#edit-${index} .checkboxes input:checked`)]
    .map(cb => cb.value);

  if (!ref || !text) {
    alert('Please enter both a verse reference and scripture text.');
    return;
  }

  if (screens.length === 0) {
    alert('Please select at least one screen.');
    return;
  }

  scriptures[index] = { ref, text, screens };
  saveToStorage();
  renderList();
}

// --- Duplicate ---
function duplicateEntry(index) {
  const copy = { ...scriptures[index], screens: [...scriptures[index].screens] };
  scriptures.splice(index + 1, 0, copy);
  saveToStorage();
  renderList();
}

// --- Remove ---
function removeEntry(index) {
  scriptures.splice(index, 1);
  saveToStorage();
  renderList();
}

// --- Clear form ---
function clearForm() {
  document.getElementById('verse-ref').value = '';
  document.getElementById('verse-text').value = '';
}

// --- Generate ---
generateBtn.addEventListener('click', () => {
  if (scriptures.length === 0) {
    alert('Add at least one scripture before generating.');
    return;
  }

  const serviceLabel = document.getElementById('service-label').value.trim();

  fetch('/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scriptures, serviceLabel })
  })
  .then(res => res.json())
  .then(data => {
    alert(data.message);
  })
  .catch(err => {
    alert('Something went wrong: ' + err);
  });
});

// --- Upload ---
uploadArea.addEventListener('click', () => docUpload.click());

uploadArea.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadArea.style.borderColor = 'var(--accent)';
  uploadArea.style.background = 'var(--accent-light)';
});

uploadArea.addEventListener('dragleave', () => {
  uploadArea.style.borderColor = 'var(--border)';
  uploadArea.style.background = '';
});

uploadArea.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadArea.style.borderColor = 'var(--border)';
  uploadArea.style.background = '';
  const file = e.dataTransfer.files[0];
  if (file) handleUpload(file);
});

docUpload.addEventListener('change', () => {
  if (docUpload.files[0]) handleUpload(docUpload.files[0]);
});

function handleUpload(file) {
  if (!file.name.endsWith('.docx') && !file.name.endsWith('.pdf')) {
    showUploadStatus('Please upload a .docx or .pdf file.', false);
    return;
}

  showUploadStatus('Reading document...', null);

  const formData = new FormData();
  formData.append('file', file);

  fetch('/upload', {
    method: 'POST',
    body: formData
  })
  .then(res => res.json())
  .then(data => {
    if (data.success) {
      data.scriptures.forEach(s => {
        scriptures.push({
          ref: s.translation ? `${s.ref} (${s.translation})` : s.ref,
          text: s.text,
          screens: s.screens
        });
      });
      saveToStorage();
      renderList();
      showUploadStatus(`${data.scriptures.length} scripture(s) found and added to the list.`, true);
    } else {
      showUploadStatus(data.message, false);
    }
  })
  .catch(() => {
    showUploadStatus('Something went wrong reading the file.', false);
  });
}

function showUploadStatus(message, success) {
  uploadStatus.style.display = 'block';
  uploadStatus.className = success === true
    ? 'upload-status-success'
    : success === false
      ? 'upload-status-error'
      : '';
  uploadStatus.textContent = message;
}

// --- Load persisted data on startup ---
loadFromStorage();