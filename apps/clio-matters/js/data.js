const SEED_DATA_VERSION = 1;

const CURRENT_USER = {
    id: 'usr_001',
    fullName: 'Sarah Mitchell',
    email: 'sarah.mitchell@harrisonlaw.com',
    role: 'Administrator',
    avatarColor: '#4A90D9',
    firmName: 'Harrison & Associates LLP',
    timezone: 'America/New_York'
};

const FIRM_USERS = [
    { id: 'usr_001', fullName: 'Sarah Mitchell', email: 'sarah.mitchell@harrisonlaw.com', role: 'Administrator', rate: 350, avatarColor: '#4A90D9' },
    { id: 'usr_002', fullName: 'James Chen', email: 'james.chen@harrisonlaw.com', role: 'Attorney', rate: 425, avatarColor: '#E67E22' },
    { id: 'usr_003', fullName: 'Maria Garcia', email: 'maria.garcia@harrisonlaw.com', role: 'Attorney', rate: 375, avatarColor: '#27AE60' },
    { id: 'usr_004', fullName: 'David Kim', email: 'david.kim@harrisonlaw.com', role: 'Partner', rate: 550, avatarColor: '#8E44AD' },
    { id: 'usr_005', fullName: 'Rachel Thompson', email: 'rachel.thompson@harrisonlaw.com', role: 'Paralegal', rate: 175, avatarColor: '#E74C3C' },
    { id: 'usr_006', fullName: 'Michael Osei', email: 'michael.osei@harrisonlaw.com', role: 'Attorney', rate: 400, avatarColor: '#2980B9' },
    { id: 'usr_007', fullName: 'Jennifer Walsh', email: 'jennifer.walsh@harrisonlaw.com', role: 'Associate', rate: 275, avatarColor: '#16A085' },
    { id: 'usr_008', fullName: 'Robert Nakamura', email: 'robert.nakamura@harrisonlaw.com', role: 'Partner', rate: 575, avatarColor: '#D35400' },
    { id: 'usr_009', fullName: 'Lisa Patel', email: 'lisa.patel@harrisonlaw.com', role: 'Paralegal', rate: 165, avatarColor: '#C0392B' },
    { id: 'usr_010', fullName: 'Thomas Wright', email: 'thomas.wright@harrisonlaw.com', role: 'Associate', rate: 300, avatarColor: '#2C3E50' }
];

const USER_GROUPS = [
    { id: 'grp_001', name: 'Partners', members: ['usr_004', 'usr_008'] },
    { id: 'grp_002', name: 'Litigation Team', members: ['usr_002', 'usr_003', 'usr_005', 'usr_007'] },
    { id: 'grp_003', name: 'Personal Injury Unit', members: ['usr_003', 'usr_006', 'usr_009'] },
    { id: 'grp_004', name: 'Corporate Group', members: ['usr_004', 'usr_010', 'usr_001'] },
    { id: 'grp_005', name: 'All Staff', members: ['usr_001','usr_002','usr_003','usr_004','usr_005','usr_006','usr_007','usr_008','usr_009','usr_010'] }
];

const PRACTICE_AREAS = [
    { id: 'pa_001', name: 'Personal Injury', enabled: true, isPrimary: true },
    { id: 'pa_002', name: 'Criminal Law', enabled: true, isPrimary: false },
    { id: 'pa_003', name: 'Family Law', enabled: true, isPrimary: false },
    { id: 'pa_004', name: 'Real Estate', enabled: true, isPrimary: false },
    { id: 'pa_005', name: 'Corporate Law', enabled: true, isPrimary: false },
    { id: 'pa_006', name: 'Employment Law', enabled: true, isPrimary: false },
    { id: 'pa_007', name: 'Immigration', enabled: true, isPrimary: false },
    { id: 'pa_008', name: 'Intellectual Property', enabled: true, isPrimary: false },
    { id: 'pa_009', name: 'Estate Planning', enabled: true, isPrimary: false },
    { id: 'pa_010', name: 'Bankruptcy', enabled: true, isPrimary: false },
    { id: 'pa_011', name: 'Tax Law', enabled: true, isPrimary: false },
    { id: 'pa_012', name: 'Medical Malpractice', enabled: true, isPrimary: false },
    { id: 'pa_013', name: 'Insurance Defense', enabled: false, isPrimary: false },
    { id: 'pa_014', name: 'Workers Compensation', enabled: true, isPrimary: false }
];

const MATTER_STAGES = {
    'pa_001': [
        { id: 'stg_pi_01', name: 'Initial Consultation', order: 0 },
        { id: 'stg_pi_02', name: 'Investigation', order: 1 },
        { id: 'stg_pi_03', name: 'Demand Letter', order: 2 },
        { id: 'stg_pi_04', name: 'Negotiation', order: 3 },
        { id: 'stg_pi_05', name: 'Litigation Filed', order: 4 },
        { id: 'stg_pi_06', name: 'Discovery', order: 5 },
        { id: 'stg_pi_07', name: 'Mediation', order: 6 },
        { id: 'stg_pi_08', name: 'Settlement/Trial', order: 7 }
    ],
    'pa_002': [
        { id: 'stg_cr_01', name: 'Arraignment', order: 0 },
        { id: 'stg_cr_02', name: 'Pre-Trial', order: 1 },
        { id: 'stg_cr_03', name: 'Trial', order: 2 },
        { id: 'stg_cr_04', name: 'Sentencing', order: 3 }
    ],
    'pa_003': [
        { id: 'stg_fl_01', name: 'Initial Filing', order: 0 },
        { id: 'stg_fl_02', name: 'Discovery', order: 1 },
        { id: 'stg_fl_03', name: 'Mediation', order: 2 },
        { id: 'stg_fl_04', name: 'Trial/Hearing', order: 3 },
        { id: 'stg_fl_05', name: 'Final Order', order: 4 }
    ],
    'pa_005': [
        { id: 'stg_co_01', name: 'Engagement', order: 0 },
        { id: 'stg_co_02', name: 'Due Diligence', order: 1 },
        { id: 'stg_co_03', name: 'Negotiation', order: 2 },
        { id: 'stg_co_04', name: 'Closing', order: 3 }
    ],
    'pa_004': [
        { id: 'stg_re_01', name: 'Contract Review', order: 0 },
        { id: 'stg_re_02', name: 'Title Search', order: 1 },
        { id: 'stg_re_03', name: 'Closing', order: 2 }
    ]
};

const CONTACTS = [
    { id: 'con_001', type: 'person', firstName: 'Angela', lastName: 'Rodriguez', email: 'angela.rodriguez@gmail.com', phone: '(555) 234-5678', address: '142 Oak Lane, Springfield, IL 62704', tags: ['client', 'personal-injury'], createdAt: '2024-09-15T10:30:00Z' },
    { id: 'con_002', type: 'person', firstName: 'Marcus', lastName: 'Williams', email: 'mwilliams@outlook.com', phone: '(555) 345-6789', address: '88 Pine Street, Chicago, IL 60601', tags: ['client'], createdAt: '2024-06-22T14:00:00Z' },
    { id: 'con_003', type: 'company', firstName: '', lastName: 'TechNova Solutions Inc.', email: 'legal@technova.com', phone: '(555) 456-7890', address: '2200 Innovation Blvd, Suite 400, Austin, TX 78701', tags: ['corporate-client'], createdAt: '2024-03-10T09:00:00Z' },
    { id: 'con_004', type: 'person', firstName: 'Diana', lastName: 'Foster', email: 'diana.foster@yahoo.com', phone: '(555) 567-8901', address: '67 Maple Drive, Evanston, IL 60201', tags: ['client', 'personal-injury'], createdAt: '2024-11-03T11:15:00Z' },
    { id: 'con_005', type: 'person', firstName: 'Kevin', lastName: 'Okafor', email: 'kokafor@protonmail.com', phone: '(555) 678-9012', address: '301 River Road, Naperville, IL 60540', tags: ['client', 'criminal'], createdAt: '2025-01-08T16:30:00Z' },
    { id: 'con_006', type: 'company', firstName: '', lastName: 'Midwest Manufacturing Group', email: 'admin@midwestmfg.com', phone: '(555) 789-0123', address: '1500 Industrial Pkwy, Gary, IN 46402', tags: ['corporate-client', 'employment'], createdAt: '2024-07-19T08:45:00Z' },
    { id: 'con_007', type: 'person', firstName: 'Patricia', lastName: 'Nguyen', email: 'pnguyen@gmail.com', phone: '(555) 890-1234', address: '445 Cherry Blossom Way, Schaumburg, IL 60173', tags: ['client', 'family'], createdAt: '2024-12-05T13:20:00Z' },
    { id: 'con_008', type: 'person', firstName: 'Robert', lastName: 'Singh', email: 'rsingh.law@hotmail.com', phone: '(555) 901-2345', address: '22 Lakeshore Drive, Highland Park, IL 60035', tags: ['client', 'estate'], createdAt: '2024-08-30T10:00:00Z' },
    { id: 'con_009', type: 'person', firstName: 'Samantha', lastName: 'Cruz', email: 'scruz@icloud.com', phone: '(555) 012-3456', address: '789 Elm Street, Oak Park, IL 60302', tags: ['client', 'personal-injury'], createdAt: '2025-02-01T09:30:00Z' },
    { id: 'con_010', type: 'company', firstName: '', lastName: 'GlobalTrade Logistics LLC', email: 'contracts@globaltrade.com', phone: '(555) 111-2222', address: '4000 Commerce Center Dr, Rosemont, IL 60018', tags: ['corporate-client'], createdAt: '2024-05-12T11:00:00Z' },
    { id: 'con_011', type: 'person', firstName: 'Thomas', lastName: 'Baker', email: 'tbaker@live.com', phone: '(555) 222-3333', address: '156 Birch Avenue, Joliet, IL 60432', tags: ['client', 'real-estate'], createdAt: '2024-10-18T15:45:00Z' },
    { id: 'con_012', type: 'person', firstName: 'Laura', lastName: 'Mendez', email: 'lmendez@gmail.com', phone: '(555) 333-4444', address: '903 Sunset Blvd, Peoria, IL 61602', tags: ['client', 'immigration'], createdAt: '2025-01-20T08:15:00Z' },
    { id: 'con_013', type: 'person', firstName: 'Richard', lastName: 'O\'Brien', email: 'robrien@comcast.net', phone: '(555) 444-5555', address: '47 Park Place, Wilmette, IL 60091', tags: ['client', 'personal-injury'], createdAt: '2024-04-02T10:30:00Z' },
    { id: 'con_014', type: 'company', firstName: '', lastName: 'Lakeside Insurance Co.', email: 'claims@lakesideins.com', phone: '(555) 555-6666', address: '600 Financial Dr, Chicago, IL 60603', tags: ['insurance', 'opposing'], createdAt: '2024-01-15T09:00:00Z' },
    { id: 'con_015', type: 'company', firstName: '', lastName: 'Premier Auto Dealers', email: 'legal@premierauto.com', phone: '(555) 666-7777', address: '2300 Motor Way, Schaumburg, IL 60173', tags: ['opposing-party'], createdAt: '2024-03-20T14:00:00Z' },
    { id: 'con_016', type: 'person', firstName: 'Janet', lastName: 'Liu', email: 'jliu@gmail.com', phone: '(555) 777-8888', address: '112 Garden St, Skokie, IL 60077', tags: ['related-contact', 'spouse'], createdAt: '2024-09-15T10:30:00Z' },
    { id: 'con_017', type: 'person', firstName: 'Gregory', lastName: 'Foster', email: 'gfoster@outlook.com', phone: '(555) 888-9999', address: '67 Maple Drive, Evanston, IL 60201', tags: ['related-contact', 'spouse'], createdAt: '2024-11-03T11:15:00Z' },
    { id: 'con_018', type: 'company', firstName: '', lastName: 'Northwestern Memorial Hospital', email: 'records@nm.org', phone: '(555) 100-2000', address: '251 E Huron St, Chicago, IL 60611', tags: ['medical-provider'], createdAt: '2023-06-01T09:00:00Z' },
    { id: 'con_019', type: 'company', firstName: '', lastName: 'Chicago Physical Therapy Center', email: 'billing@chicagopt.com', phone: '(555) 200-3000', address: '340 N Michigan Ave, Chicago, IL 60601', tags: ['medical-provider'], createdAt: '2023-09-15T10:00:00Z' },
    { id: 'con_020', type: 'company', firstName: '', lastName: 'Advanced Imaging Associates', email: 'admin@advancedimaging.com', phone: '(555) 300-4000', address: '1800 Dempster St, Evanston, IL 60201', tags: ['medical-provider'], createdAt: '2024-01-10T11:00:00Z' },
    { id: 'con_021', type: 'person', firstName: 'Dr. Amanda', lastName: 'Reeves', email: 'areeves@orthoclinic.com', phone: '(555) 400-5000', address: '500 Green Bay Rd, Winnetka, IL 60093', tags: ['medical-provider', 'specialist'], createdAt: '2024-02-20T09:30:00Z' },
    { id: 'con_022', type: 'person', firstName: 'Carlos', lastName: 'Espinoza', email: 'cespinoza@lawfirm.com', phone: '(555) 500-6000', address: '100 W Monroe St, Chicago, IL 60603', tags: ['co-counsel', 'referral'], createdAt: '2024-04-05T14:00:00Z' },
    { id: 'con_023', type: 'company', firstName: '', lastName: 'State Farm Insurance', email: 'claims@statefarm.com', phone: '(555) 600-7000', address: '1 State Farm Plaza, Bloomington, IL 61710', tags: ['insurance', 'payer'], createdAt: '2023-01-01T09:00:00Z' },
    { id: 'con_024', type: 'company', firstName: '', lastName: 'Blue Cross Blue Shield of IL', email: 'medical@bcbsil.com', phone: '(555) 700-8000', address: '300 E Randolph St, Chicago, IL 60601', tags: ['insurance', 'payer', 'health'], createdAt: '2023-03-01T09:00:00Z' },
    { id: 'con_025', type: 'person', firstName: 'William', lastName: 'Harris', email: 'wharris@gmail.com', phone: '(555) 800-9000', address: '2100 Ridge Ave, Evanston, IL 60201', tags: ['client', 'personal-injury'], createdAt: '2025-02-14T11:00:00Z' },
    { id: 'con_026', type: 'person', firstName: 'Emily', lastName: 'Kowalski', email: 'ekowalski@yahoo.com', phone: '(555) 900-1111', address: '445 Lincoln Ave, Winnetka, IL 60093', tags: ['client', 'workers-comp'], createdAt: '2024-12-20T10:45:00Z' },
    { id: 'con_027', type: 'person', firstName: 'Daniel', lastName: 'Morales', email: 'dmorales@outlook.com', phone: '(555) 111-0000', address: '78 W Washington St, Chicago, IL 60602', tags: ['client', 'criminal'], createdAt: '2025-01-05T15:00:00Z' },
    { id: 'con_028', type: 'company', firstName: '', lastName: 'Riverside Community Credit Union', email: 'legal@riversidecu.org', phone: '(555) 121-3131', address: '800 Ogden Ave, Naperville, IL 60540', tags: ['lien-holder'], createdAt: '2024-06-01T09:00:00Z' }
];

const CUSTOM_FIELD_DEFINITIONS = [
    { id: 'cf_001', name: 'Case Type', fieldType: 'dropdown', options: ['Auto Accident', 'Slip and Fall', 'Medical Malpractice', 'Product Liability', 'Workplace Injury', 'Dog Bite', 'Premises Liability'], fieldSet: 'Personal Injury Details' },
    { id: 'cf_002', name: 'Incident Date', fieldType: 'date', fieldSet: 'Personal Injury Details' },
    { id: 'cf_003', name: 'Statute of Limitations', fieldType: 'date', fieldSet: 'Personal Injury Details' },
    { id: 'cf_004', name: 'Police Report Number', fieldType: 'text', fieldSet: 'Personal Injury Details' },
    { id: 'cf_005', name: 'Opposing Counsel', fieldType: 'text', fieldSet: 'Litigation Details' },
    { id: 'cf_006', name: 'Court Case Number', fieldType: 'text', fieldSet: 'Litigation Details' },
    { id: 'cf_007', name: 'Judge Assigned', fieldType: 'text', fieldSet: 'Litigation Details' },
    { id: 'cf_008', name: 'Next Court Date', fieldType: 'date', fieldSet: 'Litigation Details' },
    { id: 'cf_009', name: 'Insurance Claim Number', fieldType: 'text', fieldSet: 'Insurance Info' },
    { id: 'cf_010', name: 'Policy Limit', fieldType: 'currency', fieldSet: 'Insurance Info' },
    { id: 'cf_011', name: 'Adjuster Name', fieldType: 'text', fieldSet: 'Insurance Info' },
    { id: 'cf_012', name: 'Referral Source', fieldType: 'dropdown', options: ['Website', 'Google', 'Word of Mouth', 'Attorney Referral', 'Advertisement', 'Social Media', 'Bar Association'], fieldSet: null }
];

const TASK_LISTS = [
    { id: 'tl_001', name: 'New PI Case Intake', tasks: ['Send engagement letter', 'Collect medical authorizations', 'File insurance claim', 'Order police report', 'Schedule initial medical evaluation'] },
    { id: 'tl_002', name: 'Litigation Preparation', tasks: ['Draft complaint', 'File with court', 'Serve defendant', 'Prepare discovery requests', 'Schedule depositions'] },
    { id: 'tl_003', name: 'Settlement Preparation', tasks: ['Compile medical records', 'Calculate damages', 'Draft demand letter', 'Review settlement offer', 'Prepare settlement statement'] },
    { id: 'tl_004', name: 'Case Closing', tasks: ['Final billing review', 'Archive documents', 'Send closing letter to client', 'Update matter status', 'Return original documents'] },
    { id: 'tl_005', name: 'Corporate Transaction', tasks: ['Draft LOI', 'Conduct due diligence', 'Negotiate terms', 'Prepare closing documents', 'File regulatory notices'] }
];

const DOCUMENT_CATEGORIES = [
    'Pleadings', 'Correspondence', 'Discovery', 'Medical Records', 'Financial Records',
    'Contracts', 'Court Orders', 'Evidence', 'Research', 'Administrative', 'Billing',
    'Client Communications', 'Insurance Documents'
];

const CURRENCIES = ['USD', 'CAD', 'EUR', 'GBP', 'AUD'];

const LOCATIONS = [
    'Cook County Circuit Court', 'DuPage County Circuit Court', 'Lake County Circuit Court',
    'Kane County Circuit Court', 'Will County Circuit Court', 'Northern District of Illinois',
    'Central District of Illinois', 'Springfield', 'Chicago', 'Rockford'
];

const DAMAGE_TYPES = [
    { category: 'Special', types: ['Medical Expenses', 'Lost Wages', 'Future Medical Costs', 'Loss of Earning Capacity', 'Property Damage', 'Out-of-Pocket Expenses', 'Rehabilitation Costs'] },
    { category: 'General', types: ['Pain and Suffering', 'Emotional Distress', 'Loss of Consortium', 'Loss of Quality of Life', 'Disfigurement', 'Disability'] },
    { category: 'Other', types: ['Punitive Damages', 'Nominal Damages', 'Aggravated Damages'] }
];

const EXPENSE_CATEGORIES = [
    'Filing Fees', 'Court Reporter', 'Expert Witness', 'Medical Records', 'Travel',
    'Copying/Printing', 'Postage', 'Service of Process', 'Investigation', 'Deposition',
    'Mediation Fees', 'Transcripts', 'Research/Westlaw', 'Miscellaneous'
];

const MATTER_TEMPLATES = [
    {
        id: 'tmpl_001', name: 'Personal Injury - Auto Accident', isDefault: true,
        practiceAreaId: 'pa_001', status: 'Open', billingMethod: 'contingency',
        description: 'Auto accident personal injury case',
        responsibleAttorneyId: 'usr_003', originatingAttorneyId: null, responsibleStaffId: 'usr_009',
        location: 'Cook County Circuit Court',
        isBillable: true, contingencyRate: 33.33, contingencyRecipientId: 'usr_003',
        deductionOrder: 'fees_first',
        taskLists: ['tl_001'],
        documentFolders: [
            { name: 'Medical Records', category: 'Medical Records' },
            { name: 'Correspondence', category: 'Correspondence' },
            { name: 'Pleadings', category: 'Pleadings' },
            { name: 'Insurance Documents', category: 'Insurance Documents' }
        ],
        customFields: [
            { definitionId: 'cf_001', value: '' },
            { definitionId: 'cf_002', value: '' },
            { definitionId: 'cf_003', value: '' },
            { definitionId: 'cf_004', value: '' },
            { definitionId: 'cf_009', value: '' },
            { definitionId: 'cf_010', value: '' },
            { definitionId: 'cf_011', value: '' }
        ],
        createdAt: '2024-06-15T10:00:00Z', updatedAt: '2025-01-10T14:30:00Z'
    },
    {
        id: 'tmpl_002', name: 'Criminal Defense - Misdemeanor', isDefault: false,
        practiceAreaId: 'pa_002', status: 'Open', billingMethod: 'hourly',
        description: 'Criminal defense for misdemeanor charges',
        responsibleAttorneyId: 'usr_002', originatingAttorneyId: null, responsibleStaffId: 'usr_005',
        location: 'Cook County Circuit Court',
        isBillable: true, contingencyRate: null, contingencyRecipientId: null,
        deductionOrder: 'fees_first',
        taskLists: ['tl_002'],
        documentFolders: [
            { name: 'Court Filings', category: 'Pleadings' },
            { name: 'Evidence', category: 'Evidence' },
            { name: 'Client Communications', category: 'Client Communications' }
        ],
        customFields: [
            { definitionId: 'cf_005', value: '' },
            { definitionId: 'cf_006', value: '' },
            { definitionId: 'cf_007', value: '' },
            { definitionId: 'cf_008', value: '' }
        ],
        createdAt: '2024-08-01T09:00:00Z', updatedAt: '2024-12-05T11:00:00Z'
    },
    {
        id: 'tmpl_003', name: 'Family Law - Divorce', isDefault: false,
        practiceAreaId: 'pa_003', status: 'Open', billingMethod: 'hourly',
        description: 'Divorce proceedings',
        responsibleAttorneyId: 'usr_006', originatingAttorneyId: null, responsibleStaffId: null,
        location: 'Cook County Circuit Court',
        isBillable: true, contingencyRate: null, contingencyRecipientId: null,
        deductionOrder: 'fees_first',
        taskLists: [],
        documentFolders: [
            { name: 'Financial Disclosures', category: 'Financial Records' },
            { name: 'Court Orders', category: 'Court Orders' },
            { name: 'Correspondence', category: 'Correspondence' }
        ],
        customFields: [],
        createdAt: '2024-09-20T08:00:00Z', updatedAt: '2024-09-20T08:00:00Z'
    },
    {
        id: 'tmpl_004', name: 'Corporate Transaction - M&A', isDefault: false,
        practiceAreaId: 'pa_005', status: 'Open', billingMethod: 'hourly',
        description: 'Merger and acquisition transaction',
        responsibleAttorneyId: 'usr_004', originatingAttorneyId: 'usr_008', responsibleStaffId: 'usr_010',
        location: '',
        isBillable: true, contingencyRate: null, contingencyRecipientId: null,
        deductionOrder: 'fees_first',
        taskLists: ['tl_005'],
        documentFolders: [
            { name: 'Due Diligence', category: 'Contracts' },
            { name: 'Transaction Documents', category: 'Contracts' },
            { name: 'Regulatory Filings', category: 'Administrative' }
        ],
        customFields: [],
        createdAt: '2024-10-01T10:00:00Z', updatedAt: '2024-10-01T10:00:00Z'
    },
    {
        id: 'tmpl_005', name: 'Flat Fee - Simple Will', isDefault: false,
        practiceAreaId: 'pa_009', status: 'Open', billingMethod: 'flat_rate',
        description: 'Simple will preparation',
        responsibleAttorneyId: 'usr_006', originatingAttorneyId: null, responsibleStaffId: null,
        location: '',
        isBillable: true, flatFeeAmount: 1500, flatFeeRecipientId: 'usr_006',
        contingencyRate: null, contingencyRecipientId: null,
        deductionOrder: 'fees_first',
        taskLists: [],
        documentFolders: [
            { name: 'Estate Documents', category: 'Contracts' }
        ],
        customFields: [],
        createdAt: '2025-01-15T09:00:00Z', updatedAt: '2025-01-15T09:00:00Z'
    }
];

const NUMBERING_SCHEME = {
    template: 'preset1',
    fields: ['matterNumber', 'clientSummaryName'],
    separator: '-',
    nextMatterNumber: 147,
    updateByDefault: false
};

const MATTERS = [
    {
        id: 'mat_001', matterNumber: '00089', displayNumber: '00089-Rodriguez',
        description: 'Rodriguez v. Premier Auto - Auto Accident',
        clientId: 'con_001', contactName: 'Angela Rodriguez',
        status: 'Open', practiceAreaId: 'pa_001', matterStageId: 'stg_pi_06',
        responsibleAttorneyId: 'usr_003', originatingAttorneyId: 'usr_006',
        responsibleStaffId: 'usr_009', clientRefNumber: 'REF-2024-0089',
        location: 'Cook County Circuit Court',
        openDate: '2024-09-20T00:00:00Z', pendingDate: null, closedDate: null, createdAt: '2024-09-20T10:00:00Z', updatedAt: '2026-02-28T09:15:00Z',
        permissions: { type: 'everyone' },
        blockedUsers: [],
        billingPreference: {
            isBillable: true, billingMethod: 'contingency', currency: 'USD',
            contingencyRate: 33.33, contingencyRecipientId: 'usr_003',
            flatFeeAmount: null, flatFeeRecipientId: null,
            customRates: [], budget: 50000, budgetNotifyUsers: ['usr_003'],
            trustMinBalance: 5000, trustNotifyUsers: ['usr_003', 'usr_009']
        },
        deductionOrder: 'fees_first',
        relatedContacts: [
            { contactId: 'con_016', relationship: 'Spouse', isBillRecipient: false },
            { contactId: 'con_015', relationship: 'Defendant', isBillRecipient: false }
        ],
        notifications: [
            { userId: 'usr_003', types: ['matter_updated', 'matter_deleted', 'budget_threshold', 'trust_low'] },
            { userId: 'usr_009', types: ['matter_updated', 'trust_low'] }
        ],
        customFields: [
            { definitionId: 'cf_001', value: 'Auto Accident' },
            { definitionId: 'cf_002', value: '2024-08-15' },
            { definitionId: 'cf_003', value: '2026-08-15' },
            { definitionId: 'cf_004', value: 'CPD-2024-08-78432' },
            { definitionId: 'cf_009', value: 'CLM-2024-889342' },
            { definitionId: 'cf_010', value: 250000 },
            { definitionId: 'cf_011', value: 'Mark Stevens' },
            { definitionId: 'cf_012', value: 'Attorney Referral' }
        ],
        taskLists: ['tl_001', 'tl_003'],
        documentFolders: ['Medical Records', 'Correspondence', 'Pleadings', 'Insurance Documents', 'Discovery'],
        reports: { useFirmSettings: false, originatingAllocation: 15, responsibleAllocation: 85 },
        templateId: 'tmpl_001',
        financials: {
            workInProgress: 12450.00, outstandingBalance: 0, trustFunds: 8500.00,
            totalTime: 42500.00, totalExpenses: 3200.00
        },
        timeline: [
            { id: 'tl_ev_001', action: 'created', timestamp: '2024-09-20T10:00:00Z', userId: 'usr_003', details: 'Matter created' },
            { id: 'tl_ev_002', action: 'stage_changed', timestamp: '2024-10-05T14:30:00Z', userId: 'usr_003', details: 'Stage changed from Initial Consultation to Investigation' },
            { id: 'tl_ev_003', action: 'stage_changed', timestamp: '2024-11-15T09:00:00Z', userId: 'usr_003', details: 'Stage changed from Investigation to Demand Letter' },
            { id: 'tl_ev_004', action: 'edited', timestamp: '2024-12-01T11:20:00Z', userId: 'usr_009', details: 'Added custom fields for insurance info' },
            { id: 'tl_ev_005', action: 'stage_changed', timestamp: '2025-01-10T16:45:00Z', userId: 'usr_003', details: 'Stage changed from Demand Letter to Negotiation' },
            { id: 'tl_ev_006', action: 'stage_changed', timestamp: '2025-02-20T10:30:00Z', userId: 'usr_003', details: 'Stage changed from Negotiation to Litigation Filed' },
            { id: 'tl_ev_007', action: 'stage_changed', timestamp: '2025-06-10T14:00:00Z', userId: 'usr_003', details: 'Stage changed from Litigation Filed to Discovery' },
            { id: 'tl_ev_008', action: 'edited', timestamp: '2026-02-28T09:15:00Z', userId: 'usr_003', details: 'Updated budget and trust balance' }
        ],
        damages: [
            { id: 'dmg_001', description: 'Emergency Room Visit', type: 'Medical Expenses', category: 'Special', amount: 15800.00, createdAt: '2024-10-01T09:00:00Z', createdBy: 'usr_009' },
            { id: 'dmg_002', description: 'Orthopedic Surgery', type: 'Medical Expenses', category: 'Special', amount: 78500.00, createdAt: '2024-12-15T14:00:00Z', createdBy: 'usr_009' },
            { id: 'dmg_003', description: 'Physical Therapy (24 sessions)', type: 'Medical Expenses', category: 'Special', amount: 12000.00, createdAt: '2025-03-01T10:30:00Z', createdBy: 'usr_009' },
            { id: 'dmg_004', description: 'Lost wages - 14 weeks', type: 'Lost Wages', category: 'Special', amount: 42000.00, createdAt: '2025-01-15T11:00:00Z', createdBy: 'usr_003' },
            { id: 'dmg_005', description: 'Future medical care estimate', type: 'Future Medical Costs', category: 'Special', amount: 35000.00, createdAt: '2025-06-01T09:00:00Z', createdBy: 'usr_003' },
            { id: 'dmg_006', description: 'Vehicle repair costs', type: 'Property Damage', category: 'Special', amount: 18200.00, createdAt: '2024-10-05T13:00:00Z', createdBy: 'usr_009' },
            { id: 'dmg_007', description: 'Pain and suffering from chronic back injury', type: 'Pain and Suffering', category: 'General', amount: 150000.00, createdAt: '2025-06-15T10:00:00Z', createdBy: 'usr_003' },
            { id: 'dmg_008', description: 'Emotional distress and PTSD', type: 'Emotional Distress', category: 'General', amount: 50000.00, createdAt: '2025-06-15T10:15:00Z', createdBy: 'usr_003' },
            { id: 'dmg_009', description: 'Loss of quality of life', type: 'Loss of Quality of Life', category: 'General', amount: 75000.00, createdAt: '2025-06-15T10:30:00Z', createdBy: 'usr_003' }
        ],
        medicalProviders: [
            {
                id: 'mp_001', contactId: 'con_018', description: 'Emergency treatment and initial surgery',
                treatmentFirstDate: '2024-08-15', treatmentLastDate: '2024-08-20', treatmentComplete: true,
                recordRequestDate: '2024-09-25', recordFollowUpDate: '2024-10-25', recordStatus: 'Received',
                billRequestDate: '2024-09-25', billFollowUpDate: '2024-10-25', billStatus: 'Received',
                medicalRecords: [
                    { id: 'mr_001', fileName: 'ER_Admission_Report.pdf', receivedDate: '2024-10-20', startDate: '2024-08-15', endDate: '2024-08-15', comments: [
                        { id: 'cmt_001', text: 'Confirms L4-L5 disc herniation', userId: 'usr_009', timestamp: '2024-10-21T09:00:00Z' }
                    ]},
                    { id: 'mr_002', fileName: 'Surgical_Report_Lumbar.pdf', receivedDate: '2024-10-22', startDate: '2024-08-18', endDate: '2024-08-20', comments: [] }
                ],
                medicalBills: [
                    { id: 'mb_001', fileName: 'NM_Hospital_Bill.pdf', billDate: '2024-09-01', receivedDate: '2024-10-20', billAmount: 45000.00, adjustment: 5000.00, payers: [
                        { payerId: 'con_024', amountPaid: 28000.00, isLien: false }
                    ], balanceOwed: 12000.00, balanceIsLien: true, balanceIsOutstanding: false, comments: [] }
                ]
            },
            {
                id: 'mp_002', contactId: 'con_019', description: 'Post-surgical rehabilitation',
                treatmentFirstDate: '2024-09-15', treatmentLastDate: '2025-03-15', treatmentComplete: true,
                recordRequestDate: '2025-04-01', recordFollowUpDate: '2025-05-01', recordStatus: 'Received',
                billRequestDate: '2025-04-01', billFollowUpDate: '2025-05-01', billStatus: 'Received',
                medicalRecords: [
                    { id: 'mr_003', fileName: 'PT_Progress_Notes.pdf', receivedDate: '2025-04-20', startDate: '2024-09-15', endDate: '2025-03-15', comments: [
                        { id: 'cmt_002', text: 'Shows significant improvement over 6 months', userId: 'usr_003', timestamp: '2025-04-22T14:00:00Z' },
                        { id: 'cmt_003', text: 'Recommend using for demand package', userId: 'usr_009', timestamp: '2025-04-23T09:30:00Z' }
                    ]}
                ],
                medicalBills: [
                    { id: 'mb_002', fileName: 'CPTC_Bill_Full.pdf', billDate: '2025-03-20', receivedDate: '2025-04-18', billAmount: 12000.00, adjustment: 0, payers: [
                        { payerId: 'con_024', amountPaid: 7200.00, isLien: false }
                    ], balanceOwed: 4800.00, balanceIsLien: false, balanceIsOutstanding: true, comments: [] }
                ]
            },
            {
                id: 'mp_003', contactId: 'con_020', description: 'MRI and diagnostic imaging',
                treatmentFirstDate: '2024-08-16', treatmentLastDate: '2025-01-10', treatmentComplete: true,
                recordRequestDate: '2025-02-01', recordFollowUpDate: null, recordStatus: 'Received',
                billRequestDate: '2025-02-01', billFollowUpDate: '2025-03-01', billStatus: 'Incomplete',
                medicalRecords: [
                    { id: 'mr_004', fileName: 'MRI_Lumbar_Spine.pdf', receivedDate: '2025-02-15', startDate: '2024-08-16', endDate: '2024-08-16', comments: [] },
                    { id: 'mr_005', fileName: 'Follow_Up_MRI.pdf', receivedDate: '2025-02-20', startDate: '2025-01-10', endDate: '2025-01-10', comments: [
                        { id: 'cmt_004', text: 'Shows post-surgical changes, no new pathology', userId: 'usr_009', timestamp: '2025-02-21T11:00:00Z' }
                    ]}
                ],
                medicalBills: [
                    { id: 'mb_003', fileName: 'AIA_Invoice_Aug.pdf', billDate: '2024-09-15', receivedDate: '2025-02-18', billAmount: 3500.00, adjustment: 500.00, payers: [], balanceOwed: 3000.00, balanceIsLien: false, balanceIsOutstanding: true, comments: [] }
                ]
            },
            {
                id: 'mp_004', contactId: 'con_021', description: 'Orthopedic specialist - ongoing evaluation',
                treatmentFirstDate: '2024-09-01', treatmentLastDate: null, treatmentComplete: false,
                recordRequestDate: '2025-06-01', recordFollowUpDate: '2025-07-01', recordStatus: 'Requested',
                billRequestDate: null, billFollowUpDate: null, billStatus: 'Not yet requested',
                medicalRecords: [],
                medicalBills: []
            }
        ],
        settlement: {
            recoveries: [
                { id: 'rec_001', sourceContactId: 'con_014', amount: 175000.00, createdAt: '2025-11-01T10:00:00Z' },
                { id: 'rec_002', sourceContactId: 'con_015', amount: 85000.00, createdAt: '2025-11-15T14:00:00Z' }
            ],
            legalFees: [
                { id: 'lf_001', recoveryId: 'rec_001', recipientId: 'usr_003', rate: 33.33, discount: 0, referralFees: [
                    { recipientId: 'con_022', rate: 10 }
                ], createdAt: '2025-11-01T10:00:00Z' },
                { id: 'lf_002', recoveryId: 'rec_002', recipientId: 'usr_003', rate: 33.33, discount: 5, referralFees: [], createdAt: '2025-11-15T14:00:00Z' }
            ],
            otherLiens: [
                { id: 'ol_001', lienHolderId: 'con_028', description: 'Personal loan against settlement', amount: 5000.00, reduction: 0, createdAt: '2025-11-20T09:00:00Z' }
            ],
            outstandingBalances: [
                { id: 'ob_001', responsibleParty: 'client', balanceHolderId: 'con_028', description: 'Credit card balance', balanceOwing: 3200.00, reduction: 0, createdAt: '2025-11-20T09:30:00Z' }
            ],
            expenses: [
                { category: 'Filing Fees', amount: 450.00 },
                { category: 'Court Reporter', amount: 1800.00 },
                { category: 'Expert Witness', amount: 5500.00 },
                { category: 'Medical Records', amount: 350.00 },
                { category: 'Service of Process', amount: 200.00 }
            ]
        }
    },
    {
        id: 'mat_002', matterNumber: '00102', displayNumber: '00102-Foster',
        description: 'Foster v. City of Evanston - Slip and Fall',
        clientId: 'con_004', contactName: 'Diana Foster',
        status: 'Open', practiceAreaId: 'pa_001', matterStageId: 'stg_pi_04',
        responsibleAttorneyId: 'usr_006', originatingAttorneyId: 'usr_003',
        responsibleStaffId: 'usr_005', clientRefNumber: 'REF-2024-0102',
        location: 'Cook County Circuit Court',
        openDate: '2024-11-10T00:00:00Z', pendingDate: null, closedDate: null, createdAt: '2024-11-10T11:00:00Z', updatedAt: '2026-01-15T16:00:00Z',
        permissions: { type: 'specific', usersAndGroups: ['usr_006', 'usr_003', 'usr_005', 'grp_003'] },
        blockedUsers: ['usr_010'],
        billingPreference: {
            isBillable: true, billingMethod: 'contingency', currency: 'USD',
            contingencyRate: 40, contingencyRecipientId: 'usr_006',
            flatFeeAmount: null, flatFeeRecipientId: null,
            customRates: [], budget: null, budgetNotifyUsers: [],
            trustMinBalance: null, trustNotifyUsers: []
        },
        deductionOrder: 'expenses_first',
        relatedContacts: [
            { contactId: 'con_017', relationship: 'Spouse', isBillRecipient: true }
        ],
        notifications: [
            { userId: 'usr_006', types: ['matter_updated', 'matter_deleted'] }
        ],
        customFields: [
            { definitionId: 'cf_001', value: 'Slip and Fall' },
            { definitionId: 'cf_002', value: '2024-10-22' },
            { definitionId: 'cf_003', value: '2026-10-22' }
        ],
        taskLists: ['tl_001'],
        documentFolders: ['Medical Records', 'Correspondence', 'Insurance Documents'],
        reports: { useFirmSettings: true, originatingAllocation: 0, responsibleAllocation: 0 },
        templateId: null,
        financials: {
            workInProgress: 5200.00, outstandingBalance: 0, trustFunds: 0,
            totalTime: 18700.00, totalExpenses: 1100.00
        },
        timeline: [
            { id: 'tl_ev_010', action: 'created', timestamp: '2024-11-10T11:00:00Z', userId: 'usr_006', details: 'Matter created' },
            { id: 'tl_ev_011', action: 'stage_changed', timestamp: '2024-12-01T10:00:00Z', userId: 'usr_006', details: 'Stage changed from Initial Consultation to Investigation' },
            { id: 'tl_ev_012', action: 'stage_changed', timestamp: '2025-03-15T14:00:00Z', userId: 'usr_006', details: 'Stage changed from Investigation to Demand Letter' },
            { id: 'tl_ev_013', action: 'stage_changed', timestamp: '2025-07-01T09:30:00Z', userId: 'usr_006', details: 'Stage changed from Demand Letter to Negotiation' }
        ],
        damages: [
            { id: 'dmg_010', description: 'Fractured wrist treatment', type: 'Medical Expenses', category: 'Special', amount: 22000.00, createdAt: '2024-12-01T10:00:00Z', createdBy: 'usr_005' },
            { id: 'dmg_011', description: 'Lost wages - 6 weeks', type: 'Lost Wages', category: 'Special', amount: 15000.00, createdAt: '2025-01-10T09:00:00Z', createdBy: 'usr_005' },
            { id: 'dmg_012', description: 'Pain and suffering', type: 'Pain and Suffering', category: 'General', amount: 60000.00, createdAt: '2025-06-01T11:00:00Z', createdBy: 'usr_006' }
        ],
        medicalProviders: [
            {
                id: 'mp_010', contactId: 'con_018', description: 'Emergency wrist surgery',
                treatmentFirstDate: '2024-10-22', treatmentLastDate: '2024-10-24', treatmentComplete: true,
                recordRequestDate: '2024-11-15', recordFollowUpDate: null, recordStatus: 'Received',
                billRequestDate: '2024-11-15', billFollowUpDate: null, billStatus: 'Received',
                medicalRecords: [
                    { id: 'mr_010', fileName: 'ER_Report_Wrist.pdf', receivedDate: '2024-12-01', startDate: '2024-10-22', endDate: '2024-10-24', comments: [] }
                ],
                medicalBills: [
                    { id: 'mb_010', fileName: 'NM_Wrist_Bill.pdf', billDate: '2024-11-15', receivedDate: '2024-12-05', billAmount: 22000.00, adjustment: 2000.00, payers: [
                        { payerId: 'con_023', amountPaid: 14000.00, isLien: false }
                    ], balanceOwed: 6000.00, balanceIsLien: false, balanceIsOutstanding: true, comments: [] }
                ]
            }
        ],
        settlement: { recoveries: [], legalFees: [], otherLiens: [], outstandingBalances: [], expenses: [] }
    },
    {
        id: 'mat_003', matterNumber: '00078', displayNumber: '00078-TechNova',
        description: 'TechNova Solutions - Series B Financing',
        clientId: 'con_003', contactName: 'TechNova Solutions Inc.',
        status: 'Open', practiceAreaId: 'pa_005', matterStageId: 'stg_co_02',
        responsibleAttorneyId: 'usr_004', originatingAttorneyId: 'usr_008',
        responsibleStaffId: 'usr_010', clientRefNumber: 'CORP-2024-0078',
        location: '',
        openDate: '2024-03-15T00:00:00Z', pendingDate: null, closedDate: null, createdAt: '2024-03-15T14:00:00Z', updatedAt: '2026-02-01T10:00:00Z',
        permissions: { type: 'specific', usersAndGroups: ['grp_004'] },
        blockedUsers: [],
        billingPreference: {
            isBillable: true, billingMethod: 'hourly', currency: 'USD',
            contingencyRate: null, contingencyRecipientId: null,
            flatFeeAmount: null, flatFeeRecipientId: null,
            customRates: [
                { userId: 'usr_004', rate: 600 },
                { userId: 'usr_010', rate: 325 }
            ],
            budget: 150000, budgetNotifyUsers: ['usr_004', 'usr_008'],
            trustMinBalance: null, trustNotifyUsers: []
        },
        deductionOrder: 'fees_first',
        relatedContacts: [],
        notifications: [
            { userId: 'usr_004', types: ['matter_updated', 'budget_threshold'] },
            { userId: 'usr_008', types: ['matter_updated', 'budget_threshold'] }
        ],
        customFields: [],
        taskLists: ['tl_005'],
        documentFolders: ['Due Diligence', 'Transaction Documents', 'Regulatory Filings'],
        reports: { useFirmSettings: true, originatingAllocation: 0, responsibleAllocation: 0 },
        templateId: 'tmpl_004',
        financials: {
            workInProgress: 35200.00, outstandingBalance: 22500.00, trustFunds: 50000.00,
            totalTime: 128500.00, totalExpenses: 8900.00
        },
        timeline: [
            { id: 'tl_ev_020', action: 'created', timestamp: '2024-03-15T14:00:00Z', userId: 'usr_004', details: 'Matter created' },
            { id: 'tl_ev_021', action: 'stage_changed', timestamp: '2024-05-01T09:00:00Z', userId: 'usr_004', details: 'Stage changed from Engagement to Due Diligence' }
        ],
        damages: [],
        medicalProviders: [],
        settlement: { recoveries: [], legalFees: [], otherLiens: [], outstandingBalances: [], expenses: [] }
    },
    {
        id: 'mat_004', matterNumber: '00115', displayNumber: '00115-Okafor',
        description: 'State v. Okafor - DUI Defense',
        clientId: 'con_005', contactName: 'Kevin Okafor',
        status: 'Open', practiceAreaId: 'pa_002', matterStageId: 'stg_cr_02',
        responsibleAttorneyId: 'usr_002', originatingAttorneyId: 'usr_002',
        responsibleStaffId: 'usr_005', clientRefNumber: '',
        location: 'Cook County Circuit Court',
        openDate: '2025-01-10T00:00:00Z', pendingDate: null, closedDate: null, createdAt: '2025-01-10T16:30:00Z', updatedAt: '2026-02-20T11:00:00Z',
        permissions: { type: 'specific', usersAndGroups: ['usr_002', 'usr_005', 'grp_002'] },
        blockedUsers: [],
        billingPreference: {
            isBillable: true, billingMethod: 'hourly', currency: 'USD',
            contingencyRate: null, contingencyRecipientId: null,
            flatFeeAmount: null, flatFeeRecipientId: null,
            customRates: [], budget: 25000, budgetNotifyUsers: ['usr_002'],
            trustMinBalance: 2000, trustNotifyUsers: ['usr_002']
        },
        deductionOrder: 'fees_first',
        relatedContacts: [],
        notifications: [
            { userId: 'usr_002', types: ['matter_updated', 'matter_deleted', 'budget_threshold', 'trust_low'] }
        ],
        customFields: [
            { definitionId: 'cf_005', value: 'Andrew Lawton, Esq.' },
            { definitionId: 'cf_006', value: '2025-CR-004521' },
            { definitionId: 'cf_007', value: 'Hon. Patricia Donovan' },
            { definitionId: 'cf_008', value: '2026-04-15' }
        ],
        taskLists: ['tl_002'],
        documentFolders: ['Court Filings', 'Evidence', 'Client Communications'],
        reports: { useFirmSettings: true, originatingAllocation: 0, responsibleAllocation: 0 },
        templateId: 'tmpl_002',
        financials: {
            workInProgress: 8300.00, outstandingBalance: 4250.00, trustFunds: 7500.00,
            totalTime: 22800.00, totalExpenses: 650.00
        },
        timeline: [
            { id: 'tl_ev_030', action: 'created', timestamp: '2025-01-10T16:30:00Z', userId: 'usr_002', details: 'Matter created' },
            { id: 'tl_ev_031', action: 'stage_changed', timestamp: '2025-02-15T10:00:00Z', userId: 'usr_002', details: 'Stage changed from Arraignment to Pre-Trial' }
        ],
        damages: [],
        medicalProviders: [],
        settlement: { recoveries: [], legalFees: [], otherLiens: [], outstandingBalances: [], expenses: [] }
    },
    {
        id: 'mat_005', matterNumber: '00098', displayNumber: '00098-Nguyen',
        description: 'Nguyen - Divorce Proceedings',
        clientId: 'con_007', contactName: 'Patricia Nguyen',
        status: 'Pending', practiceAreaId: 'pa_003', matterStageId: 'stg_fl_03',
        responsibleAttorneyId: 'usr_006', originatingAttorneyId: 'usr_001',
        responsibleStaffId: null, clientRefNumber: '',
        location: 'DuPage County Circuit Court',
        openDate: '2024-12-10T00:00:00Z', pendingDate: '2026-01-15T00:00:00Z', closedDate: null, createdAt: '2024-12-10T13:20:00Z', updatedAt: '2026-01-15T16:00:00Z',
        permissions: { type: 'specific', usersAndGroups: ['usr_006', 'usr_001'] },
        blockedUsers: ['usr_007', 'usr_010'],
        billingPreference: {
            isBillable: true, billingMethod: 'hourly', currency: 'USD',
            contingencyRate: null, contingencyRecipientId: null,
            flatFeeAmount: null, flatFeeRecipientId: null,
            customRates: [{ userId: 'usr_006', rate: 375 }],
            budget: null, budgetNotifyUsers: [],
            trustMinBalance: null, trustNotifyUsers: []
        },
        deductionOrder: 'fees_first',
        relatedContacts: [],
        notifications: [],
        customFields: [],
        taskLists: [],
        documentFolders: ['Financial Disclosures', 'Court Orders', 'Correspondence'],
        reports: { useFirmSettings: true, originatingAllocation: 0, responsibleAllocation: 0 },
        templateId: null,
        financials: {
            workInProgress: 2100.00, outstandingBalance: 6800.00, trustFunds: 3000.00,
            totalTime: 31200.00, totalExpenses: 1500.00
        },
        timeline: [
            { id: 'tl_ev_040', action: 'created', timestamp: '2024-12-10T13:20:00Z', userId: 'usr_006', details: 'Matter created' },
            { id: 'tl_ev_041', action: 'status_changed', timestamp: '2026-01-15T16:00:00Z', userId: 'usr_006', details: 'Status changed from Open to Pending' }
        ],
        damages: [],
        medicalProviders: [],
        settlement: { recoveries: [], legalFees: [], otherLiens: [], outstandingBalances: [], expenses: [] }
    },
    {
        id: 'mat_006', matterNumber: '00065', displayNumber: '00065-MidwestMfg',
        description: 'Midwest Manufacturing - Employment Discrimination Claim',
        clientId: 'con_006', contactName: 'Midwest Manufacturing Group',
        status: 'Closed', practiceAreaId: 'pa_006', matterStageId: null,
        responsibleAttorneyId: 'usr_004', originatingAttorneyId: 'usr_004',
        responsibleStaffId: 'usr_009', clientRefNumber: 'EMP-2024-065',
        location: 'Northern District of Illinois',
        openDate: '2024-07-20T00:00:00Z', pendingDate: null, closedDate: '2025-12-18T00:00:00Z', createdAt: '2024-07-20T08:45:00Z', updatedAt: '2025-12-18T17:00:00Z',
        permissions: { type: 'everyone' },
        blockedUsers: [],
        billingPreference: {
            isBillable: true, billingMethod: 'hourly', currency: 'USD',
            contingencyRate: null, contingencyRecipientId: null,
            flatFeeAmount: null, flatFeeRecipientId: null,
            customRates: [], budget: 75000, budgetNotifyUsers: ['usr_004'],
            trustMinBalance: null, trustNotifyUsers: []
        },
        deductionOrder: 'fees_first',
        relatedContacts: [],
        notifications: [],
        customFields: [],
        taskLists: [],
        documentFolders: ['Pleadings', 'Discovery', 'Correspondence'],
        reports: { useFirmSettings: true, originatingAllocation: 0, responsibleAllocation: 0 },
        templateId: null,
        financials: {
            workInProgress: 0, outstandingBalance: 0, trustFunds: 0,
            totalTime: 68400.00, totalExpenses: 4200.00
        },
        timeline: [
            { id: 'tl_ev_050', action: 'created', timestamp: '2024-07-20T08:45:00Z', userId: 'usr_004', details: 'Matter created' },
            { id: 'tl_ev_051', action: 'status_changed', timestamp: '2025-12-18T17:00:00Z', userId: 'usr_004', details: 'Status changed from Open to Closed' }
        ],
        damages: [],
        medicalProviders: [],
        settlement: { recoveries: [], legalFees: [], otherLiens: [], outstandingBalances: [], expenses: [] }
    },
    {
        id: 'mat_007', matterNumber: '00125', displayNumber: '00125-Singh',
        description: 'Singh Family Trust & Estate Plan',
        clientId: 'con_008', contactName: 'Robert Singh',
        status: 'Open', practiceAreaId: 'pa_009', matterStageId: null,
        responsibleAttorneyId: 'usr_006', originatingAttorneyId: 'usr_008',
        responsibleStaffId: null, clientRefNumber: 'EST-2024-125',
        location: '',
        openDate: '2024-08-30T00:00:00Z', pendingDate: null, closedDate: null, createdAt: '2024-08-30T10:00:00Z', updatedAt: '2026-01-05T09:00:00Z',
        permissions: { type: 'everyone' },
        blockedUsers: [],
        billingPreference: {
            isBillable: true, billingMethod: 'flat_rate', currency: 'USD',
            contingencyRate: null, contingencyRecipientId: null,
            flatFeeAmount: 4500, flatFeeRecipientId: 'usr_006',
            customRates: [], budget: null, budgetNotifyUsers: [],
            trustMinBalance: null, trustNotifyUsers: []
        },
        deductionOrder: 'fees_first',
        relatedContacts: [],
        notifications: [],
        customFields: [],
        taskLists: [],
        documentFolders: ['Estate Documents'],
        reports: { useFirmSettings: true, originatingAllocation: 0, responsibleAllocation: 0 },
        templateId: 'tmpl_005',
        financials: {
            workInProgress: 0, outstandingBalance: 4500.00, trustFunds: 0,
            totalTime: 4500.00, totalExpenses: 150.00
        },
        timeline: [
            { id: 'tl_ev_060', action: 'created', timestamp: '2024-08-30T10:00:00Z', userId: 'usr_006', details: 'Matter created' }
        ],
        damages: [],
        medicalProviders: [],
        settlement: { recoveries: [], legalFees: [], otherLiens: [], outstandingBalances: [], expenses: [] }
    },
    {
        id: 'mat_008', matterNumber: '00130', displayNumber: '00130-Cruz',
        description: 'Cruz v. Metro Transit - Bus Accident',
        clientId: 'con_009', contactName: 'Samantha Cruz',
        status: 'Open', practiceAreaId: 'pa_001', matterStageId: 'stg_pi_03',
        responsibleAttorneyId: 'usr_003', originatingAttorneyId: 'usr_001',
        responsibleStaffId: 'usr_009', clientRefNumber: 'REF-2025-0130',
        location: 'Cook County Circuit Court',
        openDate: '2025-02-05T00:00:00Z', pendingDate: null, closedDate: null, createdAt: '2025-02-05T09:30:00Z', updatedAt: '2026-03-01T10:00:00Z',
        permissions: { type: 'everyone' },
        blockedUsers: [],
        billingPreference: {
            isBillable: true, billingMethod: 'contingency', currency: 'USD',
            contingencyRate: 33.33, contingencyRecipientId: 'usr_003',
            flatFeeAmount: null, flatFeeRecipientId: null,
            customRates: [], budget: null, budgetNotifyUsers: [],
            trustMinBalance: null, trustNotifyUsers: []
        },
        deductionOrder: 'fees_first',
        relatedContacts: [],
        notifications: [
            { userId: 'usr_003', types: ['matter_updated'] },
            { userId: 'usr_001', types: ['matter_updated'] }
        ],
        customFields: [
            { definitionId: 'cf_001', value: 'Auto Accident' },
            { definitionId: 'cf_002', value: '2025-01-18' },
            { definitionId: 'cf_003', value: '2027-01-18' }
        ],
        taskLists: ['tl_001'],
        documentFolders: ['Medical Records', 'Correspondence', 'Pleadings', 'Insurance Documents'],
        reports: { useFirmSettings: true, originatingAllocation: 0, responsibleAllocation: 0 },
        templateId: 'tmpl_001',
        financials: {
            workInProgress: 3800.00, outstandingBalance: 0, trustFunds: 0,
            totalTime: 9500.00, totalExpenses: 400.00
        },
        timeline: [
            { id: 'tl_ev_070', action: 'created', timestamp: '2025-02-05T09:30:00Z', userId: 'usr_003', details: 'Matter created' },
            { id: 'tl_ev_071', action: 'stage_changed', timestamp: '2025-04-01T11:00:00Z', userId: 'usr_003', details: 'Stage changed from Initial Consultation to Investigation' },
            { id: 'tl_ev_072', action: 'stage_changed', timestamp: '2025-08-15T09:00:00Z', userId: 'usr_003', details: 'Stage changed from Investigation to Demand Letter' }
        ],
        damages: [
            { id: 'dmg_020', description: 'Whiplash treatment', type: 'Medical Expenses', category: 'Special', amount: 8500.00, createdAt: '2025-03-15T10:00:00Z', createdBy: 'usr_009' },
            { id: 'dmg_021', description: 'Lost wages - 3 weeks', type: 'Lost Wages', category: 'Special', amount: 6200.00, createdAt: '2025-04-01T09:00:00Z', createdBy: 'usr_009' },
            { id: 'dmg_022', description: 'Pain and suffering', type: 'Pain and Suffering', category: 'General', amount: 30000.00, createdAt: '2025-06-01T14:00:00Z', createdBy: 'usr_003' }
        ],
        medicalProviders: [
            {
                id: 'mp_020', contactId: 'con_018', description: 'Initial emergency treatment',
                treatmentFirstDate: '2025-01-18', treatmentLastDate: '2025-01-19', treatmentComplete: true,
                recordRequestDate: '2025-02-10', recordFollowUpDate: '2025-03-10', recordStatus: 'Received',
                billRequestDate: '2025-02-10', billFollowUpDate: null, billStatus: 'Received',
                medicalRecords: [
                    { id: 'mr_020', fileName: 'ER_Report_Cruz.pdf', receivedDate: '2025-03-05', startDate: '2025-01-18', endDate: '2025-01-19', comments: [] }
                ],
                medicalBills: [
                    { id: 'mb_020', fileName: 'NM_Cruz_Bill.pdf', billDate: '2025-02-15', receivedDate: '2025-03-10', billAmount: 8500.00, adjustment: 0, payers: [], balanceOwed: 8500.00, balanceIsLien: false, balanceIsOutstanding: true, comments: [] }
                ]
            }
        ],
        settlement: { recoveries: [], legalFees: [], otherLiens: [], outstandingBalances: [], expenses: [] }
    },
    {
        id: 'mat_009', matterNumber: '00071', displayNumber: '00071-GlobalTrade',
        description: 'GlobalTrade Logistics - Import/Export Compliance',
        clientId: 'con_010', contactName: 'GlobalTrade Logistics LLC',
        status: 'Closed', practiceAreaId: 'pa_005', matterStageId: 'stg_co_04',
        responsibleAttorneyId: 'usr_008', originatingAttorneyId: 'usr_004',
        responsibleStaffId: 'usr_001', clientRefNumber: 'CORP-2024-0071',
        location: '',
        openDate: '2024-05-15T00:00:00Z', pendingDate: '2025-08-01T00:00:00Z', closedDate: '2025-09-30T00:00:00Z', createdAt: '2024-05-15T11:00:00Z', updatedAt: '2025-09-30T16:00:00Z',
        permissions: { type: 'everyone' },
        blockedUsers: [],
        billingPreference: {
            isBillable: true, billingMethod: 'hourly', currency: 'USD',
            contingencyRate: null, contingencyRecipientId: null,
            flatFeeAmount: null, flatFeeRecipientId: null,
            customRates: [], budget: 100000, budgetNotifyUsers: ['usr_008'],
            trustMinBalance: null, trustNotifyUsers: []
        },
        deductionOrder: 'fees_first',
        relatedContacts: [],
        notifications: [],
        customFields: [],
        taskLists: [],
        documentFolders: ['Contracts', 'Regulatory Filings', 'Correspondence'],
        reports: { useFirmSettings: true, originatingAllocation: 0, responsibleAllocation: 0 },
        templateId: null,
        financials: {
            workInProgress: 0, outstandingBalance: 0, trustFunds: 0,
            totalTime: 87600.00, totalExpenses: 3500.00
        },
        timeline: [
            { id: 'tl_ev_080', action: 'created', timestamp: '2024-05-15T11:00:00Z', userId: 'usr_008', details: 'Matter created' },
            { id: 'tl_ev_081', action: 'status_changed', timestamp: '2025-08-01T10:00:00Z', userId: 'usr_008', details: 'Status changed from Open to Pending' },
            { id: 'tl_ev_082', action: 'status_changed', timestamp: '2025-09-30T16:00:00Z', userId: 'usr_008', details: 'Status changed from Pending to Closed' }
        ],
        damages: [],
        medicalProviders: [],
        settlement: { recoveries: [], legalFees: [], otherLiens: [], outstandingBalances: [], expenses: [] }
    },
    {
        id: 'mat_010', matterNumber: '00110', displayNumber: '00110-Baker',
        description: 'Baker - Residential Property Purchase',
        clientId: 'con_011', contactName: 'Thomas Baker',
        status: 'Open', practiceAreaId: 'pa_004', matterStageId: 'stg_re_02',
        responsibleAttorneyId: 'usr_007', originatingAttorneyId: 'usr_001',
        responsibleStaffId: null, clientRefNumber: 'RE-2024-0110',
        location: 'DuPage County Circuit Court',
        openDate: '2024-10-20T00:00:00Z', pendingDate: null, closedDate: null, createdAt: '2024-10-20T15:45:00Z', updatedAt: '2026-02-10T14:00:00Z',
        permissions: { type: 'everyone' },
        blockedUsers: [],
        billingPreference: {
            isBillable: true, billingMethod: 'flat_rate', currency: 'USD',
            contingencyRate: null, contingencyRecipientId: null,
            flatFeeAmount: 3500, flatFeeRecipientId: 'usr_007',
            customRates: [], budget: null, budgetNotifyUsers: [],
            trustMinBalance: null, trustNotifyUsers: []
        },
        deductionOrder: 'fees_first',
        relatedContacts: [],
        notifications: [],
        customFields: [],
        taskLists: [],
        documentFolders: ['Contracts', 'Correspondence'],
        reports: { useFirmSettings: true, originatingAllocation: 0, responsibleAllocation: 0 },
        templateId: null,
        financials: {
            workInProgress: 0, outstandingBalance: 3500.00, trustFunds: 0,
            totalTime: 3500.00, totalExpenses: 200.00
        },
        timeline: [
            { id: 'tl_ev_090', action: 'created', timestamp: '2024-10-20T15:45:00Z', userId: 'usr_007', details: 'Matter created' },
            { id: 'tl_ev_091', action: 'stage_changed', timestamp: '2025-01-15T10:00:00Z', userId: 'usr_007', details: 'Stage changed from Contract Review to Title Search' }
        ],
        damages: [],
        medicalProviders: [],
        settlement: { recoveries: [], legalFees: [], otherLiens: [], outstandingBalances: [], expenses: [] }
    },
    {
        id: 'mat_011', matterNumber: '00118', displayNumber: '00118-Mendez',
        description: 'Mendez - Work Visa Application',
        clientId: 'con_012', contactName: 'Laura Mendez',
        status: 'Open', practiceAreaId: 'pa_007', matterStageId: null,
        responsibleAttorneyId: 'usr_006', originatingAttorneyId: 'usr_006',
        responsibleStaffId: 'usr_005', clientRefNumber: 'IMM-2025-0118',
        location: '',
        openDate: '2025-01-22T00:00:00Z', pendingDate: null, closedDate: null, createdAt: '2025-01-22T08:15:00Z', updatedAt: '2026-02-28T11:00:00Z',
        permissions: { type: 'everyone' },
        blockedUsers: [],
        billingPreference: {
            isBillable: true, billingMethod: 'hourly', currency: 'USD',
            contingencyRate: null, contingencyRecipientId: null,
            flatFeeAmount: null, flatFeeRecipientId: null,
            customRates: [], budget: 10000, budgetNotifyUsers: [],
            trustMinBalance: null, trustNotifyUsers: []
        },
        deductionOrder: 'fees_first',
        relatedContacts: [],
        notifications: [],
        customFields: [{ definitionId: 'cf_012', value: 'Word of Mouth' }],
        taskLists: [],
        documentFolders: ['Administrative', 'Correspondence'],
        reports: { useFirmSettings: true, originatingAllocation: 0, responsibleAllocation: 0 },
        templateId: null,
        financials: {
            workInProgress: 1200.00, outstandingBalance: 0, trustFunds: 2500.00,
            totalTime: 6800.00, totalExpenses: 800.00
        },
        timeline: [
            { id: 'tl_ev_100', action: 'created', timestamp: '2025-01-22T08:15:00Z', userId: 'usr_006', details: 'Matter created' }
        ],
        damages: [],
        medicalProviders: [],
        settlement: { recoveries: [], legalFees: [], otherLiens: [], outstandingBalances: [], expenses: [] }
    },
    {
        id: 'mat_012', matterNumber: '00055', displayNumber: '00055-OBrien',
        description: 'O\'Brien v. Lakeside Insurance - Bad Faith Claim',
        clientId: 'con_013', contactName: 'Richard O\'Brien',
        status: 'Closed', practiceAreaId: 'pa_001', matterStageId: 'stg_pi_08',
        responsibleAttorneyId: 'usr_003', originatingAttorneyId: 'usr_003',
        responsibleStaffId: 'usr_009', clientRefNumber: 'REF-2024-0055',
        location: 'Northern District of Illinois',
        openDate: '2024-04-05T00:00:00Z', pendingDate: null, closedDate: '2025-10-20T00:00:00Z', createdAt: '2024-04-05T10:30:00Z', updatedAt: '2025-10-20T15:00:00Z',
        permissions: { type: 'everyone' },
        blockedUsers: [],
        billingPreference: {
            isBillable: true, billingMethod: 'contingency', currency: 'USD',
            contingencyRate: 33.33, contingencyRecipientId: 'usr_003',
            flatFeeAmount: null, flatFeeRecipientId: null,
            customRates: [], budget: null, budgetNotifyUsers: [],
            trustMinBalance: null, trustNotifyUsers: []
        },
        deductionOrder: 'fees_first',
        relatedContacts: [],
        notifications: [],
        customFields: [
            { definitionId: 'cf_001', value: 'Auto Accident' },
            { definitionId: 'cf_002', value: '2024-02-10' },
            { definitionId: 'cf_009', value: 'CLM-2024-551029' }
        ],
        taskLists: [],
        documentFolders: ['Medical Records', 'Correspondence', 'Pleadings', 'Insurance Documents'],
        reports: { useFirmSettings: false, originatingAllocation: 50, responsibleAllocation: 50 },
        templateId: null,
        financials: {
            workInProgress: 0, outstandingBalance: 0, trustFunds: 0,
            totalTime: 55000.00, totalExpenses: 6800.00
        },
        timeline: [
            { id: 'tl_ev_110', action: 'created', timestamp: '2024-04-05T10:30:00Z', userId: 'usr_003', details: 'Matter created' },
            { id: 'tl_ev_111', action: 'status_changed', timestamp: '2025-10-20T15:00:00Z', userId: 'usr_003', details: 'Status changed from Open to Closed' }
        ],
        damages: [],
        medicalProviders: [],
        settlement: {
            recoveries: [
                { id: 'rec_010', sourceContactId: 'con_014', amount: 320000.00, createdAt: '2025-09-15T10:00:00Z' }
            ],
            legalFees: [
                { id: 'lf_010', recoveryId: 'rec_010', recipientId: 'usr_003', rate: 33.33, discount: 0, referralFees: [], createdAt: '2025-09-15T10:00:00Z' }
            ],
            otherLiens: [],
            outstandingBalances: [],
            expenses: [
                { category: 'Filing Fees', amount: 350.00 },
                { category: 'Expert Witness', amount: 4000.00 },
                { category: 'Medical Records', amount: 250.00 },
                { category: 'Deposition', amount: 2200.00 }
            ]
        }
    },
    {
        id: 'mat_013', matterNumber: '00138', displayNumber: '00138-Harris',
        description: 'Harris v. ABC Construction - Workplace Injury',
        clientId: 'con_025', contactName: 'William Harris',
        status: 'Open', practiceAreaId: 'pa_001', matterStageId: 'stg_pi_02',
        responsibleAttorneyId: 'usr_006', originatingAttorneyId: 'usr_003',
        responsibleStaffId: 'usr_009', clientRefNumber: 'REF-2025-0138',
        location: 'Lake County Circuit Court',
        openDate: '2025-02-15T00:00:00Z', pendingDate: null, closedDate: null, createdAt: '2025-02-15T11:00:00Z', updatedAt: '2026-02-25T10:00:00Z',
        permissions: { type: 'everyone' },
        blockedUsers: [],
        billingPreference: {
            isBillable: true, billingMethod: 'contingency', currency: 'USD',
            contingencyRate: 33.33, contingencyRecipientId: 'usr_006',
            flatFeeAmount: null, flatFeeRecipientId: null,
            customRates: [], budget: null, budgetNotifyUsers: [],
            trustMinBalance: null, trustNotifyUsers: []
        },
        deductionOrder: 'fees_first',
        relatedContacts: [],
        notifications: [
            { userId: 'usr_006', types: ['matter_updated'] }
        ],
        customFields: [
            { definitionId: 'cf_001', value: 'Workplace Injury' },
            { definitionId: 'cf_002', value: '2025-01-28' },
            { definitionId: 'cf_003', value: '2027-01-28' }
        ],
        taskLists: ['tl_001'],
        documentFolders: ['Medical Records', 'Correspondence', 'Insurance Documents'],
        reports: { useFirmSettings: true, originatingAllocation: 0, responsibleAllocation: 0 },
        templateId: 'tmpl_001',
        financials: {
            workInProgress: 2100.00, outstandingBalance: 0, trustFunds: 0,
            totalTime: 4200.00, totalExpenses: 200.00
        },
        timeline: [
            { id: 'tl_ev_120', action: 'created', timestamp: '2025-02-15T11:00:00Z', userId: 'usr_006', details: 'Matter created' },
            { id: 'tl_ev_121', action: 'stage_changed', timestamp: '2025-04-01T09:00:00Z', userId: 'usr_006', details: 'Stage changed from Initial Consultation to Investigation' }
        ],
        damages: [
            { id: 'dmg_030', description: 'Hand surgery', type: 'Medical Expenses', category: 'Special', amount: 35000.00, createdAt: '2025-03-10T10:00:00Z', createdBy: 'usr_009' },
            { id: 'dmg_031', description: 'Lost wages - ongoing', type: 'Lost Wages', category: 'Special', amount: 28000.00, createdAt: '2025-04-15T09:00:00Z', createdBy: 'usr_009' }
        ],
        medicalProviders: [
            {
                id: 'mp_030', contactId: 'con_018', description: 'Emergency hand surgery',
                treatmentFirstDate: '2025-01-28', treatmentLastDate: '2025-02-02', treatmentComplete: true,
                recordRequestDate: '2025-02-20', recordFollowUpDate: '2025-03-20', recordStatus: 'Received',
                billRequestDate: '2025-02-20', billFollowUpDate: '2025-03-20', billStatus: 'Not yet requested',
                medicalRecords: [],
                medicalBills: []
            }
        ],
        settlement: { recoveries: [], legalFees: [], otherLiens: [], outstandingBalances: [], expenses: [] }
    },
    {
        id: 'mat_014', matterNumber: '00140', displayNumber: '00140-Kowalski',
        description: 'Kowalski - Workers Compensation Claim',
        clientId: 'con_026', contactName: 'Emily Kowalski',
        status: 'Open', practiceAreaId: 'pa_014', matterStageId: null,
        responsibleAttorneyId: 'usr_002', originatingAttorneyId: 'usr_001',
        responsibleStaffId: 'usr_005', clientRefNumber: 'WC-2024-0140',
        location: 'Illinois Workers Compensation Commission',
        openDate: '2024-12-22T00:00:00Z', pendingDate: null, closedDate: null, createdAt: '2024-12-22T10:45:00Z', updatedAt: '2026-02-15T09:00:00Z',
        permissions: { type: 'everyone' },
        blockedUsers: [],
        billingPreference: {
            isBillable: true, billingMethod: 'contingency', currency: 'USD',
            contingencyRate: 20, contingencyRecipientId: 'usr_002',
            flatFeeAmount: null, flatFeeRecipientId: null,
            customRates: [], budget: null, budgetNotifyUsers: [],
            trustMinBalance: null, trustNotifyUsers: []
        },
        deductionOrder: 'expenses_first',
        relatedContacts: [],
        notifications: [],
        customFields: [],
        taskLists: [],
        documentFolders: ['Medical Records', 'Administrative'],
        reports: { useFirmSettings: true, originatingAllocation: 0, responsibleAllocation: 0 },
        templateId: null,
        financials: {
            workInProgress: 950.00, outstandingBalance: 0, trustFunds: 0,
            totalTime: 3800.00, totalExpenses: 350.00
        },
        timeline: [
            { id: 'tl_ev_130', action: 'created', timestamp: '2024-12-22T10:45:00Z', userId: 'usr_002', details: 'Matter created' }
        ],
        damages: [],
        medicalProviders: [],
        settlement: { recoveries: [], legalFees: [], otherLiens: [], outstandingBalances: [], expenses: [] }
    },
    {
        id: 'mat_015', matterNumber: '00142', displayNumber: '00142-Morales',
        description: 'State v. Morales - Assault Charge',
        clientId: 'con_027', contactName: 'Daniel Morales',
        status: 'Open', practiceAreaId: 'pa_002', matterStageId: 'stg_cr_01',
        responsibleAttorneyId: 'usr_002', originatingAttorneyId: 'usr_002',
        responsibleStaffId: 'usr_005', clientRefNumber: '',
        location: 'Cook County Circuit Court',
        openDate: '2025-01-08T00:00:00Z', pendingDate: null, closedDate: null, createdAt: '2025-01-08T15:00:00Z', updatedAt: '2026-03-01T14:00:00Z',
        permissions: { type: 'specific', usersAndGroups: ['usr_002', 'usr_005'] },
        blockedUsers: [],
        billingPreference: {
            isBillable: true, billingMethod: 'hourly', currency: 'USD',
            contingencyRate: null, contingencyRecipientId: null,
            flatFeeAmount: null, flatFeeRecipientId: null,
            customRates: [], budget: 15000, budgetNotifyUsers: ['usr_002'],
            trustMinBalance: 1000, trustNotifyUsers: ['usr_002']
        },
        deductionOrder: 'fees_first',
        relatedContacts: [],
        notifications: [
            { userId: 'usr_002', types: ['matter_updated', 'budget_threshold', 'trust_low'] }
        ],
        customFields: [
            { definitionId: 'cf_006', value: '2025-CR-001203' },
            { definitionId: 'cf_007', value: 'Hon. Michael Torres' },
            { definitionId: 'cf_008', value: '2026-05-20' }
        ],
        taskLists: ['tl_002'],
        documentFolders: ['Court Filings', 'Evidence', 'Client Communications'],
        reports: { useFirmSettings: true, originatingAllocation: 0, responsibleAllocation: 0 },
        templateId: 'tmpl_002',
        financials: {
            workInProgress: 4100.00, outstandingBalance: 2800.00, trustFunds: 5000.00,
            totalTime: 11200.00, totalExpenses: 450.00
        },
        timeline: [
            { id: 'tl_ev_140', action: 'created', timestamp: '2025-01-08T15:00:00Z', userId: 'usr_002', details: 'Matter created' }
        ],
        damages: [],
        medicalProviders: [],
        settlement: { recoveries: [], legalFees: [], otherLiens: [], outstandingBalances: [], expenses: [] }
    }
];

const DELETED_MATTERS = [
    {
        id: 'mat_del_001', matterNumber: '00042', displayNumber: '00042-TestClient',
        description: 'Test Client - Initial Consultation',
        clientId: 'con_002', contactName: 'Marcus Williams',
        deletedAt: '2025-06-15T10:00:00Z', deletedBy: 'usr_001',
        canRecover: true
    }
];
