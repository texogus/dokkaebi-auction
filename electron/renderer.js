const form = document.querySelector('#settings-form');
const apiKey = document.querySelector('#api-key');
const videoId = document.querySelector('#video-id');
const memberFile = document.querySelector('#member-file');
const blockedFile = document.querySelector('#blocked-file');
const outputDir = document.querySelector('#output-dir');
const hostKeyword = document.querySelector('#host-keyword');
const pollSec = document.querySelector('#poll-sec');
const statusText = document.querySelector('#status-text');
const logText = document.querySelector('#log-text');
const startButton = document.querySelector('#start-button');
const stopButton = document.querySelector('#stop-button');
const saveButton = document.querySelector('#save-button');

const extraId = document.querySelector('#extra-id');
const extraName = document.querySelector('#extra-name');
const extraPhone = document.querySelector('#extra-phone');
const extraAddress = document.querySelector('#extra-address');
const addMemberButton = document.querySelector('#add-member-button');
const memberRows = document.querySelector('#member-rows');

const extraMembers = new Map();

function normalizeId(value) {
  return String(value || '').trim().toLowerCase().replace(/^@+/, '');
}

function appendLog(message) {
  if (!message) return;
  logText.value += `${message}\n`;
  logText.scrollTop = logText.scrollHeight;
}

function currentSettings() {
  return {
    api_key: apiKey.value,
    video_id: videoId.value,
    member_file: memberFile.value,
    blocked_file: blockedFile.value,
    output_dir: outputDir.value,
    host_keyword: hostKeyword.value || '만물도깨비',
    poll_sec: Number(pollSec.value || 6),
    extra_members: Array.from(extraMembers.values()),
  };
}

function applySettings(settings) {
  apiKey.value = settings.api_key || '';
  videoId.value = settings.video_id || '';
  memberFile.value = settings.member_file || '';
  blockedFile.value = settings.blocked_file || '';
  outputDir.value = settings.output_dir || '';
  hostKeyword.value = settings.host_keyword || '만물도깨비';
  pollSec.value = settings.poll_sec || 6;

  for (const row of settings.extra_members || []) {
    extraMembers.set(row.key, row);
  }
  renderExtraMembers();
}

function renderExtraMembers() {
  memberRows.innerHTML = '';
  for (const member of extraMembers.values()) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${member.display_id}</td>
      <td>${member.customer_name}</td>
      <td>${member.phone}</td>
      <td>${member.address}</td>
      <td><button type="button" class="icon-button" data-key="${member.key}">삭제</button></td>
    `;
    memberRows.appendChild(tr);
  }
}

function setRunning(isRunning) {
  startButton.disabled = isRunning;
  stopButton.disabled = !isRunning;
  statusText.textContent = isRunning ? '실행 중' : '대기 중';
}

document.querySelector('#choose-member-file').addEventListener('click', async () => {
  const path = await window.auctionApp.chooseMemberFile();
  if (path) memberFile.value = path;
});

document.querySelector('#choose-blocked-file').addEventListener('click', async () => {
  const path = await window.auctionApp.chooseBlockedFile();
  if (path) blockedFile.value = path;
});

document.querySelector('#choose-output-dir').addEventListener('click', async () => {
  const path = await window.auctionApp.chooseOutputDir();
  if (path) outputDir.value = path;
});

addMemberButton.addEventListener('click', () => {
  const displayId = extraId.value.trim();
  if (!displayId) {
    appendLog('추가 회원 아이디를 입력하세요.');
    return;
  }

  const key = normalizeId(displayId);
  extraMembers.set(key, {
    key,
    display_id: displayId,
    customer_name: extraName.value.trim(),
    phone: extraPhone.value.trim(),
    address: extraAddress.value.trim(),
  });
  extraId.value = '';
  extraName.value = '';
  extraPhone.value = '';
  extraAddress.value = '';
  renderExtraMembers();
});

memberRows.addEventListener('click', (event) => {
  const button = event.target.closest('button[data-key]');
  if (!button) return;
  extraMembers.delete(button.dataset.key);
  renderExtraMembers();
});

saveButton.addEventListener('click', async () => {
  await window.auctionApp.saveSettings(currentSettings());
  appendLog('설정을 저장했습니다.');
});

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  try {
    await window.auctionApp.startMonitor(currentSettings());
    setRunning(true);
  } catch (error) {
    appendLog(`오류: ${error.message}`);
  }
});

stopButton.addEventListener('click', async () => {
  await window.auctionApp.stopMonitor();
  statusText.textContent = '중지 중';
  stopButton.disabled = true;
});

window.auctionApp.onLog(appendLog);
window.auctionApp.onStopped(() => setRunning(false));

window.auctionApp.loadSettings().then(applySettings);
