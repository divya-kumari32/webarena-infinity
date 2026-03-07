# Clio Manage - Matters

A faithful replica of the Matters module from Clio Manage, a legal practice management platform. This single-page application lets law firms create, organize, track, and settle legal matters with full support for personal injury workflows, medical records management, and settlement calculations.

## Main Sections / Pages

### 1. Matters List (default view)
- Filterable table of all matters with columns: checkbox, number, description, client, practice area, status, responsible attorney, stage, actions
- Quick filters: All, Open, Pending, Closed
- Keyword search across matter number, description, and client name
- Sortable columns (click header to sort asc/desc)
- Bulk actions bar: change status or delete multiple selected matters
- Row-level context menu (three-dot icon): duplicate, delete, change status

### 2. Matter Detail (click any matter)
- Header with matter number, description, status badge, back button, and actions menu
- Four tabs: Dashboard, Damages, Medical Records, Settlement

#### Dashboard Tab
- **Financial cards**: Outstanding balance, trust balance, budget utilization
- **Matter details**: Inline-editable status dropdown, stage dropdown, practice area, billing method, responsible/originating attorney, responsible staff, client reference, location, open/close dates
- **Contacts section**: Primary client card with email, phone, address (copy button)
- **Related contacts**: Cards for opposing party, opposing counsel, insurance contacts with name, relationship, contact details
- **Custom fields**: Field set groups with text, number, date, dropdown, boolean, multi-select values
- **Activity timeline**: Chronological list of events (created, status changes, edits, comments, provider additions) with timestamps and user avatars

#### Damages Tab
- **Summary cards**: Total claimed, economic damages, non-economic damages, total medical bills
- Filterable/searchable damages table with description, type, category, amount
- Add/edit/delete damages via modal forms

#### Medical Records Tab
- **Provider cards**: Each medical provider shown as an expandable card with:
  - Provider name, description, treatment date range, treatment completion status
  - Record request status with dates (requested, follow-up)
  - Bill request status with dates (requested, follow-up)
  - Records table: file name, received date, date range, comments count
  - Bills table: file name, bill date, amount, adjustment, payers, balance owed, comments count
- Add/edit/delete providers, records, and bills via modal forms
- Comment system on records and bills (view, add, edit, delete comments)

#### Settlement Tab
- **Recovery summary**: Net compensation calculator showing total recovery, legal fees, expenses/liens, net to client, with progress bar
- **Recovery amounts**: Table of insurance/third-party recovery sources with amounts
- **Legal fees**: Table with fee recipient, rate, discount, referral fees, calculated amount per recovery
- **Expenses/Liens**: Table with lien holder, description, amount, reduction
- **Outstanding balances**: Table with responsible party (client/other), balance holder, amount, reduction
- Settlement deduction order (fees first vs expenses first) affects net compensation calculation

### 3. Matter Stages (sidebar: Stages)
- Practice area selector dropdown
- Kanban-style board showing stage columns for selected practice area
- Matter cards within each stage showing matter number, description, client, days in stage
- Colored stage bars (unique per stage)
- "No Stage" column for unassigned matters
- Context menus on stage column headers (edit/delete stage) and on matter cards (change practice area, change status, duplicate, delete)
- Add new stages to any practice area

### 4. Matter Templates (sidebar: Templates)
- Table of templates with name, default badge, practice area, billing method, actions
- Create/edit templates with: name, default toggle, description, practice area, responsible/originating attorney, responsible staff, billable checkbox, billing method
- Set/remove default template (only one default allowed)
- Delete templates with confirmation

### 5. Practice Areas (sidebar: Practice Areas)
- Table of practice areas with name, enabled status, stage count, primary badge
- Add new practice areas, rename existing ones, delete unused ones
- Set primary practice area
- Confirmation dialogs for destructive actions

### 6. Matter Numbering (sidebar: Numbering)
- Current numbering scheme display (prefix, separator, next number, digits)
- Change starting number with confirmation modal
- Auto-update numbering toggle

## Implemented Features and UI Interactions

### CRUD Operations
- Create, read, update, delete for: matters, damages, recoveries, legal fees, liens, outstanding balances, medical providers, medical records, medical bills, comments, practice areas, matter stages, matter templates

### Custom UI Components (no native elements)
- **Dropdowns**: Click-to-open with search-style trigger, scrollable option list, selected state
- **Toggle switches**: Click to toggle on/off with animated knob
- **Checkboxes**: Custom styled with checkmark icon on checked state
- **Radio buttons**: Custom with dot indicator
- **Modals**: Overlay with header/body/footer, close on escape/overlay click, small/large sizes
- **Confirm modals**: Checkbox-gated confirmation for destructive actions
- **Context menus**: Right-click style menus for row/card actions
- **Toast notifications**: Slide-in notifications with auto-dismiss (3 seconds)
- **Date inputs**: HTML date type with custom styling
- **Currency inputs**: Prefixed with $ symbol

### Navigation
- Sidebar navigation with icons and labels for all sections
- Active state highlighting on current section
- Matter detail accessed by clicking matter link in list or stage card
- Back button returns to matters list
- Hash-based view state (in-memory, not URL hash)

### State Management
- Centralized AppState object with subscriber pattern
- localStorage persistence with seed data version invalidation
- Server sync via PUT /api/state on every mutation
- SSE listener for reset events from server
- Immutable seed data capture for reset functionality

### Search and Filtering
- Matter list: keyword search + status quick filters + column sorting
- Damages tab: keyword search + category quick filters
- All filters combinable

### Bulk Operations
- Select individual matters via checkboxes or select all
- Bulk status change (Open, Pending, Closed) with confirmation
- Bulk delete with typed confirmation

## Data Model

### Matter
- `id`, `displayNumber`, `description`, `status` (Open/Pending/Closed), `clientId`, `contactName`
- `practiceAreaId`, `stageId`, `responsibleAttorneyId`, `originatingAttorneyId`, `responsibleStaffId`
- `clientRefNumber`, `location`, `templateId`, `openDate`, `closeDate`, `createdAt`
- `billingPreference`: { isBillable, billingMethod (hourly/contingency/flat_rate), currency, contingencyRate, contingencyRecipientId, flatFeeAmount, flatFeeRecipientId, customRates, budget, budgetNotifyUsers, trustMinBalance, trustNotifyUsers }
- `deductionOrder`: fees_first | expenses_first
- `damages[]`: { id, description, type, category, amount }
- `settlement`: { recoveries[], legalFees[], liens[], outstandingBalances[] }
- `medicalProviders[]`: { id, contactId, description, treatmentFirstDate, treatmentLastDate, treatmentComplete, recordRequestDate, recordFollowUpDate, recordStatus, billRequestDate, billFollowUpDate, billStatus, records[], bills[] }
- `customFieldValues{}`, `timeline[]`, `relatedContacts[]`

### Contact
- `id`, `type` (person/company), `firstName`, `lastName`, `email`, `phone`, `address`
- `tags[]`, `company`, `role`

### Practice Area
- `id`, `name`, `enabled`, `isPrimary`

### Matter Stage (keyed by practice area ID)
- `id`, `name`, `color`, `order`

### Matter Template
- `id`, `name`, `isDefault`, `description`, `practiceAreaId`, `responsibleAttorneyId`, `originatingAttorneyId`, `responsibleStaffId`, `isBillable`, `billingMethod`

### Recovery
- `id`, `sourceContactId`, `amount`, `date`

### Legal Fee
- `id`, `recoveryId`, `recipientId`, `rate`, `discount`, `referralFees[]`: { recipientId, rate }

### Lien
- `id`, `lienHolderId`, `description`, `amount`, `reduction`

### Outstanding Balance
- `id`, `responsibleParty` (client/other), `balanceHolderId`, `description`, `balanceOwing`, `reduction`

### Medical Provider
- `id`, `contactId`, `description`, treatment dates, request statuses
- `records[]`: { id, fileName, receivedDate, startDate, endDate, comments[] }
- `bills[]`: { id, fileName, billDate, receivedDate, billAmount, adjustment, payers[], balanceOwed, balanceIsLien, balanceIsOutstanding, comments[] }

### Comment
- `id`, `userId`, `text`, `createdAt`, `updatedAt`

### Custom Field Definition
- `id`, `fieldSetName`, `label`, `type` (text/number/date/dropdown/boolean/multiselect), `options[]`

### Firm User
- `id`, `firstName`, `lastName`, `email`, `role`, `rate`, `color`

### Numbering Scheme
- `prefix`, `separator`, `nextNumber`, `digits`, `updateByDefault`

## Navigation Structure

| Sidebar Item | View ID | Description |
|---|---|---|
| Matters | matters-list | Main matter list with filters |
| (matter click) | matter-detail | Detail view with 4 tabs |
| Stages | stages | Kanban board per practice area |
| Templates | templates | Template management table |
| Practice Areas | practice-areas | Practice area configuration |
| Numbering | numbering | Matter number scheme settings |

## Form Controls and Options

### Dropdowns
- **Status**: Open, Pending, Closed
- **Practice Area**: Personal Injury, Criminal Defense, Family Law, Corporate Law, Real Estate, Immigration, Employment Law, Bankruptcy, Intellectual Property, Tax Law, Estate Planning, Environmental Law, Civil Rights, Administrative Law
- **Billing Method**: Hourly, Contingency, Flat Rate
- **Currency**: USD, CAD, EUR, GBP, AUD
- **Location**: Main Office, Downtown Branch, Satellite - Westside, Remote
- **Template**: PI Auto Accident (default), Criminal Misdemeanor, Family Divorce, Corporate M&A, Flat Fee Will
- **Client/Contact**: 28 contacts (persons and companies)
- **Responsible Attorney/Staff**: 10 firm users
- **Damage Type**: 20+ types across Economic, Non-Economic, and Special Damages categories
- **Record/Bill Status**: Not yet requested, Requested, Received, Partially received, Under review
- **Stage**: Varies by practice area (e.g., PI has 8 stages from Intake through Settlement/Closed)

### Toggles
- Use as matter default template (on template form)

### Checkboxes
- Billable (matter form, template form)
- Mark as lien (medical bill payer)
- Balance is lien / Balance is outstanding (medical bill)
- Treatment complete (medical provider)
- Confirm deletion (confirm modals)
- Auto-update numbering

### Radio Buttons
- Deduction order: Fees first / Expenses first
- Responsible party: Client / Other party (outstanding balance form)

## Seed Data Summary

### Matters (15 total)
1. **mat_001** - Rodriguez v. Premier Auto Group (PI, Open, Litigation stage) - richest data: 4 medical providers, 9 damages, full settlement
2. **mat_002** - Chen v. Citywide Transport (PI, Open, Discovery)
3. **mat_003** - Thompson Wrongful Termination (Employment, Open)
4. **mat_004** - Nguyen DUI Defense (Criminal, Open, Arraignment)
5. **mat_005** - Baker v. Baker Divorce (Family, Open, Discovery)
6. **mat_006** - Morrison Estate Planning (Estate Planning, Open)
7. **mat_007** - TechStart Inc. Series A (Corporate, Open, Due Diligence)
8. **mat_008** - Williams Slip and Fall (PI, Open, Medical Treatment)
9. **mat_009** - Garcia Immigration Petition (Immigration, Pending)
10. **mat_010** - Patel v. Sunrise Properties (Real Estate, Open)
11. **mat_011** - Roberts Bankruptcy Ch.7 (Bankruptcy, Open)
12. **mat_012** - Kim Patent Application (IP, Open)
13. **mat_013** - Adams Tax Dispute (Tax, Pending)
14. **mat_014** - Jackson Custody Modification (Family, Closed)
15. **mat_015** - Riverside Commerce Park (Real Estate, Open)

### Deleted Matters (1)
- **mat_100** - Deprecated - Old Test Matter

### Contacts (28)
- Mix of persons and companies including clients, medical providers (Dr. Sarah Kim, Metro Orthopedic Center, PhysioFirst Rehabilitation, Valley Imaging Center), insurance companies (Pinnacle Auto Insurance, Shield Insurance Group, Citywide Insurance Corp), opposing parties, and attorneys

### Firm Users (10)
- Sarah Mitchell (Administrator, current user), James Rodriguez, Emily Watson, Michael Chen, Lisa Park, David Kim, Rachel Torres, Kevin O'Brien, Amanda Foster, Robert Chang

### Practice Areas (14)
- Personal Injury (primary, 8 stages), Criminal Defense (4 stages), Family Law (5 stages), Corporate Law (4 stages), Real Estate (3 stages), and 9 more without custom stages

### Matter Templates (5)
- PI Auto Accident (default), Criminal Misdemeanor, Family Divorce, Corporate M&A, Flat Fee Will

### Custom Field Definitions (12 fields across 4 field sets)
- Case Information: Case Type, Jurisdiction, Court Name, Case Number
- Insurance Details: Policy Number, Coverage Limit, Deductible, Adjuster Name
- Medical Summary: Total Medical Bills, Treatment Duration
- Financial: Retainer Amount, Payment Plan

### Task Lists (5)
- New PI Matter Checklist, Discovery Tasks, Trial Preparation, Client Onboarding, Settlement Checklist
