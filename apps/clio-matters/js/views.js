const Views = {
    renderSidebar() {
        const items = [
            { id: 'matters-list', icon: '&#128196;', label: 'Matters' },
            { id: 'stages', icon: '&#9638;', label: 'Stages' },
            { id: 'templates', icon: '&#128203;', label: 'Matter Templates' },
            { id: 'practice-areas', icon: '&#9881;', label: 'Practice Areas' },
            { id: 'numbering', icon: '&#35;', label: 'Matter Numbering' }
        ];
        return items.map(item => `
            <div class="sidebar-item ${AppState.currentView === item.id || (AppState.currentView === 'matter-detail' && item.id === 'matters-list') ? 'active' : ''}"
                 data-action="navigate" data-view="${item.id}">
                <span class="sidebar-icon">${item.icon}</span>
                <span class="sidebar-label">${item.label}</span>
            </div>
        `).join('');
    },

    renderContent() {
        switch (AppState.currentView) {
            case 'matters-list': return this.renderMattersList();
            case 'matter-detail': return this.renderMatterDetail();
            case 'stages': return this.renderStages();
            case 'templates': return this.renderTemplates();
            case 'practice-areas': return this.renderPracticeAreas();
            case 'numbering': return this.renderNumbering();
            default: return this.renderMattersList();
        }
    },

    // ============ MATTERS LIST ============
    renderMattersList() {
        const matters = AppState.getFilteredMatters();
        const counts = { All: AppState.matters.length, Open: AppState.matters.filter(m => m.status === 'Open').length, Pending: AppState.matters.filter(m => m.status === 'Pending').length, Closed: AppState.matters.filter(m => m.status === 'Closed').length };
        const filterOpts = ['All', 'Open', 'Pending', 'Closed'];

        const rows = matters.map(m => {
            const pa = AppState.getPracticeAreaName(m.practiceAreaId);
            const ra = AppState.getUserName(m.responsibleAttorneyId);
            return `<td><input type="checkbox" class="matter-checkbox" data-matter-id="${m.id}"></td>
                <td><a class="matter-link" data-action="openMatter" data-matter-id="${m.id}">${m.displayNumber}</a></td>
                <td class="matter-desc-cell">${Components._escHtml(m.description)}</td>
                <td>${Components._escHtml(m.contactName)}</td>
                <td>${Components.statusBadge(m.status)}</td>
                <td>${pa}</td>
                <td>${ra}</td>
                <td>${Components.formatDate(m.openDate)}</td>
                <td>
                    <div class="row-actions">
                        ${Components.iconButton('&#9998;', 'editMatter', 'Edit', { 'matter-id': m.id })}
                        <div class="row-actions-more">
                            ${Components.iconButton('&#8942;', 'matterRowMenu', 'More', { 'matter-id': m.id })}
                        </div>
                    </div>
                </td>`;
        });

        const headers = [
            '<input type="checkbox" id="selectAllMatters" data-action="selectAllMatters">',
            { label: 'Matter #', field: 'displayNumber', sortable: true },
            { label: 'Description', field: 'description', sortable: true },
            { label: 'Client', field: 'contactName', sortable: true },
            { label: 'Status', field: 'status', sortable: true },
            'Practice Area', 'Responsible Attorney',
            { label: 'Open Date', field: 'openDate', sortable: true },
            'Actions'
        ];

        return `<div class="page-header">
            <h1>Matters</h1>
            <div class="header-actions">
                ${Components.actionButton('New Matter', 'newMatter', { variant: 'primary' })}
            </div>
        </div>
        <div class="list-toolbar">
            ${Components.quickFilters(filterOpts.map(f => `${f} (${counts[f]})`), `${AppState.matterListFilter} (${counts[AppState.matterListFilter]})`)}
            <div class="toolbar-right">
                ${Components.searchBox('matterSearch', AppState.matterListKeyword, 'Filter by keyword...')}
                ${Components.actionButton('Filters', 'openFilters', { variant: 'secondary' })}
            </div>
        </div>
        <div class="bulk-actions" id="bulkActions" style="display:none">
            ${Components.actionButton('Update matter status', 'bulkStatus', { variant: 'secondary' })}
            ${Components.actionButton('Delete matters', 'bulkDelete', { variant: 'danger' })}
        </div>
        ${Components.table(headers, rows)}
        <div class="table-footer">
            <span>Showing ${matters.length} of ${AppState.matters.length} matters</span>
            ${Components.actionButton('Export', 'exportMatters', { variant: 'secondary' })}
        </div>`;
    },

    // ============ MATTER DETAIL ============
    renderMatterDetail() {
        const m = AppState.getCurrentMatter();
        if (!m) return Components.emptyState('Matter not found.', 'Back to Matters', 'backToList');

        const tabs = [
            { id: 'dashboard', label: 'Dashboard' },
            { id: 'damages', label: 'Damages' },
            { id: 'medical-records', label: 'Medical Records' },
            { id: 'settlement', label: 'Settlement' }
        ];

        let content;
        switch (AppState.currentMatterTab) {
            case 'damages': content = this.renderDamagesTab(m); break;
            case 'medical-records': content = this.renderMedicalRecordsTab(m); break;
            case 'settlement': content = this.renderSettlementTab(m); break;
            default: content = this.renderDashboardTab(m);
        }

        return `<div class="page-header matter-header">
            <div class="header-left">
                <button class="btn btn-text" data-action="backToList">&larr; Matters</button>
                <h1>${Components._escHtml(m.displayNumber)}</h1>
                ${Components.statusBadge(m.status)}
            </div>
            <div class="header-actions">
                ${Components.actionButton('Edit matter', 'editMatter', { variant: 'secondary', dataAttrs: { 'matter-id': m.id } })}
                ${Components.actionButton('Duplicate', 'duplicateMatter', { variant: 'secondary', dataAttrs: { 'matter-id': m.id } })}
                <div class="dropdown-inline">
                    ${Components.iconButton('&#8942;', 'matterDetailMenu', 'More actions')}
                </div>
            </div>
        </div>
        <p class="matter-description">${Components._escHtml(m.description)}</p>
        ${Components.tabs(tabs, AppState.currentMatterTab)}
        <div class="tab-content">${content}</div>`;
    },

    // ---- Dashboard Tab ----
    renderDashboardTab(m) {
        const pa = AppState.getPracticeAreaName(m.practiceAreaId);
        const stage = AppState.getStageName(m.practiceAreaId, m.matterStageId);
        const ra = AppState.getUserName(m.responsibleAttorneyId);
        const oa = AppState.getUserName(m.originatingAttorneyId);
        const rs = m.responsibleStaffId ? AppState.getUserName(m.responsibleStaffId) : '';
        const currency = m.billingPreference.currency || 'USD';

        const budgetBar = m.billingPreference.budget ? (() => {
            const spent = m.financials.totalTime + m.financials.totalExpenses;
            const pct = Math.min(100, (spent / m.billingPreference.budget) * 100);
            return `<div class="budget-section">
                <div class="budget-header"><span>Budget</span><span>${Components.formatCurrency(spent, currency)} / ${Components.formatCurrency(m.billingPreference.budget, currency)}</span></div>
                <div class="progress-bar"><div class="progress-fill ${pct > 90 ? 'danger' : pct > 70 ? 'warning' : ''}" style="width:${pct}%"></div></div>
            </div>`;
        })() : '';

        const billingMethod = m.billingPreference.billingMethod === 'contingency' ? `Contingency (${m.billingPreference.contingencyRate}%)` :
            m.billingPreference.billingMethod === 'flat_rate' ? `Flat Rate (${Components.formatCurrency(m.billingPreference.flatFeeAmount, currency)})` : 'Hourly';

        const stageOptions = AppState.getStagesForPracticeArea(m.practiceAreaId).map(s => ({ value: s.id, label: s.name }));
        const statusOptions = [{ value: 'Open', label: 'Open' }, { value: 'Pending', label: 'Pending' }, { value: 'Closed', label: 'Closed' }];

        const relatedContactsHtml = m.relatedContacts.length > 0 ? m.relatedContacts.map(rc => {
            const c = AppState.getContact(rc.contactId);
            if (!c) return '';
            const name = c.type === 'company' ? c.lastName : `${c.firstName} ${c.lastName}`;
            return `<div class="related-contact-card">
                <div class="rc-name">${name} <span class="rc-relationship">(${rc.relationship})</span></div>
                <div class="rc-details">
                    ${c.email ? `<div>Email: <a href="mailto:${c.email}">${c.email}</a></div>` : ''}
                    ${c.phone ? `<div>Phone: ${c.phone}</div>` : ''}
                    ${rc.isBillRecipient ? Components.badge('Bill Recipient', 'info') : ''}
                </div>
            </div>`;
        }).join('') : '<p class="no-data">No related contacts.</p>';

        const contactsHtml = (() => {
            const client = AppState.getContact(m.clientId);
            if (!client) return '';
            const name = client.type === 'company' ? client.lastName : `${client.firstName} ${client.lastName}`;
            return `<div class="contact-card">
                <div class="contact-name">${name}</div>
                <div class="contact-details">
                    ${client.email ? `<div>Email: <a href="mailto:${client.email}">${client.email}</a></div>` : ''}
                    ${client.phone ? `<div>Phone: ${client.phone}</div>` : ''}
                    ${client.address ? `<div>Address: ${client.address} <button class="btn-icon btn-tiny" data-action="copyAddress" data-address="${Components._escAttr(client.address)}" title="Copy address">&#128203;</button></div>` : ''}
                    ${client.tags.length ? `<div class="contact-tags">${client.tags.map(t => Components.badge(t, 'tag')).join('')}</div>` : ''}
                </div>
            </div>`;
        })();

        const customFieldsHtml = m.customFields.length > 0 ? m.customFields.map(cf => {
            const def = AppState.customFieldDefinitions.find(d => d.id === cf.definitionId);
            if (!def) return '';
            let val = cf.value;
            if (def.fieldType === 'currency') val = Components.formatCurrency(val);
            return `<div class="cf-row"><span class="cf-label">${def.name}:</span><span class="cf-value">${val || '&mdash;'}</span></div>`;
        }).join('') : '<p class="no-data">No custom fields.</p>';

        const timelineHtml = m.timeline.slice().reverse().slice(0, 20).map(ev => {
            const user = AppState.getUserName(ev.userId);
            return `<div class="timeline-event">
                <div class="timeline-dot ${ev.action}"></div>
                <div class="timeline-content">
                    <span class="timeline-detail">${ev.details}</span>
                    <span class="timeline-meta">by ${user} &middot; ${Components.formatDateTime(ev.timestamp)}</span>
                </div>
            </div>`;
        }).join('');

        return `<div class="dashboard-grid">
            <div class="dashboard-section financial-section">
                <h3>Financial</h3>
                <div class="financial-cards">
                    <div class="fin-card"><div class="fin-label">Work in Progress</div><div class="fin-value">${Components.formatCurrency(m.financials.workInProgress, currency)}</div></div>
                    <div class="fin-card"><div class="fin-label">Outstanding Balance</div><div class="fin-value">${Components.formatCurrency(m.financials.outstandingBalance, currency)}</div></div>
                    <div class="fin-card"><div class="fin-label">Trust Funds</div><div class="fin-value">${Components.formatCurrency(m.financials.trustFunds, currency)}</div></div>
                    <div class="fin-card"><div class="fin-label">Total Time</div><div class="fin-value">${Components.formatCurrency(m.financials.totalTime, currency)}</div></div>
                    <div class="fin-card"><div class="fin-label">Total Expenses</div><div class="fin-value">${Components.formatCurrency(m.financials.totalExpenses, currency)}</div></div>
                </div>
                ${budgetBar}
            </div>

            <div class="dashboard-section details-section">
                <h3>Details</h3>
                <div class="details-grid">
                    <div class="detail-row"><span class="detail-label">Status</span><span class="detail-value">${Components.dropdown('statusDropdown', m.status, statusOptions, 'Select status')}</span></div>
                    <div class="detail-row"><span class="detail-label">Practice Area</span><span class="detail-value">${pa || '&mdash;'}</span></div>
                    ${stageOptions.length > 0 ? `<div class="detail-row"><span class="detail-label">Matter Stage</span><span class="detail-value">${Components.dropdown('stageDropdown', m.matterStageId, stageOptions, 'Select stage')}</span></div>` : ''}
                    <div class="detail-row"><span class="detail-label">Responsible Attorney</span><span class="detail-value">${ra}</span></div>
                    <div class="detail-row"><span class="detail-label">Originating Attorney</span><span class="detail-value">${oa}</span></div>
                    ${rs ? `<div class="detail-row"><span class="detail-label">Responsible Staff</span><span class="detail-value">${rs}</span></div>` : ''}
                    <div class="detail-row"><span class="detail-label">Billing Method</span><span class="detail-value">${billingMethod}</span></div>
                    <div class="detail-row"><span class="detail-label">Currency</span><span class="detail-value">${currency}</span></div>
                    ${m.clientRefNumber ? `<div class="detail-row"><span class="detail-label">Client Ref #</span><span class="detail-value">${Components._escHtml(m.clientRefNumber)}</span></div>` : ''}
                    ${m.location ? `<div class="detail-row"><span class="detail-label">Location</span><span class="detail-value">${Components._escHtml(m.location)}</span></div>` : ''}
                    <div class="detail-row"><span class="detail-label">Open Date</span><span class="detail-value">${Components.formatDate(m.openDate)}</span></div>
                    ${m.pendingDate ? `<div class="detail-row"><span class="detail-label">Pending Date</span><span class="detail-value">${Components.formatDate(m.pendingDate)}</span></div>` : ''}
                    ${m.closedDate ? `<div class="detail-row"><span class="detail-label">Closed Date</span><span class="detail-value">${Components.formatDate(m.closedDate)}</span></div>` : ''}
                </div>
            </div>

            <div class="dashboard-section contacts-section">
                <h3>Contacts</h3>
                ${contactsHtml}
            </div>

            <div class="dashboard-section related-contacts-section">
                <div class="section-header-row">
                    <h3>Related Contacts</h3>
                    ${Components.actionButton(m.relatedContacts.length > 0 ? 'Edit' : 'Add', 'editRelatedContacts', { variant: 'secondary' })}
                </div>
                ${relatedContactsHtml}
            </div>

            <div class="dashboard-section custom-fields-section">
                <h3>Custom Fields</h3>
                ${customFieldsHtml}
            </div>

            <div class="dashboard-section timeline-section">
                <h3>Timeline</h3>
                <div class="timeline">${timelineHtml || '<p class="no-data">No activity yet.</p>'}</div>
            </div>
        </div>`;
    },

    // ---- Damages Tab ----
    renderDamagesTab(m) {
        const filterOpts = ['All', 'Special', 'General', 'Other'];
        let damages = [...m.damages];
        if (AppState.damagesFilter !== 'All') {
            damages = damages.filter(d => d.category === AppState.damagesFilter);
        }
        if (AppState.damagesKeyword) {
            const kw = AppState.damagesKeyword.toLowerCase();
            damages = damages.filter(d => d.description.toLowerCase().includes(kw));
        }

        const totalDamages = damages.reduce((sum, d) => sum + d.amount, 0);
        const totalAllDamages = m.damages.reduce((sum, d) => sum + d.amount, 0);
        const totalMedBills = m.medicalProviders.reduce((sum, mp) => sum + mp.medicalBills.reduce((s, b) => s + b.billAmount, 0), 0);
        const totalMedPaid = m.medicalProviders.reduce((sum, mp) => sum + mp.medicalBills.reduce((s, b) => s + b.payers.reduce((ps, p) => ps + p.amountPaid, 0), 0), 0);
        const totalMedBalance = m.medicalProviders.reduce((sum, mp) => sum + mp.medicalBills.reduce((s, b) => s + b.balanceOwed, 0), 0);

        const rows = damages.map(d => {
            const u = AppState.getUserName(d.createdBy);
            return `<td>${Components._escHtml(d.description)}</td>
                <td>${Components.badge(d.type, 'tag')}</td>
                <td>${d.category}</td>
                <td class="amount-cell">${Components.formatCurrency(d.amount)}</td>
                <td>${Components.formatDate(d.createdAt)}</td>
                <td>
                    ${Components.iconButton('&#9998;', 'editDamage', 'Edit', { 'damage-id': d.id })}
                    ${Components.iconButton('&#128465;', 'deleteDamage', 'Delete', { 'damage-id': d.id })}
                </td>`;
        });

        return `<div class="page-section">
            <div class="section-header-row">
                <h2>Damages</h2>
                <div class="header-actions">
                    ${Components.actionButton('New damage', 'newDamage', { variant: 'primary' })}
                    ${Components.actionButton('Export', 'exportDamages', { variant: 'secondary' })}
                </div>
            </div>

            <div class="summary-cards">
                <div class="summary-card"><div class="summary-label">Total Billed + Other Damages</div><div class="summary-value">${Components.formatCurrency(totalMedBills + totalAllDamages)}</div></div>
                <div class="summary-card"><div class="summary-label">Total Paid + Other Damages</div><div class="summary-value">${Components.formatCurrency(totalMedPaid + totalAllDamages)}</div></div>
                <div class="summary-card"><div class="summary-label">Total Paid + Owed + Other</div><div class="summary-value">${Components.formatCurrency(totalMedPaid + totalMedBalance + totalAllDamages)}</div></div>
            </div>

            ${totalMedBills > 0 ? `<div class="med-bill-summary">
                <h3>Medical Bills Summary</h3>
                ${this._renderMedBillSummary(m)}
            </div>` : ''}

            <div class="damages-table-section">
                <h3>All Other Damages</h3>
                <div class="table-toolbar">
                    ${Components.quickFilters(filterOpts, AppState.damagesFilter)}
                    ${Components.searchBox('damagesKeyword', AppState.damagesKeyword, 'Filter by keyword...')}
                </div>
                ${Components.table(
                    [{ label: 'Description', field: 'description', sortable: true }, 'Type', 'Category',
                     { label: 'Amount', field: 'amount', sortable: true }, 'Date', 'Actions'],
                    rows
                )}
                <div class="table-footer">
                    <span>Total: ${Components.formatCurrency(totalDamages)}</span>
                </div>
            </div>
        </div>`;
    },

    _renderMedBillSummary(m) {
        const rows = m.medicalProviders.filter(mp => mp.medicalBills.length > 0).map(mp => {
            const provider = AppState.getContactName(mp.contactId);
            const total = mp.medicalBills.reduce((s, b) => s + b.billAmount, 0);
            const adj = mp.medicalBills.reduce((s, b) => s + b.adjustment, 0);
            const paid = mp.medicalBills.reduce((s, b) => s + b.payers.reduce((ps, p) => ps + p.amountPaid, 0), 0);
            const owed = mp.medicalBills.reduce((s, b) => s + b.balanceOwed, 0);
            return `<td>${provider}</td><td class="amount-cell">${Components.formatCurrency(total)}</td><td class="amount-cell">${Components.formatCurrency(adj)}</td><td class="amount-cell">${Components.formatCurrency(paid)}</td><td class="amount-cell">${Components.formatCurrency(owed)}</td>`;
        });
        return Components.table(['Provider', 'Total Billed', 'Adjustments', 'Total Paid', 'Balance Owed'], rows);
    },

    // ---- Medical Records Tab ----
    renderMedicalRecordsTab(m) {
        const providers = m.medicalProviders;
        if (providers.length === 0) {
            return `<div class="page-section">
                <div class="section-header-row"><h2>Medical Records</h2></div>
                ${Components.emptyState('No medical providers added yet.', 'Add medical provider', 'addMedicalProvider')}
            </div>`;
        }

        const providerCards = providers.map(mp => {
            const contact = AppState.getContact(mp.contactId);
            const name = contact ? AppState.getContactName(mp.contactId) : 'Unknown Provider';
            const treatmentStatus = mp.treatmentComplete ? 'Treatment complete' : 'In treatment';
            const treatmentClass = mp.treatmentComplete ? 'complete' : 'in-progress';

            const recordsHtml = mp.medicalRecords.length > 0 ? mp.medicalRecords.map(mr => {
                const commentCount = mr.comments.length;
                return `<tr>
                    <td>${Components._escHtml(mr.fileName)}</td>
                    <td>${Components.formatDate(mr.startDate)}</td>
                    <td>${Components.formatDate(mr.endDate)}</td>
                    <td>${Components.formatDate(mr.receivedDate)}</td>
                    <td>
                        ${Components.iconButton('&#9998;', 'editMedRecord', 'Edit', { 'provider-id': mp.id, 'record-id': mr.id })}
                        ${Components.iconButton('&#128172;' + (commentCount > 0 ? `<span class="comment-count">${commentCount}</span>` : ''), 'viewComments', 'Comments', { 'provider-id': mp.id, 'item-type': 'record', 'item-id': mr.id })}
                        ${Components.iconButton('&#128465;', 'deleteMedRecord', 'Delete', { 'provider-id': mp.id, 'record-id': mr.id })}
                    </td>
                </tr>`;
            }).join('') : '<tr><td colspan="5" class="empty-row">No medical records</td></tr>';

            const billsHtml = mp.medicalBills.length > 0 ? mp.medicalBills.map(mb => {
                const commentCount = mb.comments.length;
                const totalPaid = mb.payers.reduce((s, p) => s + p.amountPaid, 0);
                return `<tr>
                    <td>${Components._escHtml(mb.fileName)}</td>
                    <td>${Components.formatDate(mb.billDate)}</td>
                    <td class="amount-cell">${Components.formatCurrency(mb.billAmount)}</td>
                    <td class="amount-cell">${Components.formatCurrency(mb.adjustment)}</td>
                    <td class="amount-cell">${Components.formatCurrency(totalPaid)}</td>
                    <td class="amount-cell">${Components.formatCurrency(mb.balanceOwed)}</td>
                    <td>
                        ${Components.iconButton('&#9998;', 'editMedBill', 'Edit', { 'provider-id': mp.id, 'bill-id': mb.id })}
                        ${Components.iconButton('&#128172;' + (commentCount > 0 ? `<span class="comment-count">${commentCount}</span>` : ''), 'viewComments', 'Comments', { 'provider-id': mp.id, 'item-type': 'bill', 'item-id': mb.id })}
                        ${Components.iconButton('&#128465;', 'deleteMedBill', 'Delete', { 'provider-id': mp.id, 'bill-id': mb.id })}
                    </td>
                </tr>`;
            }).join('') : '<tr><td colspan="7" class="empty-row">No medical bills</td></tr>';

            return `<div class="provider-card" data-provider-id="${mp.id}">
                <div class="provider-header">
                    <div class="provider-info">
                        <h3>${name}</h3>
                        ${mp.description ? `<p class="provider-desc">${Components._escHtml(mp.description)}</p>` : ''}
                    </div>
                    <div class="provider-actions">
                        ${Components.iconButton('&#9998;', 'editMedProvider', 'Edit details', { 'provider-id': mp.id })}
                        ${Components.iconButton('&#128465;', 'deleteMedProvider', 'Delete provider', { 'provider-id': mp.id })}
                    </div>
                </div>
                <div class="provider-status-row">
                    <div class="status-item"><span class="status-label">Treatment:</span> <span class="treatment-status ${treatmentClass}">${treatmentStatus}</span></div>
                    <div class="status-item"><span class="status-label">First:</span> ${Components.formatDate(mp.treatmentFirstDate) || '&mdash;'}</div>
                    <div class="status-item"><span class="status-label">Last:</span> ${Components.formatDate(mp.treatmentLastDate) || '&mdash;'}</div>
                </div>
                <div class="provider-requests">
                    <div class="request-info">
                        <span class="req-label">Medical Record:</span>
                        ${Components.badge(mp.recordStatus, this._recordStatusClass(mp.recordStatus))}
                        <span class="req-dates">Req: ${Components.formatDate(mp.recordRequestDate) || '&mdash;'} | Follow-up: ${Components.formatDate(mp.recordFollowUpDate) || '&mdash;'}</span>
                    </div>
                    <div class="request-info">
                        <span class="req-label">Medical Bill:</span>
                        ${Components.badge(mp.billStatus, this._recordStatusClass(mp.billStatus))}
                        <span class="req-dates">Req: ${Components.formatDate(mp.billRequestDate) || '&mdash;'} | Follow-up: ${Components.formatDate(mp.billFollowUpDate) || '&mdash;'}</span>
                    </div>
                </div>
                <div class="provider-records-section">
                    <div class="sub-section-header">
                        <h4>Medical Records</h4>
                        ${Components.actionButton('Add medical record', 'addMedRecord', { variant: 'secondary', dataAttrs: { 'provider-id': mp.id } })}
                    </div>
                    <table class="data-table compact">
                        <thead><tr><th>File</th><th>Start Date</th><th>End Date</th><th>Received</th><th>Actions</th></tr></thead>
                        <tbody>${recordsHtml}</tbody>
                    </table>
                </div>
                <div class="provider-bills-section">
                    <div class="sub-section-header">
                        <h4>Medical Bills</h4>
                        ${Components.actionButton('Add medical bill', 'addMedBill', { variant: 'secondary', dataAttrs: { 'provider-id': mp.id } })}
                    </div>
                    <table class="data-table compact">
                        <thead><tr><th>File</th><th>Bill Date</th><th>Amount</th><th>Adjustment</th><th>Paid</th><th>Balance</th><th>Actions</th></tr></thead>
                        <tbody>${billsHtml}</tbody>
                    </table>
                </div>
            </div>`;
        }).join('');

        return `<div class="page-section">
            <div class="section-header-row">
                <h2>Medical Records</h2>
                <div class="header-actions">
                    ${Components.actionButton('Add provider', 'addMedicalProvider', { variant: 'primary' })}
                    ${Components.actionButton('Export', 'exportMedical', { variant: 'secondary' })}
                </div>
            </div>
            ${providerCards}
        </div>`;
    },

    _recordStatusClass(status) {
        const map = { 'Received': 'success', 'Requested': 'warning', 'Not yet requested': 'neutral', 'Incomplete': 'danger', 'Certified': 'info' };
        return map[status] || 'default';
    },

    // ---- Settlement Tab ----
    renderSettlementTab(m) {
        const s = m.settlement;
        const totalRecovery = s.recoveries.reduce((sum, r) => sum + r.amount, 0);

        const deductOrder = m.deductionOrder || 'fees_first';
        const totalExpenses = s.expenses.reduce((sum, e) => sum + e.amount, 0);

        let totalLegalFees = 0;
        s.legalFees.forEach(lf => {
            const rec = s.recoveries.find(r => r.id === lf.recoveryId);
            if (!rec) return;
            const feeBase = deductOrder === 'fees_first' ? rec.amount : (rec.amount - totalExpenses);
            const fee = (feeBase * lf.rate / 100) * (1 - lf.discount / 100);
            totalLegalFees += fee;
            lf.referralFees.forEach(rf => {
                totalLegalFees -= fee * rf.rate / 100;
            });
        });

        const totalLiens = s.otherLiens.reduce((sum, l) => sum + (l.amount - l.reduction), 0);
        const medicalLiens = m.medicalProviders.reduce((sum, mp) => sum + mp.medicalBills.filter(b => b.balanceIsLien).reduce((s2, b) => s2 + b.balanceOwed, 0), 0);
        const totalOutstanding = s.outstandingBalances.reduce((sum, b) => sum + (b.balanceOwing - b.reduction), 0);

        let netCompensation;
        if (deductOrder === 'fees_first') {
            netCompensation = totalRecovery - totalLegalFees - totalExpenses - totalLiens - medicalLiens - totalOutstanding;
        } else {
            netCompensation = totalRecovery - totalExpenses - totalLegalFees - totalLiens - medicalLiens - totalOutstanding;
        }

        const recoveryRows = s.recoveries.map(r => {
            const source = AppState.getContactName(r.sourceContactId);
            return `<td>${source}</td><td class="amount-cell">${Components.formatCurrency(r.amount)}</td><td>${Components.formatDate(r.createdAt)}</td>
                <td>${Components.iconButton('&#9998;', 'editRecovery', 'Edit', { 'recovery-id': r.id })}${Components.iconButton('&#128465;', 'deleteRecovery', 'Delete', { 'recovery-id': r.id })}</td>`;
        });

        const feeRows = s.legalFees.map(lf => {
            const rec = s.recoveries.find(r => r.id === lf.recoveryId);
            const recipient = AppState.getUserName(lf.recipientId);
            const source = rec ? AppState.getContactName(rec.sourceContactId) : 'Unknown';
            const referrals = lf.referralFees.map(rf => `${AppState.getContactName(rf.recipientId)} (${rf.rate}%)`).join(', ');
            return `<td>${source}</td><td>${recipient}</td><td>${lf.rate}%</td><td>${lf.discount}%</td><td>${referrals || '&mdash;'}</td>
                <td>${Components.iconButton('&#9998;', 'editLegalFee', 'Edit', { 'fee-id': lf.id })}${Components.iconButton('&#128465;', 'deleteLegalFee', 'Delete', { 'fee-id': lf.id })}</td>`;
        });

        const expenseRows = s.expenses.map(e =>
            `<td>${e.category}</td><td class="amount-cell">${Components.formatCurrency(e.amount)}</td>`
        );

        const lienRows = s.otherLiens.map(l => {
            const holder = AppState.getContactName(l.lienHolderId);
            return `<td>${holder}</td><td>${Components._escHtml(l.description)}</td><td class="amount-cell">${Components.formatCurrency(l.amount)}</td><td class="amount-cell">${l.reduction ? Components.formatCurrency(l.reduction) : '&mdash;'}</td>
                <td>${Components.iconButton('&#9998;', 'editLien', 'Edit', { 'lien-id': l.id })}${Components.iconButton('&#128465;', 'deleteLien', 'Delete', { 'lien-id': l.id })}</td>`;
        });

        const balanceRows = s.outstandingBalances.map(b => {
            const holder = AppState.getContactName(b.balanceHolderId);
            return `<td>${b.responsibleParty === 'client' ? 'Client' : 'Lawyer'}</td><td>${holder}</td><td>${Components._escHtml(b.description)}</td><td class="amount-cell">${Components.formatCurrency(b.balanceOwing)}</td><td class="amount-cell">${b.reduction ? Components.formatCurrency(b.reduction) : '&mdash;'}</td>
                <td>${Components.iconButton('&#9998;', 'editBalance', 'Edit', { 'balance-id': b.id })}${Components.iconButton('&#128465;', 'deleteBalance', 'Delete', { 'balance-id': b.id })}</td>`;
        });

        return `<div class="page-section">
            <div class="section-header-row">
                <h2>Settlement</h2>
                <div class="header-actions">
                    ${Components.actionButton('Edit matter', 'editMatter', { variant: 'secondary', dataAttrs: { 'matter-id': m.id } })}
                    ${Components.actionButton('Export', 'exportSettlement', { variant: 'secondary' })}
                </div>
            </div>

            <div class="recovery-summary">
                <h3>Recovery Summary</h3>
                <div class="summary-grid">
                    <div class="summary-row"><span>Total Recovery</span><span class="amount">${Components.formatCurrency(totalRecovery)}</span></div>
                    <div class="summary-row deduction"><span>Legal Fees</span><span class="amount">-${Components.formatCurrency(Math.abs(totalLegalFees))}</span></div>
                    <div class="summary-row deduction"><span>Matter Expenses</span><span class="amount">-${Components.formatCurrency(totalExpenses)}</span></div>
                    <div class="summary-row deduction"><span>Liens & Outstanding</span><span class="amount">-${Components.formatCurrency(totalLiens + medicalLiens + totalOutstanding)}</span></div>
                    <div class="summary-row total"><span>Net Client Compensation</span><span class="amount ${netCompensation < 0 ? 'negative' : ''}">${Components.formatCurrency(netCompensation)}</span></div>
                </div>
                <div class="deduction-order">Order: ${deductOrder === 'fees_first' ? 'Legal fees first, then expenses' : 'Expenses first, then legal fees'}</div>
            </div>

            <div class="settlement-section">
                <div class="sub-section-header"><h3>Recovery Amounts</h3>${Components.actionButton('New recovery', 'newRecovery', { variant: 'primary' })}</div>
                ${Components.table(['Source', 'Amount', 'Date', 'Actions'], recoveryRows)}
            </div>

            <div class="settlement-section">
                <div class="sub-section-header"><h3>Legal Fees</h3>${Components.actionButton('New legal fee', 'newLegalFee', { variant: 'primary' })}</div>
                ${Components.table(['Fee Source', 'Recipient', 'Rate', 'Discount', 'Referral Fees', 'Actions'], feeRows)}
            </div>

            <div class="settlement-section">
                <h3>Matter Expenses</h3>
                ${Components.table(['Category', 'Amount'], expenseRows)}
                <div class="table-footer"><span>Total: ${Components.formatCurrency(totalExpenses)}</span></div>
            </div>

            <div class="settlement-section">
                <div class="sub-section-header"><h3>Other Liens</h3>${Components.actionButton('New lien', 'newLien', { variant: 'primary' })}</div>
                ${Components.table(['Lien Holder', 'Description', 'Amount', 'Reduction', 'Actions'], lienRows)}
            </div>

            <div class="settlement-section">
                <div class="sub-section-header"><h3>Outstanding Balances</h3>${Components.actionButton('New outstanding balance', 'newBalance', { variant: 'primary' })}</div>
                ${Components.table(['Paid By', 'Balance Holder', 'Description', 'Amount', 'Reduction', 'Actions'], balanceRows)}
            </div>
        </div>`;
    },

    // ============ STAGES VIEW ============
    renderStages() {
        const paOptions = AppState.practiceAreas.filter(pa => pa.enabled).map(pa => ({ value: pa.id, label: pa.name }));
        if (!AppState.currentStagesPracticeArea && paOptions.length > 0) {
            AppState.currentStagesPracticeArea = paOptions[0].value;
        }
        const currentPA = AppState.currentStagesPracticeArea;
        const stages = currentPA ? AppState.getStagesForPracticeArea(currentPA) : [];
        const mattersInPA = AppState.matters.filter(m => m.practiceAreaId === currentPA && m.status !== 'Closed');

        const noStageMatters = mattersInPA.filter(m => !m.matterStageId || !stages.find(s => s.id === m.matterStageId));
        const columns = stages.map(stage => {
            const stageMatters = mattersInPA.filter(m => m.matterStageId === stage.id);
            const cards = stageMatters.map(m => {
                const statusColor = m.status === 'Open' ? '#27ae60' : '#f1c40f';
                const daysInStage = this._daysInStage(m);
                return `<div class="stage-card" data-matter-id="${m.id}">
                    <div class="stage-card-bar" style="background:${statusColor}"></div>
                    <div class="stage-card-content">
                        <div class="stage-card-title">${Components._escHtml(m.displayNumber)}</div>
                        <div class="stage-card-desc">${Components._escHtml(m.description)}</div>
                        <div class="stage-card-client">${Components._escHtml(m.contactName)}</div>
                        ${daysInStage !== null ? `<div class="stage-card-days">${daysInStage} days</div>` : ''}
                        <div class="stage-card-actions">
                            ${Components.iconButton('&#8942;', 'stageCardMenu', 'Actions', { 'matter-id': m.id })}
                        </div>
                    </div>
                </div>`;
            }).join('');
            return `<div class="stage-column" data-stage-id="${stage.id}">
                <div class="stage-column-header">
                    <span class="stage-name">${Components._escHtml(stage.name)}</span>
                    <span class="stage-count">${stageMatters.length}</span>
                    ${Components.iconButton('&#8942;', 'stageColumnMenu', 'Options', { 'stage-id': stage.id })}
                </div>
                <div class="stage-column-body">${cards}</div>
            </div>`;
        });

        const noStageColumn = noStageMatters.length > 0 ? `<div class="stage-column no-stage">
            <div class="stage-column-header"><span class="stage-name">No Stage Assigned</span><span class="stage-count">${noStageMatters.length}</span></div>
            <div class="stage-column-body">${noStageMatters.map(m => `<div class="stage-card" data-matter-id="${m.id}">
                <div class="stage-card-bar" style="background:${m.status === 'Open' ? '#27ae60' : '#f1c40f'}"></div>
                <div class="stage-card-content">
                    <div class="stage-card-title">${Components._escHtml(m.displayNumber)}</div>
                    <div class="stage-card-desc">${Components._escHtml(m.description)}</div>
                    <div class="stage-card-client">${Components._escHtml(m.contactName)}</div>
                </div>
            </div>`).join('')}</div>
        </div>` : '';

        return `<div class="page-header">
            <h1>Matter Stages</h1>
            <div class="header-actions">
                ${Components.actionButton('Add a matter stage', 'addStage', { variant: 'primary' })}
            </div>
        </div>
        <div class="stages-toolbar">
            ${Components.dropdown('stagesPADropdown', currentPA, paOptions, 'Select practice area')}
        </div>
        <div class="stages-board">
            ${noStageColumn}
            ${columns.join('')}
        </div>`;
    },

    _daysInStage(m) {
        const ev = [...m.timeline].reverse().find(e => e.action === 'stage_changed');
        if (!ev) return null;
        return Math.floor((new Date() - new Date(ev.timestamp)) / 86400000);
    },

    // ============ TEMPLATES VIEW ============
    renderTemplates() {
        const templates = AppState.matterTemplates;
        const rows = templates.map(t => {
            const pa = AppState.getPracticeAreaName(t.practiceAreaId);
            return `<td><a class="template-link" data-action="editTemplate" data-template-id="${t.id}">${Components._escHtml(t.name)}</a>${t.isDefault ? ' ' + Components.badge('Default', 'info') : ''}</td>
                <td>${pa || '&mdash;'}</td>
                <td>${t.billingMethod}</td>
                <td>${Components.formatDate(t.updatedAt)}</td>
                <td>
                    ${Components.iconButton('&#9998;', 'editTemplate', 'Edit', { 'template-id': t.id })}
                    ${Components.iconButton('&#8942;', 'templateMenu', 'More', { 'template-id': t.id })}
                </td>`;
        });

        return `<div class="page-header">
            <h1>Matter Templates</h1>
            <div class="header-actions">
                ${Components.actionButton('New matter template', 'newTemplate', { variant: 'primary' })}
            </div>
        </div>
        ${Components.table(['Template', 'Practice Area', 'Billing Method', 'Last Updated', 'Actions'], rows)}`;
    },

    // ============ PRACTICE AREAS VIEW ============
    renderPracticeAreas() {
        const rows = AppState.practiceAreas.map(pa => {
            const matterCount = AppState.matters.filter(m => m.practiceAreaId === pa.id).length;
            return `<td>${Components._escHtml(pa.name)} ${pa.isPrimary ? Components.badge('Primary', 'info') : ''}</td>
                <td>${pa.enabled ? Components.badge('Enabled', 'success') : Components.badge('Disabled', 'neutral')}</td>
                <td>${matterCount}</td>
                <td>
                    ${Components.iconButton('&#9998;', 'renamePracticeArea', 'Rename', { 'pa-id': pa.id })}
                    ${matterCount === 0 ? Components.iconButton('&#128465;', 'deletePracticeArea', 'Delete', { 'pa-id': pa.id }) : ''}
                </td>`;
        });

        return `<div class="page-header">
            <h1>Practice Areas</h1>
            <div class="header-actions">
                ${Components.actionButton('Add practice area', 'addPracticeArea', { variant: 'primary' })}
            </div>
        </div>
        ${Components.table(['Name', 'Status', 'Matters', 'Actions'], rows)}`;
    },

    // ============ NUMBERING VIEW ============
    renderNumbering() {
        const ns = AppState.numberingScheme;
        return `<div class="page-header"><h1>Matter Numbering</h1></div>
        <div class="settings-section">
            <div class="setting-row">
                <span class="setting-label">Current Template</span>
                <span class="setting-value">${ns.template}</span>
            </div>
            <div class="setting-row">
                <span class="setting-label">Next Matter Number</span>
                <span class="setting-value">${ns.nextMatterNumber}</span>
                ${Components.actionButton('Change', 'changeStartNumber', { variant: 'secondary' })}
            </div>
            <div class="setting-row">
                <span class="setting-label">Separator</span>
                <span class="setting-value">${ns.separator}</span>
            </div>
            <div class="setting-row">
                <span class="setting-label">Fields</span>
                <span class="setting-value">${ns.fields.join(', ')}</span>
            </div>
            <div class="setting-row">
                ${Components.checkbox('autoUpdateNumbering', ns.updateByDefault, 'Update matter name/number by default when saving changes')}
            </div>
        </div>`;
    },

    // ============ MODALS ============
    renderModal() {
        if (!AppState.activeModal) return '';
        switch (AppState.activeModal) {
            case 'newMatter': return this._renderMatterFormModal('New Matter', null);
            case 'editMatter': return this._renderMatterFormModal('Edit Matter', AppState.modalData);
            case 'newDamage': return this._renderDamageModal(null);
            case 'editDamage': return this._renderDamageModal(AppState.modalData);
            case 'newRecovery': return this._renderRecoveryModal(null);
            case 'editRecovery': return this._renderRecoveryModal(AppState.modalData);
            case 'newLegalFee': return this._renderLegalFeeModal(null);
            case 'editLegalFee': return this._renderLegalFeeModal(AppState.modalData);
            case 'newLien': return this._renderLienModal(null);
            case 'editLien': return this._renderLienModal(AppState.modalData);
            case 'newBalance': return this._renderBalanceModal(null);
            case 'editBalance': return this._renderBalanceModal(AppState.modalData);
            case 'addMedicalProvider': return this._renderMedProviderModal(null);
            case 'editMedProvider': return this._renderMedProviderModal(AppState.modalData);
            case 'addMedRecord': return this._renderMedRecordModal(null);
            case 'editMedRecord': return this._renderMedRecordModal(AppState.modalData);
            case 'addMedBill': return this._renderMedBillModal(null);
            case 'editMedBill': return this._renderMedBillModal(AppState.modalData);
            case 'viewComments': return this._renderCommentsModal(AppState.modalData);
            case 'addPracticeArea': return this._renderSimpleInputModal('Add Practice Area', 'practiceAreaName', 'Enter name...', 'confirmAddPracticeArea');
            case 'renamePracticeArea': return this._renderSimpleInputModal('Rename Practice Area', 'practiceAreaName', 'Enter new name...', 'confirmRenamePracticeArea', AppState.modalData ? AppState.modalData.name : '');
            case 'addStage': return this._renderSimpleInputModal('Add Matter Stage', 'stageName', 'Enter stage name...', 'confirmAddStage');
            case 'editStage': return this._renderSimpleInputModal('Edit Matter Stage', 'stageName', 'Enter new name...', 'confirmEditStage', AppState.modalData ? AppState.modalData.name : '');
            case 'newTemplate': return this._renderTemplateModal(null);
            case 'editTemplate': return this._renderTemplateModal(AppState.modalData);
            case 'changeStartNumber': return this._renderSimpleInputModal('Change Starting Number', 'startNumber', 'Enter number...', 'confirmChangeNumber', String(AppState.numberingScheme.nextMatterNumber));
            case 'confirmDelete': return Components.confirmModal('Delete Matter', 'Are you sure you want to delete this matter? This action may affect related data.', 'confirmDeleteMatter', 'Delete matter');
            case 'confirmDeleteProvider': return Components.confirmModal('Delete Medical Provider', 'All information added to this provider will be deleted, including treatment info and records.', 'confirmDeleteProvider', 'Delete medical provider card');
            case 'confirmDeleteRecord': return Components.confirmModal('Delete Medical Record', 'This record will be permanently deleted.', 'confirmDeleteRecord', 'Delete medical record');
            case 'confirmDeleteBill': return Components.confirmModal('Delete Medical Bill', 'This bill will be permanently deleted.', 'confirmDeleteBill', 'Delete medical bill');
            case 'bulkStatusUpdate': return this._renderBulkStatusModal();
            case 'stageCardMenu': return this._renderStageCardMenuModal(AppState.modalData);
            case 'stageColumnMenu': return this._renderStageColumnMenuModal(AppState.modalData);
            case 'matterRowMenu': return this._renderMatterRowMenuModal(AppState.modalData);
            case 'matterDetailMenu': return this._renderMatterDetailMenuModal();
            case 'templateMenu': return this._renderTemplateMenuModal(AppState.modalData);
            default: return '';
        }
    },

    _renderMatterFormModal(title, existingMatter) {
        const m = existingMatter || {};
        const contactOptions = AppState.contacts.map(c => ({ value: c.id, label: c.type === 'company' ? c.lastName : `${c.firstName} ${c.lastName}` }));
        const paOptions = [{ value: '', label: 'None' }, ...AppState.practiceAreas.filter(pa => pa.enabled).map(pa => ({ value: pa.id, label: pa.name }))];
        const userOptions = [{ value: '', label: 'None' }, ...AppState.firmUsers.map(u => ({ value: u.id, label: u.fullName }))];
        const locationOptions = ['', ...AppState.locations].map(l => ({ value: l, label: l || 'None' }));
        const currencyOptions = AppState.currencies.map(c => ({ value: c, label: c }));
        const statusOptions = ['Open', 'Pending', 'Closed'].map(s => ({ value: s, label: s }));
        const billingOptions = [{ value: 'hourly', label: 'Hourly' }, { value: 'contingency', label: 'Contingency fee' }, { value: 'flat_rate', label: 'Flat rate' }];
        const templateOptions = [{ value: '', label: 'No template' }, ...AppState.matterTemplates.map(t => ({ value: t.id, label: t.name }))];

        const bp = m.billingPreference || {};

        const body = `<div class="form-section">
            <h4>Template Information</h4>
            <div class="form-row">
                <label>Use an existing template</label>
                ${Components.dropdown('formTemplate', m.templateId || '', templateOptions, 'Select template')}
            </div>
        </div>
        <div class="form-section">
            <h4>Matter Details</h4>
            <div class="form-row">
                <label>Client <span class="required">*</span></label>
                ${Components.dropdown('formClient', m.clientId || '', contactOptions, 'Select contact')}
            </div>
            <div class="form-row">
                <label>Description</label>
                ${Components.textInput('formDescription', m.description, 'Enter matter description')}
            </div>
            <div class="form-row">
                <label>Matter Status</label>
                ${Components.dropdown('formStatus', m.status || 'Open', statusOptions)}
            </div>
            <div class="form-row">
                <label>Practice Area</label>
                ${Components.dropdown('formPracticeArea', m.practiceAreaId || '', paOptions)}
            </div>
            <div class="form-row">
                <label>Responsible Attorney</label>
                ${Components.dropdown('formRespAttorney', m.responsibleAttorneyId || '', userOptions)}
            </div>
            <div class="form-row">
                <label>Originating Attorney</label>
                ${Components.dropdown('formOrigAttorney', m.originatingAttorneyId || '', userOptions)}
            </div>
            <div class="form-row">
                <label>Responsible Staff</label>
                ${Components.dropdown('formRespStaff', m.responsibleStaffId || '', userOptions)}
            </div>
            <div class="form-row">
                <label>Client Reference Number</label>
                ${Components.textInput('formClientRef', m.clientRefNumber, 'Enter reference number')}
            </div>
            <div class="form-row">
                <label>Location</label>
                ${Components.dropdown('formLocation', m.location || '', locationOptions)}
            </div>
        </div>
        <div class="form-section">
            <h4>Billing Preference</h4>
            <div class="form-row">
                ${Components.checkbox('formBillable', bp.isBillable !== false, 'This matter is billable')}
            </div>
            <div class="form-row">
                <label>Billing Method</label>
                ${Components.dropdown('formBillingMethod', bp.billingMethod || 'hourly', billingOptions)}
            </div>
            <div class="form-row">
                <label>Currency</label>
                ${Components.dropdown('formCurrency', bp.currency || 'USD', currencyOptions)}
            </div>
            <div class="form-row" id="contingencyFields" style="display:${bp.billingMethod === 'contingency' ? 'block' : 'none'}">
                <label>Contingency Rate (%)</label>
                ${Components.textInput('formContRate', bp.contingencyRate, '33.33', { type: 'number' })}
                <label>Fee Recipient</label>
                ${Components.dropdown('formContRecipient', bp.contingencyRecipientId || '', userOptions)}
            </div>
            <div class="form-row" id="flatFeeFields" style="display:${bp.billingMethod === 'flat_rate' ? 'block' : 'none'}">
                <label>Fee Amount</label>
                ${Components.currencyInput('formFlatFee', bp.flatFeeAmount, '0.00')}
                <label>Fee Recipient</label>
                ${Components.dropdown('formFlatRecipient', bp.flatFeeRecipientId || '', userOptions)}
            </div>
            <div class="form-row">
                <label>Budget</label>
                ${Components.currencyInput('formBudget', bp.budget, 'No budget')}
            </div>
        </div>
        <div class="form-section">
            <h4>Personal Injury Preferences</h4>
            <div class="form-row">
                <label>Order of Settlement Deductions</label>
                ${Components.radio('deductionOrder', 'fees_first', m.deductionOrder || 'fees_first', 'Deduct legal fees first, then expenses')}
                ${Components.radio('deductionOrder', 'expenses_first', m.deductionOrder || 'fees_first', 'Deduct expenses first, then legal fees')}
            </div>
        </div>`;

        const footer = `<button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            ${existingMatter ? `<button class="btn btn-danger" data-action="deleteMatterFromForm" data-matter-id="${m.id}">Delete matter</button>` : ''}
            <button class="btn btn-primary" data-action="saveMatter">${existingMatter ? 'Save matter' : 'Save matter'}</button>`;

        return Components.modal('matterForm', title, body, footer, 'large');
    },

    _renderDamageModal(existing) {
        const d = existing || {};
        const allTypes = [];
        AppState.damageTypes.forEach(cat => cat.types.forEach(t => allTypes.push({ value: t, label: t, category: cat.category })));
        const typeOptions = allTypes.map(t => ({ value: t.value, label: `${t.label} (${t.category})` }));

        const body = `<div class="form-row">
            <label>Description <span class="required">*</span></label>
            ${Components.textInput('dmgDescription', d.description, 'Enter damage description')}
        </div>
        <div class="form-row">
            <label>Type <span class="required">*</span></label>
            ${Components.dropdown('dmgType', d.type || '', typeOptions, 'Select damage type')}
        </div>
        <div class="form-row">
            <label>Amount <span class="required">*</span></label>
            ${Components.currencyInput('dmgAmount', d.amount, '0.00')}
        </div>`;
        const footer = `<button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="saveDamage">Save damage</button>`;
        return Components.modal('damageForm', existing ? 'Edit Damage' : 'New Damage', body, footer);
    },

    _renderRecoveryModal(existing) {
        const r = existing || {};
        const contactOptions = AppState.contacts.map(c => ({ value: c.id, label: c.type === 'company' ? c.lastName : `${c.firstName} ${c.lastName}` }));
        const m = AppState.getCurrentMatter();
        const isContingency = m && m.billingPreference.billingMethod === 'contingency';
        const body = `<div class="form-row">
            <label>Source <span class="required">*</span></label>
            ${Components.dropdown('recSource', r.sourceContactId || '', contactOptions, 'Select opposing party')}
        </div>
        <div class="form-row">
            <label>Amount <span class="required">*</span></label>
            ${Components.currencyInput('recAmount', r.amount, '0.00')}
        </div>
        ${!existing && isContingency ? `<div class="form-row">${Components.checkbox('recDefaultFee', true, 'Add default contingency legal fee')}</div>` : ''}`;
        const footer = `<button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="saveRecovery">Save recovery</button>`;
        return Components.modal('recoveryForm', existing ? 'Edit Recovery' : 'New Recovery', body, footer);
    },

    _renderLegalFeeModal(existing) {
        const lf = existing || {};
        const m = AppState.getCurrentMatter();
        const recoveryOptions = m ? m.settlement.recoveries.map(r => ({ value: r.id, label: `${AppState.getContactName(r.sourceContactId)} - ${Components.formatCurrency(r.amount)}` })) : [];
        const userOptions = AppState.firmUsers.map(u => ({ value: u.id, label: u.fullName }));
        const contactOptions = AppState.contacts.map(c => ({ value: c.id, label: c.type === 'company' ? c.lastName : `${c.firstName} ${c.lastName}` }));

        const referralHtml = (lf.referralFees || []).map((rf, i) => `
            <div class="referral-row" data-index="${i}">
                <label>Referral Fee Recipient</label>
                ${Components.dropdown('refRecipient_' + i, rf.recipientId || '', contactOptions, 'Select contact')}
                <label>Rate (%)</label>
                ${Components.textInput('refRate_' + i, rf.rate, '0', { type: 'number' })}
            </div>
        `).join('');

        const body = `<div class="form-row">
            <label>Fee Source <span class="required">*</span></label>
            ${Components.dropdown('lfSource', lf.recoveryId || '', recoveryOptions, 'Select recovery')}
        </div>
        <div class="form-row">
            <label>Fee Recipient <span class="required">*</span></label>
            ${Components.dropdown('lfRecipient', lf.recipientId || '', userOptions, 'Select firm user')}
        </div>
        <div class="form-row">
            <label>Rate (%) <span class="required">*</span></label>
            ${Components.textInput('lfRate', lf.rate, '33.33', { type: 'number' })}
        </div>
        <div class="form-row">
            <label>Discount (%)</label>
            ${Components.textInput('lfDiscount', lf.discount, '0', { type: 'number' })}
        </div>
        <div class="form-section">
            <h4>Referral Fees</h4>
            <div id="referralFees">${referralHtml}</div>
            ${Components.actionButton('Add referral fee', 'addReferralFeeRow', { variant: 'secondary' })}
        </div>`;
        const footer = `<button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="saveLegalFee">Save fee</button>`;
        return Components.modal('legalFeeForm', existing ? 'Edit Legal Fee' : 'New Legal Fee', body, footer, 'large');
    },

    _renderLienModal(existing) {
        const l = existing || {};
        const contactOptions = AppState.contacts.map(c => ({ value: c.id, label: c.type === 'company' ? c.lastName : `${c.firstName} ${c.lastName}` }));
        const body = `<div class="form-row">
            <label>Lien Holder <span class="required">*</span></label>
            ${Components.dropdown('lienHolder', l.lienHolderId || '', contactOptions, 'Select contact')}
        </div>
        <div class="form-row">
            <label>Description</label>
            ${Components.textInput('lienDesc', l.description, 'Enter description')}
        </div>
        <div class="form-row">
            <label>Amount <span class="required">*</span></label>
            ${Components.currencyInput('lienAmount', l.amount, '0.00')}
        </div>
        <div class="form-row">
            <label>Reduction</label>
            ${Components.currencyInput('lienReduction', l.reduction, '0.00')}
        </div>`;
        const footer = `<button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="saveLien">Save lien</button>`;
        return Components.modal('lienForm', existing ? 'Edit Lien' : 'New Lien', body, footer);
    },

    _renderBalanceModal(existing) {
        const b = existing || {};
        const contactOptions = AppState.contacts.map(c => ({ value: c.id, label: c.type === 'company' ? c.lastName : `${c.firstName} ${c.lastName}` }));
        const body = `<div class="form-row">
            <label>Balance to be paid by</label>
            ${Components.radio('balanceParty', 'client', b.responsibleParty || 'client', 'Client')}
            ${Components.radio('balanceParty', 'lawyer', b.responsibleParty || 'client', 'Lawyer')}
        </div>
        <div class="form-row">
            <label>Balance Holder <span class="required">*</span></label>
            ${Components.dropdown('balanceHolder', b.balanceHolderId || '', contactOptions, 'Select contact')}
        </div>
        <div class="form-row">
            <label>Description</label>
            ${Components.textInput('balanceDesc', b.description, 'Enter description')}
        </div>
        <div class="form-row">
            <label>Balance Owing <span class="required">*</span></label>
            ${Components.currencyInput('balanceAmount', b.balanceOwing, '0.00')}
        </div>
        <div class="form-row">
            <label>Reduction</label>
            ${Components.currencyInput('balanceReduction', b.reduction, '0.00')}
        </div>`;
        const footer = `<button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="saveBalance">Save outstanding balance</button>`;
        return Components.modal('balanceForm', existing ? 'Edit Outstanding Balance' : 'New Outstanding Balance', body, footer);
    },

    _renderMedProviderModal(existing) {
        const mp = existing || {};
        const contactOptions = AppState.contacts.filter(c => c.tags.some(t => t.includes('medical') || t.includes('specialist'))).map(c => ({ value: c.id, label: c.type === 'company' ? c.lastName : `${c.firstName} ${c.lastName}` }));
        const allContacts = AppState.contacts.map(c => ({ value: c.id, label: c.type === 'company' ? c.lastName : `${c.firstName} ${c.lastName}` }));
        const statusOptions = ['Not yet requested', 'Requested', 'Received', 'Incomplete', 'Certified'].map(s => ({ value: s, label: s }));

        const body = `<div class="form-section">
            <h4>Medical Provider Details</h4>
            <div class="form-row">
                <label>Medical Provider <span class="required">*</span></label>
                ${Components.dropdown('mpContact', mp.contactId || '', allContacts, 'Select provider')}
            </div>
            <div class="form-row">
                <label>Description</label>
                ${Components.textInput('mpDescription', mp.description, 'Enter description')}
            </div>
        </div>
        <div class="form-section">
            <h4>Treatment Dates</h4>
            <div class="form-row"><label>First Treatment Date</label>${Components.dateInput('mpFirstDate', mp.treatmentFirstDate)}</div>
            <div class="form-row"><label>Last Treatment Date</label>${Components.dateInput('mpLastDate', mp.treatmentLastDate)}</div>
            <div class="form-row">${Components.checkbox('mpTreatmentComplete', mp.treatmentComplete || false, 'Treatment is complete')}</div>
        </div>
        <div class="form-section">
            <h4>Medical Record Request</h4>
            <div class="form-row"><label>Request Date</label>${Components.dateInput('mpRecordReqDate', mp.recordRequestDate)}</div>
            <div class="form-row"><label>Follow-up Date</label>${Components.dateInput('mpRecordFollowUp', mp.recordFollowUpDate)}</div>
            <div class="form-row"><label>Status</label>${Components.dropdown('mpRecordStatus', mp.recordStatus || 'Not yet requested', statusOptions)}</div>
        </div>
        <div class="form-section">
            <h4>Bill Request</h4>
            <div class="form-row"><label>Request Date</label>${Components.dateInput('mpBillReqDate', mp.billRequestDate)}</div>
            <div class="form-row"><label>Follow-up Date</label>${Components.dateInput('mpBillFollowUp', mp.billFollowUpDate)}</div>
            <div class="form-row"><label>Status</label>${Components.dropdown('mpBillStatus', mp.billStatus || 'Not yet requested', statusOptions)}</div>
        </div>`;
        const footer = `<button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="saveMedProvider">Save</button>`;
        return Components.modal('medProviderForm', existing ? 'Edit Medical Provider' : 'Add Medical Provider', body, footer, 'large');
    },

    _renderMedRecordModal(existing) {
        const mr = existing || {};
        const statusOptions = [{ value: 'Received', label: 'Received' }, { value: 'Incomplete', label: 'Incomplete' }];
        const body = `<div class="form-row">
            <label>File Name</label>
            ${Components.textInput('mrFileName', mr.fileName, 'medical_record.pdf')}
        </div>
        <div class="form-row"><label>Record Received Date</label>${Components.dateInput('mrReceivedDate', mr.receivedDate)}</div>
        <div class="form-row"><label>Record Start Date</label>${Components.dateInput('mrStartDate', mr.startDate)}</div>
        <div class="form-row"><label>Record End Date</label>${Components.dateInput('mrEndDate', mr.endDate)}</div>
        ${!existing ? `<div class="form-row"><label>Status Update</label>${Components.dropdown('mrStatusUpdate', '', statusOptions, 'Select status')}</div>` : ''}`;
        const footer = `<button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="saveMedRecord">${existing ? 'Save' : 'Upload'}</button>`;
        return Components.modal('medRecordForm', existing ? 'Edit Medical Record' : 'Add Medical Record', body, footer);
    },

    _renderMedBillModal(existing) {
        const mb = existing || {};
        const contactOptions = AppState.contacts.map(c => ({ value: c.id, label: c.type === 'company' ? c.lastName : `${c.firstName} ${c.lastName}` }));
        const statusOptions = [{ value: 'Received', label: 'Received' }, { value: 'Incomplete', label: 'Incomplete' }];

        const payersHtml = (mb.payers || []).map((p, i) => `
            <div class="payer-row" data-index="${i}">
                <label>Payer</label>
                ${Components.dropdown('payerContact_' + i, p.payerId || '', contactOptions, 'Select payer')}
                <label>Amount Paid</label>
                ${Components.currencyInput('payerAmount_' + i, p.amountPaid, '0.00')}
                ${Components.checkbox('payerLien_' + i, p.isLien || false, 'Mark as lien')}
            </div>
        `).join('');

        const body = `<div class="form-row">
            <label>File Name</label>
            ${Components.textInput('mbFileName', mb.fileName, 'medical_bill.pdf')}
        </div>
        <div class="form-row"><label>Bill Date</label>${Components.dateInput('mbBillDate', mb.billDate)}</div>
        <div class="form-row"><label>Received Date</label>${Components.dateInput('mbReceivedDate', mb.receivedDate)}</div>
        <div class="form-row"><label>Bill Amount</label>${Components.currencyInput('mbBillAmount', mb.billAmount, '0.00')}</div>
        <div class="form-row"><label>Adjustment</label>${Components.currencyInput('mbAdjustment', mb.adjustment, '0.00')}</div>
        <div class="form-section">
            <h4>Payments</h4>
            <div id="payerRows">${payersHtml}</div>
            ${Components.actionButton('Add another payer', 'addPayerRow', { variant: 'secondary' })}
        </div>
        <div class="form-row"><label>Balance Owed to Provider</label>${Components.currencyInput('mbBalanceOwed', mb.balanceOwed, '0.00')}</div>
        <div class="form-row">${Components.checkbox('mbBalanceLien', mb.balanceIsLien || false, 'Mark balance as lien')}</div>
        <div class="form-row">${Components.checkbox('mbBalanceOutstanding', mb.balanceIsOutstanding || false, 'Mark balance as outstanding')}</div>
        ${!existing ? `<div class="form-row"><label>Status Update</label>${Components.dropdown('mbStatusUpdate', '', statusOptions, 'Select status')}</div>` : ''}`;
        const footer = `<button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="saveMedBill">Save</button>`;
        return Components.modal('medBillForm', existing ? 'Edit Medical Bill' : 'Add Medical Bill', body, footer, 'large');
    },

    _renderCommentsModal(data) {
        if (!data) return '';
        const m = AppState.getCurrentMatter();
        if (!m) return '';
        const mp = m.medicalProviders.find(p => p.id === data.providerId);
        if (!mp) return '';
        const list = data.itemType === 'record' ? mp.medicalRecords : mp.medicalBills;
        const item = list.find(i => i.id === data.itemId);
        if (!item) return '';

        const commentsHtml = item.comments.map(c => {
            const user = AppState.getUserName(c.userId);
            const isOwn = c.userId === AppState.currentUser.id;
            return `<div class="comment">
                <div class="comment-header"><strong>${user}</strong> <span class="comment-time">${Components.formatDateTime(c.timestamp)}</span></div>
                <div class="comment-text">${Components._escHtml(c.text)}</div>
                ${isOwn ? `<div class="comment-actions">
                    ${Components.actionButton('Edit', 'editComment', { variant: 'text', dataAttrs: { 'comment-id': c.id } })}
                    ${Components.actionButton('Delete', 'deleteCommentAction', { variant: 'text', dataAttrs: { 'comment-id': c.id } })}
                </div>` : ''}
            </div>`;
        }).join('') || '<p class="no-data">No comments yet.</p>';

        const body = `<div class="comments-list">${commentsHtml}</div>
            <div class="comment-input-row">
                ${Components.textInput('newCommentText', '', 'Add a comment...')}
                ${Components.actionButton('Post', 'postComment', { variant: 'primary' })}
            </div>`;
        return Components.modal('commentsModal', `Comments - ${item.fileName}`, body, null);
    },

    _renderSimpleInputModal(title, inputId, placeholder, confirmAction, currentValue) {
        const body = `<div class="form-row">${Components.textInput(inputId, currentValue || '', placeholder)}</div>`;
        const footer = `<button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="${confirmAction}">Save</button>`;
        return Components.modal('simpleInput', title, body, footer, 'small');
    },

    _renderBulkStatusModal() {
        const body = `<p>Select new status for selected matters:</p>
            <div class="form-row">
                ${Components.radio('bulkStatus', 'Open', '', 'Open')}
                ${Components.radio('bulkStatus', 'Pending', '', 'Pending')}
                ${Components.radio('bulkStatus', 'Closed', '', 'Closed')}
            </div>`;
        const footer = `<button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="confirmBulkStatus">Save</button>`;
        return Components.modal('bulkStatus', 'Update Matter Status', body, footer, 'small');
    },

    _renderStageCardMenuModal(data) {
        if (!data) return '';
        const m = AppState.getMatter(data.matterId);
        if (!m) return '';
        const paOptions = AppState.practiceAreas.filter(pa => pa.enabled && pa.id !== m.practiceAreaId).map(pa => `<div class="menu-item" data-action="switchPracticeArea" data-matter-id="${m.id}" data-pa-id="${pa.id}">${pa.name}</div>`).join('');
        const body = `<div class="context-menu">
            <div class="menu-section"><div class="menu-section-title">Switch practice area</div>${paOptions || '<div class="menu-item disabled">No other practice areas</div>'}</div>
            <div class="menu-divider"></div>
            ${m.status === 'Open' ? `<div class="menu-item" data-action="markPending" data-matter-id="${m.id}">Mark as pending</div>` : `<div class="menu-item" data-action="markOpen" data-matter-id="${m.id}">Mark as open</div>`}
            <div class="menu-item danger" data-action="closeMatter" data-matter-id="${m.id}">Close matter</div>
        </div>`;
        return Components.modal('stageCardMenu', m.displayNumber, body, null, 'small');
    },

    _renderStageColumnMenuModal(data) {
        if (!data) return '';
        const body = `<div class="context-menu">
            <div class="menu-item" data-action="editStageFromMenu" data-stage-id="${data.stageId}">Edit matter stage</div>
            <div class="menu-item danger" data-action="deleteStageFromMenu" data-stage-id="${data.stageId}">Delete matter stage</div>
        </div>`;
        return Components.modal('stageColumnMenu', 'Stage Options', body, null, 'small');
    },

    _renderMatterRowMenuModal(data) {
        if (!data) return '';
        const body = `<div class="context-menu">
            <div class="menu-item" data-action="duplicateMatter" data-matter-id="${data.matterId}">Duplicate</div>
            <div class="menu-item danger" data-action="deleteMatterAction" data-matter-id="${data.matterId}">Delete matter</div>
        </div>`;
        return Components.modal('matterRowMenu', 'Matter Actions', body, null, 'small');
    },

    _renderMatterDetailMenuModal() {
        const m = AppState.getCurrentMatter();
        if (!m) return '';
        const body = `<div class="context-menu">
            ${m.status === 'Open' ? `<div class="menu-item" data-action="markPending" data-matter-id="${m.id}">Mark as pending</div>` : ''}
            ${m.status === 'Pending' ? `<div class="menu-item" data-action="markOpen" data-matter-id="${m.id}">Mark as open</div>` : ''}
            ${m.status !== 'Closed' ? `<div class="menu-item" data-action="closeMatter" data-matter-id="${m.id}">Close matter</div>` : `<div class="menu-item" data-action="markOpen" data-matter-id="${m.id}">Reopen matter</div>`}
            <div class="menu-divider"></div>
            <div class="menu-item danger" data-action="deleteMatterAction" data-matter-id="${m.id}">Delete matter</div>
        </div>`;
        return Components.modal('matterDetailMenu', 'Matter Actions', body, null, 'small');
    },

    _renderTemplateModal(existing) {
        const t = existing || {};
        const paOptions = [{ value: '', label: 'None' }, ...AppState.practiceAreas.filter(pa => pa.enabled).map(pa => ({ value: pa.id, label: pa.name }))];
        const userOptions = [{ value: '', label: 'None' }, ...AppState.firmUsers.map(u => ({ value: u.id, label: u.fullName }))];
        const billingOptions = [{ value: 'hourly', label: 'Hourly' }, { value: 'contingency', label: 'Contingency fee' }, { value: 'flat_rate', label: 'Flat rate' }];

        const body = `<div class="form-section">
            <h4>Template Information</h4>
            <div class="form-row">
                <label>Template Name <span class="required">*</span></label>
                ${Components.textInput('tmplName', t.name, 'Enter template name')}
            </div>
            <div class="form-row">
                ${Components.toggle('tmplDefault', t.isDefault || false, 'Use as matter default template')}
            </div>
        </div>
        <div class="form-section">
            <h4>Matter Details</h4>
            <div class="form-row"><label>Description</label>${Components.textInput('tmplDescription', t.description, 'Enter template description')}</div>
            <div class="form-row"><label>Practice Area</label>${Components.dropdown('tmplPracticeArea', t.practiceAreaId || '', paOptions)}</div>
            <div class="form-row"><label>Responsible Attorney</label>${Components.dropdown('tmplRespAttorney', t.responsibleAttorneyId || '', userOptions)}</div>
            <div class="form-row"><label>Originating Attorney</label>${Components.dropdown('tmplOrigAttorney', t.originatingAttorneyId || '', userOptions)}</div>
            <div class="form-row"><label>Responsible Staff</label>${Components.dropdown('tmplRespStaff', t.responsibleStaffId || '', userOptions)}</div>
        </div>
        <div class="form-section">
            <h4>Billing Preference</h4>
            <div class="form-row">${Components.checkbox('tmplBillable', t.isBillable !== false, 'This matter is billable')}</div>
            <div class="form-row"><label>Billing Method</label>${Components.dropdown('tmplBillingMethod', t.billingMethod || 'hourly', billingOptions)}</div>
        </div>`;
        const footer = `<button class="btn btn-secondary" data-action="closeModal">Cancel</button>
            <button class="btn btn-primary" data-action="saveTemplate">Save template</button>`;
        return Components.modal('templateForm', existing ? 'Edit Template' : 'New Matter Template', body, footer, 'large');
    },

    _renderTemplateMenuModal(data) {
        if (!data) return '';
        const t = AppState.matterTemplates.find(tmpl => tmpl.id === data.templateId);
        if (!t) return '';
        const body = `<div class="context-menu">
            ${t.isDefault ? `<div class="menu-item" data-action="removeDefaultTemplate" data-template-id="${t.id}">Remove as default</div>` : `<div class="menu-item" data-action="setDefaultTemplate" data-template-id="${t.id}">Set as default</div>`}
            <div class="menu-item danger" data-action="deleteTemplateAction" data-template-id="${t.id}">Delete</div>
        </div>`;
        return Components.modal('templateMenu', t.name, body, null, 'small');
    }
};
