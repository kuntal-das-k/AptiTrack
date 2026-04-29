/* AptiTrack Quiz Engine JS */
let currentQuestion = 0;
let totalQuestions = 0;
let timeLimit = 0;
let timerInterval = null;
let remainingSeconds = 0;
let answers = {};
let startTime = Date.now();

function initQuiz(total, timeLimitMinutes) {
  totalQuestions = total;
  timeLimit = timeLimitMinutes;
  remainingSeconds = timeLimitMinutes * 60;
  showQuestion(0);
  startTimer();
  updateNav();
}

function startTimer() {
  const timerEl = document.getElementById('quiz-timer');
  const progressEl = document.getElementById('timer-progress');
  const totalSeconds = remainingSeconds;

  timerInterval = setInterval(() => {
    remainingSeconds--;
    const mins = Math.floor(remainingSeconds / 60);
    const secs = remainingSeconds % 60;
    timerEl.textContent = `${String(mins).padStart(2,'0')}:${String(secs).padStart(2,'0')}`;

    // Progress bar
    const pct = (remainingSeconds / totalSeconds) * 100;
    if (progressEl) progressEl.style.width = pct + '%';

    // Warning states
    timerEl.classList.remove('warning', 'danger');
    if (remainingSeconds <= 60) timerEl.classList.add('danger');
    else if (remainingSeconds <= 300) timerEl.classList.add('warning');

    if (remainingSeconds <= 0) {
      clearInterval(timerInterval);
      submitQuiz();
    }
  }, 1000);
}

function showQuestion(index) {
  document.querySelectorAll('.quiz-question').forEach(q => q.classList.remove('active'));
  const target = document.getElementById(`question-${index}`);
  if (target) target.classList.add('active');
  currentQuestion = index;
  updateNav();
  document.getElementById('q-current').textContent = index + 1;
}

function updateNav() {
  document.querySelectorAll('.quiz-nav-btn').forEach((btn, i) => {
    btn.classList.remove('current');
    if (i === currentQuestion) btn.classList.add('current');
    const qid = btn.dataset.questionId;
    if (answers[qid]) btn.classList.add('answered');
  });
}

function selectAnswer(questionId, answer) {
  answers[questionId] = answer;
  // Update option UI
  document.querySelectorAll(`#question-${currentQuestion} .option-item`).forEach(opt => {
    opt.classList.remove('selected');
  });
  const selected = document.querySelector(`#question-${currentQuestion} .option-item[data-answer="${answer}"]`);
  if (selected) selected.classList.add('selected');
  // Update hidden input
  const input = document.getElementById(`answer-${questionId}`);
  if (input) input.value = answer;
  updateNav();
}

function nextQuestion() {
  if (currentQuestion < totalQuestions - 1) showQuestion(currentQuestion + 1);
}

function prevQuestion() {
  if (currentQuestion > 0) showQuestion(currentQuestion - 1);
}

function submitQuiz() {
  clearInterval(timerInterval);
  const elapsed = Math.floor((Date.now() - startTime) / 1000);
  document.getElementById('time-taken-input').value = elapsed;
  document.getElementById('quiz-form').submit();
}

function confirmSubmit() {
  const answered = Object.keys(answers).length;
  const unanswered = totalQuestions - answered;
  let msg = `Are you sure you want to submit?`;
  if (unanswered > 0) msg += `\n\n⚠️ You have ${unanswered} unanswered question${unanswered > 1 ? 's' : ''}.`;
  if (confirm(msg)) submitQuiz();
}
