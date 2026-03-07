const Components = {
    modal(id, title, bodyHtml, footerHtml, size) {
        const sizeClass = size === 'large' ? 'modal-large' : size === 'small' ? 'modal-small' : '';
        return `<div class="modal-overlay" data-action="closeModal">
            <div class="modal ${sizeClass}" onclick="event.stopPropagation()">
                <div class="modal-header">
                    <h2>${title}</h2>
                    <button class="modal-close" data-action="closeModal">&times;</button>
                </div>
                <div class="modal-body">${bodyHtml}</div>
                ${footerHtml ? `<div class="modal-footer">${footerHtml}</div>` : ''}
            </div>
        </div>`;
    },

    dropdown(id, currentValue, options, placeholder) {
        const displayLabel = currentValue || placeholder || 'Select...';
        const items = options.map(opt => {
            const val = typeof opt === 'object' ? opt.value : opt;
            const label = typeof opt === 'object' ? opt.label : opt;
            const selected = val === currentValue;
            return `<div class="dropdown-item ${selected ? 'selected' : ''}" data-dropdown-id="${id}" data-value="${this._escAttr(val)}">${label}${selected ? ' <span class="check-mark">&#10003;</span>' : ''}</div>`;
        }).join('');
        return `<div class="custom-dropdown" id="${id}">
            <div class="dropdown-trigger" data-dropdown-id="${id}">${displayLabel} <span class="dropdown-arrow">&#9662;</span></div>
            <div class="dropdown-menu">${items}</div>
        </div>`;
    },

    toggle(id, checked, label) {
        return `<div class="toggle-row">
            ${label ? `<span class="toggle-label">${label}</span>` : ''}
            <div class="toggle-switch ${checked ? 'active' : ''}" data-toggle-id="${id}">
                <div class="toggle-knob"></div>
            </div>
        </div>`;
    },

    textInput(id, value, placeholder, opts) {
        const extra = opts || {};
        const type = extra.type || 'text';
        const req = extra.required ? 'required' : '';
        const readonly = extra.readonly ? 'readonly' : '';
        return `<input type="${type}" id="${id}" class="form-input ${extra.className || ''}" value="${this._escAttr(value || '')}" placeholder="${placeholder || ''}" ${req} ${readonly}>`;
    },

    textArea(id, value, placeholder, rows) {
        return `<textarea id="${id}" class="form-input form-textarea" rows="${rows || 3}" placeholder="${placeholder || ''}">${this._escHtml(value || '')}</textarea>`;
    },

    currencyInput(id, value, placeholder) {
        return `<div class="currency-input-wrapper">
            <span class="currency-symbol">$</span>
            <input type="number" id="${id}" class="form-input currency-input" value="${value || ''}" placeholder="${placeholder || '0.00'}" step="0.01" min="0">
        </div>`;
    },

    dateInput(id, value) {
        return `<input type="text" id="${id}" class="form-input date-input" value="${value || ''}" placeholder="YYYY-MM-DD" pattern="\\d{4}-\\d{2}-\\d{2}">`;
    },

    checkbox(id, checked, label) {
        return `<label class="checkbox-label">
            <div class="custom-checkbox ${checked ? 'checked' : ''}" data-checkbox-id="${id}">
                ${checked ? '<span class="check-icon">&#10003;</span>' : ''}
            </div>
            <span>${label}</span>
        </label>`;
    },

    radio(name, value, currentValue, label) {
        const checked = value === currentValue;
        return `<label class="radio-label">
            <div class="custom-radio ${checked ? 'checked' : ''}" data-radio-name="${name}" data-radio-value="${this._escAttr(value)}">
                ${checked ? '<div class="radio-dot"></div>' : ''}
            </div>
            <span>${label}</span>
        </label>`;
    },

    badge(text, type) {
        const cls = type || 'default';
        return `<span class="badge badge-${cls}">${text}</span>`;
    },

    statusBadge(status) {
        const colors = { 'Open': 'success', 'Pending': 'warning', 'Closed': 'neutral' };
        return this.badge(status, colors[status] || 'default');
    },

    avatar(name, color, size) {
        const sz = size || 32;
        const initials = (name || '?').split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase();
        return `<div class="avatar" style="width:${sz}px;height:${sz}px;background:${color || '#666'};font-size:${sz * 0.4}px">${initials}</div>`;
    },

    actionButton(label, action, opts) {
        const extra = opts || {};
        const cls = extra.className || '';
        const variant = extra.variant || 'primary';
        const disabled = extra.disabled ? 'disabled' : '';
        const dataAttrs = extra.dataAttrs ? Object.entries(extra.dataAttrs).map(([k, v]) => `data-${k}="${this._escAttr(v)}"`).join(' ') : '';
        return `<button class="btn btn-${variant} ${cls}" data-action="${action}" ${dataAttrs} ${disabled}>${label}</button>`;
    },

    iconButton(icon, action, title, dataAttrs) {
        const attrs = dataAttrs ? Object.entries(dataAttrs).map(([k, v]) => `data-${k}="${this._escAttr(v)}"`).join(' ') : '';
        return `<button class="btn-icon" data-action="${action}" ${attrs} title="${title || ''}">${icon}</button>`;
    },

    table(headers, rows, opts) {
        const extra = opts || {};
        const ths = headers.map(h => {
            if (typeof h === 'object') {
                const sortAttr = h.sortable ? `data-action="sortTable" data-sort-field="${h.field}"` : '';
                return `<th ${sortAttr} class="${h.sortable ? 'sortable' : ''}">${h.label}</th>`;
            }
            return `<th>${h}</th>`;
        }).join('');
        const trs = rows.map(r => `<tr>${r}</tr>`).join('');
        return `<table class="data-table ${extra.className || ''}">
            <thead><tr>${ths}</tr></thead>
            <tbody>${trs || `<tr><td colspan="${headers.length}" class="empty-row">No data available</td></tr>`}</tbody>
        </table>`;
    },

    tabs(items, activeId) {
        return `<div class="tab-bar">${items.map(item =>
            `<div class="tab-item ${item.id === activeId ? 'active' : ''}" data-action="switchTab" data-tab="${item.id}">${item.label}</div>`
        ).join('')}</div>`;
    },

    quickFilters(options, active) {
        return `<div class="quick-filters">${options.map(opt =>
            `<button class="filter-btn ${opt === active ? 'active' : ''}" data-action="quickFilter" data-filter="${opt}">${opt}</button>`
        ).join('')}</div>`;
    },

    searchBox(id, value, placeholder) {
        return `<div class="search-box">
            <span class="search-icon">&#128269;</span>
            <input type="text" id="${id}" class="search-input" value="${this._escAttr(value || '')}" placeholder="${placeholder || 'Search...'}">
        </div>`;
    },

    emptyState(message, actionLabel, actionName) {
        return `<div class="empty-state">
            <p>${message}</p>
            ${actionLabel ? `<button class="btn btn-primary" data-action="${actionName}">${actionLabel}</button>` : ''}
        </div>`;
    },

    confirmModal(title, message, confirmAction, confirmLabel) {
        const body = `<p>${message}</p>
            ${Components.checkbox('confirmCheck', false, 'I confirm that I understand the consequences of this action')}`;
        const footer = `<button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-danger" data-action="${confirmAction}" id="confirmBtn" disabled>${confirmLabel || 'Confirm'}</button>`;
        return Components.modal('confirmModal', title, body, footer, 'small');
    },

    formatCurrency(amount, currency) {
        const n = parseFloat(amount) || 0;
        const sym = { USD: '$', CAD: 'C$', EUR: '\u20AC', GBP: '\u00A3', AUD: 'A$' }[currency || 'USD'] || '$';
        return sym + n.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    },

    formatDate(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        if (isNaN(d.getTime())) return dateStr;
        return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
    },

    formatDateTime(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        if (isNaN(d.getTime())) return dateStr;
        return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
    },

    timeAgo(dateStr) {
        if (!dateStr) return '';
        const d = new Date(dateStr);
        const now = new Date();
        const diff = now - d;
        const mins = Math.floor(diff / 60000);
        if (mins < 1) return 'just now';
        if (mins < 60) return `${mins}m ago`;
        const hrs = Math.floor(mins / 60);
        if (hrs < 24) return `${hrs}h ago`;
        const days = Math.floor(hrs / 24);
        if (days < 30) return `${days}d ago`;
        const months = Math.floor(days / 30);
        if (months < 12) return `${months}mo ago`;
        return `${Math.floor(months / 12)}y ago`;
    },

    _escHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },

    _escAttr(str) {
        return String(str || '').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }
};
