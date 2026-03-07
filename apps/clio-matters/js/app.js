const App = {
    _selectedMatters: new Set(),

    render() {
        document.getElementById('sidebarNav').innerHTML = Views.renderSidebar();
        document.getElementById('mainContent').innerHTML = Views.renderContent();
        document.getElementById('modalContainer').innerHTML = Views.renderModal();

        const toast = document.getElementById('toast');
        if (AppState.toastMessage) {
            toast.textContent = AppState.toastMessage;
            toast.classList.add('visible');
        } else {
            toast.classList.remove('visible');
        }

        this._updateBulkActions();
    },

    _updateBulkActions() {
        const ba = document.getElementById('bulkActions');
        if (ba) ba.style.display = this._selectedMatters.size > 0 ? 'flex' : 'none';
    },

    handleClick(e) {
        const target = e.target;

        // Dropdown trigger
        const dropdownTrigger = target.closest('.dropdown-trigger');
        if (dropdownTrigger) {
            e.stopPropagation();
            const dd = dropdownTrigger.closest('.custom-dropdown');
            const wasOpen = dd.classList.contains('open');
            document.querySelectorAll('.custom-dropdown.open').forEach(d => d.classList.remove('open'));
            if (!wasOpen) dd.classList.add('open');
            return;
        }

        // Dropdown item
        const dropdownItem = target.closest('.dropdown-item');
        if (dropdownItem) {
            e.stopPropagation();
            const ddId = dropdownItem.dataset.dropdownId;
            const value = dropdownItem.dataset.value;
            this._handleDropdownSelect(ddId, value);
            const dd = dropdownItem.closest('.custom-dropdown');
            if (dd) dd.classList.remove('open');
            return;
        }

        // Toggle switch
        const toggleSwitch = target.closest('.toggle-switch');
        if (toggleSwitch) {
            const id = toggleSwitch.dataset.toggleId;
            const isActive = toggleSwitch.classList.contains('active');
            toggleSwitch.classList.toggle('active');
            this._handleToggle(id, !isActive);
            return;
        }

        // Checkbox
        const checkbox = target.closest('.custom-checkbox');
        if (checkbox) {
            const id = checkbox.dataset.checkboxId;
            const wasChecked = checkbox.classList.contains('checked');
            checkbox.classList.toggle('checked');
            if (wasChecked) {
                checkbox.innerHTML = '';
            } else {
                checkbox.innerHTML = '<span class="check-icon">&#10003;</span>';
            }
            this._handleCheckbox(id, !wasChecked);
            return;
        }

        // Radio
        const radio = target.closest('.custom-radio');
        if (radio) {
            const name = radio.dataset.radioName;
            const value = radio.dataset.radioValue;
            document.querySelectorAll(`.custom-radio[data-radio-name="${name}"]`).forEach(r => {
                r.classList.remove('checked');
                r.innerHTML = '';
            });
            radio.classList.add('checked');
            radio.innerHTML = '<div class="radio-dot"></div>';
            this._handleRadio(name, value);
            return;
        }

        // Matter checkbox (bulk select)
        if (target.classList.contains('matter-checkbox')) {
            const matterId = target.dataset.matterId;
            if (target.checked) this._selectedMatters.add(matterId);
            else this._selectedMatters.delete(matterId);
            this._updateBulkActions();
            return;
        }

        // Select all matters
        if (target.id === 'selectAllMatters') {
            const checkboxes = document.querySelectorAll('.matter-checkbox');
            checkboxes.forEach(cb => {
                cb.checked = target.checked;
                if (target.checked) this._selectedMatters.add(cb.dataset.matterId);
                else this._selectedMatters.delete(cb.dataset.matterId);
            });
            this._updateBulkActions();
            return;
        }

        // Data-action handling
        const actionEl = target.closest('[data-action]');
        if (actionEl) {
            const action = actionEl.dataset.action;
            this._handleAction(action, actionEl);
            return;
        }

        // Close dropdowns when clicking elsewhere
        document.querySelectorAll('.custom-dropdown.open').forEach(d => d.classList.remove('open'));
    },

    _handleAction(action, el) {
        const matterId = el.dataset.matterId;
        const damageId = el.dataset.damageId;
        const recoveryId = el.dataset.recoveryId;
        const feeId = el.dataset.feeId;
        const lienId = el.dataset.lienId;
        const balanceId = el.dataset.balanceId;
        const providerId = el.dataset.providerId;
        const recordId = el.dataset.recordId;
        const billId = el.dataset.billId;
        const templateId = el.dataset.templateId;
        const paId = el.dataset.paId;
        const stageId = el.dataset.stageId;
        const commentId = el.dataset.commentId;

        switch (action) {
            // Navigation
            case 'navigate':
                AppState.currentView = el.dataset.view;
                AppState.currentMatterId = null;
                this._selectedMatters.clear();
                this.render();
                break;
            case 'backToList':
                AppState.currentView = 'matters-list';
                AppState.currentMatterId = null;
                this.render();
                break;
            case 'openMatter':
                AppState.currentView = 'matter-detail';
                AppState.currentMatterId = matterId;
                AppState.currentMatterTab = 'dashboard';
                this.render();
                break;
            case 'switchTab':
                AppState.currentMatterTab = el.dataset.tab;
                AppState.damagesFilter = 'All';
                AppState.damagesKeyword = '';
                this.render();
                break;

            // Matter CRUD
            case 'newMatter':
                AppState.activeModal = 'newMatter';
                AppState.modalData = null;
                this.render();
                break;
            case 'editMatter':
                AppState.activeModal = 'editMatter';
                AppState.modalData = AppState.getMatter(matterId);
                this.render();
                break;
            case 'saveMatter':
                this._saveMatter();
                break;
            case 'duplicateMatter':
                const dup = AppState.duplicateMatter(matterId);
                if (dup) {
                    AppState.showToast('Matter duplicated: ' + dup.displayNumber);
                    AppState.activeModal = null;
                }
                break;
            case 'deleteMatterAction':
                AppState.activeModal = 'confirmDelete';
                AppState.modalData = { matterId: matterId };
                this.render();
                break;
            case 'deleteMatterFromForm':
                AppState.activeModal = 'confirmDelete';
                AppState.modalData = { matterId: matterId };
                this.render();
                break;
            case 'confirmDeleteMatter':
                if (AppState.modalData) {
                    AppState.deleteMatter(AppState.modalData.matterId);
                    AppState.activeModal = null;
                    AppState.showToast('Matter deleted');
                }
                break;

            // Status changes
            case 'markPending':
                AppState.changeMatterStatus(matterId, 'Pending');
                AppState.activeModal = null;
                AppState.showToast('Matter marked as pending');
                break;
            case 'markOpen':
                AppState.changeMatterStatus(matterId, 'Open');
                AppState.activeModal = null;
                AppState.showToast('Matter marked as open');
                break;
            case 'closeMatter':
                AppState.changeMatterStatus(matterId, 'Closed');
                AppState.activeModal = null;
                AppState.showToast('Matter closed');
                break;

            // Bulk
            case 'bulkStatus':
                AppState.activeModal = 'bulkStatusUpdate';
                this.render();
                break;
            case 'confirmBulkStatus': {
                const checked = document.querySelector('.custom-radio[data-radio-name="bulkStatus"].checked');
                if (checked) {
                    AppState.bulkUpdateStatus([...this._selectedMatters], checked.dataset.radioValue);
                    this._selectedMatters.clear();
                    AppState.activeModal = null;
                    AppState.showToast('Statuses updated');
                }
                break;
            }
            case 'bulkDelete': {
                [...this._selectedMatters].forEach(id => AppState.deleteMatter(id));
                this._selectedMatters.clear();
                AppState.showToast('Matters deleted');
                break;
            }

            // Quick filters
            case 'quickFilter': {
                const filterText = el.dataset.filter;
                const filterName = filterText.replace(/\s*\(\d+\)$/, '');
                if (['All', 'Open', 'Pending', 'Closed'].includes(filterName)) {
                    AppState.matterListFilter = filterName;
                } else {
                    AppState.damagesFilter = filterName;
                }
                this.render();
                break;
            }

            // Sorting
            case 'sortTable': {
                const field = el.dataset.sortField;
                if (AppState.matterListSortField === field) {
                    AppState.matterListSortDir = AppState.matterListSortDir === 'asc' ? 'desc' : 'asc';
                } else {
                    AppState.matterListSortField = field;
                    AppState.matterListSortDir = 'asc';
                }
                this.render();
                break;
            }

            // Damages
            case 'newDamage':
                AppState.activeModal = 'newDamage';
                AppState.modalData = null;
                this.render();
                break;
            case 'editDamage': {
                const m = AppState.getCurrentMatter();
                AppState.activeModal = 'editDamage';
                AppState.modalData = m ? m.damages.find(d => d.id === damageId) : null;
                this.render();
                break;
            }
            case 'saveDamage':
                this._saveDamage();
                break;
            case 'deleteDamage':
                AppState.deleteDamage(AppState.currentMatterId, damageId);
                AppState.showToast('Damage deleted');
                break;

            // Recoveries
            case 'newRecovery':
                AppState.activeModal = 'newRecovery';
                AppState.modalData = null;
                this.render();
                break;
            case 'editRecovery': {
                const m2 = AppState.getCurrentMatter();
                AppState.activeModal = 'editRecovery';
                AppState.modalData = m2 ? m2.settlement.recoveries.find(r => r.id === recoveryId) : null;
                this.render();
                break;
            }
            case 'saveRecovery':
                this._saveRecovery();
                break;
            case 'deleteRecovery':
                AppState.deleteRecovery(AppState.currentMatterId, recoveryId);
                AppState.showToast('Recovery deleted');
                break;

            // Legal Fees
            case 'newLegalFee':
                AppState.activeModal = 'newLegalFee';
                AppState.modalData = null;
                this.render();
                break;
            case 'editLegalFee': {
                const m3 = AppState.getCurrentMatter();
                AppState.activeModal = 'editLegalFee';
                AppState.modalData = m3 ? m3.settlement.legalFees.find(f => f.id === feeId) : null;
                this.render();
                break;
            }
            case 'saveLegalFee':
                this._saveLegalFee();
                break;
            case 'deleteLegalFee':
                AppState.deleteLegalFee(AppState.currentMatterId, feeId);
                AppState.showToast('Legal fee deleted');
                break;

            // Liens
            case 'newLien':
                AppState.activeModal = 'newLien';
                AppState.modalData = null;
                this.render();
                break;
            case 'editLien': {
                const m4 = AppState.getCurrentMatter();
                AppState.activeModal = 'editLien';
                AppState.modalData = m4 ? m4.settlement.otherLiens.find(l => l.id === lienId) : null;
                this.render();
                break;
            }
            case 'saveLien':
                this._saveLien();
                break;
            case 'deleteLien':
                AppState.deleteLien(AppState.currentMatterId, lienId);
                AppState.showToast('Lien deleted');
                break;

            // Outstanding Balances
            case 'newBalance':
                AppState.activeModal = 'newBalance';
                AppState.modalData = null;
                this.render();
                break;
            case 'editBalance': {
                const m5 = AppState.getCurrentMatter();
                AppState.activeModal = 'editBalance';
                AppState.modalData = m5 ? m5.settlement.outstandingBalances.find(b => b.id === balanceId) : null;
                this.render();
                break;
            }
            case 'saveBalance':
                this._saveBalance();
                break;
            case 'deleteBalance':
                AppState.deleteOutstandingBalance(AppState.currentMatterId, balanceId);
                AppState.showToast('Outstanding balance deleted');
                break;

            // Medical Providers
            case 'addMedicalProvider':
                AppState.activeModal = 'addMedicalProvider';
                AppState.modalData = null;
                this.render();
                break;
            case 'editMedProvider': {
                const m6 = AppState.getCurrentMatter();
                AppState.activeModal = 'editMedProvider';
                AppState.modalData = m6 ? m6.medicalProviders.find(p => p.id === providerId) : null;
                this.render();
                break;
            }
            case 'saveMedProvider':
                this._saveMedProvider();
                break;
            case 'deleteMedProvider':
                AppState.activeModal = 'confirmDeleteProvider';
                AppState.modalData = { providerId: providerId };
                this.render();
                break;
            case 'confirmDeleteProvider':
                if (AppState.modalData) {
                    AppState.deleteMedicalProvider(AppState.currentMatterId, AppState.modalData.providerId);
                    AppState.activeModal = null;
                    AppState.showToast('Medical provider deleted');
                }
                break;

            // Medical Records
            case 'addMedRecord':
                AppState.activeModal = 'addMedRecord';
                AppState.modalData = { providerId: providerId };
                this.render();
                break;
            case 'editMedRecord': {
                const m7 = AppState.getCurrentMatter();
                const mp7 = m7 ? m7.medicalProviders.find(p => p.id === providerId) : null;
                const mr7 = mp7 ? mp7.medicalRecords.find(r => r.id === recordId) : null;
                AppState.activeModal = 'editMedRecord';
                AppState.modalData = mr7 ? { ...mr7, providerId } : null;
                this.render();
                break;
            }
            case 'saveMedRecord':
                this._saveMedRecord();
                break;
            case 'deleteMedRecord':
                AppState.activeModal = 'confirmDeleteRecord';
                AppState.modalData = { providerId, recordId };
                this.render();
                break;
            case 'confirmDeleteRecord':
                if (AppState.modalData) {
                    AppState.deleteMedicalRecord(AppState.currentMatterId, AppState.modalData.providerId, AppState.modalData.recordId);
                    AppState.activeModal = null;
                    AppState.showToast('Medical record deleted');
                }
                break;

            // Medical Bills
            case 'addMedBill':
                AppState.activeModal = 'addMedBill';
                AppState.modalData = { providerId };
                this.render();
                break;
            case 'editMedBill': {
                const m8 = AppState.getCurrentMatter();
                const mp8 = m8 ? m8.medicalProviders.find(p => p.id === providerId) : null;
                const mb8 = mp8 ? mp8.medicalBills.find(b => b.id === billId) : null;
                AppState.activeModal = 'editMedBill';
                AppState.modalData = mb8 ? { ...mb8, providerId } : null;
                this.render();
                break;
            }
            case 'saveMedBill':
                this._saveMedBill();
                break;
            case 'deleteMedBill':
                AppState.activeModal = 'confirmDeleteBill';
                AppState.modalData = { providerId, billId };
                this.render();
                break;
            case 'confirmDeleteBill':
                if (AppState.modalData) {
                    AppState.deleteMedicalBill(AppState.currentMatterId, AppState.modalData.providerId, AppState.modalData.billId);
                    AppState.activeModal = null;
                    AppState.showToast('Medical bill deleted');
                }
                break;

            // Comments
            case 'viewComments':
                AppState.activeModal = 'viewComments';
                AppState.modalData = { providerId, itemType: el.dataset.itemType, itemId: el.dataset.itemId };
                this.render();
                break;
            case 'postComment': {
                const text = document.getElementById('newCommentText')?.value;
                if (text && AppState.modalData) {
                    AppState.addComment(AppState.currentMatterId, AppState.modalData.providerId, AppState.modalData.itemType, AppState.modalData.itemId, text);
                    this.render();
                }
                break;
            }
            case 'editComment': {
                const commentEl = el.closest('.comment');
                const textEl = commentEl?.querySelector('.comment-text');
                if (textEl) {
                    const currentText = textEl.textContent;
                    textEl.innerHTML = `<input type="text" class="form-input comment-edit-input" value="${Components._escAttr(currentText)}">
                        <button class="btn btn-primary btn-small" data-action="saveCommentEdit" data-comment-id="${commentId}">Save</button>`;
                    textEl.querySelector('input').focus();
                }
                break;
            }
            case 'saveCommentEdit': {
                const input = document.querySelector('.comment-edit-input');
                if (input && AppState.modalData) {
                    AppState.updateComment(AppState.currentMatterId, AppState.modalData.providerId, AppState.modalData.itemType, AppState.modalData.itemId, commentId, input.value);
                    this.render();
                }
                break;
            }
            case 'deleteCommentAction': {
                if (AppState.modalData) {
                    AppState.deleteComment(AppState.currentMatterId, AppState.modalData.providerId, AppState.modalData.itemType, AppState.modalData.itemId, commentId);
                    this.render();
                }
                break;
            }

            // Practice Areas
            case 'addPracticeArea':
                AppState.activeModal = 'addPracticeArea';
                AppState.modalData = null;
                this.render();
                break;
            case 'confirmAddPracticeArea': {
                const name = document.getElementById('practiceAreaName')?.value;
                if (name) {
                    AppState.addPracticeArea(name.trim());
                    AppState.activeModal = null;
                    AppState.showToast('Practice area added');
                }
                break;
            }
            case 'renamePracticeArea': {
                const pa = AppState.practiceAreas.find(p => p.id === paId);
                AppState.activeModal = 'renamePracticeArea';
                AppState.modalData = pa;
                this.render();
                break;
            }
            case 'confirmRenamePracticeArea': {
                const name = document.getElementById('practiceAreaName')?.value;
                if (name && AppState.modalData) {
                    AppState.renamePracticeArea(AppState.modalData.id, name.trim());
                    AppState.activeModal = null;
                    AppState.showToast('Practice area renamed');
                }
                break;
            }
            case 'deletePracticeArea': {
                const success = AppState.deletePracticeArea(paId);
                if (!success) AppState.showToast('Cannot delete: practice area is in use');
                else AppState.showToast('Practice area deleted');
                break;
            }

            // Stages
            case 'addStage':
                AppState.activeModal = 'addStage';
                AppState.modalData = null;
                this.render();
                break;
            case 'confirmAddStage': {
                const name = document.getElementById('stageName')?.value;
                if (name && AppState.currentStagesPracticeArea) {
                    const result = AppState.addMatterStage(AppState.currentStagesPracticeArea, name.trim());
                    AppState.activeModal = null;
                    if (result) AppState.showToast('Stage added');
                    else AppState.showToast('Maximum 15 stages per practice area');
                }
                break;
            }
            case 'stageColumnMenu':
                AppState.activeModal = 'stageColumnMenu';
                AppState.modalData = { stageId };
                this.render();
                break;
            case 'editStageFromMenu': {
                const stages = AppState.matterStages[AppState.currentStagesPracticeArea] || [];
                const stage = stages.find(s => s.id === stageId);
                AppState.activeModal = 'editStage';
                AppState.modalData = stage;
                this.render();
                break;
            }
            case 'confirmEditStage': {
                const name = document.getElementById('stageName')?.value;
                if (name && AppState.modalData) {
                    AppState.renameMatterStage(AppState.currentStagesPracticeArea, AppState.modalData.id, name.trim());
                    AppState.activeModal = null;
                    AppState.showToast('Stage renamed');
                }
                break;
            }
            case 'deleteStageFromMenu':
                AppState.deleteMatterStage(AppState.currentStagesPracticeArea, stageId);
                AppState.activeModal = null;
                AppState.showToast('Stage deleted');
                break;
            case 'stageCardMenu':
                AppState.activeModal = 'stageCardMenu';
                AppState.modalData = { matterId };
                this.render();
                break;
            case 'switchPracticeArea': {
                const m = AppState.getMatter(matterId);
                if (m) {
                    m.practiceAreaId = paId;
                    const stages = AppState.getStagesForPracticeArea(paId);
                    m.matterStageId = stages.length > 0 ? stages[0].id : null;
                    m.updatedAt = new Date().toISOString();
                    AppState.notify();
                }
                AppState.activeModal = null;
                AppState.showToast('Practice area switched');
                break;
            }

            // Templates
            case 'newTemplate':
                AppState.activeModal = 'newTemplate';
                AppState.modalData = null;
                this.render();
                break;
            case 'editTemplate': {
                const tmpl = AppState.matterTemplates.find(t => t.id === templateId);
                AppState.activeModal = 'editTemplate';
                AppState.modalData = tmpl;
                this.render();
                break;
            }
            case 'saveTemplate':
                this._saveTemplate();
                break;
            case 'templateMenu':
                AppState.activeModal = 'templateMenu';
                AppState.modalData = { templateId };
                this.render();
                break;
            case 'setDefaultTemplate':
                AppState.updateTemplate(templateId, { isDefault: true });
                AppState.activeModal = null;
                AppState.showToast('Default template set');
                break;
            case 'removeDefaultTemplate':
                AppState.removeDefaultTemplate(templateId);
                AppState.activeModal = null;
                AppState.showToast('Default template removed');
                break;
            case 'deleteTemplateAction':
                AppState.deleteTemplate(templateId);
                AppState.activeModal = null;
                AppState.showToast('Template deleted');
                break;

            // Numbering
            case 'changeStartNumber':
                AppState.activeModal = 'changeStartNumber';
                this.render();
                break;
            case 'confirmChangeNumber': {
                const num = parseInt(document.getElementById('startNumber')?.value);
                if (!isNaN(num) && num > 0) {
                    AppState.updateNumberingScheme({ nextMatterNumber: num });
                    AppState.activeModal = null;
                    AppState.showToast('Starting number updated');
                }
                break;
            }

            // Modal
            case 'closeModal':
                AppState.activeModal = null;
                AppState.modalData = null;
                this.render();
                break;

            // Misc
            case 'matterDetailMenu':
                AppState.activeModal = 'matterDetailMenu';
                this.render();
                break;
            case 'matterRowMenu':
                AppState.activeModal = 'matterRowMenu';
                AppState.modalData = { matterId };
                this.render();
                break;
            case 'addReferralFeeRow':
                this._addReferralFeeRow();
                break;
            case 'addPayerRow':
                this._addPayerRow();
                break;
            case 'copyAddress':
                navigator.clipboard?.writeText(el.dataset.address);
                AppState.showToast('Address copied');
                break;
        }
    },

    _handleDropdownSelect(ddId, value) {
        switch (ddId) {
            case 'statusDropdown':
                if (AppState.currentMatterId) {
                    AppState.changeMatterStatus(AppState.currentMatterId, value);
                    AppState.showToast('Status updated');
                }
                break;
            case 'stageDropdown':
                if (AppState.currentMatterId) {
                    AppState.changeMatterStage(AppState.currentMatterId, value);
                    AppState.showToast('Stage updated');
                }
                break;
            case 'stagesPADropdown':
                AppState.currentStagesPracticeArea = value;
                this.render();
                break;
            case 'formBillingMethod': {
                const contFields = document.getElementById('contingencyFields');
                const flatFields = document.getElementById('flatFeeFields');
                if (contFields) contFields.style.display = value === 'contingency' ? 'block' : 'none';
                if (flatFields) flatFields.style.display = value === 'flat_rate' ? 'block' : 'none';
                break;
            }
        }
    },

    _handleToggle(id, isActive) {
        switch (id) {
            case 'tmplDefault':
                break;
        }
    },

    _handleCheckbox(id, isChecked) {
        switch (id) {
            case 'confirmCheck': {
                const btn = document.getElementById('confirmBtn');
                if (btn) btn.disabled = !isChecked;
                break;
            }
            case 'autoUpdateNumbering':
                AppState.updateNumberingScheme({ updateByDefault: isChecked });
                break;
        }
    },

    _handleRadio(name, value) {
        // Radios are read during save
    },

    handleInput(e) {
        const target = e.target;
        if (target.id === 'matterSearch') {
            AppState.matterListKeyword = target.value;
            this.render();
            const input = document.getElementById('matterSearch');
            if (input) { input.focus(); input.setSelectionRange(target.value.length, target.value.length); }
        }
        if (target.id === 'damagesKeyword') {
            AppState.damagesKeyword = target.value;
            this.render();
            const input = document.getElementById('damagesKeyword');
            if (input) { input.focus(); input.setSelectionRange(target.value.length, target.value.length); }
        }
    },

    handleKeydown(e) {
        if (e.key === 'Escape') {
            if (AppState.activeModal) {
                AppState.activeModal = null;
                AppState.modalData = null;
                this.render();
            }
            document.querySelectorAll('.custom-dropdown.open').forEach(d => d.classList.remove('open'));
        }
        if (e.key === 'Enter' && AppState.activeModal) {
            const confirmBtn = document.querySelector('.modal-footer .btn-primary');
            if (confirmBtn && !confirmBtn.disabled && e.target.tagName !== 'TEXTAREA') {
                confirmBtn.click();
            }
        }
    },

    _getDropdownValue(id) {
        const dd = document.getElementById(id);
        if (!dd) return '';
        const selected = dd.querySelector('.dropdown-item.selected');
        return selected ? selected.dataset.value : '';
    },

    _saveMatter() {
        const clientId = this._getDropdownValue('formClient');
        if (!clientId) { AppState.showToast('Client is required'); return; }

        const data = {
            clientId,
            description: document.getElementById('formDescription')?.value || '',
            status: this._getDropdownValue('formStatus') || 'Open',
            practiceAreaId: this._getDropdownValue('formPracticeArea') || null,
            responsibleAttorneyId: this._getDropdownValue('formRespAttorney') || null,
            originatingAttorneyId: this._getDropdownValue('formOrigAttorney') || null,
            responsibleStaffId: this._getDropdownValue('formRespStaff') || null,
            clientRefNumber: document.getElementById('formClientRef')?.value || '',
            location: this._getDropdownValue('formLocation') || '',
            templateId: this._getDropdownValue('formTemplate') || null,
            billingPreference: {
                isBillable: !!document.querySelector('#formBillable .custom-checkbox.checked, [data-checkbox-id="formBillable"].checked'),
                billingMethod: this._getDropdownValue('formBillingMethod') || 'hourly',
                currency: this._getDropdownValue('formCurrency') || 'USD',
                contingencyRate: parseFloat(document.getElementById('formContRate')?.value) || null,
                contingencyRecipientId: this._getDropdownValue('formContRecipient') || null,
                flatFeeAmount: parseFloat(document.getElementById('formFlatFee')?.value) || null,
                flatFeeRecipientId: this._getDropdownValue('formFlatRecipient') || null,
                customRates: [],
                budget: parseFloat(document.getElementById('formBudget')?.value) || null,
                budgetNotifyUsers: [],
                trustMinBalance: null,
                trustNotifyUsers: []
            },
            deductionOrder: document.querySelector('.custom-radio[data-radio-name="deductionOrder"].checked')?.dataset.radioValue || 'fees_first'
        };

        data.contactName = AppState.getContactName(clientId);

        if (AppState.activeModal === 'editMatter' && AppState.modalData) {
            AppState.updateMatter(AppState.modalData.id, data);
            AppState.showToast('Matter saved');
        } else {
            const m = AppState.createMatter(data);
            AppState.showToast('Matter created: ' + m.displayNumber);
        }
        AppState.activeModal = null;
    },

    _saveDamage() {
        const desc = document.getElementById('dmgDescription')?.value;
        const typeValue = this._getDropdownValue('dmgType');
        const amount = document.getElementById('dmgAmount')?.value;
        if (!desc || !typeValue) { AppState.showToast('Description and type are required'); return; }

        let category = 'Other';
        AppState.damageTypes.forEach(cat => {
            if (cat.types.includes(typeValue)) category = cat.category;
        });

        const data = { description: desc, type: typeValue, category, amount };

        if (AppState.activeModal === 'editDamage' && AppState.modalData) {
            AppState.updateDamage(AppState.currentMatterId, AppState.modalData.id, data);
            AppState.showToast('Damage updated');
        } else {
            AppState.addDamage(AppState.currentMatterId, data);
            AppState.showToast('Damage added');
        }
        AppState.activeModal = null;
    },

    _saveRecovery() {
        const source = this._getDropdownValue('recSource');
        const amount = document.getElementById('recAmount')?.value;
        if (!source) { AppState.showToast('Source is required'); return; }

        const addDefaultFee = !!document.querySelector('[data-checkbox-id="recDefaultFee"].checked');

        if (AppState.activeModal === 'editRecovery' && AppState.modalData) {
            AppState.updateRecovery(AppState.currentMatterId, AppState.modalData.id, { sourceContactId: source, amount });
            AppState.showToast('Recovery updated');
        } else {
            AppState.addRecovery(AppState.currentMatterId, { sourceContactId: source, amount, addDefaultFee });
            AppState.showToast('Recovery added');
        }
        AppState.activeModal = null;
    },

    _saveLegalFee() {
        const recoveryId = this._getDropdownValue('lfSource');
        const recipientId = this._getDropdownValue('lfRecipient');
        const rate = document.getElementById('lfRate')?.value;
        const discount = document.getElementById('lfDiscount')?.value;
        if (!recoveryId || !recipientId) { AppState.showToast('Fee source and recipient are required'); return; }

        const referralFees = [];
        document.querySelectorAll('.referral-row').forEach((row, i) => {
            const rid = this._getDropdownValue('refRecipient_' + i);
            const rrate = document.getElementById('refRate_' + i)?.value;
            if (rid) referralFees.push({ recipientId: rid, rate: parseFloat(rrate) || 0 });
        });

        const data = { recoveryId, recipientId, rate, discount, referralFees };

        if (AppState.activeModal === 'editLegalFee' && AppState.modalData) {
            AppState.updateLegalFee(AppState.currentMatterId, AppState.modalData.id, data);
            AppState.showToast('Legal fee updated');
        } else {
            AppState.addLegalFee(AppState.currentMatterId, data);
            AppState.showToast('Legal fee added');
        }
        AppState.activeModal = null;
    },

    _saveLien() {
        const holder = this._getDropdownValue('lienHolder');
        if (!holder) { AppState.showToast('Lien holder is required'); return; }
        const data = {
            lienHolderId: holder,
            description: document.getElementById('lienDesc')?.value || '',
            amount: document.getElementById('lienAmount')?.value,
            reduction: document.getElementById('lienReduction')?.value
        };
        if (AppState.activeModal === 'editLien' && AppState.modalData) {
            AppState.updateLien(AppState.currentMatterId, AppState.modalData.id, data);
            AppState.showToast('Lien updated');
        } else {
            AppState.addLien(AppState.currentMatterId, data);
            AppState.showToast('Lien added');
        }
        AppState.activeModal = null;
    },

    _saveBalance() {
        const holder = this._getDropdownValue('balanceHolder');
        if (!holder) { AppState.showToast('Balance holder is required'); return; }
        const party = document.querySelector('.custom-radio[data-radio-name="balanceParty"].checked')?.dataset.radioValue || 'client';
        const data = {
            responsibleParty: party,
            balanceHolderId: holder,
            description: document.getElementById('balanceDesc')?.value || '',
            balanceOwing: document.getElementById('balanceAmount')?.value,
            reduction: document.getElementById('balanceReduction')?.value
        };
        if (AppState.activeModal === 'editBalance' && AppState.modalData) {
            AppState.updateOutstandingBalance(AppState.currentMatterId, AppState.modalData.id, data);
            AppState.showToast('Outstanding balance updated');
        } else {
            AppState.addOutstandingBalance(AppState.currentMatterId, data);
            AppState.showToast('Outstanding balance added');
        }
        AppState.activeModal = null;
    },

    _saveMedProvider() {
        const contactId = this._getDropdownValue('mpContact');
        if (!contactId) { AppState.showToast('Provider is required'); return; }
        const data = {
            contactId,
            description: document.getElementById('mpDescription')?.value || '',
            treatmentFirstDate: document.getElementById('mpFirstDate')?.value || null,
            treatmentLastDate: document.getElementById('mpLastDate')?.value || null,
            treatmentComplete: !!document.querySelector('[data-checkbox-id="mpTreatmentComplete"].checked'),
            recordRequestDate: document.getElementById('mpRecordReqDate')?.value || null,
            recordFollowUpDate: document.getElementById('mpRecordFollowUp')?.value || null,
            recordStatus: this._getDropdownValue('mpRecordStatus') || 'Not yet requested',
            billRequestDate: document.getElementById('mpBillReqDate')?.value || null,
            billFollowUpDate: document.getElementById('mpBillFollowUp')?.value || null,
            billStatus: this._getDropdownValue('mpBillStatus') || 'Not yet requested'
        };
        if (AppState.activeModal === 'editMedProvider' && AppState.modalData) {
            AppState.updateMedicalProvider(AppState.currentMatterId, AppState.modalData.id, data);
            AppState.showToast('Provider updated');
        } else {
            AppState.addMedicalProvider(AppState.currentMatterId, data);
            AppState.showToast('Provider added');
        }
        AppState.activeModal = null;
    },

    _saveMedRecord() {
        const providerId = AppState.modalData?.providerId;
        if (!providerId) return;
        const data = {
            fileName: document.getElementById('mrFileName')?.value || 'medical_record.pdf',
            receivedDate: document.getElementById('mrReceivedDate')?.value || '',
            startDate: document.getElementById('mrStartDate')?.value || '',
            endDate: document.getElementById('mrEndDate')?.value || '',
            statusUpdate: this._getDropdownValue('mrStatusUpdate') || null
        };
        if (AppState.activeModal === 'editMedRecord' && AppState.modalData?.id) {
            AppState.updateMedicalRecord(AppState.currentMatterId, providerId, AppState.modalData.id, data);
            AppState.showToast('Record updated');
        } else {
            AppState.addMedicalRecord(AppState.currentMatterId, providerId, data);
            AppState.showToast('Record added');
        }
        AppState.activeModal = null;
    },

    _saveMedBill() {
        const providerId = AppState.modalData?.providerId;
        if (!providerId) return;

        const payers = [];
        document.querySelectorAll('.payer-row').forEach((row, i) => {
            const payerId = this._getDropdownValue('payerContact_' + i);
            const amount = document.getElementById('payerAmount_' + i)?.value;
            const isLien = !!document.querySelector(`[data-checkbox-id="payerLien_${i}"].checked`);
            if (payerId) payers.push({ payerId, amountPaid: parseFloat(amount) || 0, isLien });
        });

        const data = {
            fileName: document.getElementById('mbFileName')?.value || 'medical_bill.pdf',
            billDate: document.getElementById('mbBillDate')?.value || '',
            receivedDate: document.getElementById('mbReceivedDate')?.value || '',
            billAmount: document.getElementById('mbBillAmount')?.value,
            adjustment: document.getElementById('mbAdjustment')?.value,
            payers,
            balanceOwed: document.getElementById('mbBalanceOwed')?.value,
            balanceIsLien: !!document.querySelector('[data-checkbox-id="mbBalanceLien"].checked'),
            balanceIsOutstanding: !!document.querySelector('[data-checkbox-id="mbBalanceOutstanding"].checked'),
            statusUpdate: this._getDropdownValue('mbStatusUpdate') || null
        };
        if (AppState.activeModal === 'editMedBill' && AppState.modalData?.id) {
            AppState.updateMedicalBill(AppState.currentMatterId, providerId, AppState.modalData.id, data);
            AppState.showToast('Bill updated');
        } else {
            AppState.addMedicalBill(AppState.currentMatterId, providerId, data);
            AppState.showToast('Bill added');
        }
        AppState.activeModal = null;
    },

    _saveTemplate() {
        const name = document.getElementById('tmplName')?.value;
        if (!name) { AppState.showToast('Template name is required'); return; }
        const isDefault = !!document.querySelector('[data-toggle-id="tmplDefault"].active');
        const data = {
            name,
            isDefault,
            description: document.getElementById('tmplDescription')?.value || '',
            practiceAreaId: this._getDropdownValue('tmplPracticeArea') || null,
            responsibleAttorneyId: this._getDropdownValue('tmplRespAttorney') || null,
            originatingAttorneyId: this._getDropdownValue('tmplOrigAttorney') || null,
            responsibleStaffId: this._getDropdownValue('tmplRespStaff') || null,
            isBillable: !!document.querySelector('[data-checkbox-id="tmplBillable"].checked'),
            billingMethod: this._getDropdownValue('tmplBillingMethod') || 'hourly'
        };
        if (AppState.activeModal === 'editTemplate' && AppState.modalData) {
            AppState.updateTemplate(AppState.modalData.id, data);
            AppState.showToast('Template saved');
        } else {
            AppState.addTemplate(data);
            AppState.showToast('Template created');
        }
        AppState.activeModal = null;
    },

    _addReferralFeeRow() {
        const container = document.getElementById('referralFees');
        if (!container) return;
        const i = container.children.length;
        const contactOptions = AppState.contacts.map(c => ({ value: c.id, label: c.type === 'company' ? c.lastName : `${c.firstName} ${c.lastName}` }));
        const html = `<div class="referral-row" data-index="${i}">
            <label>Referral Fee Recipient</label>
            ${Components.dropdown('refRecipient_' + i, '', contactOptions, 'Select contact')}
            <label>Rate (%)</label>
            ${Components.textInput('refRate_' + i, '', '0', { type: 'number' })}
        </div>`;
        container.insertAdjacentHTML('beforeend', html);
    },

    _addPayerRow() {
        const container = document.getElementById('payerRows');
        if (!container) return;
        const i = container.children.length;
        const contactOptions = AppState.contacts.map(c => ({ value: c.id, label: c.type === 'company' ? c.lastName : `${c.firstName} ${c.lastName}` }));
        const html = `<div class="payer-row" data-index="${i}">
            <label>Payer</label>
            ${Components.dropdown('payerContact_' + i, '', contactOptions, 'Select payer')}
            <label>Amount Paid</label>
            ${Components.currencyInput('payerAmount_' + i, '', '0.00')}
            ${Components.checkbox('payerLien_' + i, false, 'Mark as lien')}
        </div>`;
        container.insertAdjacentHTML('beforeend', html);
    }
};

// ======== INITIALIZATION ========
document.addEventListener('click', (e) => App.handleClick(e));
document.addEventListener('keydown', (e) => App.handleKeydown(e));
document.addEventListener('input', (e) => App.handleInput(e));

AppState.subscribe(() => App.render());
AppState.init();
App.render();

// SSE for reset events
const _sseConnection = new EventSource('/api/events');
_sseConnection.onmessage = (e) => {
    if (e.data === 'reset') {
        AppState.resetToSeedData();
        App.render();
    }
};
