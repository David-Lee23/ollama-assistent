// Dashboard JavaScript - Student Assistant Frontend

class StudentAssistant {
    constructor() {
        this.init();
    }

    init() {
        this.bindEvents();
        this.updateMemoryStatus();
        this.setupAutoResize();
    }

    bindEvents() {
        // Chat input events
        const messageInput = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');
        
        messageInput.addEventListener('input', this.handleInputChange.bind(this));
        messageInput.addEventListener('keypress', this.handleKeyPress.bind(this));
        sendBtn.addEventListener('click', this.sendMessage.bind(this));

        // Memory search events
        const memorySearchBtn = document.getElementById('memory-search-btn');
        const memorySearchInput = document.getElementById('memory-search-input');
        
        memorySearchBtn.addEventListener('click', this.searchMemory.bind(this));
        memorySearchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchMemory();
        });

        // Canvas tool events
        document.getElementById('get-assignments-btn').addEventListener('click', () => {
            this.getCanvasData('assignments');
        });
        document.getElementById('get-announcements-btn').addEventListener('click', () => {
            this.getCanvasData('announcements');
        });

        // Clear memory events
        document.getElementById('clear-chat-btn').addEventListener('click', this.clearMemory.bind(this));
    }

    handleInputChange() {
        const input = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');
        sendBtn.disabled = input.value.trim() === '';
    }

    handleKeyPress(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.sendMessage();
        }
    }

    async sendMessage() {
        const input = document.getElementById('message-input');
        const message = input.value.trim();
        
        if (!message) return;

        // Add user message to chat
        this.addMessage('user', message);
        input.value = '';
        this.handleInputChange();

        // Show loading
        this.showLoading();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.addMessage('assistant', data.response);
                this.updateMemoryCount(data.message_count);
            } else {
                this.addMessage('assistant', `Error: ${data.error}`);
            }
        } catch (error) {
            this.addMessage('assistant', `Network error: ${error.message}`);
        } finally {
            this.hideLoading();
        }
    }

    addMessage(role, content) {
        const chatMessages = document.getElementById('chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;

        const avatarDiv = document.createElement('div');
        avatarDiv.className = 'message-avatar';
        avatarDiv.innerHTML = role === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';

        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';

        const textDiv = document.createElement('div');
        textDiv.className = 'message-text';
        textDiv.innerHTML = this.formatMessage(content);

        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = new Date().toLocaleTimeString();

        contentDiv.appendChild(textDiv);
        contentDiv.appendChild(timeDiv);
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(contentDiv);

        // Remove welcome message if it exists
        const welcomeMessage = chatMessages.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.remove();
        }

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    formatMessage(content) {
        // Basic formatting for message content
        return content
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>');
    }

    async searchMemory() {
        const input = document.getElementById('memory-search-input');
        const term = input.value.trim();
        
        if (!term) return;

        const resultsDiv = document.getElementById('search-results');
        resultsDiv.innerHTML = '<div class="loading">Searching...</div>';

        try {
            const response = await fetch('/api/memory/search', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ term, limit: 5 })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.displaySearchResults(data.results, data.term);
            } else {
                resultsDiv.innerHTML = `<div class="error">Error: ${data.error}</div>`;
            }
        } catch (error) {
            resultsDiv.innerHTML = `<div class="error">Network error: ${error.message}</div>`;
        }
    }

    displaySearchResults(results, term) {
        const resultsDiv = document.getElementById('search-results');
        
        if (results.length === 0) {
            resultsDiv.innerHTML = `<div class="no-results">No results found for "${term}"</div>`;
            return;
        }

        const resultsHtml = results.map(result => {
            const date = new Date(result.timestamp).toLocaleDateString();
            const preview = result.content.length > 100 ? 
                result.content.substring(0, 97) + '...' : 
                result.content;
            
            return `
                <div class="search-result">
                    <div class="search-result-role">${result.role === 'user' ? '👤 You' : '🤖 Assistant'}</div>
                    <div class="search-result-content">${preview}</div>
                    <div class="search-result-time">${date}</div>
                </div>
            `;
        }).join('');

        resultsDiv.innerHTML = `
            <div class="search-header">Found ${results.length} result(s) for "${term}":</div>
            ${resultsHtml}
        `;
    }

    async getCanvasData(type) {
        const resultsDiv = document.getElementById('canvas-results');
        resultsDiv.innerHTML = '<div class="loading">Loading...</div>';

        try {
            const response = await fetch(`/api/canvas/${type}`);
            const data = await response.json();
            
            if (response.ok) {
                this.displayCanvasResults(type, data[type] || data);
            } else {
                resultsDiv.innerHTML = `<div class="error">Error: ${data.error}</div>`;
            }
        } catch (error) {
            resultsDiv.innerHTML = `<div class="error">Network error: ${error.message}</div>`;
        }
    }

    displayCanvasResults(type, data) {
        const resultsDiv = document.getElementById('canvas-results');
        
        if (!data || data.length === 0) {
            resultsDiv.innerHTML = `<div class="no-results">No ${type} found</div>`;
            return;
        }

        const resultsHtml = Array.isArray(data) ? 
            data.slice(0, 5).map(item => `
                <div class="canvas-result">
                    <div class="canvas-result-title">${item.title || item.name || 'Item'}</div>
                    <div class="canvas-result-meta">${item.due_date || item.created_at || ''}</div>
                </div>
            `).join('') :
            `<div class="canvas-result">${JSON.stringify(data, null, 2)}</div>`;

        resultsDiv.innerHTML = `
            <div class="canvas-header">${type.charAt(0).toUpperCase() + type.slice(1)}:</div>
            ${resultsHtml}
        `;
    }

    async clearMemory() {
        if (!confirm('Are you sure you want to clear all conversation memory? This cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch('/api/memory/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();
            
            if (response.ok) {
                // Clear chat messages
                const chatMessages = document.getElementById('chat-messages');
                chatMessages.innerHTML = `
                    <div class="message assistant-message">
                        <div class="message-avatar">
                            <i class="fas fa-robot"></i>
                        </div>
                        <div class="message-content">
                            <div class="message-text">
                                <p>Memory cleared! Starting fresh. How can I help you today?</p>
                            </div>
                            <div class="message-time">Just now</div>
                        </div>
                    </div>
                `;
                
                // Update memory count
                this.updateMemoryCount(0);
                
                // Clear search results
                document.getElementById('search-results').innerHTML = '';
                
                this.showToast('Memory cleared successfully', 'success');
            } else {
                this.showToast(`Error: ${data.error}`, 'error');
            }
        } catch (error) {
            this.showToast(`Network error: ${error.message}`, 'error');
        }
    }

    async updateMemoryStatus() {
        try {
            const response = await fetch('/api/memory/status');
            const data = await response.json();
            
            if (response.ok) {
                this.updateMemoryCount(data.message_count);
            }
        } catch (error) {
            console.error('Failed to update memory status:', error);
        }
    }

    updateMemoryCount(count) {
        document.getElementById('memory-count').textContent = count;
        const totalMessages = document.getElementById('total-messages');
        if (totalMessages) {
            totalMessages.textContent = count;
        }
    }

    showLoading() {
        document.getElementById('loading-overlay').classList.add('show');
    }

    hideLoading() {
        document.getElementById('loading-overlay').classList.remove('show');
    }

    showToast(message, type = 'info') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        
        const container = document.getElementById('toast-container');
        if (!container) {
            const toastContainer = document.createElement('div');
            toastContainer.id = 'toast-container';
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
        
        document.getElementById('toast-container').appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    setupAutoResize() {
        const input = document.getElementById('message-input');
        input.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new StudentAssistant();
});
