// Dashboard JavaScript - Student Assistant Frontend with Project Management

class StudentAssistant {
    constructor() {
        this.currentProjectId = null;
        this.projects = [];
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadProjects();
        this.updateMemoryCount();
    }

    setupEventListeners() {
        // Chat input events
        const messageInput = document.getElementById('message-input');
        const sendBtn = document.getElementById('send-btn');

        messageInput.addEventListener('input', () => {
            sendBtn.disabled = !messageInput.value.trim();
        });

        messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey && messageInput.value.trim()) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        sendBtn.addEventListener('click', () => this.sendMessage());

        // Project management events
        document.getElementById('project-select').addEventListener('change', (e) => {
            this.switchProject(parseInt(e.target.value));
        });

        document.getElementById('new-project-btn').addEventListener('click', () => {
            this.showNewProjectModal();
        });

        document.getElementById('project-settings-btn').addEventListener('click', () => {
            this.showProjectSettingsModal();
        });

        // Modal events
        this.setupModalEvents();

        // Memory search events
        document.getElementById('memory-search-btn').addEventListener('click', () => this.searchMemory());
        document.getElementById('memory-search-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.searchMemory();
        });

        // Canvas tool events
        document.getElementById('get-assignments-btn').addEventListener('click', () => this.getCanvasData('assignments'));
        document.getElementById('get-announcements-btn').addEventListener('click', () => this.getCanvasData('announcements'));

        // Clear memory events
        document.getElementById('clear-chat-btn').addEventListener('click', () => this.clearMemory());
    }

    setupModalEvents() {
        // New project modal
        document.getElementById('close-new-project-modal').addEventListener('click', () => {
            this.hideModal('new-project-modal');
        });

        document.getElementById('cancel-new-project').addEventListener('click', () => {
            this.hideModal('new-project-modal');
        });

        document.getElementById('new-project-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createProject();
        });

        // Project settings modal
        document.getElementById('close-project-settings-modal').addEventListener('click', () => {
            this.hideModal('project-settings-modal');
        });

        document.getElementById('cancel-project-settings').addEventListener('click', () => {
            this.hideModal('project-settings-modal');
        });

        document.getElementById('project-settings-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.updateProject();
        });

        document.getElementById('delete-project-btn').addEventListener('click', () => {
            this.deleteProject();
        });

        // Generate summary event
        document.getElementById('generate-summary-btn').addEventListener('click', () => {
            this.generateProjectSummary();
        });

        // Close modals on overlay click
        document.querySelectorAll('.modal-overlay').forEach(overlay => {
            overlay.addEventListener('click', (e) => {
                if (e.target === overlay) {
                    this.hideModal(overlay.id);
                }
            });
        });
    }

    async loadProjects() {
        try {
            const response = await fetch('/api/projects');
            const data = await response.json();
            
            if (response.ok) {
                this.projects = data.projects;
                this.updateProjectSelector();
                
                // Select first project by default
                if (this.projects.length > 0 && !this.currentProjectId) {
                    this.switchProject(this.projects[0].id);
                }
            } else {
                this.showToast(data.error, 'error');
            }
        } catch (error) {
            this.showToast(`Failed to load projects: ${error.message}`, 'error');
        }
    }

    updateProjectSelector() {
        const select = document.getElementById('project-select');
        select.innerHTML = '';
        
        this.projects.forEach(project => {
            const option = document.createElement('option');
            option.value = project.id;
            const summaryIndicator = project.summary ? '📝' : '📄';
            option.textContent = `${summaryIndicator} ${project.name} (${project.message_count} msgs)`;
            option.dataset.description = project.description || '';
            option.dataset.systemPrompt = project.system_prompt || '';
            option.dataset.summary = project.summary || '';
            select.appendChild(option);
        });
        
        if (this.currentProjectId) {
            select.value = this.currentProjectId;
        }
    }

    switchProject(projectId) {
        this.currentProjectId = projectId;
        
        // Update project info display
        const project = this.projects.find(p => p.id === projectId);
        if (project) {
            const descriptionElement = document.getElementById('project-description-text');
            descriptionElement.textContent = project.description || `Working on ${project.name}`;
            
            // Update project summary display
            this.updateProjectSummaryDisplay(project);
            
            // Update memory count for this project
            this.updateMemoryCount();
            
            // Clear current chat display
            this.clearChatDisplay();
            
            // Load recent messages for this project
            this.loadRecentMessages();
        }
        
        // Update project selector
        document.getElementById('project-select').value = projectId;
    }

    async loadRecentMessages() {
        try {
            const response = await fetch(`/api/memory/status?project_id=${this.currentProjectId}`);
            const data = await response.json();
            
            if (response.ok && data.recent_messages && data.recent_messages.length > 0) {
                const chatMessages = document.getElementById('chat-messages');
                
                data.recent_messages.forEach(msg => {
                    this.addMessage(msg.role, msg.content, false);
                });
            }
        } catch (error) {
            console.log('No recent messages to load');
        }
    }

    clearChatDisplay() {
        const chatMessages = document.getElementById('chat-messages');
        chatMessages.innerHTML = `
            <div class="message assistant-message">
                <div class="message-avatar">
                    <i class="fas fa-robot"></i>
                </div>
                <div class="message-content">
                    <div class="message-text">
                        <h4>Project switched! 📂</h4>
                        <p>You're now working on this project. How can I help you today?</p>
                    </div>
                    <div class="message-time">Just now</div>
                </div>
            </div>
        `;
    }

    showNewProjectModal() {
        // Reset form
        document.getElementById('new-project-form').reset();
        this.showModal('new-project-modal');
    }

    showProjectSettingsModal() {
        if (!this.currentProjectId) {
            this.showToast('Please select a project first', 'error');
            return;
        }

        const project = this.projects.find(p => p.id === this.currentProjectId);
        if (!project) return;

        // Populate form
        document.getElementById('edit-project-name').value = project.name;
        document.getElementById('edit-project-description').value = project.description || '';
        document.getElementById('edit-project-system-prompt').value = project.system_prompt || '';

        // Disable delete button for default project
        const deleteBtn = document.getElementById('delete-project-btn');
        deleteBtn.disabled = project.id === 1;
        if (project.id === 1) {
            deleteBtn.textContent = 'Cannot Delete Default Project';
        }

        this.showModal('project-settings-modal');
    }

    async createProject() {
        const name = document.getElementById('project-name').value.trim();
        const description = document.getElementById('project-description').value.trim();
        const systemPrompt = document.getElementById('project-system-prompt').value.trim();

        if (!name) {
            this.showToast('Project name is required', 'error');
            return;
        }

        try {
            const response = await fetch('/api/projects', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name,
                    description,
                    system_prompt: systemPrompt
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.hideModal('new-project-modal');
                this.showToast(data.message, 'success');
                await this.loadProjects();
                this.switchProject(data.project.id);
            } else {
                this.showToast(data.error, 'error');
            }
        } catch (error) {
            this.showToast(`Failed to create project: ${error.message}`, 'error');
        }
    }

    async updateProject() {
        if (!this.currentProjectId) return;

        const name = document.getElementById('edit-project-name').value.trim();
        const description = document.getElementById('edit-project-description').value.trim();
        const systemPrompt = document.getElementById('edit-project-system-prompt').value.trim();

        try {
            const response = await fetch(`/api/projects/${this.currentProjectId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name,
                    description,
                    system_prompt: systemPrompt
                })
            });

            const data = await response.json();

            if (response.ok) {
                this.hideModal('project-settings-modal');
                this.showToast(data.message, 'success');
                await this.loadProjects();
                this.switchProject(this.currentProjectId);
            } else {
                this.showToast(data.error, 'error');
            }
        } catch (error) {
            this.showToast(`Failed to update project: ${error.message}`, 'error');
        }
    }

    async deleteProject() {
        if (!this.currentProjectId || this.currentProjectId === 1) return;

        const project = this.projects.find(p => p.id === this.currentProjectId);
        if (!project) return;

        if (!confirm(`Are you sure you want to delete "${project.name}" and all its messages? This cannot be undone.`)) {
            return;
        }

        try {
            const response = await fetch(`/api/projects/${this.currentProjectId}`, {
                method: 'DELETE'
            });

            const data = await response.json();

            if (response.ok) {
                this.hideModal('project-settings-modal');
                this.showToast(data.message, 'success');
                await this.loadProjects();
                
                // Switch to default project
                if (this.projects.length > 0) {
                    this.switchProject(this.projects[0].id);
                }
            } else {
                this.showToast(data.error, 'error');
            }
        } catch (error) {
            this.showToast(`Failed to delete project: ${error.message}`, 'error');
        }
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.add('show');
        
        // Focus first input
        const firstInput = modal.querySelector('input, textarea');
        if (firstInput) {
            setTimeout(() => firstInput.focus(), 100);
        }
    }

    hideModal(modalId) {
        const modal = document.getElementById(modalId);
        modal.classList.remove('show');
    }

    async sendMessage() {
        const input = document.getElementById('message-input');
        const message = input.value.trim();
        
        if (!message || !this.currentProjectId) return;

        // Add user message to chat
        this.addMessage('user', message);
        input.value = '';
        document.getElementById('send-btn').disabled = true;

        // Show loading
        this.showLoading();

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    message,
                    project_id: this.currentProjectId
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.addMessage('assistant', data.response);
                this.updateMemoryCount(data.message_count);
            } else {
                this.addMessage('assistant', `Error: ${data.error}`, true);
            }
        } catch (error) {
            this.addMessage('assistant', `Network error: ${error.message}`, true);
        } finally {
            this.hideLoading();
        }
    }

    addMessage(role, content, isError = false) {
        const chatMessages = document.getElementById('chat-messages');
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        
        const avatarClass = role === 'user' ? 'fa-user' : 'fa-robot';
        const messageClass = isError ? 'error-message' : '';
        
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="fas ${avatarClass}"></i>
            </div>
            <div class="message-content">
                <div class="message-text ${messageClass}">
                    ${this.formatMessage(content)}
                </div>
                <div class="message-time">${new Date().toLocaleTimeString()}</div>
            </div>
        `;
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        // Remove welcome message if it exists
        const welcomeMessage = chatMessages.querySelector('.message:first-child');
        if (welcomeMessage && welcomeMessage.querySelector('h4')?.textContent.includes('Welcome')) {
            welcomeMessage.remove();
        }
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
                body: JSON.stringify({ 
                    term, 
                    limit: 5,
                    project_id: this.currentProjectId
                })
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

        let html = `<div class="search-header">Found ${results.length} result(s) for "${term}":</div>`;
        
        results.forEach((result, index) => {
            const time = new Date(result.timestamp).toLocaleDateString();
            const roleIcon = result.role === 'user' ? '👤' : '🤖';
            const content = result.content.length > 100 ? 
                result.content.substring(0, 100) + '...' : result.content;
            
            html += `
                <div class="search-result">
                    <div class="search-result-header">
                        <span class="search-result-role">${roleIcon} ${result.role}</span>
                        <span class="search-result-time">${time}</span>
                    </div>
                    <div class="search-result-content">${content}</div>
                </div>
            `;
        });
        
        resultsDiv.innerHTML = html;
    }

    async getCanvasData(type) {
        this.showLoading();
        
        try {
            const response = await fetch(`/api/canvas/${type}`);
            const data = await response.json();
            
            if (response.ok) {
                this.displayCanvasResults(type, data[type] || []);
            } else {
                document.getElementById('canvas-results').innerHTML = 
                    `<div class="error">Error: ${data.error}</div>`;
            }
        } catch (error) {
            document.getElementById('canvas-results').innerHTML = 
                `<div class="error">Network error: ${error.message}</div>`;
        } finally {
            this.hideLoading();
        }
    }

    displayCanvasResults(type, results) {
        const resultsDiv = document.getElementById('canvas-results');
        
        if (results.length === 0) {
            resultsDiv.innerHTML = `<div class="no-results">No ${type} found</div>`;
            return;
        }

        let html = `<div class="canvas-header">${type.charAt(0).toUpperCase() + type.slice(1)}:</div>`;
        results.slice(0, 5).forEach(item => {
            html += `<div class="canvas-item">${item.title || item.name || item}</div>`;
        });
        
        resultsDiv.innerHTML = html;
    }

    async clearMemory() {
        if (!confirm('Are you sure you want to clear all conversation memory for this project? This cannot be undone.')) {
            return;
        }

        try {
            const response = await fetch('/api/memory/clear', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ project_id: this.currentProjectId })
            });

            const data = await response.json();
            
            if (response.ok) {
                // Clear chat messages
                this.clearChatDisplay();
                
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

    async updateMemoryCount(count = null) {
        if (count === null) {
            try {
                const response = await fetch(`/api/memory/status?project_id=${this.currentProjectId}`);
                const data = await response.json();
                
                if (response.ok) {
                    count = data.message_count;
                }
            } catch (error) {
                console.log('Failed to fetch memory count');
                return;
            }
        }

        document.getElementById('memory-count').textContent = count || 0;
    }

    showLoading() {
        document.getElementById('loading-overlay').classList.add('show');
    }

    hideLoading() {
        document.getElementById('loading-overlay').classList.remove('show');
    }

    showToast(message, type = 'info') {
        // Create toast element
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check' : type === 'error' ? 'fa-exclamation-triangle' : 'fa-info'}"></i>
            <span>${message}</span>
        `;
        
        // Add to body
        document.body.appendChild(toast);
        
        // Show toast
        setTimeout(() => toast.classList.add('show'), 100);
        
        // Remove toast
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => document.body.removeChild(toast), 300);
        }, 3000);
    }

    updateProjectSummaryDisplay(project) {
        const summaryContainer = document.getElementById('project-summary');
        const summaryText = document.getElementById('project-summary-text');
        
        if (project && project.summary) {
            summaryText.textContent = project.summary;
            summaryContainer.style.display = 'block';
        } else {
            summaryContainer.style.display = 'none';
        }
    }

    async generateProjectSummary() {
        if (!this.currentProjectId) {
            this.showToast('Please select a project first', 'error');
            return;
        }

        const project = this.projects.find(p => p.id === this.currentProjectId);
        if (!project) {
            this.showToast('Project not found', 'error');
            return;
        }

        if (project.message_count < 5) {
            this.showToast('Project needs at least 5 messages to generate a summary', 'error');
            return;
        }

        try {
            this.showLoading();
            
            const response = await fetch(`/api/projects/${this.currentProjectId}/summary`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();
            this.hideLoading();

            if (response.ok) {
                this.showToast(data.message, 'success');
                
                // Update the project in our local data
                const projectIndex = this.projects.findIndex(p => p.id === this.currentProjectId);
                if (projectIndex !== -1) {
                    this.projects[projectIndex].summary = data.summary;
                    this.updateProjectSummaryDisplay(this.projects[projectIndex]);
                    this.updateProjectSelector(); // Update the summary indicator
                }
            } else {
                this.showToast(data.error, 'error');
            }
        } catch (error) {
            this.hideLoading();
            this.showToast(`Failed to generate summary: ${error.message}`, 'error');
        }
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new StudentAssistant();
});
