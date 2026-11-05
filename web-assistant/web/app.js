/* Jervis web UI — talks to the local Python server. */
const conversation = document.querySelector("#conversation");
const commandForm = document.querySelector("#commandForm");
const commandInput = document.querySelector("#commandInput");
const micButton = document.querySelector("#micButton");
const muteButton = document.querySelector("#muteButton");
const listenState = document.querySelector("#listenState");
const voiceHint = document.querySelector("#voiceHint");
const serverStatus = document.querySelector("#serverStatus");
const voiceStatus = document.querySelector("#voiceStatus");
const aiStatus = document.querySelector("#aiStatus");
const clearButton = document.querySelector("#clearButton");
const turnCount = document.querySelector("#turnCount");
const taskForm = document.querySelector("#taskForm");
const taskInput = document.querySelector("#taskInput");
const taskList = document.querySelector("#taskList");
const taskCount = document.querySelector("#taskCount");
const clearCompletedButton = document.querySelector("#clearCompleted");
const navCommand = document.querySelector("#navCommand");
const navTasks = document.querySelector("#navTasks");
const canvas = document.querySelector("#waveform");
const ctx = canvas.getContext("2d");

let listening = false;
let spokenResponses = true;
let pulse = 0;
let turns = 1;
let recognition = null;

const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

function browserSpeak(text) {
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text.replace(/`/g, "").slice(0, 400));
  utterance.rate = 1;
  utterance.pitch = 0.95;
  window.speechSynthesis.speak(utterance);
}

function linkify(container, text) {
  const urlPattern = /(https?:\/\/[^\s]+)/g;
  let last = 0;
  let match;
  while ((match = urlPattern.exec(text)) !== null) {
    container.append(document.createTextNode(text.slice(last, match.index)));
    const link = document.createElement("a");
    link.href = match[0];
    link.target = "_blank";
    link.rel = "noopener noreferrer";
    link.textContent = match[0];
    container.append(link);
    last = match.index + match[0].length;
  }
  container.append(document.createTextNode(text.slice(last)));
}

function addMessage(role, text) {
  const article = document.createElement("article");
  article.className = `message ${role}`;
  const meta = document.createElement("div");
  meta.className = "message-meta";
  meta.textContent = role === "user" ? "You" : "Jervis";
  const paragraph = document.createElement("p");
  linkify(paragraph, String(text));
  article.append(meta, paragraph);
  conversation.append(article);
  article.scrollIntoView({ behavior: "smooth", block: "end" });
  turns += 1;
  turnCount.textContent = `${turns} messages`;
}

async function speak(text) {
  if (!spokenResponses) return;
  try {
    const response = await fetch("/api/speak", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const result = await response.json();
    if (!response.ok || !result.ok) browserSpeak(text);
  } catch {
    browserSpeak(text);
  }
}

async function renderTasks(tasks) {
  taskList.innerHTML = "";
  const open = tasks.filter((task) => !task.done).length;
  taskCount.textContent = `${open} open`;
  if (tasks.length === 0) {
    const empty = document.createElement("li");
    empty.className = "task-empty";
    empty.textContent = "No tasks yet — add one above.";
    taskList.append(empty);
    return;
  }
  tasks.forEach((task) => {
    const item = document.createElement("li");
    item.className = `task-item${task.done ? " done" : ""}`;

    const toggle = document.createElement("button");
    toggle.className = "task-toggle";
    toggle.textContent = task.done ? "✓" : "";
    toggle.title = task.done ? "Mark as open" : "Mark as done";
    toggle.setAttribute("aria-label", toggle.title);
    toggle.addEventListener("click", () => updateTask(task.id, "toggle"));

    const body = document.createElement("span");
    body.className = "task-body";
    body.textContent = `#${task.id}  ${task.body}`;

    const remove = document.createElement("button");
    remove.className = "task-delete";
    remove.textContent = "×";
    remove.title = "Delete task";
    remove.setAttribute("aria-label", "Delete task");
    remove.addEventListener("click", () => updateTask(task.id, "delete"));

    item.append(toggle, body, remove);
    taskList.append(item);
  });
}

async function refreshTasks() {
  try {
    const response = await fetch("/api/tasks");
    const result = await response.json();
    if (result.ok) await renderTasks(result.tasks || []);
  } catch {
    taskCount.textContent = "offline";
  }
}

async function updateTask(id, action) {
  try {
    const response = await fetch("/api/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ id, action }),
    });
    const result = await response.json();
    if (result.ok) await renderTasks(result.tasks || []);
  } catch (error) {
    addMessage("assistant", `Could not update task: ${error.message}`);
  }
}

async function runCommand(command) {
  const trimmed = command.trim();
  if (!trimmed) return;

  addMessage("user", trimmed);
  commandInput.value = "";
  listenState.textContent = "Working";

  try {
    const response = await fetch("/api/command", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command: trimmed }),
    });
    const result = await response.json();
    const text = result.response || result.error || "No response.";
    addMessage("assistant", text);
    await speak(text);
    listenState.textContent = "Ready";
    await refreshTasks();
  } catch (error) {
    addMessage("assistant", `Could not reach Jervis: ${error.message}`);
    listenState.textContent = "Offline";
  }
}

function stopListening() {
  listening = false;
  micButton.disabled = false;
  micButton.classList.remove("listening");
  listenState.textContent = "Ready";
}

async function listenFromServer() {
  listening = true;
  micButton.disabled = true;
  micButton.classList.add("listening");
  listenState.textContent = "Listening";
  voiceHint.textContent = "Speak now — Jervis is listening through the server microphone.";

  try {
    const response = await fetch("/api/listen", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}",
    });
    const result = await response.json();
    if (!result.ok) throw new Error(result.error || "Voice recognition failed.");
    await runCommand(result.command || "");
    voiceStatus.textContent = "Server mic";
  } catch (error) {
    addMessage("assistant", `Voice error: ${error.message}`);
    voiceStatus.textContent = "Voice needs attention";
    voiceHint.textContent = "Typed commands still work — use the box below.";
  } finally {
    stopListening();
  }
}

function listenInBrowser() {
  if (!SpeechRecognition) return false;
  listening = true;
  micButton.disabled = true;
  micButton.classList.add("listening");
  listenState.textContent = "Listening";
  voiceHint.textContent = "Speak now — your browser is transcribing.";

  recognition = new SpeechRecognition();
  recognition.lang = "en-US";
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onresult = (event) => {
    const heard = event.results[0][0].transcript.trim();
    voiceHint.textContent = `Heard: “${heard}”`;
    stopListening();
    if (heard) runCommand(heard);
  };
  recognition.onerror = (event) => {
    addMessage("assistant", `Microphone: ${event.error}. You can still type a command.`);
    stopListening();
  };
  recognition.onend = () => stopListening();

  try {
    recognition.start();
  } catch (error) {
    addMessage("assistant", `Could not start the microphone: ${error.message}`);
    stopListening();
  }
  return true;
}

function drawWaveform() {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  const dpr = window.devicePixelRatio || 1;
  if (canvas.width !== Math.floor(width * dpr) || canvas.height !== Math.floor(height * dpr)) {
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
  }
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, width, height);
  ctx.lineWidth = 2;
  ctx.strokeStyle = listening ? "rgba(180, 63, 82, 0.78)" : "rgba(15, 143, 122, 0.46)";
  ctx.beginPath();
  const amplitude = listening ? 46 : 18;
  const center = height / 2;
  for (let x = 0; x <= width; x += 6) {
    const y = center + Math.sin((x + pulse) / 34) * amplitude + Math.sin((x + pulse) / 15) * 8;
    if (x === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();
  pulse += listening ? 4 : 1;
  requestAnimationFrame(drawWaveform);
}

async function checkServer() {
  try {
    const response = await fetch("/health");
    const result = await response.json();
    if (!response.ok) throw new Error("bad status");
    serverStatus.textContent = "Connected";
    const canSpeak = Boolean(SpeechRecognition);
    voiceStatus.textContent = result.voice ? "Server mic" : canSpeak ? "Browser mic" : "Text only";
    aiStatus.textContent = result.ai ? "Ready" : "Offline mode";
    micButton.disabled = !(result.voice || canSpeak);
    if (!listening) {
      voiceHint.textContent = result.voice || canSpeak
        ? "Press the mic to speak, or type a command below."
        : "Voice is unavailable here — typed commands work fine.";
    }
  } catch {
    serverStatus.textContent = "Disconnected";
    voiceStatus.textContent = "Offline";
    aiStatus.textContent = "Offline";
  }
}

commandForm.addEventListener("submit", (event) => {
  event.preventDefault();
  runCommand(commandInput.value);
});

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const body = taskInput.value.trim();
  if (!body) return;
  taskInput.value = "";
  try {
    const response = await fetch("/api/tasks", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ body }),
    });
    const result = await response.json();
    if (result.ok) await renderTasks(result.tasks || []);
    addMessage("assistant", `Added “${body}” to your task list.`);
  } catch (error) {
    addMessage("assistant", `Could not add task: ${error.message}`);
  }
});

clearCompletedButton.addEventListener("click", () => runCommand("clear completed"));

micButton.addEventListener("click", () => {
  if (listening) {
    if (recognition) recognition.stop();
    stopListening();
    return;
  }
  if (SpeechRecognition) listenInBrowser();
  else listenFromServer();
});

muteButton.addEventListener("click", () => {
  spokenResponses = !spokenResponses;
  muteButton.textContent = spokenResponses ? "Sound On" : "Muted";
  muteButton.title = spokenResponses ? "Spoken responses on" : "Spoken responses off";
  if (!spokenResponses) window.speechSynthesis?.cancel();
});

clearButton.addEventListener("click", () => {
  conversation.innerHTML = "";
  turns = 0;
  addMessage("assistant", "Conversation cleared. What would you like me to do?");
});

navCommand.addEventListener("click", () => commandInput.focus());
navTasks.addEventListener("click", () => taskInput.focus());

document.querySelectorAll("[data-command]").forEach((button) => {
  button.addEventListener("click", () => runCommand(button.dataset.command || ""));
});

checkServer();
refreshTasks();
drawWaveform();
setInterval(checkServer, 10000);
