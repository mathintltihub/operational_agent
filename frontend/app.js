/**
 * Operations Agent - Frontend JavaScript
 */

// API Configuration
const API_BASE = 'http://127.0.0.1:8000';

// State
let sampleTickets = [];

// DOM Elements
const elements = {
    ticketTitle: document.getElementById('ticket-title'),
    ticketDescription: document.getElementById('ticket-description'),
    analyzeBtn: document.getElementById('analyze-btn'),
    resetBtn: document.getElementById('reset-btn'),
    sampleTicketsContainer: document.getElementById('sample-tickets'),
    resultsSection: document.getElementById('results-section'),
    loading: document.getElementById('loading'),
    errorMessage: document.getElementById('error-message'),
    resultCards: document.getElementById('result-cards'),

    // Result fields
    ticketId: document.getElementById('ticket-id'),
    issueType: document.getElementById('issue-type'),
    priority: document.getElementById('priority'),
    impactedArea: document.getElementById('impacted-area'),
    recommendedTeam: document.getElementById('recommended-team'),
    confidenceScore: document.getElementById('confidence-score'),
    confidenceFill: document.getElementById('confidence-fill'),
    troubleshootingSteps: document.getElementById('troubleshooting-steps'),
    reasoningSummary: document.getElementById('reasoning-summary')
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadSampleTickets();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    elements.analyzeBtn.addEventListener('click', analyzeTicket);
    elements.resetBtn.addEventListener('click', resetForm);

    // Allow Enter key to submit
    elements.ticketTitle.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') elements.ticketDescription.focus();
    });
    elements.ticketDescription.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && e.ctrlKey) analyzeTicket();
    });
}

// Load Sample Tickets
async function loadSampleTickets() {
    try {
        const response = await fetch(`${API_BASE}/sample-tickets`);
        if (!response.ok) throw new Error('Failed to load sample tickets');

        sampleTickets = await response.json();
        renderSampleTickets();
    } catch (error) {
        console.error('Error loading sample tickets:', error);
        elements.sampleTicketsContainer.innerHTML = `
            <p class="sample-error">Could not load sample tickets. Make sure the backend is running.</p>
        `;
    }
}

// Render Sample Tickets
function renderSampleTickets() {
    elements.sampleTicketsContainer.innerHTML = sampleTickets.map(ticket => `
        <div class="sample-ticket" data-id="${ticket.id}">
            <div class="sample-ticket-title">${escapeHtml(ticket.title)}</div>
            <div class="sample-ticket-desc">${escapeHtml(truncate(ticket.description, 100))}</div>
        </div>
    `).join('');

    // Add click handlers
    document.querySelectorAll('.sample-ticket').forEach(el => {
        el.addEventListener('click', () => {
            const ticketId = el.dataset.id;
            const ticket = sampleTickets.find(t => t.id === ticketId);
            if (ticket) {
                loadTicket(ticket);
            }
        });
    });
}

// Load a ticket into the form
function loadTicket(ticket) {
    elements.ticketTitle.value = ticket.title;
    elements.ticketDescription.value = ticket.description;
    hideResults();
}

// Analyze Ticket
async function analyzeTicket() {
    const title = elements.ticketTitle.value.trim();
    const description = elements.ticketDescription.value.trim();

    // Validation
    if (!title) {
        showError('Please enter a ticket title');
        elements.ticketTitle.focus();
        return;
    }
    if (!description) {
        showError('Please enter a ticket description');
        elements.ticketDescription.focus();
        return;
    }

    // Show loading state
    hideError();
    showLoading(true);
    elements.analyzeBtn.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/analyze-ticket`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ title, description })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Analysis failed');
        }

        const result = await response.json();
        displayResults(result);
    } catch (error) {
        showError(error.message);
        console.error('Analysis error:', error);
    } finally {
        showLoading(false);
        elements.analyzeBtn.disabled = false;
    }
}

// Display Results
function displayResults(result) {
    // Fill in result fields
    elements.ticketId.textContent = result.ticket_id || '-';
    elements.issueType.textContent = result.issue_type || '-';
    elements.priority.textContent = result.priority || '-';
    elements.impactedArea.textContent = result.impacted_area || '-';
    elements.recommendedTeam.textContent = result.recommended_team || '-';

    // Confidence
    const confidence = result.confidence_score || 0;
    elements.confidenceScore.textContent = `${(confidence * 100).toFixed(0)}%`;
    elements.confidenceFill.style.width = `${confidence * 100}%`;

    // Priority color
    elements.priority.className = `card-value priority-${result.priority || ''}`;

    // Troubleshooting steps
    if (result.troubleshooting_steps && result.troubleshooting_steps.length > 0) {
        elements.troubleshootingSteps.innerHTML = result.troubleshooting_steps
            .map(step => `<li>${escapeHtml(step)}</li>`)
            .join('');
    } else {
        elements.troubleshootingSteps.innerHTML = '<li>No troubleshooting steps available</li>';
    }

    // Reasoning
    elements.reasoningSummary.textContent = result.reasoning_summary || '-';

    // Show results
    elements.resultsSection.classList.remove('hidden');
}

// Reset Form
function resetForm() {
    elements.ticketTitle.value = '';
    elements.ticketDescription.value = '';
    hideResults();
    hideError();
    elements.ticketTitle.focus();
}

// Hide Results
function hideResults() {
    elements.resultsSection.classList.add('hidden');
}

// Show Loading
function showLoading(show) {
    if (show) {
        elements.loading.classList.add('active');
        elements.resultCards.classList.add('hidden');
    } else {
        elements.loading.classList.remove('active');
        elements.resultCards.classList.remove('hidden');
    }
}

// Show Error
function showError(message) {
    elements.errorMessage.textContent = message;
    elements.errorMessage.classList.add('active');
}

// Hide Error
function hideError() {
    elements.errorMessage.classList.remove('active');
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function truncate(text, length) {
    if (text.length <= length) return text;
    return text.substring(0, length) + '...';
}