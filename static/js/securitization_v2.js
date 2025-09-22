// Securitization Platform V2 - Clean Frontend Implementation
"use strict";

class SecuritizationPlatform {
    constructor() {
        this.currentGate = 1;
        this.currentProject = null;
        this.gate2Id = null;
        this.gate3Id = null;
        this.autoSaveInterval = null;
        this.init();
    }

    init() {
        console.log('Initializing Securitization Platform V2');
        this.clearLocalStorage();
        this.setupEventListeners();
        this.loadInitialData();
    }

    clearLocalStorage() {
        // Remove all localStorage usage to ensure cloud-only storage
        const keysToRemove = ['projects', 'drafts', 'trash', 'fredDailyCache', 'fredWeeklyCache', 'fredMonthlyCache'];
        keysToRemove.forEach(key => localStorage.removeItem(key));
        console.log('LocalStorage cleared');
    }

    setupEventListeners() {
        // Gate navigation
        document.querySelectorAll('[data-gate]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const gate = parseInt(e.target.dataset.gate);
                this.navigateToGate(gate);
            });
        });

        // Project creation
        const createBtn = document.getElementById('create-project-btn');
        if (createBtn) {
            createBtn.addEventListener('click', () => this.createNewProject());
        }

        // Auto-save on input changes
        document.querySelectorAll('.project-input').forEach(input => {
            input.addEventListener('blur', () => this.autoSave());
            input.addEventListener('change', () => this.scheduleAutoSave());
        });

        // Gate progression buttons
        const progressGate2Btn = document.getElementById('progress-gate2-btn');
        if (progressGate2Btn) {
            progressGate2Btn.addEventListener('click', () => this.progressToGate2());
        }

        const progressGate3Btn = document.getElementById('progress-gate3-btn');
        if (progressGate3Btn) {
            progressGate3Btn.addEventListener('click', () => this.progressToGate3());
        }

        // Calculate button for Gate 2
        const calculateBtn = document.getElementById('calculate-derived-btn');
        if (calculateBtn) {
            calculateBtn.addEventListener('click', () => this.calculateDerivedFields());
        }

        // Permutation controls
        const addVariableBtn = document.getElementById('add-variable-btn');
        if (addVariableBtn) {
            addVariableBtn.addEventListener('click', () => this.showAddVariableModal());
        }

        const runPermutationBtn = document.getElementById('run-permutation-btn');
        if (runPermutationBtn) {
            runPermutationBtn.addEventListener('click', () => this.runPermutation());
        }

        // Trash controls
        const trashBtn = document.getElementById('trash-btn');
        if (trashBtn) {
            trashBtn.addEventListener('click', () => this.toggleTrashView());
        }
    }

    async loadInitialData() {
        try {
            this.showLoader('Loading projects...');
            await this.loadProjects();
            this.hideLoader();
        } catch (error) {
            console.error('Failed to load initial data:', error);
            this.hideLoader();
            this.showNotification('Failed to load projects', 'error');
        }
    }

    // ========== GATE 1: PROJECT MANAGEMENT ==========

    async createNewProject() {
        const projectData = {
            name: prompt('Enter project name:'),
            principal_amount: 1000000,
            interest_rate: 5.0,
            loan_term: 10,
            collateral_value: 1200000,
            collateral_type: 'Commercial Real Estate',
            default_probability: 1.0,
            recovery_rate: 40.0
        };

        if (!projectData.name) return;

        try {
            const response = await fetch('/api/gate1/projects', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(projectData)
            });

            const result = await response.json();

            if (result.status === 'success') {
                this.currentProject = result.project_id;
                this.showNotification('Project created successfully', 'success');
                await this.loadProjects();
                this.loadProjectIntoForm(result.project_id);
                this.startAutoSave();
            } else {
                throw new Error(result.message || 'Failed to create project');
            }
        } catch (error) {
            console.error('Error creating project:', error);
            this.showNotification(error.message || 'Failed to create project', 'error');
        }
    }

    async loadProjects() {
        try {
            const response = await fetch('/api/gate1/projects');
            const result = await response.json();

            if (result.status === 'success') {
                this.displayProjects(result.data.projects || []);
            }
        } catch (error) {
            console.error('Error loading projects:', error);
        }
    }

    displayProjects(projects) {
        const container = document.getElementById('projects-list');
        if (!container) return;

        if (projects.length === 0) {
            container.innerHTML = '<div class="empty-state">No projects yet. Click "Create Project" to get started.</div>';
            return;
        }

        let html = '';
        projects.forEach(project => {
            const data = project.project_data || {};
            html += `
                <div class="project-card" data-project-id="${project.project_id}">
                    <h3>${data.name || 'Unnamed Project'}</h3>
                    <div class="project-details">
                        <span>Principal: $${(data.principal_amount || 0).toLocaleString()}</span>
                        <span>Rate: ${data.interest_rate || 0}%</span>
                        <span>Term: ${data.loan_term || 0} years</span>
                    </div>
                    <div class="project-actions">
                        <button onclick="securitizationPlatform.loadProjectIntoForm('${project.project_id}')">Edit</button>
                        <button onclick="securitizationPlatform.deleteProject('${project.project_id}')">Delete</button>
                    </div>
                </div>
            `;
        });

        container.innerHTML = html;
    }

    loadProjectIntoForm(projectId) {
        // Find project data
        const projectCard = document.querySelector(`[data-project-id="${projectId}"]`);
        if (!projectCard) return;

        this.currentProject = projectId;

        // Load data into form fields
        // This would populate the actual form fields with project data
        console.log('Loading project:', projectId);

        this.startAutoSave();
    }

    gatherFormData() {
        const data = {};

        // Gather all input fields with class 'project-input'
        document.querySelectorAll('.project-input').forEach(input => {
            const fieldName = input.name || input.id;
            if (fieldName) {
                if (input.type === 'number') {
                    data[fieldName] = parseFloat(input.value) || 0;
                } else {
                    data[fieldName] = input.value;
                }
            }
        });

        return data;
    }

    startAutoSave() {
        // Clear existing interval
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }

        // Auto-save every 30 seconds
        this.autoSaveInterval = setInterval(() => {
            this.autoSave();
        }, 30000);
    }

    scheduleAutoSave() {
        // Debounce auto-save on rapid changes
        if (this.autoSaveTimeout) {
            clearTimeout(this.autoSaveTimeout);
        }

        this.autoSaveTimeout = setTimeout(() => {
            this.autoSave();
        }, 2000);
    }

    async autoSave() {
        if (!this.currentProject) return;

        const projectData = this.gatherFormData();

        try {
            const response = await fetch(`/api/gate1/projects/${this.currentProject}/autosave`, {
                method: 'PUT',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(projectData)
            });

            if (response.ok) {
                this.showNotification('Auto-saved', 'info', 1000);
            }
        } catch (error) {
            console.error('Auto-save failed:', error);
        }
    }

    async validateGate1() {
        if (!this.currentProject) {
            this.showNotification('No project selected', 'error');
            return false;
        }

        try {
            const response = await fetch(`/api/gate1/projects/${this.currentProject}/validate`);
            const result = await response.json();

            if (!result.valid) {
                this.showValidationErrors(result.errors || []);
                return false;
            }

            return true;
        } catch (error) {
            console.error('Validation failed:', error);
            return false;
        }
    }

    showValidationErrors(errors) {
        let message = 'Please fix the following errors:\n';
        errors.forEach(error => {
            message += `• ${error}\n`;
        });
        this.showNotification(message, 'error');
    }

    // ========== GATE 2: DERIVED CALCULATIONS ==========

    async progressToGate2() {
        const isValid = await this.validateGate1();
        if (!isValid) {
            this.showNotification('Please complete all required fields in Gate 1', 'error');
            return;
        }

        try {
            this.showLoader('Initializing Gate 2...');

            const response = await fetch(`/api/gate2/initialize/${this.currentProject}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (result.status === 'success') {
                this.gate2Id = result.gate2_id;
                this.currentGate = 2;
                this.navigateToGate(2);
                this.showNotification('Ready for calculations', 'success');
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Failed to progress to Gate 2:', error);
            this.showNotification(error.message || 'Failed to initialize Gate 2', 'error');
        } finally {
            this.hideLoader();
        }
    }

    async calculateDerivedFields() {
        if (!this.gate2Id) {
            this.showNotification('Please complete Gate 1 first', 'error');
            return;
        }

        try {
            this.showLoader('Running calculations...');

            const response = await fetch(`/api/gate2/calculate/${this.gate2Id}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (result.status === 'success') {
                this.displayDerivedFields(result.data.derived_fields || {});
                this.showNotification('Calculations complete', 'success');
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Calculation failed:', error);
            this.showNotification(error.message || 'Calculation failed', 'error');
        } finally {
            this.hideLoader();
        }
    }

    displayDerivedFields(fields) {
        const container = document.getElementById('derived-fields-container');
        if (!container) return;

        let html = '<div class="derived-fields-grid">';

        // Display each calculated field
        for (const [key, value] of Object.entries(fields)) {
            if (key === 'cash_flows' || key === 'tranches') continue; // Handle separately

            html += `
                <div class="field-card">
                    <label>${this.formatFieldName(key)}</label>
                    <div class="value">${this.formatValue(value)}</div>
                </div>
            `;
        }

        html += '</div>';

        // Add special sections
        if (fields.tranches) {
            html += this.renderTranches(fields.tranches);
        }

        if (fields.cash_flows) {
            html += this.renderCashFlows(fields.cash_flows);
        }

        container.innerHTML = html;
    }

    renderTranches(tranches) {
        let html = '<div class="tranches-section"><h3>Tranche Structure</h3>';
        html += '<table class="data-table"><thead><tr>';
        html += '<th>Class</th><th>Rating</th><th>Size</th><th>Coupon</th><th>CE</th>';
        html += '</tr></thead><tbody>';

        tranches.forEach(tranche => {
            html += `<tr>
                <td>${tranche.class}</td>
                <td>${tranche.rating}</td>
                <td>$${(tranche.size || 0).toLocaleString()}</td>
                <td>${tranche.coupon}%</td>
                <td>${tranche.credit_enhancement}%</td>
            </tr>`;
        });

        html += '</tbody></table></div>';
        return html;
    }

    renderCashFlows(cashFlows) {
        // Render first 12 periods only
        const displayFlows = cashFlows.slice(0, 12);

        let html = '<div class="cash-flows-section"><h3>Cash Flow Schedule (First Year)</h3>';
        html += '<table class="data-table"><thead><tr>';
        html += '<th>Period</th><th>Principal</th><th>Interest</th><th>Total</th><th>Balance</th>';
        html += '</tr></thead><tbody>';

        displayFlows.forEach(flow => {
            html += `<tr>
                <td>${flow.period}</td>
                <td>$${(flow.principal || 0).toLocaleString()}</td>
                <td>$${(flow.interest || 0).toLocaleString()}</td>
                <td>$${((flow.principal || 0) + (flow.interest || 0)).toLocaleString()}</td>
                <td>$${(flow.balance || 0).toLocaleString()}</td>
            </tr>`;
        });

        html += '</tbody></table></div>';
        return html;
    }

    // ========== GATE 3: PERMUTATION ENGINE ==========

    async progressToGate3() {
        if (!this.gate2Id) {
            this.showNotification('Please complete Gate 2 first', 'error');
            return;
        }

        try {
            this.showLoader('Initializing Gate 3...');

            const response = await fetch(`/api/gate3/initialize/${this.gate2Id}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (result.status === 'success') {
                this.gate3Id = result.gate3_id;
                this.currentGate = 3;
                this.navigateToGate(3);
                this.showNotification('Ready for permutation setup', 'success');
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Failed to progress to Gate 3:', error);
            this.showNotification(error.message || 'Failed to initialize Gate 3', 'error');
        } finally {
            this.hideLoader();
        }
    }

    showAddVariableModal() {
        // Create modal for adding variables
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <h2>Add Permutation Variable</h2>
                <form id="add-variable-form">
                    <label>Variable Name:
                        <input type="text" name="name" required>
                    </label>
                    <label>Type:
                        <select name="type" required>
                            <option value="continuous">Continuous</option>
                            <option value="discrete">Discrete</option>
                            <option value="categorical">Categorical</option>
                        </select>
                    </label>
                    <label>Min Value:
                        <input type="number" name="min_value" step="0.01">
                    </label>
                    <label>Max Value:
                        <input type="number" name="max_value" step="0.01">
                    </label>
                    <label>Step Size:
                        <input type="number" name="step_size" step="0.01">
                    </label>
                    <button type="submit">Add Variable</button>
                    <button type="button" onclick="this.closest('.modal').remove()">Cancel</button>
                </form>
            </div>
        `;

        document.body.appendChild(modal);

        modal.querySelector('form').addEventListener('submit', async (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            const variable = Object.fromEntries(formData);

            await this.addVariable(variable);
            modal.remove();
        });
    }

    async addVariable(variable) {
        if (!this.gate3Id) {
            this.showNotification('No Gate 3 project loaded', 'error');
            return;
        }

        try {
            const response = await fetch(`/api/gate3/${this.gate3Id}/variables`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(variable)
            });

            const result = await response.json();

            if (result.status === 'success') {
                this.showNotification('Variable added', 'success');
                // Refresh variables display
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Failed to add variable:', error);
            this.showNotification(error.message || 'Failed to add variable', 'error');
        }
    }

    async runPermutation() {
        if (!this.gate3Id) {
            this.showNotification('Please configure variables first', 'error');
            return;
        }

        if (!confirm('Run permutation analysis? This may take several minutes.')) {
            return;
        }

        try {
            this.showLoader('Running permutation analysis...');

            const response = await fetch(`/api/permutation/execute/${this.gate3Id}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (result.status === 'success') {
                this.showNotification('Permutation analysis complete', 'success');
                // Display results
                if (result.data && result.data.summary) {
                    this.displayPermutationResults(result.data.summary);
                }
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Permutation failed:', error);
            this.showNotification(error.message || 'Permutation failed', 'error');
        } finally {
            this.hideLoader();
        }
    }

    displayPermutationResults(summary) {
        const container = document.getElementById('permutation-results-container');
        if (!container) return;

        let html = '<div class="permutation-results">';
        html += '<h3>Permutation Analysis Results</h3>';

        for (const [metric, stats] of Object.entries(summary)) {
            html += `
                <div class="metric-card">
                    <h4>${this.formatFieldName(metric)}</h4>
                    <div class="stats-grid">
                        <div>Mean: ${this.formatValue(stats.mean)}</div>
                        <div>Median: ${this.formatValue(stats.median)}</div>
                        <div>Std Dev: ${this.formatValue(stats.std)}</div>
                        <div>Min: ${this.formatValue(stats.min)}</div>
                        <div>Max: ${this.formatValue(stats.max)}</div>
                    </div>
                </div>
            `;
        }

        html += '</div>';
        container.innerHTML = html;
    }

    // ========== TRASH MANAGEMENT ==========

    async deleteProject(projectId) {
        if (!confirm('Move this project to trash?')) return;

        try {
            const response = await fetch('/api/trash/move', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    collection: 'gate1_projects',
                    document_id: projectId
                })
            });

            const result = await response.json();

            if (result.status === 'success') {
                this.showNotification('Project moved to trash', 'success');
                await this.loadProjects();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Failed to delete project:', error);
            this.showNotification(error.message || 'Failed to delete project', 'error');
        }
    }

    async restoreFromTrash(trashId) {
        try {
            const response = await fetch(`/api/trash/restore/${trashId}`, {
                method: 'POST'
            });

            const result = await response.json();

            if (result.status === 'success') {
                this.showNotification('Project restored', 'success');
                await this.loadProjects();
            } else {
                throw new Error(result.message);
            }
        } catch (error) {
            console.error('Failed to restore:', error);
            this.showNotification(error.message || 'Failed to restore', 'error');
        }
    }

    toggleTrashView() {
        const trashSection = document.getElementById('trash-section');
        if (trashSection) {
            trashSection.style.display = trashSection.style.display === 'none' ? 'block' : 'none';
        }
    }

    // ========== UTILITY FUNCTIONS ==========

    navigateToGate(gateNumber) {
        // Hide all gate sections
        document.querySelectorAll('.gate-section').forEach(section => {
            section.style.display = 'none';
        });

        // Show selected gate
        const targetSection = document.getElementById(`gate${gateNumber}-section`);
        if (targetSection) {
            targetSection.style.display = 'block';
        }

        // Update navigation
        document.querySelectorAll('[data-gate]').forEach(nav => {
            nav.classList.remove('active');
            if (parseInt(nav.dataset.gate) === gateNumber) {
                nav.classList.add('active');
            }
        });

        this.currentGate = gateNumber;
    }

    showNotification(message, type = 'info', duration = 3000) {
        // Remove any existing notifications
        document.querySelectorAll('.notification').forEach(n => n.remove());

        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'error' ? '#ef4444' : type === 'success' ? '#22c55e' : '#60a5fa'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, duration);
    }

    showLoader(message = 'Loading...') {
        let loader = document.getElementById('global-loader');
        if (!loader) {
            loader = document.createElement('div');
            loader.id = 'global-loader';
            loader.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.8);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 9999;
            `;
            document.body.appendChild(loader);
        }

        loader.innerHTML = `
            <div style="text-align: center; color: white;">
                <div class="spinner"></div>
                <p style="margin-top: 20px;">${message}</p>
            </div>
        `;

        loader.style.display = 'flex';
    }

    hideLoader() {
        const loader = document.getElementById('global-loader');
        if (loader) {
            loader.style.display = 'none';
        }
    }

    formatFieldName(field) {
        return field
            .replace(/_/g, ' ')
            .replace(/\b\w/g, c => c.toUpperCase());
    }

    formatValue(value) {
        if (typeof value === 'number') {
            if (value > 1000) {
                return value.toLocaleString('en-US', {
                    minimumFractionDigits: 0,
                    maximumFractionDigits: 2
                });
            }
            return value.toFixed(2);
        }
        return value;
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.securitizationPlatform = new SecuritizationPlatform();

    // Add CSS animations
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
        .spinner {
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top: 3px solid white;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 0 auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .notification {
            transition: all 0.3s ease;
        }
        .project-card {
            background: rgba(96, 165, 250, 0.1);
            border: 1px solid rgba(96, 165, 250, 0.3);
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
        }
        .derived-fields-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .field-card {
            background: rgba(96, 165, 250, 0.05);
            padding: 15px;
            border-radius: 8px;
            border: 1px solid rgba(96, 165, 250, 0.2);
        }
        .field-card label {
            display: block;
            font-size: 0.9em;
            color: #94a3b8;
            margin-bottom: 5px;
        }
        .field-card .value {
            font-size: 1.2em;
            font-weight: 600;
            color: #60a5fa;
        }
        .data-table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .data-table th {
            background: rgba(96, 165, 250, 0.1);
            padding: 10px;
            text-align: left;
            border-bottom: 2px solid rgba(96, 165, 250, 0.3);
        }
        .data-table td {
            padding: 10px;
            border-bottom: 1px solid rgba(96, 165, 250, 0.1);
        }
    `;
    document.head.appendChild(style);
});