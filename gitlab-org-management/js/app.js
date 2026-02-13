// ============================================================
// app.js — Router and application initialization
// ============================================================

const Router = {
    routes: {
        '/': () => Views.home(),
        '/organizations': () => Views.organizations(),
        '/organizations/:id': (params) => Views.organizationDetail(params.id),
        '/groups': () => Views.groups(),
        '/groups/:id': (params) => Views.groupDetail(params.id),
        '/projects': () => Views.projects(),
        '/projects/:id': (params) => Views.projectDetail(params.id),
        '/members': () => Views.members(),
        '/namespaces': () => Views.namespaces(),
        '/profile': () => Views.profile(),
        '/profile/:username': (params) => Views.profile(params.username),
        '/import': () => Views.importPage(),
        '/settings': () => Views.settings()
    },

    navigate(path, skipHistory = false) {
        // Parse query params for tabs etc.
        const [basePath, queryString] = path.split('?');
        const params = {};
        if (queryString) {
            queryString.split('&').forEach(p => {
                const [k, v] = p.split('=');
                params[k] = decodeURIComponent(v);
            });
        }

        AppState.routeParams = params;
        AppState.currentRoute = basePath;

        if (!skipHistory) {
            history.pushState({ path }, '', `#${path}`);
        }

        Router.render();
    },

    refresh() {
        Router.render();
    },

    render() {
        const path = AppState.currentRoute;
        const contentWrapper = document.getElementById('contentWrapper');

        // Match route
        let html = null;
        for (const [pattern, handler] of Object.entries(Router.routes)) {
            const match = Router.matchRoute(pattern, path);
            if (match !== null) {
                html = handler(match);
                break;
            }
        }

        if (html === null) {
            html = Views._notFound('Page not found');
        }

        contentWrapper.innerHTML = html;

        // Update active sidebar item
        document.querySelectorAll('.sidebar-item').forEach(item => {
            const route = item.getAttribute('data-route');
            if (route === path || (route !== '/' && path.startsWith(route))) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });

        // Attach event handlers for dynamic content
        Router.attachHandlers();
    },

    matchRoute(pattern, path) {
        const patternParts = pattern.split('/');
        const pathParts = path.split('/');

        if (patternParts.length !== pathParts.length) return null;

        const params = {};
        for (let i = 0; i < patternParts.length; i++) {
            if (patternParts[i].startsWith(':')) {
                params[patternParts[i].substring(1)] = pathParts[i];
            } else if (patternParts[i] !== pathParts[i]) {
                return null;
            }
        }
        return params;
    },

    attachHandlers() {
        // Route links
        document.querySelectorAll('[data-route]').forEach(el => {
            if (el._routeHandlerAttached) return;
            el._routeHandlerAttached = true;
            el.addEventListener('click', (e) => {
                e.preventDefault();
                Router.navigate(el.getAttribute('data-route'));
            });
        });

        // Tab handling
        document.querySelectorAll('.tab-item').forEach(tab => {
            if (tab._tabHandlerAttached) return;
            tab._tabHandlerAttached = true;
            tab.addEventListener('click', () => {
                const tabId = tab.getAttribute('data-tab');
                const basePath = AppState.currentRoute;
                Router.navigate(`${basePath}?tab=${tabId}`);
            });
        });

        // Group search
        const groupSearch = document.getElementById('groupSearch');
        if (groupSearch && !groupSearch._handlerAttached) {
            groupSearch._handlerAttached = true;
            groupSearch.addEventListener('input', () => {
                const query = groupSearch.value.toLowerCase();
                document.querySelectorAll('.tree-item').forEach(item => {
                    const name = item.querySelector('.tree-item-name')?.textContent.toLowerCase() || '';
                    item.style.display = name.includes(query) || !query ? '' : 'none';
                });
            });
        }

        // Group visibility filter
        const groupVisFilter = document.getElementById('groupVisFilter');
        if (groupVisFilter && !groupVisFilter._handlerAttached) {
            groupVisFilter._handlerAttached = true;
            groupVisFilter.addEventListener('change', (e) => {
                const vis = e.detail.value;
                document.querySelectorAll('.tree-item').forEach(item => {
                    if (vis === 'all') {
                        item.style.display = '';
                    } else {
                        const badge = item.querySelector('.visibility-badge');
                        const itemVis = badge ? badge.className.includes(vis) : false;
                        item.style.display = itemVis ? '' : 'none';
                    }
                });
            });
        }

        // Project search
        const projectSearch = document.getElementById('projectSearch');
        if (projectSearch && !projectSearch._handlerAttached) {
            projectSearch._handlerAttached = true;
            projectSearch.addEventListener('input', () => {
                const query = projectSearch.value.toLowerCase();
                document.querySelectorAll('.project-list .list-item').forEach(item => {
                    const text = item.textContent.toLowerCase();
                    item.style.display = text.includes(query) ? '' : 'none';
                });
            });
        }

        // Project visibility filter
        const projectVisFilter = document.getElementById('projectVisFilter');
        if (projectVisFilter && !projectVisFilter._handlerAttached) {
            projectVisFilter._handlerAttached = true;
            projectVisFilter.addEventListener('change', (e) => {
                const vis = e.detail.value;
                document.querySelectorAll('.project-list .list-item').forEach(item => {
                    if (vis === 'all') {
                        item.style.display = '';
                    } else {
                        const badge = item.querySelector('.visibility-badge');
                        item.style.display = badge && badge.className.includes(vis) ? '' : 'none';
                    }
                });
            });
        }

        // Member search
        ['memberSearch', 'projectMemberSearch', 'globalMemberSearch'].forEach(searchId => {
            const input = document.getElementById(searchId);
            if (input && !input._handlerAttached) {
                input._handlerAttached = true;
                input.addEventListener('input', () => {
                    const query = input.value.toLowerCase();
                    const list = input.closest('.tab-content, .main-content, [data-testid]')?.querySelectorAll('.member-list-row') ||
                                 document.querySelectorAll('.member-list-row');
                    list.forEach(row => {
                        const text = row.textContent.toLowerCase();
                        row.style.display = text.includes(query) ? '' : 'none';
                    });
                });
            }
        });

        // Member type filter
        ['memberTypeFilter', 'projectMemberTypeFilter'].forEach(filterId => {
            const filter = document.getElementById(filterId);
            if (filter && !filter._handlerAttached) {
                filter._handlerAttached = true;
                filter.addEventListener('change', (e) => {
                    AppState.routeParams.memberFilter = e.detail.value;
                    Router.render();
                });
            }
        });

        // Namespace search
        const nsSearch = document.getElementById('namespaceSearch');
        if (nsSearch && !nsSearch._handlerAttached) {
            nsSearch._handlerAttached = true;
            nsSearch.addEventListener('input', () => {
                const query = nsSearch.value.toLowerCase();
                document.querySelectorAll('.namespace-list .member-list-row').forEach(row => {
                    row.style.display = row.textContent.toLowerCase().includes(query) ? '' : 'none';
                });
            });
        }

        // Create group button (from groups list page)
        const createGroupBtn = document.getElementById('createGroupBtn');
        if (createGroupBtn && !createGroupBtn._handlerAttached) {
            createGroupBtn._handlerAttached = true;
            createGroupBtn.addEventListener('click', () => Views._showCreateGroupModal());
        }

        // Create org button
        const createOrgBtn = document.getElementById('createOrgBtn');
        if (createOrgBtn && !createOrgBtn._handlerAttached) {
            createOrgBtn._handlerAttached = true;
            createOrgBtn.addEventListener('click', () => {
                Components.showToast('Organization creation via UI only (simulated). On GitLab.com, top-level groups can only be created through the UI.', 'info');
            });
        }

        // Reset data
        const resetDataBtn = document.getElementById('resetDataBtn');
        if (resetDataBtn && !resetDataBtn._handlerAttached) {
            resetDataBtn._handlerAttached = true;
            resetDataBtn.addEventListener('click', () => {
                Components.confirm(
                    'Reset all data?',
                    'This will discard all your changes and restore the original seed data. This cannot be undone.',
                    () => {
                        AppState.resetToSeedData();
                        Components.showToast('All data has been reset to defaults', 'success');
                        Router.navigate('/');
                    },
                    { danger: true, confirmLabel: 'Reset data' }
                );
            });
        }

        // Save group settings
        const saveGroupSettings = document.getElementById('saveGroupSettingsBtn');
        if (saveGroupSettings && !saveGroupSettings._handlerAttached) {
            saveGroupSettings._handlerAttached = true;
            saveGroupSettings.addEventListener('click', () => {
                const groupId = parseInt(AppState.currentRoute.split('/').pop());
                const group = AppState.getGroupById(groupId);
                if (!group) return;

                const name = document.getElementById('groupName')?.value.trim();
                const path = document.getElementById('groupPath')?.value.trim();
                const desc = document.getElementById('groupDesc')?.value.trim();
                const vis = document.getElementById('groupVisibility')?.getAttribute('data-value');
                const subCreate = document.getElementById('subgroupCreation')?.getAttribute('data-value');
                const projCreate = document.getElementById('projectCreation')?.getAttribute('data-value');
                const branchProt = document.getElementById('branchProtection')?.getAttribute('data-value');
                const userCapVal = document.getElementById('userCap')?.value.trim();
                const preventInv = document.getElementById('preventInvitations')?.checked;
                const preventShare = document.getElementById('preventSharingOutside')?.checked;
                const disableMentions = document.getElementById('disableMentions')?.checked;
                const require2FA = document.getElementById('requireTwoFactor')?.checked;

                // Validate name
                const nameErrors = AppState.validateName(name);
                if (nameErrors.length > 0) {
                    Components.showToast(nameErrors[0], 'error');
                    return;
                }

                AppState.updateGroup(groupId, {
                    name, path,
                    description: desc,
                    visibility: vis,
                    subgroupCreationLevel: subCreate,
                    projectCreationLevel: projCreate,
                    defaultBranchProtection: branchProt,
                    userCap: userCapVal ? parseInt(userCapVal) : null,
                    preventInvitations: preventInv,
                    preventSharingOutsideHierarchy: preventShare,
                    disableMentions,
                    requireTwoFactor: require2FA
                });

                Views._rebuildGroupPaths(groupId);
                Components.showToast('Group settings saved', 'success');
                Router.refresh();
            });
        }

        // Save project settings
        const saveProjectSettings = document.getElementById('saveProjectSettingsBtn');
        if (saveProjectSettings && !saveProjectSettings._handlerAttached) {
            saveProjectSettings._handlerAttached = true;
            saveProjectSettings.addEventListener('click', () => {
                const projectId = parseInt(AppState.currentRoute.split('/').pop());
                const project = AppState.getProjectById(projectId);
                if (!project) return;

                const name = document.getElementById('projectName')?.value.trim();
                const path = document.getElementById('projectPath')?.value.trim();
                const desc = document.getElementById('projectDesc')?.value.trim();
                const vis = document.getElementById('projectVisibility')?.getAttribute('data-value');
                const topicsStr = document.getElementById('projectTopics')?.value || '';
                const topics = topicsStr.split(',').map(t => t.trim()).filter(t => t);

                const nameErrors = AppState.validateName(name, 'project');
                if (nameErrors.length > 0) {
                    Components.showToast(nameErrors[0], 'error');
                    return;
                }

                project.name = name;
                project.path = path;
                project.description = desc;
                project.visibility = vis;
                project.topics = topics;
                project.updatedAt = new Date().toISOString();

                // Rebuild path
                const group = AppState.getGroupById(project.groupId);
                if (group) project.fullPath = group.fullPath + '/' + path;

                AppState.notify();
                Components.showToast('Project settings saved', 'success');
                Router.refresh();
            });
        }

        // Save profile
        const saveProfile = document.getElementById('saveProfileBtn');
        if (saveProfile && !saveProfile._handlerAttached) {
            saveProfile._handlerAttached = true;
            saveProfile.addEventListener('click', () => {
                const user = AppState.currentUser;
                user.name = document.getElementById('profileName')?.value.trim() || user.name;
                user.pronouns = document.getElementById('profilePronouns')?.value.trim() || '';
                user.bio = document.getElementById('profileBio')?.value.trim() || '';
                user.location = document.getElementById('profileLocation')?.value.trim() || '';
                user.organization = document.getElementById('profileOrg')?.value.trim() || '';
                user.website = document.getElementById('profileWebsite')?.value.trim() || '';
                user.status = {
                    emoji: document.getElementById('statusEmoji')?.value.trim() || '',
                    message: document.getElementById('statusMessage')?.value.trim() || '',
                    busy: document.getElementById('statusBusy')?.checked || false
                };
                user.linkedin = document.getElementById('profileLinkedin')?.value.trim() || '';
                user.discord = document.getElementById('profileDiscord')?.value.trim() || '';
                user.bluesky = document.getElementById('profileBluesky')?.value.trim() || '';
                user.profileVisibility = document.getElementById('profileVisibility')?.getAttribute('data-value') || user.profileVisibility;

                // Sync to users array
                const u = AppState.getUserById(user.id);
                if (u) Object.assign(u, user);

                AppState.notify();
                Components.showToast('Profile updated', 'success');
                Router.refresh();
            });
        }

        // Change username
        const changeUsername = document.getElementById('changeUsernameBtn');
        if (changeUsername && !changeUsername._handlerAttached) {
            changeUsername._handlerAttached = true;
            changeUsername.addEventListener('click', () => {
                const newUsername = document.getElementById('accountUsername')?.value.trim();
                if (!newUsername) return;

                const errors = AppState.validateName(newUsername, 'username');
                if (errors.length > 0) {
                    Components.showToast(errors[0], 'error');
                    return;
                }

                // Check uniqueness
                const existing = AppState.users.find(u => u.username === newUsername && u.id !== AppState.currentUser.id);
                if (existing) {
                    Components.showToast('Username is already taken', 'error');
                    return;
                }

                Components.confirm(
                    'Change username?',
                    `Changing your username from "${AppState.currentUser.username}" to "${newUsername}" will change your namespace URL and create redirects. Existing links may break.`,
                    () => {
                        AppState.currentUser.username = newUsername;
                        const u = AppState.getUserById(AppState.currentUser.id);
                        if (u) u.username = newUsername;
                        Components.showToast('Username changed. URL redirects have been created.', 'success');
                        AppState.notify();
                        Router.refresh();
                    },
                    { confirmLabel: 'Change username' }
                );
            });
        }

        // Add email
        const addEmailBtn = document.getElementById('addEmailBtn');
        if (addEmailBtn && !addEmailBtn._handlerAttached) {
            addEmailBtn._handlerAttached = true;
            addEmailBtn.addEventListener('click', () => {
                const input = document.getElementById('newEmailInput');
                const email = input?.value.trim();
                if (!email) return;

                // Basic email validation
                if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                    Components.showToast('Invalid email format', 'error');
                    return;
                }

                // Check duplicates
                const allEmails = [AppState.currentUser.email, ...(AppState.currentUser.secondaryEmails || [])];
                if (allEmails.includes(email)) {
                    Components.showToast('Email already exists', 'error');
                    return;
                }

                AppState.currentUser.secondaryEmails = AppState.currentUser.secondaryEmails || [];
                AppState.currentUser.secondaryEmails.push(email);
                const u = AppState.getUserById(AppState.currentUser.id);
                if (u) u.secondaryEmails = AppState.currentUser.secondaryEmails;

                Components.showToast(`Email ${email} added. Confirmation email sent (simulated).`, 'success');
                AppState.notify();
                Router.refresh();
            });
        }
    }
};

// ---- Server API (SSE) ----
function _connectAPI() {
    const es = new EventSource('/api/events');
    let connected = false;

    es.onmessage = (event) => {
        if (event.data === 'connected') {
            connected = true;
            console.log('[API] Connected to server events');
            return;
        }
        if (event.data === 'reset') {
            console.log('[API] Reset signal received');
            AppState.resetToSeedData();
            Components.showToast('State has been reset via API', 'info');
            Router.navigate('/');
        }
    };

    es.onerror = () => {
        if (!connected) {
            // Server doesn't support SSE (e.g. plain python3 -m http.server), stop trying
            es.close();
        }
        // If previously connected, EventSource auto-reconnects
    };
}

// ---- Initialize Application ----
function initApp() {
    // Set up current user avatar
    const userAvatar = document.getElementById('currentUserAvatar');
    if (userAvatar) {
        userAvatar.innerHTML = Components.avatar(AppState.currentUser, 28);
    }

    // Set up user dropdown header
    const dropdownHeader = document.getElementById('userDropdownHeader');
    if (dropdownHeader) {
        dropdownHeader.innerHTML = `<strong>${Components.escapeHtml(AppState.currentUser.name)}</strong><br><span class="text-muted">@${Components.escapeHtml(AppState.currentUser.username)}</span>`;
    }

    // Sidebar toggle
    document.getElementById('sidebarToggle')?.addEventListener('click', () => {
        document.getElementById('sidebar').classList.toggle('collapsed');
        document.getElementById('mainContent').classList.toggle('sidebar-collapsed');
        AppState.sidebarOpen = !AppState.sidebarOpen;
    });

    // Handle browser back/forward
    window.addEventListener('popstate', (e) => {
        if (e.state?.path) {
            Router.navigate(e.state.path, true);
        } else {
            Router.navigate('/', true);
        }
    });

    // Initial route from hash
    const hash = window.location.hash.substring(1);
    if (hash) {
        Router.navigate(hash, true);
    } else {
        Router.navigate('/', true);
    }

    // Connect to server API (SSE) for remote commands
    _connectAPI();
}

// Start the app
document.addEventListener('DOMContentLoaded', initApp);
