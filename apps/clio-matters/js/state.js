const AppState = {
    currentUser: null,
    firmUsers: [],
    userGroups: [],
    practiceAreas: [],
    matterStages: {},
    contacts: [],
    customFieldDefinitions: [],
    taskLists: [],
    documentCategories: [],
    currencies: [],
    locations: [],
    damageTypes: [],
    expenseCategories: [],
    matterTemplates: [],
    numberingScheme: {},
    matters: [],
    deletedMatters: [],

    // UI state (not persisted)
    currentView: 'matters-list',
    currentMatterId: null,
    currentMatterTab: 'dashboard',
    currentStagesPracticeArea: null,
    matterListFilter: 'All',
    matterListKeyword: '',
    matterListSortField: 'displayNumber',
    matterListSortDir: 'asc',
    activeModal: null,
    modalData: null,
    toastMessage: null,
    damagesFilter: 'All',
    damagesKeyword: '',

    _listeners: [],
    _seedVersion: null,
    _nextIds: {},

    init() {
        const persisted = this._loadPersistedData();
        if (persisted) {
            this._applyPersisted(persisted);
        } else {
            this._loadSeedData();
        }
        this._pushStateToServer();
    },

    _loadSeedData() {
        this.currentUser = JSON.parse(JSON.stringify(CURRENT_USER));
        this.firmUsers = JSON.parse(JSON.stringify(FIRM_USERS));
        this.userGroups = JSON.parse(JSON.stringify(USER_GROUPS));
        this.practiceAreas = JSON.parse(JSON.stringify(PRACTICE_AREAS));
        this.matterStages = JSON.parse(JSON.stringify(MATTER_STAGES));
        this.contacts = JSON.parse(JSON.stringify(CONTACTS));
        this.customFieldDefinitions = JSON.parse(JSON.stringify(CUSTOM_FIELD_DEFINITIONS));
        this.taskLists = JSON.parse(JSON.stringify(TASK_LISTS));
        this.documentCategories = [...DOCUMENT_CATEGORIES];
        this.currencies = [...CURRENCIES];
        this.locations = [...LOCATIONS];
        this.damageTypes = JSON.parse(JSON.stringify(DAMAGE_TYPES));
        this.expenseCategories = [...EXPENSE_CATEGORIES];
        this.matterTemplates = JSON.parse(JSON.stringify(MATTER_TEMPLATES));
        this.numberingScheme = JSON.parse(JSON.stringify(NUMBERING_SCHEME));
        this.matters = JSON.parse(JSON.stringify(MATTERS));
        this.deletedMatters = JSON.parse(JSON.stringify(DELETED_MATTERS));
        this._seedVersion = SEED_DATA_VERSION;
        this._nextIds = { matter: 147, contact: 29, damage: 100, recovery: 20, legalFee: 20, lien: 10, balance: 10, medProvider: 50, medRecord: 50, medBill: 50, comment: 20, template: 6, practiceArea: 15, stage: 30, timeline: 200 };
    },

    _loadPersistedData() {
        try {
            const saved = localStorage.getItem('clioMattersState');
            if (!saved) return null;
            const parsed = JSON.parse(saved);
            if (parsed._seedVersion !== SEED_DATA_VERSION) {
                localStorage.removeItem('clioMattersState');
                return null;
            }
            return parsed;
        } catch (e) {
            localStorage.removeItem('clioMattersState');
            return null;
        }
    },

    _applyPersisted(data) {
        const fields = ['currentUser', 'firmUsers', 'userGroups', 'practiceAreas', 'matterStages',
            'contacts', 'customFieldDefinitions', 'taskLists', 'documentCategories', 'currencies',
            'locations', 'damageTypes', 'expenseCategories', 'matterTemplates', 'numberingScheme',
            'matters', 'deletedMatters', '_seedVersion', '_nextIds'];
        fields.forEach(f => { if (data[f] !== undefined) this[f] = data[f]; });
    },

    _persist() {
        const data = {
            currentUser: this.currentUser,
            firmUsers: this.firmUsers,
            userGroups: this.userGroups,
            practiceAreas: this.practiceAreas,
            matterStages: this.matterStages,
            contacts: this.contacts,
            customFieldDefinitions: this.customFieldDefinitions,
            taskLists: this.taskLists,
            documentCategories: this.documentCategories,
            currencies: this.currencies,
            locations: this.locations,
            damageTypes: this.damageTypes,
            expenseCategories: this.expenseCategories,
            matterTemplates: this.matterTemplates,
            numberingScheme: this.numberingScheme,
            matters: this.matters,
            deletedMatters: this.deletedMatters,
            _seedVersion: this._seedVersion,
            _nextIds: this._nextIds
        };
        localStorage.setItem('clioMattersState', JSON.stringify(data));
    },

    _pushStateToServer() {
        const data = {
            currentUser: this.currentUser,
            firmUsers: this.firmUsers,
            userGroups: this.userGroups,
            practiceAreas: this.practiceAreas,
            matterStages: this.matterStages,
            contacts: this.contacts,
            customFieldDefinitions: this.customFieldDefinitions,
            taskLists: this.taskLists,
            documentCategories: this.documentCategories,
            currencies: this.currencies,
            locations: this.locations,
            damageTypes: this.damageTypes,
            expenseCategories: this.expenseCategories,
            matterTemplates: this.matterTemplates,
            numberingScheme: this.numberingScheme,
            matters: this.matters,
            deletedMatters: this.deletedMatters,
            _seedVersion: this._seedVersion,
            _nextIds: this._nextIds
        };
        fetch('/api/state', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).catch(() => {});
    },

    subscribe(fn) {
        this._listeners.push(fn);
    },

    notify() {
        this._persist();
        this._pushStateToServer();
        this._listeners.forEach(fn => fn());
    },

    resetToSeedData() {
        localStorage.removeItem('clioMattersState');
        this._loadSeedData();
        this.currentView = 'matters-list';
        this.currentMatterId = null;
        this.currentMatterTab = 'dashboard';
        this.matterListFilter = 'All';
        this.matterListKeyword = '';
        this.activeModal = null;
        this.modalData = null;
    },

    _genId(type) {
        const n = this._nextIds[type]++;
        return n;
    },

    getContact(id) {
        return this.contacts.find(c => c.id === id);
    },

    getContactName(id) {
        const c = this.getContact(id);
        if (!c) return 'Unknown';
        return c.type === 'company' ? c.lastName : `${c.firstName} ${c.lastName}`;
    },

    getUser(id) {
        return this.firmUsers.find(u => u.id === id);
    },

    getUserName(id) {
        const u = this.getUser(id);
        return u ? u.fullName : 'Unknown';
    },

    getPracticeArea(id) {
        return this.practiceAreas.find(pa => pa.id === id);
    },

    getPracticeAreaName(id) {
        const pa = this.getPracticeArea(id);
        return pa ? pa.name : '';
    },

    getMatter(id) {
        return this.matters.find(m => m.id === id);
    },

    getCurrentMatter() {
        return this.getMatter(this.currentMatterId);
    },

    getStagesForPracticeArea(paId) {
        return this.matterStages[paId] || [];
    },

    getStageName(paId, stageId) {
        const stages = this.getStagesForPracticeArea(paId);
        const s = stages.find(st => st.id === stageId);
        return s ? s.name : 'No Stage Assigned';
    },

    getFilteredMatters() {
        let list = [...this.matters];
        if (this.matterListFilter === 'Open') list = list.filter(m => m.status === 'Open');
        else if (this.matterListFilter === 'Pending') list = list.filter(m => m.status === 'Pending');
        else if (this.matterListFilter === 'Closed') list = list.filter(m => m.status === 'Closed');

        if (this.matterListKeyword) {
            const kw = this.matterListKeyword.toLowerCase();
            list = list.filter(m =>
                m.displayNumber.toLowerCase().includes(kw) ||
                m.description.toLowerCase().includes(kw) ||
                m.contactName.toLowerCase().includes(kw) ||
                (m.clientRefNumber && m.clientRefNumber.toLowerCase().includes(kw))
            );
        }

        list.sort((a, b) => {
            let va = a[this.matterListSortField] || '';
            let vb = b[this.matterListSortField] || '';
            if (typeof va === 'string') va = va.toLowerCase();
            if (typeof vb === 'string') vb = vb.toLowerCase();
            if (va < vb) return this.matterListSortDir === 'asc' ? -1 : 1;
            if (va > vb) return this.matterListSortDir === 'asc' ? 1 : -1;
            return 0;
        });

        return list;
    },

    // --- Matter CRUD ---
    createMatter(data) {
        const num = String(this._genId('matter')).padStart(5, '0');
        const contactName = this.getContactName(data.clientId);
        const shortName = contactName.split(' ').pop().replace(/[^a-zA-Z]/g, '');
        const matter = {
            id: 'mat_' + num,
            matterNumber: num,
            displayNumber: num + '-' + shortName,
            description: data.description || '',
            clientId: data.clientId,
            contactName: contactName,
            status: data.status || 'Open',
            practiceAreaId: data.practiceAreaId || null,
            matterStageId: data.matterStageId || null,
            responsibleAttorneyId: data.responsibleAttorneyId || null,
            originatingAttorneyId: data.originatingAttorneyId || null,
            responsibleStaffId: data.responsibleStaffId || null,
            clientRefNumber: data.clientRefNumber || '',
            location: data.location || '',
            openDate: new Date().toISOString(),
            pendingDate: null, closedDate: null,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            permissions: data.permissions || { type: 'everyone' },
            blockedUsers: data.blockedUsers || [],
            billingPreference: data.billingPreference || {
                isBillable: true, billingMethod: 'hourly', currency: 'USD',
                contingencyRate: null, contingencyRecipientId: null,
                flatFeeAmount: null, flatFeeRecipientId: null,
                customRates: [], budget: null, budgetNotifyUsers: [],
                trustMinBalance: null, trustNotifyUsers: []
            },
            deductionOrder: data.deductionOrder || 'fees_first',
            relatedContacts: data.relatedContacts || [],
            notifications: data.notifications || [],
            customFields: data.customFields || [],
            taskLists: data.taskLists || [],
            documentFolders: data.documentFolders || [],
            reports: data.reports || { useFirmSettings: true, originatingAllocation: 0, responsibleAllocation: 0 },
            templateId: data.templateId || null,
            financials: { workInProgress: 0, outstandingBalance: 0, trustFunds: 0, totalTime: 0, totalExpenses: 0 },
            timeline: [{ id: 'tl_ev_' + this._genId('timeline'), action: 'created', timestamp: new Date().toISOString(), userId: this.currentUser.id, details: 'Matter created' }],
            damages: [],
            medicalProviders: [],
            settlement: { recoveries: [], legalFees: [], otherLiens: [], outstandingBalances: [], expenses: [] }
        };
        if (matter.practiceAreaId && !matter.matterStageId) {
            const stages = this.getStagesForPracticeArea(matter.practiceAreaId);
            if (stages.length > 0) matter.matterStageId = stages[0].id;
        }
        this.matters.push(matter);
        this.notify();
        return matter;
    },

    updateMatter(id, data) {
        const m = this.getMatter(id);
        if (!m) return;
        Object.keys(data).forEach(k => {
            if (k !== 'id' && k !== 'matterNumber' && k !== 'createdAt') {
                m[k] = data[k];
            }
        });
        m.updatedAt = new Date().toISOString();
        m.timeline.push({ id: 'tl_ev_' + this._genId('timeline'), action: 'edited', timestamp: new Date().toISOString(), userId: this.currentUser.id, details: 'Matter edited' });
        this.notify();
    },

    deleteMatter(id) {
        const idx = this.matters.findIndex(m => m.id === id);
        if (idx === -1) return;
        const m = this.matters[idx];
        this.deletedMatters.push({
            id: m.id, matterNumber: m.matterNumber, displayNumber: m.displayNumber,
            description: m.description, clientId: m.clientId, contactName: m.contactName,
            deletedAt: new Date().toISOString(), deletedBy: this.currentUser.id, canRecover: true
        });
        this.matters.splice(idx, 1);
        if (this.currentMatterId === id) {
            this.currentMatterId = null;
            this.currentView = 'matters-list';
        }
        this.notify();
    },

    recoverMatter(id) {
        const idx = this.deletedMatters.findIndex(m => m.id === id);
        if (idx === -1) return;
        this.deletedMatters.splice(idx, 1);
        this.notify();
    },

    duplicateMatter(id) {
        const orig = this.getMatter(id);
        if (!orig) return;
        const clone = JSON.parse(JSON.stringify(orig));
        const num = String(this._genId('matter')).padStart(5, '0');
        clone.id = 'mat_' + num;
        clone.matterNumber = num;
        clone.displayNumber = num + '-' + clone.contactName.split(' ').pop().replace(/[^a-zA-Z]/g, '');
        clone.createdAt = new Date().toISOString();
        clone.updatedAt = new Date().toISOString();
        clone.timeline = [{ id: 'tl_ev_' + this._genId('timeline'), action: 'created', timestamp: new Date().toISOString(), userId: this.currentUser.id, details: 'Matter created (duplicated from ' + orig.displayNumber + ')' }];
        clone.financials = { workInProgress: 0, outstandingBalance: 0, trustFunds: 0, totalTime: 0, totalExpenses: 0 };
        this.matters.push(clone);
        this.notify();
        return clone;
    },

    changeMatterStatus(id, status) {
        const m = this.getMatter(id);
        if (!m) return;
        const old = m.status;
        m.status = status;
        m.updatedAt = new Date().toISOString();
        if (status === 'Pending' && !m.pendingDate) m.pendingDate = new Date().toISOString();
        if (status === 'Closed' && !m.closedDate) m.closedDate = new Date().toISOString();
        if (status === 'Open') { m.closedDate = null; }
        m.timeline.push({ id: 'tl_ev_' + this._genId('timeline'), action: 'status_changed', timestamp: new Date().toISOString(), userId: this.currentUser.id, details: `Status changed from ${old} to ${status}` });
        this.notify();
    },

    changeMatterStage(matterId, stageId) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const oldName = this.getStageName(m.practiceAreaId, m.matterStageId);
        m.matterStageId = stageId;
        m.updatedAt = new Date().toISOString();
        const newName = this.getStageName(m.practiceAreaId, stageId);
        m.timeline.push({ id: 'tl_ev_' + this._genId('timeline'), action: 'stage_changed', timestamp: new Date().toISOString(), userId: this.currentUser.id, details: `Stage changed from ${oldName} to ${newName}` });
        this.notify();
    },

    bulkUpdateStatus(matterIds, status) {
        matterIds.forEach(id => {
            const m = this.getMatter(id);
            if (m) {
                const old = m.status;
                m.status = status;
                m.updatedAt = new Date().toISOString();
                if (status === 'Pending' && !m.pendingDate) m.pendingDate = new Date().toISOString();
                if (status === 'Closed' && !m.closedDate) m.closedDate = new Date().toISOString();
                if (status === 'Open') { m.closedDate = null; }
                m.timeline.push({ id: 'tl_ev_' + this._genId('timeline'), action: 'status_changed', timestamp: new Date().toISOString(), userId: this.currentUser.id, details: `Status changed from ${old} to ${status}` });
            }
        });
        this.notify();
    },

    // --- Damages ---
    addDamage(matterId, data) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const dmg = {
            id: 'dmg_' + String(this._genId('damage')).padStart(3, '0'),
            description: data.description,
            type: data.type,
            category: data.category,
            amount: parseFloat(data.amount) || 0,
            createdAt: new Date().toISOString(),
            createdBy: this.currentUser.id
        };
        m.damages.push(dmg);
        m.updatedAt = new Date().toISOString();
        m.timeline.push({ id: 'tl_ev_' + this._genId('timeline'), action: 'damage_added', timestamp: new Date().toISOString(), userId: this.currentUser.id, details: `Damage added: ${dmg.description}` });
        this.notify();
    },

    updateDamage(matterId, damageId, data) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const d = m.damages.find(dd => dd.id === damageId);
        if (!d) return;
        Object.assign(d, data);
        if (data.amount !== undefined) d.amount = parseFloat(data.amount) || 0;
        m.updatedAt = new Date().toISOString();
        m.timeline.push({ id: 'tl_ev_' + this._genId('timeline'), action: 'damage_edited', timestamp: new Date().toISOString(), userId: this.currentUser.id, details: `Damage edited: ${d.description}` });
        this.notify();
    },

    deleteDamage(matterId, damageId) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const idx = m.damages.findIndex(d => d.id === damageId);
        if (idx === -1) return;
        const d = m.damages[idx];
        m.damages.splice(idx, 1);
        m.updatedAt = new Date().toISOString();
        m.timeline.push({ id: 'tl_ev_' + this._genId('timeline'), action: 'damage_deleted', timestamp: new Date().toISOString(), userId: this.currentUser.id, details: `Damage deleted: ${d.description}` });
        this.notify();
    },

    // --- Settlement: Recoveries ---
    addRecovery(matterId, data) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const rec = {
            id: 'rec_' + String(this._genId('recovery')).padStart(3, '0'),
            sourceContactId: data.sourceContactId,
            amount: parseFloat(data.amount) || 0,
            createdAt: new Date().toISOString()
        };
        m.settlement.recoveries.push(rec);
        if (data.addDefaultFee && m.billingPreference.billingMethod === 'contingency') {
            const lf = {
                id: 'lf_' + String(this._genId('legalFee')).padStart(3, '0'),
                recoveryId: rec.id,
                recipientId: m.billingPreference.contingencyRecipientId,
                rate: m.billingPreference.contingencyRate,
                discount: 0,
                referralFees: [],
                createdAt: new Date().toISOString()
            };
            m.settlement.legalFees.push(lf);
        }
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    updateRecovery(matterId, recoveryId, data) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const r = m.settlement.recoveries.find(rc => rc.id === recoveryId);
        if (!r) return;
        if (data.sourceContactId !== undefined) r.sourceContactId = data.sourceContactId;
        if (data.amount !== undefined) r.amount = parseFloat(data.amount) || 0;
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    deleteRecovery(matterId, recoveryId) {
        const m = this.getMatter(matterId);
        if (!m) return;
        m.settlement.recoveries = m.settlement.recoveries.filter(r => r.id !== recoveryId);
        m.settlement.legalFees = m.settlement.legalFees.filter(lf => lf.recoveryId !== recoveryId);
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    // --- Settlement: Legal Fees ---
    addLegalFee(matterId, data) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const lf = {
            id: 'lf_' + String(this._genId('legalFee')).padStart(3, '0'),
            recoveryId: data.recoveryId,
            recipientId: data.recipientId,
            rate: parseFloat(data.rate) || 0,
            discount: parseFloat(data.discount) || 0,
            referralFees: data.referralFees || [],
            createdAt: new Date().toISOString()
        };
        m.settlement.legalFees.push(lf);
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    updateLegalFee(matterId, feeId, data) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const lf = m.settlement.legalFees.find(f => f.id === feeId);
        if (!lf) return;
        Object.assign(lf, data);
        if (data.rate !== undefined) lf.rate = parseFloat(data.rate) || 0;
        if (data.discount !== undefined) lf.discount = parseFloat(data.discount) || 0;
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    deleteLegalFee(matterId, feeId) {
        const m = this.getMatter(matterId);
        if (!m) return;
        m.settlement.legalFees = m.settlement.legalFees.filter(f => f.id !== feeId);
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    // --- Settlement: Liens ---
    addLien(matterId, data) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const lien = {
            id: 'ol_' + String(this._genId('lien')).padStart(3, '0'),
            lienHolderId: data.lienHolderId,
            description: data.description || '',
            amount: parseFloat(data.amount) || 0,
            reduction: parseFloat(data.reduction) || 0,
            createdAt: new Date().toISOString()
        };
        m.settlement.otherLiens.push(lien);
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    updateLien(matterId, lienId, data) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const l = m.settlement.otherLiens.find(li => li.id === lienId);
        if (!l) return;
        Object.assign(l, data);
        if (data.amount !== undefined) l.amount = parseFloat(data.amount) || 0;
        if (data.reduction !== undefined) l.reduction = parseFloat(data.reduction) || 0;
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    deleteLien(matterId, lienId) {
        const m = this.getMatter(matterId);
        if (!m) return;
        m.settlement.otherLiens = m.settlement.otherLiens.filter(l => l.id !== lienId);
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    // --- Settlement: Outstanding Balances ---
    addOutstandingBalance(matterId, data) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const ob = {
            id: 'ob_' + String(this._genId('balance')).padStart(3, '0'),
            responsibleParty: data.responsibleParty || 'client',
            balanceHolderId: data.balanceHolderId,
            description: data.description || '',
            balanceOwing: parseFloat(data.balanceOwing) || 0,
            reduction: parseFloat(data.reduction) || 0,
            createdAt: new Date().toISOString()
        };
        m.settlement.outstandingBalances.push(ob);
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    updateOutstandingBalance(matterId, balanceId, data) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const ob = m.settlement.outstandingBalances.find(b => b.id === balanceId);
        if (!ob) return;
        Object.assign(ob, data);
        if (data.balanceOwing !== undefined) ob.balanceOwing = parseFloat(data.balanceOwing) || 0;
        if (data.reduction !== undefined) ob.reduction = parseFloat(data.reduction) || 0;
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    deleteOutstandingBalance(matterId, balanceId) {
        const m = this.getMatter(matterId);
        if (!m) return;
        m.settlement.outstandingBalances = m.settlement.outstandingBalances.filter(b => b.id !== balanceId);
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    // --- Medical Providers ---
    addMedicalProvider(matterId, data) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const mp = {
            id: 'mp_' + String(this._genId('medProvider')).padStart(3, '0'),
            contactId: data.contactId,
            description: data.description || '',
            treatmentFirstDate: data.treatmentFirstDate || null,
            treatmentLastDate: data.treatmentLastDate || null,
            treatmentComplete: data.treatmentComplete || false,
            recordRequestDate: data.recordRequestDate || null,
            recordFollowUpDate: data.recordFollowUpDate || null,
            recordStatus: data.recordStatus || 'Not yet requested',
            billRequestDate: data.billRequestDate || null,
            billFollowUpDate: data.billFollowUpDate || null,
            billStatus: data.billStatus || 'Not yet requested',
            medicalRecords: [],
            medicalBills: []
        };
        m.medicalProviders.push(mp);
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    updateMedicalProvider(matterId, providerId, data) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const mp = m.medicalProviders.find(p => p.id === providerId);
        if (!mp) return;
        Object.assign(mp, data);
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    deleteMedicalProvider(matterId, providerId) {
        const m = this.getMatter(matterId);
        if (!m) return;
        m.medicalProviders = m.medicalProviders.filter(p => p.id !== providerId);
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    addMedicalRecord(matterId, providerId, data) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const mp = m.medicalProviders.find(p => p.id === providerId);
        if (!mp) return;
        const mr = {
            id: 'mr_' + String(this._genId('medRecord')).padStart(3, '0'),
            fileName: data.fileName || 'medical_record.pdf',
            receivedDate: data.receivedDate || '',
            startDate: data.startDate || '',
            endDate: data.endDate || '',
            comments: []
        };
        mp.medicalRecords.push(mr);
        if (data.statusUpdate) mp.recordStatus = data.statusUpdate;
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    updateMedicalRecord(matterId, providerId, recordId, data) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const mp = m.medicalProviders.find(p => p.id === providerId);
        if (!mp) return;
        const mr = mp.medicalRecords.find(r => r.id === recordId);
        if (!mr) return;
        Object.assign(mr, data);
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    deleteMedicalRecord(matterId, providerId, recordId) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const mp = m.medicalProviders.find(p => p.id === providerId);
        if (!mp) return;
        mp.medicalRecords = mp.medicalRecords.filter(r => r.id !== recordId);
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    addMedicalBill(matterId, providerId, data) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const mp = m.medicalProviders.find(p => p.id === providerId);
        if (!mp) return;
        const mb = {
            id: 'mb_' + String(this._genId('medBill')).padStart(3, '0'),
            fileName: data.fileName || 'medical_bill.pdf',
            billDate: data.billDate || '',
            receivedDate: data.receivedDate || '',
            billAmount: parseFloat(data.billAmount) || 0,
            adjustment: parseFloat(data.adjustment) || 0,
            payers: data.payers || [],
            balanceOwed: parseFloat(data.balanceOwed) || 0,
            balanceIsLien: data.balanceIsLien || false,
            balanceIsOutstanding: data.balanceIsOutstanding || false,
            comments: []
        };
        mp.medicalBills.push(mb);
        if (data.statusUpdate) mp.billStatus = data.statusUpdate;
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    updateMedicalBill(matterId, providerId, billId, data) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const mp = m.medicalProviders.find(p => p.id === providerId);
        if (!mp) return;
        const mb = mp.medicalBills.find(b => b.id === billId);
        if (!mb) return;
        Object.assign(mb, data);
        if (data.billAmount !== undefined) mb.billAmount = parseFloat(data.billAmount) || 0;
        if (data.adjustment !== undefined) mb.adjustment = parseFloat(data.adjustment) || 0;
        if (data.balanceOwed !== undefined) mb.balanceOwed = parseFloat(data.balanceOwed) || 0;
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    deleteMedicalBill(matterId, providerId, billId) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const mp = m.medicalProviders.find(p => p.id === providerId);
        if (!mp) return;
        mp.medicalBills = mp.medicalBills.filter(b => b.id !== billId);
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    addComment(matterId, providerId, itemType, itemId, text) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const mp = m.medicalProviders.find(p => p.id === providerId);
        if (!mp) return;
        const list = itemType === 'record' ? mp.medicalRecords : mp.medicalBills;
        const item = list.find(i => i.id === itemId);
        if (!item) return;
        item.comments.push({
            id: 'cmt_' + String(this._genId('comment')).padStart(3, '0'),
            text: text,
            userId: this.currentUser.id,
            timestamp: new Date().toISOString()
        });
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    updateComment(matterId, providerId, itemType, itemId, commentId, text) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const mp = m.medicalProviders.find(p => p.id === providerId);
        if (!mp) return;
        const list = itemType === 'record' ? mp.medicalRecords : mp.medicalBills;
        const item = list.find(i => i.id === itemId);
        if (!item) return;
        const c = item.comments.find(cm => cm.id === commentId);
        if (!c) return;
        c.text = text;
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    deleteComment(matterId, providerId, itemType, itemId, commentId) {
        const m = this.getMatter(matterId);
        if (!m) return;
        const mp = m.medicalProviders.find(p => p.id === providerId);
        if (!mp) return;
        const list = itemType === 'record' ? mp.medicalRecords : mp.medicalBills;
        const item = list.find(i => i.id === itemId);
        if (!item) return;
        item.comments = item.comments.filter(c => c.id !== commentId);
        m.updatedAt = new Date().toISOString();
        this.notify();
    },

    // --- Practice Areas ---
    addPracticeArea(name) {
        const id = 'pa_' + String(this._genId('practiceArea')).padStart(3, '0');
        this.practiceAreas.push({ id, name, enabled: true, isPrimary: false });
        this.notify();
        return id;
    },

    renamePracticeArea(id, newName) {
        const pa = this.practiceAreas.find(p => p.id === id);
        if (pa) { pa.name = newName; this.notify(); }
    },

    deletePracticeArea(id) {
        const inUse = this.matters.some(m => m.practiceAreaId === id);
        if (inUse) return false;
        this.practiceAreas = this.practiceAreas.filter(p => p.id !== id);
        delete this.matterStages[id];
        this.notify();
        return true;
    },

    setPrimaryPracticeArea(id) {
        this.practiceAreas.forEach(pa => { pa.isPrimary = pa.id === id; });
        this.notify();
    },

    // --- Matter Stages ---
    addMatterStage(practiceAreaId, name) {
        if (!this.matterStages[practiceAreaId]) this.matterStages[practiceAreaId] = [];
        const stages = this.matterStages[practiceAreaId];
        if (stages.length >= 15) return null;
        const id = 'stg_' + String(this._genId('stage')).padStart(3, '0');
        stages.push({ id, name, order: stages.length });
        this.notify();
        return id;
    },

    renameMatterStage(practiceAreaId, stageId, newName) {
        const stages = this.matterStages[practiceAreaId];
        if (!stages) return;
        const s = stages.find(st => st.id === stageId);
        if (s) { s.name = newName; this.notify(); }
    },

    deleteMatterStage(practiceAreaId, stageId) {
        const stages = this.matterStages[practiceAreaId];
        if (!stages) return;
        this.matterStages[practiceAreaId] = stages.filter(s => s.id !== stageId);
        this.matters.forEach(m => {
            if (m.matterStageId === stageId) m.matterStageId = null;
        });
        this.notify();
    },

    reorderMatterStages(practiceAreaId, orderedIds) {
        const stages = this.matterStages[practiceAreaId];
        if (!stages) return;
        orderedIds.forEach((id, i) => {
            const s = stages.find(st => st.id === id);
            if (s) s.order = i;
        });
        stages.sort((a, b) => a.order - b.order);
        this.notify();
    },

    // --- Matter Templates ---
    addTemplate(data) {
        const id = 'tmpl_' + String(this._genId('template')).padStart(3, '0');
        const tmpl = {
            id, name: data.name, isDefault: data.isDefault || false,
            practiceAreaId: data.practiceAreaId || null,
            status: data.status || 'Open',
            billingMethod: data.billingMethod || 'hourly',
            description: data.description || '',
            responsibleAttorneyId: data.responsibleAttorneyId || null,
            originatingAttorneyId: data.originatingAttorneyId || null,
            responsibleStaffId: data.responsibleStaffId || null,
            location: data.location || '',
            isBillable: data.isBillable !== false,
            contingencyRate: data.contingencyRate || null,
            contingencyRecipientId: data.contingencyRecipientId || null,
            flatFeeAmount: data.flatFeeAmount || null,
            flatFeeRecipientId: data.flatFeeRecipientId || null,
            deductionOrder: data.deductionOrder || 'fees_first',
            taskLists: data.taskLists || [],
            documentFolders: data.documentFolders || [],
            customFields: data.customFields || [],
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString()
        };
        if (tmpl.isDefault) {
            this.matterTemplates.forEach(t => { t.isDefault = false; });
        }
        this.matterTemplates.push(tmpl);
        this.notify();
        return id;
    },

    updateTemplate(id, data) {
        const tmpl = this.matterTemplates.find(t => t.id === id);
        if (!tmpl) return;
        Object.assign(tmpl, data);
        tmpl.updatedAt = new Date().toISOString();
        if (data.isDefault) {
            this.matterTemplates.forEach(t => { if (t.id !== id) t.isDefault = false; });
        }
        this.notify();
    },

    deleteTemplate(id) {
        this.matterTemplates = this.matterTemplates.filter(t => t.id !== id);
        this.notify();
    },

    removeDefaultTemplate(id) {
        const tmpl = this.matterTemplates.find(t => t.id === id);
        if (tmpl) { tmpl.isDefault = false; this.notify(); }
    },

    // --- Numbering Scheme ---
    updateNumberingScheme(data) {
        Object.assign(this.numberingScheme, data);
        this.notify();
    },

    showToast(message) {
        this.toastMessage = message;
        this._listeners.forEach(fn => fn());
        setTimeout(() => {
            this.toastMessage = null;
            this._listeners.forEach(fn => fn());
        }, 3000);
    }
};
