/**
 * Operations Agent - Chatbot Frontend
 */

// API Configuration
const API_BASE = 'http://127.0.0.1:8000';

// State
let conversationId = null;
let isProcessing = false;

// DOM Elements
const elements = {
    chatMessages: document.getElementById('chat-messages'),
    messageInput: document.getElementById('message-input'),
    sendBtn: document.getElementById('send-btn'),
    clearChatBtn: document.getElementById('clear-chat-btn'),
    quickActions: document.getElementById('quick-actions'),
    statusText: document.getElementById('status-text'),
    analysisModal: document.getElementById('analysis-modal'),
    modalBody: document.getElementById('modal-body'),
    modalClose: document.getElementById('modal-close')
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    checkHealth();
    setupEventListeners();
    autoResizeTextarea();
});

// Event Listeners
function setupEventListeners() {
    elements.sendBtn.addEventListener('click', sendMessage);
    elements.clearChatBtn.addEventListener('click', clearChat);
    elements.modalClose.addEventListener('click', closeModal);

    // Quick action buttons
    document.querySelectorAll('.quick-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const message = btn.dataset.message;
            elements.messageInput.value = message;
            sendMessage();
        });
    });

    // Enter to send (Shift+Enter for new line)
    elements.messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    elements.messageInput.addEventListener('input', autoResizeTextarea);

    // Close modal on outside click
    elements.analysisModal.addEventListener('click', (e) => {
        if (e.target === elements.analysisModal) {
            closeModal();
        }
    });
}

// Check API health
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        if (response.ok) {
            const health = await response.json();
            const mode = (health.mode || 'unknown').toUpperCase();
            elements.statusText.textContent = 'Online';
            elements.statusText.title = `Runtime mode: ${mode}`;
            elements.statusText.previousElementSibling.style.background = '#4ade80';
        } else {
            throw new Error('Health check failed');
        }
    } catch (error) {
        elements.statusText.textContent = 'Offline';
        elements.statusText.previousElementSibling.style.background = '#ef4444';
        console.error('Health check failed:', error);
    }
}

// Auto-resize textarea
function autoResizeTextarea() {
    elements.messageInput.style.height = 'auto';
    elements.messageInput.style.height = Math.min(elements.messageInput.scrollHeight, 120) + 'px';
}

// Send Message
async function sendMessage() {
    const message = elements.messageInput.value.trim();

    if (!message || isProcessing) return;

    // Add user message to chat
    addMessage('user', message);

    // Clear input
    elements.messageInput.value = '';
    autoResizeTextarea();

    // Show typing indicator
    isProcessing = true;
    elements.sendBtn.disabled = true;
    const typingIndicator = showTypingIndicator();

    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                conversation_id: conversationId
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to send message');
        }

        const result = await response.json();

        // Store conversation ID for continuity
        conversationId = result.conversation_id;

        // Remove typing indicator
        typingIndicator.remove();

        // Add assistant response
        addMessage('assistant', result.message.content, result.structured || result.analysis);

    } catch (error) {
        typingIndicator.remove();
        addMessage('assistant', `Error: ${error.message}. Please try again.`);
        console.error('Chat error:', error);
    } finally {
        isProcessing = false;
        elements.sendBtn.disabled = false;
        elements.messageInput.focus();
    }
}

// Add Message to Chat
function addMessage(role, content, analysis = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;

    const avatarSvg = role === 'user'
        ? `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
             <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
             <circle cx="12" cy="7" r="4"/>
           </svg>`
        : `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
             <circle cx="12" cy="12" r="3"/>
             <path d="M12 1v6m0 6v6m11-7h-6m-6 0H3"/>
           </svg>`;

    // Format content with line breaks and parse markdown-like formatting
    const formattedContent = formatMessageContent(content);

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatarSvg}</div>
        <div class="message-content">
            <div class="message-bubble">${formattedContent}</div>
            <div class="message-time">${formatTime(new Date())}</div>
        </div>
    `;

    elements.chatMessages.appendChild(messageDiv);
    scrollToBottom();

    // Add analysis card if available
    if (analysis) {
        setTimeout(() => {
            addAnalysisCard(analysis);
        }, 100);
    }
}

// Format message content
function formatMessageContent(content) {
    // Convert markdown-like formatting to HTML
    return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n\n/g, '<br><br>')
        .replace(/\n/g, '<br>')
        .replace(/🔍/g, '<span>🔍</span>')
        .replace(/🔴|🟠|🟡|🟢/g, '<span>$&</span>')
        .replace(/🖥️|🌐|🗄️|📱|🔐|❓|📋/g, '<span>$&</span>')
        .replace(/👥|📍|📊|💡/g, '<span>$&</span>');
}

// Add Analysis Card
function addAnalysisCard(analysis) {
    const cardDiv = document.createElement('div');
    cardDiv.className = 'analysis-card';

    // Support both structured and legacy payloads
    const issueType = analysis.issue_type || 'unknown';
    const priority = analysis.priority || 'medium';
    const team = analysis.assigned_team || analysis.recommended_team || 'Manual Review Queue';
    const source = analysis.source || 'deterministic_skills';
    const confidenceVal = analysis.confidence_score
        ? (analysis.confidence_score * 100).toFixed(0)
        : (analysis.confidence === 'high' ? '85' : analysis.confidence === 'medium' ? '60' : '40');

    const priorityClass = `priority-${priority}`;

    cardDiv.innerHTML = `
        <div class="analysis-row">
            <span class="label">Issue Type</span>
            <span class="value">${issueType}</span>
        </div>
        <div class="analysis-row">
            <span class="label">Priority</span>
            <span class="value ${priorityClass}">${priority.toUpperCase()}</span>
        </div>
        <div class="analysis-row">
            <span class="label">Team</span>
            <span class="value">${team}</span>
        </div>
        <div class="analysis-row">
            <span class="label">Confidence</span>
            <span class="value">${confidenceVal}%</span>
        </div>
        <div class="analysis-row">
            <span class="label">Source</span>
            <span class="value">${source}</span>
        </div>
        <div style="margin-top: 12px; text-align: center;">
            <button class="quick-btn" onclick="showAnalysisDetails(${JSON.stringify(analysis).replace(/"/g, '&quot;')})">
                View Full Details
            </button>
        </div>
    `;

    elements.chatMessages.appendChild(cardDiv);
    scrollToBottom();
}

// Show Analysis Details Modal
window.showAnalysisDetails = function(analysis) {
    const priority = analysis.priority || 'medium';
    const issueType = analysis.issue_type || 'unknown';
    const impactedArea = analysis.impacted_area || 'Not provided';
    const team = analysis.assigned_team || analysis.recommended_team || 'Manual Review Queue';
    const steps = analysis.solution_steps || analysis.troubleshooting_steps || [];
    const reasoning = analysis.analysis || analysis.reasoning_summary || 'No reasoning provided';
    const confScore = analysis.confidence_score
        ? analysis.confidence_score
        : (analysis.confidence === 'high' ? 0.85 : analysis.confidence === 'medium' ? 0.60 : 0.40);
    const priorityClass = `priority-${priority}`;
    const source = analysis.source || 'deterministic_skills';
    const runtimeMode = analysis.runtime_mode || 'unknown';
    const ticketId = analysis.ticket_id || 'n/a';

    elements.modalBody.innerHTML = `
        <div style="display: grid; gap: 16px;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                <div style="padding: 12px; background: var(--bg-color); border-radius: 8px;">
                    <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase;">Issue Type</div>
                    <div style="font-size: 1.1rem; font-weight: 600;">${issueType}</div>
                </div>
                <div style="padding: 12px; background: var(--bg-color); border-radius: 8px;">
                    <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase;">Priority</div>
                    <div style="font-size: 1.1rem; font-weight: 600;" class="${priorityClass}">${priority.toUpperCase()}</div>
                </div>
            </div>
            <div style="padding: 12px; background: var(--bg-color); border-radius: 8px;">
                <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase;">Impacted Area</div>
                <div style="font-size: 1.1rem; font-weight: 600;">${impactedArea}</div>
            </div>
            <div style="padding: 12px; background: var(--bg-color); border-radius: 8px;">
                <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase;">Recommended Team</div>
                <div style="font-size: 1.1rem; font-weight: 600;">${team}</div>
            </div>
            <div style="padding: 12px; background: var(--bg-color); border-radius: 8px;">
                <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase;">Confidence Score</div>
                <div style="display: flex; align-items: center; gap: 12px; margin-top: 8px;">
                    <div style="flex: 1; height: 8px; background: var(--border-color); border-radius: 4px; overflow: hidden;">
                        <div style="width: ${confScore * 100}%; height: 100%; background: var(--primary-color); border-radius: 4px;"></div>
                    </div>
                    <span style="font-weight: 600;">${(confScore * 100).toFixed(0)}%</span>
                </div>
            </div>
            <div style="padding: 12px; background: var(--bg-color); border-radius: 8px;">
                <div style="font-size: 0.75rem; color: var(--text-secondary); text-transform: uppercase; margin-bottom: 8px;">Troubleshooting Steps</div>
                <ol style="margin: 0; padding-left: 20px;">
                    ${steps.map(step => `<li style="margin: 6px 0; color: var(--text-primary);">${step}</li>`).join('')}
                </ol>
            </div>
            <div style="padding: 12px; background: var(--primary-light); border-radius: 8px; border-left: 3px solid var(--primary-color);">
                <div style="font-size: 0.75rem; color: var(--primary-color); text-transform: uppercase; margin-bottom: 4px;">Analysis Reasoning</div>
                <div style="color: var(--text-primary);">${reasoning}</div>
            </div>
            <div style="font-size: 0.75rem; color: var(--text-secondary); text-align: center; margin-top: 8px;">
                Source: ${source} | Runtime: ${runtimeMode} | Ticket ID: ${ticketId}
            </div>
        </div>
    `;

    elements.analysisModal.classList.add('active');
};

function closeModal() {
    elements.analysisModal.classList.remove('active');
}

// Show Typing Indicator
function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant-message';
    typingDiv.id = 'typing-indicator';

    typingDiv.innerHTML = `
        <div class="message-avatar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="3"/>
                <path d="M12 1v6m0 6v6m11-7h-6m-6 0H3"/>
            </svg>
        </div>
        <div class="message-content">
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        </div>
    `;

    elements.chatMessages.appendChild(typingDiv);
    scrollToBottom();

    return typingDiv;
}

// Clear Chat
async function clearChat() {
    if (conversationId) {
        try {
            await fetch(`${API_BASE}/conversation/${conversationId}`, {
                method: 'DELETE'
            });
        } catch (error) {
            console.error('Failed to clear conversation:', error);
        }
    }

    conversationId = null;
    elements.chatMessages.innerHTML = `
        <div class="message assistant-message">
            <div class="message-avatar">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <circle cx="12" cy="12" r="3"/>
                    <path d="M12 1v6m0 6v6m11-7h-6m-6 0H3"/>
                </svg>
            </div>
                <div class="message-content">
                    <div class="message-bubble">
                    Chat cleared. Share an IT operations issue and I will triage it.
                    </div>
                    <div class="message-time">${formatTime(new Date())}</div>
                </div>
            </div>
    `;
}

// Scroll to Bottom
function scrollToBottom() {
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

// Format Time
function formatTime(date) {
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}
