/**
 * Health Awareness Assistant - Main Frontend Application Logic
 * Implements conversational chat with guardrails, prompt explanation view,
 * interactive health quiz engine with instant feedback, and modal controls.
 */

document.addEventListener('DOMContentLoaded', () => {
  // =========================================================================
  // DOM Elements Selection
  // =========================================================================
  
  // Navigation & Views
  const navChatBtn = document.getElementById('navChatBtn');
  const navPromptExplanationBtn = document.getElementById('navPromptExplanationBtn');
  const navQuizBtn = document.getElementById('navQuizBtn');
  const currentViewTitle = document.getElementById('currentViewTitle');
  const chatView = document.getElementById('chatView');
  const promptExplanationView = document.getElementById('promptExplanationView');
  const quizView = document.getElementById('quizView');
  
  // Mobile Navigation
  const mobileMenuBtn = document.getElementById('mobileMenuBtn');
  const sidebar = document.getElementById('sidebar');

  // Chat Elements
  const chatForm = document.getElementById('chatForm');
  const userInput = document.getElementById('userInput');
  const sendBtn = document.getElementById('sendBtn');
  const chatViewport = document.getElementById('chatViewport');
  const chatMessages = document.getElementById('chatMessages');
  const typingIndicator = document.getElementById('typingIndicator');
  const clearChatBtn = document.getElementById('clearChatBtn');
  
  // Prompt Explanation Elements
  const copyPromptBtn = document.getElementById('copyPromptBtn');
  const testDiagnosticBtn = document.getElementById('testDiagnosticBtn');
  const testEmergencyBtn = document.getElementById('testEmergencyBtn');
  const testEducationBtn = document.getElementById('testEducationBtn');

  // Quiz Elements
  const quizProgressText = document.getElementById('quizProgressText');
  const quizCategoryTag = document.getElementById('quizCategoryTag');
  const quizProgressFill = document.getElementById('quizProgressFill');
  const questionNumberDisplay = document.getElementById('questionNumberDisplay');
  const questionTextDisplay = document.getElementById('questionTextDisplay');
  const optionsList = document.getElementById('optionsList');
  const feedbackBox = document.getElementById('feedbackBox');
  const feedbackIcon = document.getElementById('feedbackIcon');
  const feedbackTitle = document.getElementById('feedbackTitle');
  const feedbackExplanation = document.getElementById('feedbackExplanation');
  const prevQuestionBtn = document.getElementById('prevQuestionBtn');
  const checkAnswerBtn = document.getElementById('checkAnswerBtn');
  const nextQuestionBtn = document.getElementById('nextQuestionBtn');
  const finishQuizBtn = document.getElementById('finishQuizBtn');
  const quizQuestionCard = document.getElementById('quizQuestionCard');
  const quizResultsCard = document.getElementById('quizResultsCard');
  const scorePercentDisplay = document.getElementById('scorePercentDisplay');
  const scoreRatioDisplay = document.getElementById('scoreRatioDisplay');
  const resultsTitle = document.getElementById('resultsTitle');
  const resultsSummaryText = document.getElementById('resultsSummaryText');
  const detailedReviewContainer = document.getElementById('detailedReviewContainer');
  const retakeQuizBtn = document.getElementById('retakeQuizBtn');
  const reviewChatBtn = document.getElementById('reviewChatBtn');

  // Emergency Modal Elements
  const emergencyInfoBtn = document.getElementById('emergencyInfoBtn');
  const emergencyModal = document.getElementById('emergencyModal');
  const closeEmergencyModalBtn = document.getElementById('closeEmergencyModalBtn');
  const dismissEmergencyModalBtn = document.getElementById('dismissEmergencyModalBtn');

  // Google API Key Modal Elements
  const apiKeySettingsBtn = document.getElementById('apiKeySettingsBtn');
  const headerKeyDot = document.getElementById('headerKeyDot');
  const headerKeyLabel = document.getElementById('headerKeyLabel');
  const apiKeyModal = document.getElementById('apiKeyModal');
  const closeApiKeyModalBtn = document.getElementById('closeApiKeyModalBtn');
  const cancelApiKeyModalBtn = document.getElementById('cancelApiKeyModalBtn');
  const saveApiKeyBtn = document.getElementById('saveApiKeyBtn');
  const removeApiKeyBtn = document.getElementById('removeApiKeyBtn');
  const apiKeyInput = document.getElementById('apiKeyInput');
  const toggleKeyVisibilityBtn = document.getElementById('toggleKeyVisibilityBtn');
  const apiKeyModalStatusBanner = document.getElementById('apiKeyModalStatusBanner');
  const modalStatusDot = document.getElementById('modalStatusDot');
  const modalStatusText = document.getElementById('modalStatusText');

  // Search History Elements
  const historyItemsContainer = document.getElementById('historyItemsContainer');
  const historyEmpty = document.getElementById('historyEmpty');
  const clearHistoryBtn = document.getElementById('clearHistoryBtn');

  // =========================================================================
  // State Management
  // =========================================================================
  let currentView = 'chatView';
  let quizQuestions = [];
  let currentQuestionIndex = 0;
  let userQuizAnswers = {}; // { questionId: selectedIndex }
  let checkedQuestions = {}; // { questionId: boolean }
  let conversationHistory = []; // [ { role: 'user'|'assistant', content: string } ]
  let searchHistory = []; // [ { id: string, query: string, timestamp: number } ]

  // =========================================================================
  // View Routing Logic
  // =========================================================================
  function switchView(targetViewId) {
    // Hide all view panels
    [chatView, promptExplanationView, quizView].forEach(panel => {
      if (panel) panel.style.display = 'none';
    });

    // Remove active class from nav buttons
    [navChatBtn, navPromptExplanationBtn, navQuizBtn].forEach(btn => {
      if (btn) btn.classList.remove('active');
    });

    // Close mobile sidebar if open
    if (sidebar) sidebar.classList.remove('open');

    // Activate selected view
    currentView = targetViewId;
    if (targetViewId === 'chatView') {
      chatView.style.display = 'flex';
      navChatBtn.classList.add('active');
      currentViewTitle.textContent = 'Health Awareness Chat';
      scrollToBottom();
      userInput.focus();
    } else if (targetViewId === 'promptExplanationView') {
      promptExplanationView.style.display = 'flex';
      navPromptExplanationBtn.classList.add('active');
      currentViewTitle.textContent = 'Prompt Explanation & Safety';
    } else if (targetViewId === 'quizView') {
      quizView.style.display = 'flex';
      navQuizBtn.classList.add('active');
      currentViewTitle.textContent = 'Health Awareness Quiz';
      if (quizQuestions.length === 0) {
        loadQuizQuestions();
      }
    }
  }

  navChatBtn.addEventListener('click', () => switchView('chatView'));
  navPromptExplanationBtn.addEventListener('click', () => switchView('promptExplanationView'));
  navQuizBtn.addEventListener('click', () => switchView('quizView'));

  // Mobile menu toggle
  if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
  }

  // =========================================================================
  // Conversational Chat Engine
  // =========================================================================
  function formatMarkdown(text) {
    if (!text) return '';
    
    let html = text
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');

    // Bold
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Italics
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

    // Bullet points
    const lines = html.split('\n');
    let inList = false;
    let formattedLines = [];

    lines.forEach(line => {
      const trimmed = line.trim();
      if (trimmed.startsWith('• ') || trimmed.startsWith('- ')) {
        if (!inList) {
          formattedLines.push('<ul>');
          inList = true;
        }
        formattedLines.push(`<li>${trimmed.substring(2)}</li>`);
      } else {
        if (inList) {
          formattedLines.push('</ul>');
          inList = false;
        }
        if (trimmed.length > 0) {
          formattedLines.push(`<p>${trimmed}</p>`);
        }
      }
    });

    if (inList) formattedLines.push('</ul>');
    return formattedLines.join('');
  }

  function scrollToBottom() {
    if (chatViewport) {
      chatViewport.scrollTo({
        top: chatViewport.scrollHeight,
        behavior: 'smooth'
      });
    }
  }

  function appendUserMessage(text) {
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const row = document.createElement('div');
    row.className = 'message-row user-row';
    row.innerHTML = `
      <div class="avatar-badge user-avatar">👤</div>
      <div class="message-bubble user-bubble">
        <div class="bubble-header">
          <span class="sender-name">You</span>
          <span class="message-time">${timeStr}</span>
        </div>
        <div class="bubble-body">
          <p>${text.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</p>
        </div>
      </div>
    `;
    chatMessages.appendChild(row);
    scrollToBottom();
  }

  function appendBotMessage(data) {
    const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const row = document.createElement('div');
    row.className = 'message-row bot-row';

    let bubbleClass = 'bot-bubble';
    let icon = '🌿';

    if (data.type === 'emergency') {
      bubbleClass += ' emergency-bubble';
      icon = '🚨';
    } else if (data.type === 'refusal') {
      bubbleClass += ' refusal-bubble';
      icon = '🛡️';
    }

    const formattedContent = formatMarkdown(data.reply);

    // Source Model Badge
    let sourceBadge = '';
    if (data.source === 'gemini') {
      sourceBadge = `<span class="model-badge gemini" title="Generated by Google Gemini 1.5 Flash">⚡ Gemini 1.5 Flash</span>`;
    } else {
      sourceBadge = `<span class="model-badge knowledge-base" title="Evidence-based curated knowledge base">📚 Curated KB</span>`;
    }
    
    // Suggested chips
    let suggestionsHtml = '';
    if (data.suggested_topics && data.suggested_topics.length > 0) {
      suggestionsHtml = `
        <div class="bubble-actions">
          <span class="bubble-label">Explore related topics:</span>
          <div class="prompt-chips">
            ${data.suggested_topics.map(t => `<button class="chip-btn" data-text="${t}">${t}</button>`).join('')}
          </div>
        </div>
      `;
    }

    // Emergency action banner if emergency
    let emergencyActionHtml = '';
    if (data.type === 'emergency') {
      emergencyActionHtml = `
        <div class="emergency-action-banner">
          <span class="emergency-call-text">📞 Need immediate help? Call 911 or local emergency dispatch now.</span>
        </div>
      `;
    }

    row.innerHTML = `
      <div class="avatar-badge">${icon}</div>
      <div class="message-bubble ${bubbleClass}">
        <div class="bubble-header">
          <span class="sender-name">Vitalis Health Assistant ${sourceBadge}</span>
          <span class="message-time">${timeStr}</span>
        </div>
        <div class="bubble-body">
          ${formattedContent}
          ${emergencyActionHtml}
          <div class="disclaimer-footer-line">
            ${data.disclaimer || 'Educational purposes only. Not medical advice.'}
          </div>
        </div>
        ${suggestionsHtml}
      </div>
    `;

    chatMessages.appendChild(row);
    scrollToBottom();

    // Attach listeners to suggestion chips
    row.querySelectorAll('.chip-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const text = btn.getAttribute('data-text');
        if (text) {
          if (text.toLowerCase().includes('quiz')) {
            switchView('quizView');
          } else if (text.toLowerCase().includes('prompt explanation')) {
            switchView('promptExplanationView');
          } else {
            handleSendMessage(text);
          }
        }
      });
    });
  }

  async function handleSendMessage(messageText) {
    const text = (messageText || userInput.value || '').trim();
    if (!text) return;

    // Reset input
    userInput.value = '';
    userInput.style.height = 'auto';
    sendBtn.disabled = true;

    // Save to Search & Chat History
    addSearchHistoryItem(text);

    // Snapshot prior conversation history before this turn
    const priorHistory = [...conversationHistory];
    conversationHistory.push({ role: 'user', content: text });

    // Display user message
    appendUserMessage(text);

    // Show typing indicator
    typingIndicator.style.display = 'flex';
    scrollToBottom();

    try {
      const storedApiKey = getStoredApiKey();
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(storedApiKey ? { 'X-Google-Api-Key': storedApiKey } : {})
        },
        body: JSON.stringify({
          message: text,
          history: priorHistory,
          api_key: storedApiKey
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned HTTP ${response.status}`);
      }

      const data = await response.json();

      // Record bot response in conversation history
      conversationHistory.push({ role: 'assistant', content: data.reply || '' });
      
      // Simulate natural typing delay for smooth UX
      setTimeout(() => {
        typingIndicator.style.display = 'none';
        appendBotMessage(data);
        sendBtn.disabled = false;
      }, 400);

    } catch (err) {
      typingIndicator.style.display = 'none';
      const fallbackData = {
        reply: "I am having difficulty connecting to the health education server. Please ensure the local backend is running.",
        type: "standard",
        source: "knowledge_base",
        disclaimer: "Educational health assistant."
      };
      conversationHistory.push({ role: 'assistant', content: fallbackData.reply });
      appendBotMessage(fallbackData);
      sendBtn.disabled = false;
    }
  }

  // Handle form submission
  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    handleSendMessage();
  });

  // Handle Enter key for textarea
  userInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  });

  // Auto-resize textarea
  userInput.addEventListener('input', () => {
    userInput.style.height = 'auto';
    userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
  });

  // Sidebar suggested topics
  document.querySelectorAll('.topic-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const prompt = chip.getAttribute('data-prompt');
      switchView('chatView');
      handleSendMessage(prompt);
    });
  });

  // Chat bubble initial chips
  document.querySelectorAll('.chip-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const text = btn.getAttribute('data-text');
      if (text) handleSendMessage(text);
    });
  });

  // Clear Chat Button
  clearChatBtn.addEventListener('click', () => {
    const welcome = document.getElementById('welcomeMessage');
    chatMessages.innerHTML = '';
    if (welcome) chatMessages.appendChild(welcome);
    conversationHistory = [];
    scrollToBottom();
  });

  // =========================================================================
  // Prompt Explanation View Logic
  // =========================================================================
  copyPromptBtn.addEventListener('click', () => {
    const promptText = document.getElementById('systemPromptCode').textContent;
    navigator.clipboard.writeText(promptText).then(() => {
      const orig = copyPromptBtn.textContent;
      copyPromptBtn.textContent = '✅ Copied!';
      setTimeout(() => {
        copyPromptBtn.textContent = orig;
      }, 2000);
    });
  });

  // Guardrail test buttons
  testDiagnosticBtn.addEventListener('click', () => {
    switchView('chatView');
    handleSendMessage("Do I have bronchitis? Diagnose my persistent cough.");
  });

  testEmergencyBtn.addEventListener('click', () => {
    switchView('chatView');
    handleSendMessage("I have severe crushing chest pain and cannot breathe.");
  });

  testEducationBtn.addEventListener('click', () => {
    switchView('chatView');
    handleSendMessage("What are healthy daily hydration habits and hydration markers?");
  });

  // =========================================================================
  // Health Awareness Quiz Engine
  // =========================================================================
  async function loadQuizQuestions() {
    try {
      const response = await fetch('/api/quiz');
      const data = await response.json();
      quizQuestions = data.questions || [];
      currentQuestionIndex = 0;
      userQuizAnswers = {};
      checkedQuestions = {};

      const countBadge = document.getElementById('quizCountBadge');
      if (countBadge) countBadge.textContent = `${quizQuestions.length} Qs`;

      renderCurrentQuestion();
    } catch (err) {
      console.error("Failed to load quiz:", err);
      questionTextDisplay.textContent = "Unable to load quiz questions at this time.";
    }
  }

  function renderCurrentQuestion() {
    if (quizQuestions.length === 0) return;

    quizQuestionCard.style.display = 'flex';
    quizResultsCard.style.display = 'none';

    const q = quizQuestions[currentQuestionIndex];
    const total = quizQuestions.length;

    // Progress updates
    quizProgressText.textContent = `Question ${currentQuestionIndex + 1} of ${total}`;
    quizCategoryTag.textContent = q.category || "General Health";
    const percent = Math.round(((currentQuestionIndex + 1) / total) * 100);
    quizProgressFill.style.width = `${percent}%`;

    // Question content
    questionNumberDisplay.textContent = `Q${currentQuestionIndex + 1}`;
    questionTextDisplay.textContent = q.question;

    // Reset controls
    prevQuestionBtn.disabled = (currentQuestionIndex === 0);
    feedbackBox.style.display = 'none';

    const selectedIdx = userQuizAnswers[q.id];
    const isChecked = checkedQuestions[q.id];

    // Render options
    optionsList.innerHTML = '';
    const letters = ['A', 'B', 'C', 'D', 'E'];

    q.options.forEach((optText, idx) => {
      const btn = document.createElement('button');
      btn.className = 'option-btn';
      if (selectedIdx === idx) btn.classList.add('selected');
      if (isChecked) btn.disabled = true;

      btn.innerHTML = `
        <span class="opt-letter">${letters[idx] || (idx + 1)}</span>
        <span class="opt-text">${optText}</span>
      `;

      btn.addEventListener('click', () => {
        if (checkedQuestions[q.id]) return;

        userQuizAnswers[q.id] = idx;
        optionsList.querySelectorAll('.option-btn').forEach((b, i) => {
          b.classList.toggle('selected', i === idx);
        });
        checkAnswerBtn.disabled = false;
      });

      optionsList.appendChild(btn);
    });

    if (isChecked) {
      checkAnswerBtn.style.display = 'none';
      if (currentQuestionIndex === total - 1) {
        finishQuizBtn.style.display = 'inline-flex';
        nextQuestionBtn.style.display = 'none';
      } else {
        nextQuestionBtn.style.display = 'inline-flex';
        finishQuizBtn.style.display = 'none';
      }
      showCachedFeedback(q);
    } else {
      checkAnswerBtn.style.display = 'inline-flex';
      checkAnswerBtn.disabled = (selectedIdx === undefined);
      nextQuestionBtn.style.display = 'none';
      finishQuizBtn.style.display = 'none';
    }
  }

  async function checkCurrentAnswer() {
    const q = quizQuestions[currentQuestionIndex];
    const selectedIdx = userQuizAnswers[q.id];
    if (selectedIdx === undefined) return;

    checkAnswerBtn.disabled = true;

    try {
      const response = await fetch('/api/quiz/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers: { [q.id]: selectedIdx } })
      });

      const data = await response.json();
      const feedbackItem = (data.feedback || []).find(f => f.id === q.id);

      if (feedbackItem) {
        checkedQuestions[q.id] = true;
        q._feedback = feedbackItem;

        // Visual coloring on options
        const optionBtns = optionsList.querySelectorAll('.option-btn');
        optionBtns.forEach((btn, idx) => {
          btn.disabled = true;
          if (idx === feedbackItem.correct_index) {
            btn.classList.add('correct');
          } else if (idx === selectedIdx && !feedbackItem.is_correct) {
            btn.classList.add('incorrect');
          }
        });

        // Display feedback box
        feedbackBox.className = 'feedback-box ' + (feedbackItem.is_correct ? 'correct' : 'incorrect');
        feedbackIcon.textContent = feedbackItem.is_correct ? '✅' : '💡';
        feedbackTitle.textContent = feedbackItem.is_correct ? 'Correct!' : 'Incorrect — Learning Opportunity';
        feedbackExplanation.textContent = feedbackItem.explanation;
        feedbackBox.style.display = 'block';

        // Toggle buttons
        checkAnswerBtn.style.display = 'none';
        if (currentQuestionIndex === quizQuestions.length - 1) {
          finishQuizBtn.style.display = 'inline-flex';
        } else {
          nextQuestionBtn.style.display = 'inline-flex';
        }
      }
    } catch (err) {
      console.error("Error evaluating answer:", err);
      checkAnswerBtn.disabled = false;
    }
  }

  function showCachedFeedback(q) {
    if (!q._feedback) return;
    const f = q._feedback;
    const selectedIdx = userQuizAnswers[q.id];

    const optionBtns = optionsList.querySelectorAll('.option-btn');
    optionBtns.forEach((btn, idx) => {
      btn.disabled = true;
      if (idx === f.correct_index) {
        btn.classList.add('correct');
      } else if (idx === selectedIdx && !f.is_correct) {
        btn.classList.add('incorrect');
      }
    });

    feedbackBox.className = 'feedback-box ' + (f.is_correct ? 'correct' : 'incorrect');
    feedbackIcon.textContent = f.is_correct ? '✅' : '💡';
    feedbackTitle.textContent = f.is_correct ? 'Correct!' : 'Incorrect';
    feedbackExplanation.textContent = f.explanation;
    feedbackBox.style.display = 'block';
  }

  checkAnswerBtn.addEventListener('click', checkCurrentAnswer);

  nextQuestionBtn.addEventListener('click', () => {
    if (currentQuestionIndex < quizQuestions.length - 1) {
      currentQuestionIndex++;
      renderCurrentQuestion();
    }
  });

  prevQuestionBtn.addEventListener('click', () => {
    if (currentQuestionIndex > 0) {
      currentQuestionIndex--;
      renderCurrentQuestion();
    }
  });

  async function completeQuiz() {
    try {
      const response = await fetch('/api/quiz/evaluate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ answers: userQuizAnswers })
      });

      const data = await response.json();
      displayQuizResults(data);
    } catch (err) {
      console.error("Error completing quiz:", err);
    }
  }

  finishQuizBtn.addEventListener('click', completeQuiz);

  function displayQuizResults(results) {
    quizQuestionCard.style.display = 'none';
    quizResultsCard.style.display = 'flex';

    scorePercentDisplay.textContent = `${results.percentage}%`;
    scoreRatioDisplay.textContent = `${results.score}/${results.total} Correct`;
    resultsTitle.textContent = results.percentage >= 80
      ? '🏆 Outstanding Health Literacy!'
      : results.percentage >= 50
      ? '👏 Solid Health Awareness!'
      : '🌱 Great Learning Opportunity!';
    
    resultsSummaryText.textContent = results.summary;

    // Render detailed review
    detailedReviewContainer.innerHTML = '';
    (results.feedback || []).forEach((item, i) => {
      const div = document.createElement('div');
      div.className = 'review-item ' + (item.is_correct ? 'correct' : 'incorrect');

      const correctChoiceText = item.options[item.correct_index] || '';
      const userChoiceText = item.selected_index !== null && item.selected_index !== undefined
        ? item.options[item.selected_index]
        : 'Not answered';

      div.innerHTML = `
        <div class="review-q-title">
          <span class="review-badge ${item.is_correct ? 'correct' : 'incorrect'}">
            ${item.is_correct ? 'Correct' : 'Needs Review'}
          </span>
          Q${i + 1}: ${item.question}
        </div>
        <div style="font-size: 0.84rem; color: var(--text-secondary);">
          <strong>Your Answer:</strong> ${userChoiceText} ${item.is_correct ? '✓' : '✗'}
          ${!item.is_correct ? `<br><strong>Correct Answer:</strong> ${correctChoiceText}` : ''}
        </div>
        <div class="review-explanation">
          <strong>Key Health Insight:</strong> ${item.explanation}
        </div>
      `;
      detailedReviewContainer.appendChild(div);
    });
  }

  retakeQuizBtn.addEventListener('click', () => {
    userQuizAnswers = {};
    checkedQuestions = {};
    currentQuestionIndex = 0;
    quizQuestions.forEach(q => delete q._feedback);
    renderCurrentQuestion();
  });

  reviewChatBtn.addEventListener('click', () => {
    switchView('chatView');
    handleSendMessage("I just completed the health awareness quiz! Can we discuss evidence-based habits for preventive health?");
  });

  // =========================================================================
  // Emergency Modal Handlers
  // =========================================================================
  emergencyInfoBtn.addEventListener('click', () => {
    emergencyModal.style.display = 'flex';
  });

  closeEmergencyModalBtn.addEventListener('click', () => {
    emergencyModal.style.display = 'none';
  });

  dismissEmergencyModalBtn.addEventListener('click', () => {
    emergencyModal.style.display = 'none';
  });

  emergencyModal.addEventListener('click', (e) => {
    if (e.target === emergencyModal) {
      emergencyModal.style.display = 'none';
    }
  });

  // =========================================================================
  // Search & Conversation History Management
  // =========================================================================
  function loadSearchHistory() {
    try {
      const stored = localStorage.getItem('vitalis_search_history');
      searchHistory = stored ? JSON.parse(stored) : [];
    } catch (e) {
      searchHistory = [];
    }
    renderSearchHistory();
  }

  function saveSearchHistory() {
    try {
      localStorage.setItem('vitalis_search_history', JSON.stringify(searchHistory));
    } catch (e) {
      console.warn('Could not save search history', e);
    }
  }

  function formatTimeAgo(timestamp) {
    if (!timestamp) return 'Earlier';
    const seconds = Math.floor((Date.now() - timestamp) / 1000);
    if (seconds < 60) return 'Just now';
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  }

  function addSearchHistoryItem(query) {
    if (!query || !query.trim()) return;
    const clean = query.trim();
    // Exclude simple one-word commands from bloating history
    if (clean.length < 2) return;

    // Filter out existing occurrence to move to top
    searchHistory = searchHistory.filter(item => item.query.toLowerCase() !== clean.toLowerCase());
    searchHistory.unshift({
      id: Date.now().toString(36) + Math.random().toString(36).substr(2, 4),
      query: clean,
      timestamp: Date.now()
    });

    if (searchHistory.length > 25) {
      searchHistory = searchHistory.slice(0, 25);
    }

    saveSearchHistory();
    renderSearchHistory();
  }

  function deleteSearchHistoryItem(id) {
    searchHistory = searchHistory.filter(item => item.id !== id);
    saveSearchHistory();
    renderSearchHistory();
  }

  function renderSearchHistory() {
    if (!historyItemsContainer) return;
    historyItemsContainer.innerHTML = '';

    if (searchHistory.length === 0) {
      const emptyDiv = document.createElement('div');
      emptyDiv.className = 'history-empty';
      emptyDiv.id = 'historyEmpty';
      emptyDiv.innerHTML = '<span>No previous searches yet</span>';
      historyItemsContainer.appendChild(emptyDiv);
      return;
    }

    searchHistory.forEach(item => {
      const el = document.createElement('div');
      el.className = 'history-item';
      el.title = `Click to re-search: "${item.query}"`;
      el.innerHTML = `
        <div class="history-item-content">
          <span class="history-item-text">${item.query.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</span>
          <span class="history-item-time">${formatTimeAgo(item.timestamp)}</span>
        </div>
        <button type="button" class="history-item-del" title="Delete from search history" data-id="${item.id}">&times;</button>
      `;

      el.addEventListener('click', (e) => {
        if (e.target.classList.contains('history-item-del')) return;
        switchView('chatView');
        handleSendMessage(item.query);
      });

      const delBtn = el.querySelector('.history-item-del');
      if (delBtn) {
        delBtn.addEventListener('click', (e) => {
          e.stopPropagation();
          deleteSearchHistoryItem(item.id);
        });
      }

      historyItemsContainer.appendChild(el);
    });
  }

  if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener('click', () => {
      if (searchHistory.length === 0) return;
      if (confirm("Clear all previous search and query history?")) {
        searchHistory = [];
        saveSearchHistory();
        renderSearchHistory();
      }
    });
  }

  // =========================================================================
  // Google Gemini API Key Management
  // =========================================================================
  function getStoredApiKey() {
    try {
      return (localStorage.getItem('vitalis_google_api_key') || '').trim();
    } catch (e) {
      return '';
    }
  }

  async function checkApiKeyStatus() {
    const localKey = getStoredApiKey();
    try {
      const res = await fetch('/api/api-key/status');
      const data = await res.json();
      
      const isConnected = !!(localKey || data.configured);

      if (isConnected) {
        headerKeyDot.className = 'key-status-dot';
        headerKeyLabel.textContent = 'Gemini Live';
        apiKeySettingsBtn.className = 'action-btn api-key-badge-btn';
        apiKeySettingsBtn.title = 'Google Gemini API Active - Click to configure';
      } else {
        headerKeyDot.className = 'key-status-dot offline';
        headerKeyLabel.textContent = 'Offline Mode';
        apiKeySettingsBtn.className = 'action-btn api-key-badge-btn offline';
        apiKeySettingsBtn.title = 'Offline Knowledge Base Mode - Click to add Google API key';
      }
    } catch (err) {
      console.warn('Could not check API key status:', err);
    }
  }

  function openApiKeyModal() {
    const localKey = getStoredApiKey();
    apiKeyInput.value = localKey;
    apiKeyInput.type = 'password';

    if (localKey) {
      removeApiKeyBtn.style.display = 'inline-block';
      apiKeyModalStatusBanner.className = 'api-status-banner connected';
      modalStatusText.textContent = 'Google Gemini API key active in browser.';
    } else {
      removeApiKeyBtn.style.display = 'none';
      apiKeyModalStatusBanner.className = 'api-status-banner disconnected';
      modalStatusText.textContent = 'Offline mode: Using curated evidence-based knowledge base.';
    }

    apiKeyModal.style.display = 'flex';
  }

  function closeApiKeyModal() {
    apiKeyModal.style.display = 'none';
  }

  async function handleSaveApiKey() {
    const key = apiKeyInput.value.trim();
    if (!key) {
      alert("Please enter a Google API Key or click Cancel.");
      return;
    }

    saveApiKeyBtn.disabled = true;
    saveApiKeyBtn.textContent = "Verifying...";
    apiKeyModalStatusBanner.className = 'api-status-banner';
    modalStatusText.textContent = "Testing key with Google Generative Language API...";

    try {
      const res = await fetch('/api/api-key/validate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: key })
      });
      const data = await res.json();

      if (data.valid) {
        localStorage.setItem('vitalis_google_api_key', key);
        apiKeyModalStatusBanner.className = 'api-status-banner connected';
        modalStatusText.textContent = "✅ Google Gemini API key verified and saved successfully!";
        removeApiKeyBtn.style.display = 'inline-block';
        checkApiKeyStatus();
        setTimeout(() => {
          closeApiKeyModal();
        }, 1200);
      } else {
        apiKeyModalStatusBanner.className = 'api-status-banner error';
        modalStatusText.textContent = `❌ ${data.message || 'Invalid API Key. Please verify in Google AI Studio.'}`;
      }
    } catch (err) {
      apiKeyModalStatusBanner.className = 'api-status-banner error';
      modalStatusText.textContent = `❌ Verification error: ${err.message}`;
    } finally {
      saveApiKeyBtn.disabled = false;
      saveApiKeyBtn.textContent = "Test & Save";
    }
  }

  function handleRemoveApiKey() {
    if (confirm("Remove Google API key from browser? Vitalis will revert to the offline knowledge base.")) {
      localStorage.removeItem('vitalis_google_api_key');
      apiKeyInput.value = '';
      removeApiKeyBtn.style.display = 'none';
      apiKeyModalStatusBanner.className = 'api-status-banner disconnected';
      modalStatusText.textContent = 'API key removed. Running on offline knowledge base.';
      checkApiKeyStatus();
    }
  }

  // API Key event listeners
  if (apiKeySettingsBtn) {
    apiKeySettingsBtn.addEventListener('click', openApiKeyModal);
  }
  if (closeApiKeyModalBtn) {
    closeApiKeyModalBtn.addEventListener('click', closeApiKeyModal);
  }
  if (cancelApiKeyModalBtn) {
    cancelApiKeyModalBtn.addEventListener('click', closeApiKeyModal);
  }
  if (saveApiKeyBtn) {
    saveApiKeyBtn.addEventListener('click', handleSaveApiKey);
  }
  if (removeApiKeyBtn) {
    removeApiKeyBtn.addEventListener('click', handleRemoveApiKey);
  }
  if (toggleKeyVisibilityBtn) {
    toggleKeyVisibilityBtn.addEventListener('click', () => {
      apiKeyInput.type = apiKeyInput.type === 'password' ? 'text' : 'password';
    });
  }
  if (apiKeyModal) {
    apiKeyModal.addEventListener('click', (e) => {
      if (e.target === apiKeyModal) closeApiKeyModal();
    });
  }

  // =========================================================================
  // Initialize App State
  // =========================================================================
  loadSearchHistory();
  checkApiKeyStatus();

  // Focus input
  userInput.focus();
});
