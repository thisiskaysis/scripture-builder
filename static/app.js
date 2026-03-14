const scriptures = [];

const addBtn = document.getElementById('add-btn');
const generateBtn = document.getElementById('generate-btn');
const list = document.getElementById('scripture-list');
const emptyMsg = document.getElementById('empty-msg');

addBtn.addEventListener('click', () => {
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

  const entry = { ref, text, screens };
  scriptures.push(entry);
  renderList();
  clearForm();
});

function renderList() {
  emptyMsg.style.display = scriptures.length === 0 ? 'block' : 'none';
  list.innerHTML = '';
  scriptures.forEach((s, i) => {
    const li = document.createElement('li');
    li.className = 'scripture-item';
    li.innerHTML = `
      <div>
        <div class="ref">${s.ref}</div>
        <div class="screens">Screens: ${s.screens.join(', ')}</div>
      </div>
      <button class="remove" onclick="removeEntry(${i})">Remove</button>
    `;
    list.appendChild(li);
  });
}

function removeEntry(index) {
  scriptures.splice(index, 1);
  renderList();
}

function clearForm() {
  document.getElementById('verse-ref').value = '';
  document.getElementById('verse-text').value = '';
}

generateBtn.addEventListener('click', () => {
  if (scriptures.length === 0) {
    alert('Add at least one scripture before generating.');
    return;
  }

  fetch('/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ scriptures })
  })
  .then(res => res.json())
  .then(data => {
    alert(data.message);
  })
  .catch(err => {
    alert('Something went wrong: ' + err);
  });
});