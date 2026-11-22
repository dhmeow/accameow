(() => {
  'use strict';

  const app = document.getElementById('app');
  const chapters = Array.isArray(window.MA_STUDY_DATA) ? window.MA_STUDY_DATA : [];
  const totalQuestions = chapters.reduce((sum, chapter) => sum + chapter.questions.length, 0);
  const attempts = Object.create(null);
  let view = 'home';
  let activeChapterId = null;
  let questionIndex = 0;
  let searchValue = '';
  let completionStats = null;

  const icons = {
    arrow: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M5 12h14M13 5l7 7-7 7"/></svg>',
    home: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z"/></svg>',
    search: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" aria-hidden="true"><circle cx="10.8" cy="10.8" r="6.8"/><path d="m16 16 4.5 4.5"/></svg>',
    sparkle: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m12 2 1.8 7.2L21 12l-7.2 1.8L12 21l-1.8-7.2L3 12l7.2-2.8L12 2Z"/><path d="m19 2 .7 2.3L22 5l-2.3.7L19 8l-.7-2.3L16 5l2.3-.7L19 2Z"/></svg>',
    book: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v17H6.5A2.5 2.5 0 0 0 4 21.5v-17Z"/><path d="M4 18.5A2.5 2.5 0 0 1 6.5 16H20M8 6h8M8 10h7"/></svg>',
    check: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 12 4 4L19 6"/></svg>',
    clock: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>',
    layers: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m12 3 9 5-9 5-9-5 9-5Z"/><path d="m3 12 9 5 9-5M3 16l9 5 9-5"/></svg>',
    lightbulb: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M9 18h6M10 22h4M8.5 14.5a6 6 0 1 1 7 0c-.8.6-1.2 1.3-1.3 2.5h-4.4c-.1-1.2-.5-1.9-1.3-2.5Z"/></svg>',
    chevron: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m9 18 6-6-6-6"/></svg>',
    skip: '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="m5 5 10 7-10 7V5ZM19 5v14"/></svg>'
  };

  function esc(value) {
    return String(value ?? '').replace(/[&<>"']/g, ch => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[ch]));
  }
  function lines(value) { return esc(value).replace(/\r?\n/g, '<br>'); }
  function pad(num) { return String(num).padStart(2, '0'); }
  function activeChapter() { return chapters.find(c => c.id === activeChapterId) || null; }
  function activeQuestion() { const c = activeChapter(); return c ? c.questions[questionIndex] : null; }
  function attemptFor(q) {
    if (!attempts[q.id]) attempts[q.id] = { selected: [], matrix: {}, response: '', confirmed: false, isCorrect: false, skipped: false };
    return attempts[q.id];
  }
  function setRoute(hash) {
    if (window.location.hash !== hash) history.replaceState(null, '', hash);
  }

  function renderHome() {
    view = 'home'; activeChapterId = null; questionIndex = 0; completionStats = null;
    setRoute('#home');
    app.innerHTML = `
      <div class="home-dark-shell">
        <header class="home-topbar">
          <span class="home-topbar-label">ACCA <i></i> MANAGEMENT ACCOUNTING</span>
          <span class="home-topbar-count">${chapters.length} CHAPTERS <b>·</b> ${totalQuestions} QUESTIONS</span>
        </header>
        <main class="home-dark-main">
          <section class="home-dark-hero" aria-labelledby="home-title">
            <div class="home-orb home-orb-a" aria-hidden="true"></div>
            <div class="home-orb home-orb-b" aria-hidden="true"></div>
            <div class="home-glass-refraction" aria-hidden="true"></div>
            <div class="home-title-wrap">
              <p class="home-overline">YOUR MA QUESTION LIBRARY</p>
              <h1 id="home-title">MA Study<br>Resources<span>.</span></h1>
              <button class="home-enter-btn" data-action="chapters">ALL CHAPTERS <span>${icons.arrow}</span></button>
            </div>
            <div class="home-glass-index" aria-hidden="true"><span>01 — 26</span><strong>MA</strong><i></i><small>STUDY<br>RESOURCES</small></div>
          </section>
          <section class="home-credit-plate" aria-label="Creator credits">
            <span class="home-credit-overline">WITH RESPECT & CREDIT TO THE ORIGINAL CREATOR</span>
            <div class="home-credit-name"><span>ALL CREDITS GO TO</span><strong>MEOW<span>®</span></strong></div>
            <span class="home-credit-rule"></span>
          </section>
        </main>
        <footer class="home-dark-footer"><span>MA STUDY RESOURCES</span><span>BUILT FOR PRACTICE <i></i> ALL CREDITS TO MEOW</span></footer>
      </div>`;
  }

  function renderChapters() {
    view = 'chapters'; activeChapterId = null; questionIndex = 0; completionStats = null;
    setRoute('#chapters');
    app.innerHTML = `
      <div class="site-wrap">
        <header class="site-header">
          <a class="brand" href="#home" data-action="home"><span class="brand-mark">M</span><span class="brand-copy"><span class="brand-title">MA Study Resources</span><span class="brand-sub">ALL CREDITS TO MEOW</span></span></a>
          <button class="back-home-btn" data-action="home">${icons.home}<span>Home</span></button>
        </header>
        <section class="page-main">
          <div class="eyebrow">Your learning library</div>
          <div class="page-heading"><div><h1>All chapters<span style="color:var(--red)">.</span></h1><p>Choose a chapter to open its questions. Each question is presented on its own screen, with your progress kept in view.</p></div><div class="chapter-summary"><span class="summary-num">${pad(chapters.length)}</span><span class="summary-label">Chapters<br>in this hub</span></div></div>
          <div class="chapter-tools"><label class="search-wrap">${icons.search}<input class="search-input" id="chapter-search" type="search" placeholder="Search by chapter name or number…" autocomplete="off" value="${esc(searchValue)}" aria-label="Search chapters"></label><span class="header-pill"><span class="header-pill-dot"></span>${totalQuestions} questions ready</span></div>
          <div class="chapter-grid" id="chapter-grid">${chapterCards(searchValue)}</div>
        </section>
        <footer class="home-footer"><span><strong>MA Study Resources</strong> · 26 chapters</span><span>ALL CREDITS TO MEOW</span></footer>
      </div>`;
    const input = document.getElementById('chapter-search');
    if (input) input.addEventListener('input', event => {
      searchValue = event.target.value;
      const grid = document.getElementById('chapter-grid');
      if (grid) grid.innerHTML = chapterCards(searchValue);
    });
  }

  function chapterCards(filter) {
    const needle = String(filter || '').trim().toLowerCase();
    const visible = chapters.filter(ch => !needle || `${ch.id} ${ch.title}`.toLowerCase().includes(needle));
    if (!visible.length) return '<div class="empty-state">No chapters match that search. Try another title or chapter number.</div>';
    return visible.map(ch => `
      <button class="chapter-card" data-action="open-chapter" data-chapter="${ch.id}" aria-label="Open Chapter ${ch.id}: ${esc(ch.title)}">
        <div class="chapter-card-top"><span class="chapter-number">CHAPTER ${pad(ch.id)}</span><span class="chapter-arrow">${icons.chevron}</span></div>
        <h2>${esc(ch.title)}</h2>
        <div class="chapter-card-bottom"><span>${ch.questions.length} questions</span><span class="open-label">Open chapter ↗</span></div>
      </button>`).join('');
  }

  function renderQuiz() {
    view = 'quiz';
    const chapter = activeChapter();
    if (!chapter) return renderChapters();
    const question = chapter.questions[questionIndex];
    if (!question) return renderCompletion();
    const attempt = attemptFor(question);
    const percent = Math.round(((questionIndex + 1) / chapter.questions.length) * 100);
    const current = pad(questionIndex + 1);
    setRoute(`#chapter-${chapter.id}-question-${question.number}`);

    app.innerHTML = `
      <div class="quiz-shell">
        <header class="quiz-top">
          <div class="quiz-progress-track"><div class="quiz-progress-fill" style="width:${percent}%"></div></div>
          <div class="quiz-top-row">
            <button class="quiz-home" data-action="home">${icons.home}<span>Home</span></button>
            <div class="quiz-progress-info">
              <div class="quiz-progress-meta"><span class="quiz-chapter-label">CHAPTER ${pad(chapter.id)} · ${esc(chapter.title)}</span><span class="quiz-counter">${current} / ${pad(chapter.questions.length)}</span></div>
              <div class="quiz-mini-track"><div class="quiz-mini-fill" style="width:${percent}%"></div></div>
            </div>
          </div>
        </header>
        <section class="quiz-body">
          <div class="quiz-heading"><div class="quiz-heading-copy"><div class="quiz-kicker">Question ${question.number} · Practice</div><h1>${esc(chapter.title)}</h1></div><span class="source-chip">PDF SOURCE · P. ${question.sourcePage || '—'}</span></div>
          <article class="question-card">
            ${question.context ? `<div class="scenario">${lines(question.context)}</div>` : ''}
            <p class="question-prompt">${lines(question.question || `Question ${question.number}`)}</p>
            ${question.figure ? `<img class="question-figure" src="${esc(question.figure)}" alt="Original graph options from the PDF for this question" loading="eager">` : ''}
            ${renderAnswerControls(question, attempt)}
            ${attempt.confirmed ? renderFeedback(question, attempt) : ''}
          </article>
          <div class="quiz-actions">
            <button class="skip-btn" data-action="skip" ${attempt.confirmed ? 'disabled' : ''}>Skip question ${icons.skip}</button>
            ${attempt.confirmed
              ? `<button class="confirm-btn" data-action="next">${questionIndex === chapter.questions.length - 1 ? 'Finish chapter' : 'Next question'} <span class="btn-arrow">${icons.arrow}</span></button>`
              : `<button class="confirm-btn" data-action="confirm" ${canConfirm(question, attempt) ? '' : 'disabled'}>Confirm answer <span class="btn-arrow">${icons.check}</span></button>`}
          </div>
          <p class="quiz-lower-note">Your answer is only revealed after you confirm.</p>
        </section>
      </div>`;
  }

  function renderAnswerControls(question, attempt) {
    if (question.type === 'matrix') {
      const rows = question.matrixRows || [];
      return `<div class="answer-type-note">Choose one answer for each row</div><div class="matrix-list">${rows.map((row, index) => {
        const selected = attempt.matrix[index];
        return `<section class="matrix-row"><p class="matrix-row-title">${esc(row.label)}</p><div class="matrix-options">${row.options.map(opt => {
          const isSelected = selected === opt;
          const isCorrect = attempt.confirmed && String(opt) === String(row.correct);
          const isWrong = attempt.confirmed && isSelected && !isCorrect;
          const cls = [isSelected ? 'is-selected' : '', isCorrect ? 'is-correct' : '', isWrong ? 'is-wrong' : ''].filter(Boolean).join(' ');
          return `<button class="matrix-choice ${cls}" data-action="matrix-select" data-row="${index}" data-value="${esc(opt)}" ${attempt.confirmed ? 'disabled' : ''}>${esc(opt)}</button>`;
        }).join('')}</div></section>`;
      }).join('')}</div>`;
    }
    if (question.type === 'numeric') {
      const value = attempt.response || '';
      let inputClass = '';
      if (attempt.confirmed) inputClass = attempt.isCorrect ? 'is-correct' : 'is-wrong';
      return `<div class="answer-type-note">Enter your answer</div><div class="numeric-wrap"><input class="numeric-input ${inputClass}" id="numeric-answer" type="text" inputmode="decimal" placeholder="Type your answer here…" value="${esc(value)}" ${attempt.confirmed ? 'disabled' : ''} aria-label="Your numerical answer"><span style="color:#a2a3a9;font-size:9px">Enter the number only. Currency symbols and commas are optional.</span></div>`;
    }
    const isMulti = question.type === 'multi';
    const options = question.options || [];
    const correct = (question.correct || []).map(String);
    return `<div class="answer-type-note">${isMulti ? `Select ${correct.length === 2 ? 'two answers' : 'all applicable answers'}` : 'Select one answer'}</div><div class="option-list">${options.map(option => {
      const key = String(option.key);
      const isSelected = isMulti ? attempt.selected.includes(key) : attempt.selected[0] === key;
      const isCorrect = attempt.confirmed && correct.includes(key);
      const isWrong = attempt.confirmed && isSelected && !correct.includes(key);
      const cls = [isMulti ? 'multi' : '', isSelected ? 'is-selected' : '', isCorrect ? 'is-correct' : '', isWrong ? 'is-wrong' : ''].filter(Boolean).join(' ');
      return `<button class="option-button ${cls}" data-action="select-option" data-key="${esc(key)}" ${attempt.confirmed ? 'disabled' : ''}><span class="option-key">${esc(key)}</span><span class="option-copy">${esc(option.text)}</span><span class="option-mark"></span></button>`;
    }).join('')}</div>`;
  }

  function canConfirm(question, attempt) {
    if (question.type === 'matrix') return (question.matrixRows || []).length > 0 && (question.matrixRows || []).every((row, i) => !!attempt.matrix[i]);
    if (question.type === 'numeric') return !!String(attempt.response || '').trim();
    return attempt.selected.length > 0;
  }

  function renderFeedback(question, attempt) {
    let answerSummary = '';
    if (question.type === 'numeric') {
      answerSummary = `Correct answer: ${question.correct?.[0] ?? question.answerText ?? 'See source PDF'}`;
    }
    const explanation = String(question.explanation || '').trim();
    return `${explanation ? `<div class="explanation-box"><div class="explanation-copy">${lines(explanation)}</div></div>` : ''}
      ${question.type === 'numeric' ? `<div class="correct-answer-line">${esc(answerSummary)}</div>` : ''}`;
  }

  function normalizeNumeric(value) {
    const normalized = String(value ?? '').trim().replace(/,/g, '').replace(/[^0-9.+-]/g, '');
    const n = Number(normalized);
    return Number.isFinite(n) ? n : null;
  }
  function checkAttempt(question, attempt) {
    if (question.type === 'matrix') {
      return (question.matrixRows || []).every((row, index) => String(attempt.matrix[index] ?? '') === String(row.correct));
    }
    if (question.type === 'numeric') {
      const entered = normalizeNumeric(attempt.response);
      const correct = normalizeNumeric(question.correct?.[0] ?? question.answerText);
      return entered !== null && correct !== null && Math.abs(entered - correct) < 0.000001;
    }
    const expected = (question.correct || []).map(String).sort();
    const selected = (attempt.selected || []).map(String).sort();
    return expected.length === selected.length && expected.every((value, index) => value === selected[index]);
  }

  function confirmAnswer() {
    const question = activeQuestion();
    if (!question) return;
    const attempt = attemptFor(question);
    if (!canConfirm(question, attempt)) return;
    attempt.isCorrect = checkAttempt(question, attempt);
    attempt.confirmed = true;
    renderQuiz();
  }

  function goNext() {
    const chapter = activeChapter();
    if (!chapter) return;
    if (questionIndex >= chapter.questions.length - 1) return renderCompletion();
    questionIndex += 1;
    renderQuiz();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function skipQuestion() {
    const question = activeQuestion();
    if (!question) return;
    const attempt = attemptFor(question);
    if (attempt.confirmed) return;
    attempt.skipped = true;
    goNext();
  }

  function renderCompletion() {
    const chapter = activeChapter();
    if (!chapter) return renderChapters();
    view = 'completion';
    const result = chapter.questions.reduce((acc, q) => {
      const a = attempts[q.id];
      if (!a || a.skipped) acc.skipped += 1;
      else if (a.confirmed && a.isCorrect) acc.correct += 1;
      else if (a.confirmed) acc.incorrect += 1;
      return acc;
    }, { correct: 0, incorrect: 0, skipped: 0 });
    completionStats = result;
    setRoute(`#chapter-${chapter.id}-complete`);
    app.innerHTML = `<div class="completion-wrap"><header class="site-header"><a class="brand" href="#home" data-action="home"><span class="brand-mark">M</span><span class="brand-copy"><span class="brand-title">MA Study Resources</span><span class="brand-sub">ALL CREDITS TO MEOW</span></span></a><button class="back-home-btn" data-action="home">${icons.home}<span>Home</span></button></header><section class="completion-card"><span class="completion-icon">${icons.check}</span><div class="eyebrow" style="justify-content:center">Chapter complete</div><h1>Nice work<span style="color:var(--red)">.</span></h1><p>You’ve reached the end of <strong>${esc(chapter.title)}</strong>. Take a moment to review your result, then choose where to go next.</p><div class="completion-stats"><div class="completion-stat"><strong>${result.correct}</strong><span>Correct</span></div><div class="completion-stat"><strong>${result.incorrect}</strong><span>Incorrect</span></div><div class="completion-stat"><strong>${result.skipped}</strong><span>Skipped</span></div></div><div class="completion-actions"><button class="primary-btn" data-action="chapters">All chapters <span class="arrow">${icons.arrow}</span></button><button class="outline-btn" data-action="home">Return home</button></div></section></div>`;
  }

  function openChapter(id) {
    const chapter = chapters.find(c => c.id === Number(id));
    if (!chapter) return;
    activeChapterId = chapter.id;
    questionIndex = 0;
    completionStats = null;
    renderQuiz();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  app.addEventListener('click', event => {
    const button = event.target.closest('[data-action]');
    if (!button) return;
    const action = button.dataset.action;
    if (action === 'home') { renderHome(); window.scrollTo({top:0,behavior:'smooth'}); return; }
    if (action === 'chapters') { searchValue = ''; renderChapters(); window.scrollTo({top:0,behavior:'smooth'}); return; }
    if (action === 'open-chapter') { openChapter(button.dataset.chapter); return; }
    if (action === 'select-option') {
      const question = activeQuestion(); if (!question) return;
      const attempt = attemptFor(question); if (attempt.confirmed) return;
      const key = button.dataset.key;
      if (question.type === 'multi') {
        const index = attempt.selected.indexOf(key);
        if (index >= 0) attempt.selected.splice(index, 1);
        else {
          const limit = (question.correct || []).length || 2;
          if (attempt.selected.length >= limit) return;
          attempt.selected.push(key);
        }
      } else attempt.selected = [key];
      renderQuiz(); return;
    }
    if (action === 'matrix-select') {
      const question = activeQuestion(); if (!question) return;
      const attempt = attemptFor(question); if (attempt.confirmed) return;
      attempt.matrix[button.dataset.row] = button.dataset.value;
      renderQuiz(); return;
    }
    if (action === 'confirm') { confirmAnswer(); return; }
    if (action === 'next') { goNext(); return; }
    if (action === 'skip') { skipQuestion(); return; }
  });

  app.addEventListener('input', event => {
    if (event.target && event.target.id === 'numeric-answer') {
      const question = activeQuestion(); if (!question) return;
      const attempt = attemptFor(question);
      attempt.response = event.target.value;
      const confirm = app.querySelector('[data-action="confirm"]');
      if (confirm) confirm.disabled = !canConfirm(question, attempt);
    }
  });

  // Start cleanly at the homepage. Direct chapter links are deliberately not exposed
  // because a student enters each quiz through the chapter library.
  renderHome();
})();
