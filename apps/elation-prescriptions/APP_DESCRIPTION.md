# Elation Health — Prescriptions Module

## Summary
An e-prescribing module for a primary care EHR (Electronic Health Record) platform. The app operates in the context of a selected patient and allows providers to manage prescriptions, handle refill requests, check drug interactions, and configure prescribing settings. It supports multi-patient switching via a top-bar patient selector.

## Main Sections / Pages

### 1. Active Medications (default view, route: `medications`)
- Table of the current patient's medications showing drug name, form/strength, sig (directions), prescriber, start date, refills remaining, and status
- Filter tabs: Active (default), All, Discontinued, Completed
- Sort dropdown: Name A-Z, Name Z-A, Newest First, Oldest First, Status
- Search by medication name (text input with debounce)
- Click any row to open Prescription Detail view
- "New Prescription" button navigates to Prescribe form

### 2. Prescribe New Medication (route: `prescribe`)
- Patient header showing name, DOB, age, gender, MRN, and allergy tags with severity coloring
- **Drug search**: Type-ahead search by brand or generic name with results showing drug class and schedule info
- **Favorites grid**: Quick-access buttons for frequently prescribed drugs (configurable in Settings)
- **Drug selection info panel**: Shows generic name, brand name, drug class, controlled substance schedule
- **Form/Strength dropdown**: Auto-populated from selected drug's available forms and strengths
- **Dosing section**: Dosage (text), Frequency (dropdown with 19 options), Route (dropdown, filtered by drug)
- **Quantity, Days Supply, Refills**: Numeric inputs with defaults from settings
- **Directions (Sig)**: Free text with quick-preset buttons from drug's common sigs
- **Dispensing section**: Pharmacy dropdown (15 pharmacies), DAW toggle, Prior Authorization toggle with PA number field
- **Allergy alerts**: Red warning banners if the selected drug cross-reacts with patient allergies
- **Drug interaction alerts**: Severity-colored alerts (major/moderate/minor) checking against all active patient medications
- **Notes**: Free-text clinical note
- **Actions**: Cancel, Print/Fax, E-Prescribe (submit)

### 3. Prescription Detail (route: `prescription-detail`)
- Full prescription details in a two-column layout (main + sidebar)
- **Main area**: Status badge, drug info, sig, frequency, route, quantity, days supply, refills, DAW, prescriber, pharmacy, dates, prior auth info, controlled substance schedule, discontinue reason
- **Prescription History timeline**: Chronological events (prescribed, filled, renewed, modified, discontinued, etc.) with colored dots and notes
- **Fill History table**: Fill number, date, pharmacy, quantity, days supply
- **Sidebar**: Pharmacy info card (name, address, phone, fax, type, EPCS status), Quick actions (add/remove from favorites)
- **Action buttons** (context-dependent):
  - Active: Renew, Modify, Hold, Discontinue
  - On Hold: Resume, Discontinue
  - Discontinued/Completed: Re-prescribe

### 4. Refill Requests (route: `refills`)
- Cards showing incoming refill requests from pharmacies
- Filter tabs: Pending (default), All, Approved, Denied, Modified
- Each card shows: drug name, urgency badge, status badge, patient name, pharmacy, request date, original prescriber, refills remaining, notes
- Urgent requests highlighted with red left border
- **Pending actions**: Approve, Modify & Approve, Deny
- **Deny modal**: Radio buttons with 10 deny reasons + optional notes
- **Modify modal**: Text area for modification details

### 5. Medication History (route: `history`)
- Chronological list of all prescriptions (past and present) for the current patient
- **Filters**: Date From, Date To, Medication search, Provider dropdown
- Each row shows: drug name, form/strength, status badge, date range, prescriber, sig
- Discontinued prescriptions show DC reason
- Click any row to view full prescription detail

### 6. Drug Interaction Checker (route: `interactions`)
- Two-column layout: input panel + results panel
- **Add drugs**: Search and add drugs one at a time
- **Selected drugs list**: Shows chips with remove buttons, "Clear All" button
- **Load Current Patient Medications**: One-click loads all active medications for current patient
- **Results**: Shows count of interactions found, or "No interactions found" with checkmark
- Interaction alerts colored by severity with description and clinical recommendation

### 7. Settings (route: `settings`)
- **Prescriber Information**: Name, title, specialty, DEA number, NPI, EPCS enrollment status (read-only display)
- **Default Pharmacy**: Dropdown selector (15 pharmacies)
- **Prescribing Defaults**: Default Days Supply (numeric), Default Refills (numeric), Print Format (Standard/Detailed/Compact)
- **E-Prescribing Options** (toggles): Enable E-Prescribing, Show Generic Name First, Auto-Check Drug Interactions, Require Allergy Review, Require Signature
- **Formulary / Favorites**: List of favorite drugs with remove buttons
- **Save Settings** button

## Data Model

### Patients (6 entities)
Fields: id, firstName, lastName, dob, gender, mrn, allergies[] (substance, reaction, severity), preferredPharmacy, insurance (plan, memberId, group, bin, pcn)

### Providers (6 entities)
Fields: id, firstName, lastName, title (MD/DO/NP/PA-C), specialty, deaNumber, npi, epcsEnrolled, isCurrentUser

### Pharmacies (15 entities)
Fields: id, name, address, phone, fax, type (retail/hospital/mail-order/specialty), acceptsEPCS, hours, ncpdpId

### Drug Catalog (60 entities)
Fields: id, brandName, genericName, drugClass, schedule (null/II/III/IV/V), forms[] (form, strengths[]), routes[], commonSigs[], allergenCrossReactivity[]

### Prescriptions (30 entities)
Fields: id, patientId, drugId, drugName, brandName, formStrength, dosage, frequency, route, quantity, daysSupply, refillsTotal, refillsRemaining, sig, daw, pharmacyId, prescriberId, status (active/discontinued/on-hold/completed/cancelled), startDate, endDate, priorAuth, priorAuthNumber, discontinuedReason, discontinuedDate, fillHistory[], history[]

### Refill Requests (12 entities)
Fields: id, prescriptionId, patientId, drugName, patientName, pharmacyId, pharmacyName, requestDate, status (pending/approved/denied/modified), urgency (routine/urgent), originalPrescriber, refillsRemaining, notes, denyReason, responseDate, respondedBy, modifiedDetails

### Drug Interactions (25 pairs)
Fields: id, drug1Id, drug2Id, drug1Name, drug2Name, severity (major/moderate/minor), description, recommendation

### Settings (1 object)
Fields: defaultPharmacy, prescriptionFormat, defaultDaysSupply, defaultRefills, showGenericFirst, autoCheckInteractions, requireAllergyReview, eRxEnabled, printFormat, signatureRequired, favoritesDrugIds[]

## Entity Relationships
- Patient -> Prescriptions (1:many via patientId)
- Patient -> Preferred Pharmacy (many:1 via preferredPharmacy)
- Prescription -> Drug Catalog (many:1 via drugId)
- Prescription -> Pharmacy (many:1 via pharmacyId)
- Prescription -> Provider (many:1 via prescriberId)
- Refill Request -> Prescription (many:1 via prescriptionId)
- Refill Request -> Patient (many:1 via patientId)
- Refill Request -> Pharmacy (many:1 via pharmacyId)
- Drug Interaction -> Drug Catalog (many:many via drug1Id/drug2Id)
- Patient.allergies cross-references Drug.allergenCrossReactivity for allergy alerts

## Navigation Structure
- **Top bar**: Logo, "Prescriptions" breadcrumb, Patient Selector dropdown (center), Provider name (right)
- **Sidebar**: Active Medications, Prescribe New, Refill Requests (with pending count badge), Medication History, Interaction Checker, Settings
- **Patient switching**: Top bar dropdown changes patient context; resets to medications view

## Available Form Controls

### Dropdowns (custom, not native `<select>`)
- Patient selector (6 patients)
- Medication sort (5 options: Name A-Z, Name Z-A, Newest First, Oldest First, Status)
- Form/Strength (varies per drug, e.g. Atorvastatin: 10mg/20mg/40mg/80mg Tablet)
- Frequency (19 options: Once daily, Twice daily, Three times daily, Four times daily, Every 4 hours, Every 4-6 hours, Every 6 hours, Every 6-8 hours, Every 8 hours, Every 12 hours, Once weekly, Twice weekly, Every other day, Once monthly, As needed, At bedtime, Before meals, After meals, With meals)
- Route (13 options: Oral, Sublingual, Topical, Inhalation, Intranasal, Ophthalmic, Otic, Rectal, Vaginal, Subcutaneous, Intramuscular, Intravenous, Transdermal)
- Pharmacy (15 pharmacies with type labels)
- History Provider filter (6 providers + "All Providers")
- Default Pharmacy (settings, 15 pharmacies)
- Print Format (Standard, Detailed, Compact)

### Toggles
- DAW (Dispense As Written)
- Prior Authorization Required
- Enable E-Prescribing (settings)
- Show Generic Name First (settings)
- Auto-Check Drug Interactions (settings)
- Require Allergy Review (settings)
- Require Signature (settings)

### Filter Tabs
- Medication status: Active, All, Discontinued, Completed
- Refill status: Pending, All, Approved, Denied, Modified

### Search Inputs
- Drug search (prescribe form, type-ahead with results dropdown)
- Medication list search (text input with debounce)
- Interaction checker drug search (type-ahead)
- History medication filter (text input)

### Text/Number Inputs
- Dosage, Quantity, Days Supply, Refills (prescribe form)
- Sig / Directions (textarea with preset buttons)
- Prior Authorization Number
- Clinical Note (prescribe form)
- History date range filters (YYYY-MM-DD)
- Default Days Supply, Default Refills (settings)
- Renew refills (modal)
- Modify dosage, frequency, sig, quantity (modal)
- Discontinue reason (modal textarea)
- Hold reason (modal textarea)
- Deny reason notes (modal textarea)
- Modify refill details (modal textarea)

### Radio Buttons
- Deny reason selection (10 options in modal)

## Seed Data Summary

### Patients (6)
1. Margaret Chen (pat_001) — Female, DOB 1958-03-14, MRN-20180423, allergies: Penicillin (severe), Sulfa drugs (moderate), Codeine (mild). Preferred pharmacy: CVS #4521. Medicare Part D.
2. David Kowalski (pat_002) — Male, DOB 1975-09-28, MRN-20190817, allergies: Aspirin (severe), Ibuprofen (severe). Preferred: Rite Aid #5612. Blue Cross PPO.
3. Aisha Rahman (pat_003) — Female, DOB 1992-01-05, MRN-20200312, NKDA. Preferred: Walgreens #7893. Aetna HMO.
4. William Thornton (pat_004) — Male, DOB 1944-11-22, MRN-20170605, allergies: Lisinopril/ACE Inhibitors (severe), Latex (moderate). Preferred: Kaiser Geary. Medicare Part D.
5. Jessica Morales (pat_005) — Female, DOB 1988-06-17, MRN-20210901, allergies: Erythromycin (mild). Preferred: CVS #4521. Cigna Open Access.
6. Robert Fitzgerald (pat_006) — Male, DOB 1961-08-03, MRN-20160214, allergies: Metformin (severe), Shellfish (moderate). Preferred: UCSF Pharmacy. UnitedHealth.

### Current Patient (default)
Margaret Chen (pat_001) — has 16 prescriptions (11 active, 3 discontinued, 1 on-hold, 1 completed; Apixaban and Semaglutide have prior auth)

### Providers (6)
1. Dr. Sarah Mitchell, MD — Internal Medicine, DEA: BM1234563, NPI: 1234567890, EPCS enrolled, **current user**
2. Dr. James Okafor, DO — Family Medicine, EPCS enrolled
3. Dr. Linda Reyes, MD — Internal Medicine, EPCS not enrolled
4. Michael Brandt, NP — Family Medicine, EPCS enrolled
5. Priya Sharma, PA-C — Internal Medicine, EPCS not enrolled
6. Dr. Robert Tanaka, MD — Cardiology, EPCS enrolled

### Drug Catalog (60 drugs across categories)
- Cardiovascular: Atorvastatin, Simvastatin, Rosuvastatin, Lisinopril, Amlodipine, Metoprolol Tartrate, Metoprolol Succinate ER, Valsartan, Furosemide, Hydrochlorothiazide, Warfarin, Apixaban, Rivaroxaban, Clopidogrel, Carvedilol, Diltiazem, Spironolactone
- Endocrine/Diabetes: Metformin, Sitagliptin, Empagliflozin, Insulin Glargine, Levothyroxine, Semaglutide, Dulaglutide, Glipizide
- GI: Pantoprazole, Esomeprazole, Omeprazole
- Respiratory: Albuterol, Fluticasone/Salmeterol, Tiotropium, Montelukast, Fluticasone Nasal
- Antibiotics: Amoxicillin, Amoxicillin/Clavulanate, Cephalexin, Azithromycin, Clarithromycin, Ciprofloxacin, Sulfamethoxazole/Trimethoprim, Fluconazole
- Neuropsych: Sertraline, Escitalopram, Duloxetine, Fluoxetine, Gabapentin, Pregabalin (Schedule V)
- Sedatives: Zolpidem (Schedule IV), Alprazolam (Schedule IV), Lorazepam (Schedule IV)
- Pain: Oxycodone/Acetaminophen (Schedule II), Codeine/Acetaminophen (Schedule III), Ibuprofen, Diclofenac
- Steroids: Prednisone, Methylprednisolone
- Muscle Relaxant: Cyclobenzaprine
- Antivirals: Oseltamivir, Valacyclovir

### Prescriptions (30 across 6 patients)
- Margaret Chen: 16 prescriptions (Atorvastatin, Amlodipine, Metformin, Levothyroxine, Pantoprazole, Albuterol, Gabapentin, Flonase, Sertraline, Apixaban [PA], Semaglutide [PA] — all active; Lisinopril [DC], Amoxicillin [DC], Warfarin [DC] — discontinued; Prednisone [completed]; HCTZ [on-hold])
- David Kowalski: 4 prescriptions (Metoprolol ER, Atorvastatin, Escitalopram, Metformin ER)
- Aisha Rahman: 2 prescriptions (Azithromycin [completed], Escitalopram)
- William Thornton: 3 prescriptions (Valsartan, Insulin Glargine [PA], Furosemide)
- Jessica Morales: 2 prescriptions (Cephalexin, Fluoxetine)
- Robert Fitzgerald: 3 prescriptions (Empagliflozin [PA], Carvedilol, Spironolactone)

### Refill Requests (12)
- 7 pending, 3 approved, 1 denied, 1 modified
- 3 urgent (Pantoprazole, Apixaban, Furosemide)
- Spans multiple patients and pharmacies

### Drug Interactions (25 pairs)
- 11 major (e.g., Statin+Clarithromycin, Warfarin+NSAID, dual anticoagulants, opioid+benzo)
- 12 moderate (e.g., Warfarin+Azithromycin, ACE+Spiro, SSRI+NSAID)
- 2 minor (e.g., Cipro+Levothyroxine)

### Pharmacies (15)
- 7 retail (CVS, Walgreens, Rite Aid, Kaiser, Costco, Safeway, Good Neighbor)
- 4 mail-order (Alto, Express Scripts, Capsule, Amazon)
- 3 specialty (BioPlus, Accredo, Optum)
- 1 hospital (UCSF Medical Center)

### Settings (defaults)
- Default pharmacy: CVS #4521
- Days supply: 30, Refills: 0
- Print format: Standard
- All toggles on (e-Rx, generic first, auto interactions, allergy review, signature)
- 10 favorite drugs in formulary
