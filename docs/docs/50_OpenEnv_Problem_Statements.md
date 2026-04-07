# 50 High-Utility OpenEnv Problem Statements

Since the Round 1 mandate dictates that the environment must have **high real-world utility (30%)**, be **creative/novel (10%)**, and feature a strictly graded **Easy → Medium → Hard (25%)** task progression, this document outlines 50 highly actionable, non-game domains to base your environment on.

---

## 🛠️ Software Engineering & DevOps (1-10)

### 1. Production Log Triage Agent
**Goal:** Navigate a simulated server log directory to find the root cause of an outage.
**Tasks:** (E) Find 500 errors in access.log → (M) Trace the Error ID to a database timeout in app.log → (H) Identify the exact SQL query causing the deadlock.
**Reward Signal:** +0.1 per correct log file opened, +0.3 for identifying the timestamp, +0.6 for identifying the exact broken query. Penalty for deleting logs.

### 2. Automated Pull Request Reviewer
**Goal:** Review diffs in a simulated Python codebase and approve/reject based on a company style guide.
**Tasks:** (E) Reject missing docstrings → (M) Identify and comment on a variable shadowing bug → (H) Spot an SQL injection vulnerability and request changes.
**Reward Signal:** Partial points for correctly highlighting the exact line number of the violation.

### 3. Kubernetes Auto-Scaler Simulator
**Goal:** Manage CPU/Memory limits across pods to handle fluctuating traffic without crashing the cluster or overspending.
**Tasks:** (E) Scale up web-servers during a linear traffic spike → (M) Handle a sudden DDOS without bankrupting the cloud budget → (H) Optimize node allocation across 3 microservices with interdependent latencies.
**Reward Signal:** +Score for uptime, -Score for exceeding max budget constraints.

### 4. Database Migration Assistant
**Goal:** Write and execute safely rolling SQL migrations on a dummy Postgres state.
**Tasks:** (E) Add a nullable column → (M) Safely split a "Full Name" column into First/Last without data loss → (H) Change a primary key type from INT to UUID across 5 joined tables.
**Reward Signal:** Reward for preserving row count and data fidelity; strict failure for data deletion.

### 5. Dependency Vulnerability Patcher
**Goal:** Given a `package.json` with known CVEs, update constraints to fix vulnerabilities without breaking the build.
**Tasks:** (E) Bump a minor version of a leaf dependency → (M) Resolve a conflicting peer dependency issue → (H) Upgrade a major React version and fix the resulting breaking syntax changes in 3 files.
**Reward Signal:** +Score for every CVE eliminated.

### 6. Git Conflict Resolution Agent
**Goal:** Attempt to merge 2 branches and resolve the resulting merge conflicts according to business logic.
**Tasks:** (E) Resolve a simple appending conflict → (M) Resolve a logic conflict where a function signature changed → (H) Handle a 5-file conflict where one branch renamed a file the other branch edited.
**Reward Signal:** Compiling code after merge attempt yields rewards.

### 7. Cloud IAM Permission Optimizer
**Goal:** Given an oversized JSON AWS IAM policy, reduce the permissions to the absolute principle of least privilege required to run a specific script.
**Tasks:** (E) Remove `*` access to S3 → (M) Restrict permissions to specific ARNs based on application logs → (H) untangle a nested AssumeRole vulnerability constraint.
**Reward Signal:** Reward for removing unused permissions; penalty if the target application script starts failing.

### 8. Network Firewall Configurator
**Goal:** Open and close ports on a simulated router config to allow specific app traffic while blocking malicious IPs.
**Tasks:** (E) Block a single static IP → (M) Allow port 443 only from a specific VPN subnet → (H) Implement rate limiting against a dynamic botnet attack mimicking real traffic.
**Reward Signal:** +Uptime for valid requests, -Score for malicious traffic let through.

### 9. API Rate Limit Optimizer
**Goal:** Fetch 10,000 records from a mock third-party API respecting its hidden, dynamic rate limits.
**Tasks:** (E) Pull 100 API records → (M) Pull 1,000 records respectfully responding to HTTP 429s (Backoffs) → (H) Optimize a multi-threaded fetcher to extract 10,000 records precisely within the limit bucket.
**Reward Signal:** +Score for records extracted; severe penalties for getting IP-banned.

### 10. Legacy Code Translator (Cobol to Python)
**Goal:** Iteratively translate chunks of spaghetti Cobol/Fortran logic into Python.
**Tasks:** (E) Translate simple mathematical formulas → (M) Translate loop structures and GOTO statements → (H) Translate a full financial subroutine with complex data-type casting.
**Reward Signal:** Passing unit tests on the generated Python code matching the original inputs/outputs.

---

## 📊 Data Science & Data Engineering (11-20)

### 11. Messy CSV ETL Cleaner
**Goal:** Transform a horribly formatted, messy CSV dataset into a standardized schema table.
**Tasks:** (E) Drop NaN columns and strip whitespace → (M) Standardize 5 different date formats into ISO-8601 → (H) Impute missing categorical values based on context from other columns.
**Reward Signal:** Points awarded for each row successfully ingested into the typed target database.

### 12. PII Data Redactor
**Goal:** Identify and mask Personally Identifiable Information (SSNs, Phones, Names) in raw customer database dumps.
**Tasks:** (E) Mask standard 9-digit SSNs → (M) Mask international phone numbers hidden in custom text strings → (H) Contextually redact names that might be part of company titles (e.g., "John" but not "Papa John's").
**Reward Signal:** +Reward for correctly masked PII; -Penalty for unmasked PII or falsely masked utility data.

### 13. Smart SQL Query Optimizer
**Goal:** Rewrite terribly inefficient SQL queries to reduce cost/time on a simulated execution engine planner.
**Tasks:** (E) Replace `SELECT *` with specific columns → (M) Replace correlated subqueries with JOINs → (H) Introduce proper indexing syntax and partition filtering for a billion-row table query.
**Reward Signal:** Measured reduction in simulated "execution cost" metric.

### 14. JSON Schema Enforcer
**Goal:** Read thousands of raw API payloads and correctly map them into a strict Pydantic/JSON schema, fixing type errors on the fly.
**Tasks:** (E) Cast strings to ints → (M) Extract nested addresses into flattened maps → (H) Handle deeply nested, highly polymorphic event schemas and group them into 3 normalized tables.
**Reward Signal:** +Score per successfully validated JSON document.

### 15. Web Scraper Rule Auto-Healer
**Goal:** Extract pricing data from a simulated e-commerce HTML DOM that randomly changes class names and layouts.
**Tasks:** (E) Extract price from a static DOM → (M) Extract price when the class name is randomized but structure remains → (H) Extract price when the entire div hierarchy is structurally AB tested.
**Reward Signal:** +0.1 per correct product price extracted across 10 changing DOM states.

### 16. Outlier Detection Engine
**Goal:** Iterate through streams of sensor telemetry data and flag catastrophic hardware failure anomalies.
**Tasks:** (E) Flag values > 3 standard deviations → (M) Flag context anomalies (e.g., freezer temperature is -5C which is fine, but it's summer and AC is broken) → (H) Predict impending failure 5 ticks in advance via trend analysis.
**Reward Signal:** Points for correct flags; negative points for false alarms.

### 17. API Payload Pagination Crawler
**Goal:** Traverse a deeply paginated API using cursor offsets that randomly change schema logic.
**Tasks:** (E) Loop through standard page=1,2,3 → (M) Handle string-based cursors returned in headers → (H) Handle dynamic throttling constraints requiring payload caching based on ETag.
**Reward Signal:** Extracting the exact total sum of items hidden across 50 pages.

### 18. Spreadsheet Formula Debugger
**Goal:** Identify circular dependencies and broken REF errors in a simulated CSV-based spreadsheet format.
**Tasks:** (E) Fix a #DIV/0 error → (M) Fix a broken VLOOKUP mapping → (H) Untangle a massive 5-sheet circular dependency chain without breaking the final calculation.
**Reward Signal:** Accurate floating-point match to the hidden "correct" spreadsheet output.

### 19. Data Format Converter (XML to JSON)
**Goal:** Parse complex enterprise XML payloads into clean JSON APIs.
**Tasks:** (E) Convert direct key-values → (M) Map XML attributes correctly into JSON array objects → (H) Handle deeply conflicting schema namespaces identically.
**Reward Signal:** Strict JSON linters matching the expected output tree.

### 20. NLP Sentiment Labeler
**Goal:** Classify the true sentiment of ambiguous product reviews for a routing system.
**Tasks:** (E) Label pure positive/negative text → (M) Label sarcasm (e.g., "Yeah right, like this battery actually lasts 4 hours") → (H) Label complex dual-sentiment texts (e.g., "The UI is garbage but the API is best in class").
**Reward Signal:** Accuracy percentage against a golden dataset hidden from the agent.

---

## 🏦 Finance, Compliance & Admin (21-30)

### 21. Expense Report Auditor
**Goal:** Compare employee submitted expense receipts (text) against the strict corporate travel policy to approve/deny.
**Tasks:** (E) Deny an alcohol purchase on a daily per-diem → (M) Flag an Uber receipt that was taken outside working hours → (H) Find a discrepancy where a user submitted the same $45 transit receipt across two different months.
**Reward Signal:** +1.0 for correctly categorizing the report (Approve vs Deny) with the correct reason code.

### 22. Anti-Money Laundering (AML) Freeze System
**Goal:** Review a ledger of daily bank transactions and freeze accounts exhibiting structuring behavior.
**Tasks:** (E) Freeze an account making ten $9,999 deposits a day → (M) Trace money moving rapidly across 4 internal sleeper accounts → (H) Catch a sophisticated 10-node cycle involving international shell company wire transfers.
**Reward Signal:** +Score for correctly frozen accounts; massive penalty for freezing innocent civilian accounts.

### 23. Corporate Tax Form Mapper
**Goal:** Given a raw text summary of business expenditures, properly slot the values into a mocked IRS JSON specific form.
**Tasks:** (E) Map gross revenue correctly → (M) Calculate and map depreciation schedules correctly → (H) Identify and exclude non-deductible entertainment expenses masked as "client meetings" in the ledger.
**Reward Signal:** Passing validations on the simulated IRS submission endpoint.

### 24. Contract Clause Extractor
**Goal:** Read a 50-page legal markdown document and output the exact parameters of Liability and Termination.
**Tasks:** (E) Extract the termination notice period (e.g., 30 days) → (M) Identify the governing jurisdiction (e.g., State of Delaware) → (H) Identify complex indemnification carve-outs buried in the footnotes.
**Reward Signal:** Perfect text matching against the ground-truth legal variables.

### 25. Invoice Reconciliation Clerk
**Goal:** Match incoming payments off a simulated bank feed statement against pending company invoices.
**Tasks:** (E) Match exact dollar amounts and exact names → (M) Match a bulk wire transfer covering 3 distinct invoices at once → (H) Reconcile a payment that is short by 2% due to foreign exchange fees and log the discrepancy correctly.
**Reward Signal:** +1 for every invoice correctly marked explicitly as "Paid".

### 26. Dynamic Pricing Engine
**Goal:** Adjust the price of an airline ticket up and down based on simulated competitor prices and seat availability.
**Tasks:** (E) Drop price if seats are empty 24 hours out → (M) Match competitor price drops instantly → (H) Maximize yield revenue by exploiting a sudden surge in demand while competitor flights show "Sold Out".
**Reward Signal:** Final total revenue generated at the end of the 30-day simulated booking window.

### 27. Insurance Claim Adjudicator
**Goal:** Approve or deny medical claims by crossing ICD-10 codes with patient coverage policies.
**Tasks:** (E) Deny a cosmetic surgery on a basic plan → (M) Approve a complex surgery but deny the out-of-network anesthesiologist → (H) Handle primary and secondary insurance coordination of benefits limits.
**Reward Signal:** Perfect claim adjudication match rate.

### 28. Supply Chain Re-router
**Goal:** Manage logistics paths for cargo shipments reacting to weather and port strikes.
**Tasks:** (E) Re-route a truck around a closed highway → (M) Re-book ocean freight to air freight when a port goes on strike to meet an SLA → (H) Optimize a 50-pallet global distribution reacting to 3 complex weather delays simultaneously.
**Reward Signal:** Negative points per day late and per extra dollar spent.

### 29. Compliance Framework Mapper
**Goal:** Cross-reference a mock company's security protocol text against SOC2 requirement checklists.
**Tasks:** (E) Verify password complexity rules exist → (M) Identify gaps in disaster recovery RTO times → (H) Map a messy 30-page confluence doc into the exact required 20 SOC2 control evidence brackets.
**Reward Signal:** Coverage percentage.

### 30. Procurement Bid Evaluator
**Goal:** Review 5 vendor RFPs (Requests for Proposal) and rank them based on an internal weighted scoring matrix.
**Tasks:** (E) Eliminate a vendor over budget → (M) Score vendors accurately on technical specs → (H) Fact-check vendor security claims against a provided internal blacklist registry.
**Reward Signal:** Correctness of the final selected vendor ranking.

---

## 🎧 Customer Support & Human Ops (31-40)

### 31. Urgent Support Ticket Triager
**Goal:** Read customer support emails, categorize their intent, and route them to the correct department with a priority score.
**Tasks:** (E) Route "password reset" to automated IT (Low Priority) → (M) Route "my server is down" to DevOps (High Priority) → (H) Read a heavily nuanced email mentioning a billing error but implying a major security breach, routing it strictly to InfoSec (Critical).
**Reward Signal:** +0.5 for correct department, +0.5 for correct priority queue.

### 32. Refund & Return Processor
**Goal:** Read customer return requests and interface with a mocked order database API to issue refunds within policy.
**Tasks:** (E) Approve a 10-day return on shoes → (M) Deny a 45-day return on electronics (out of 30-day policy) → (H) Execute a complex partial refund for 1 damaged item in a 5-item bundled discount package.
**Reward Signal:** +1 for mathematically accurate ledger adjustments to exactly match the return policy.

### 33. Community Forum Moderator
**Goal:** Approve, edit, or delete user comments based on simulated community guidelines.
**Tasks:** (E) Delete explicit profanity → (M) Flag subtle spam links disguised as helpful advice → (H) Safely mediate a heated political argument by issuing warnings without triggering censorship appeals.
**Reward Signal:** Human-aligned precision/recall scoring on flagged items.

### 34. Smart Calendar Meeting Scheduler
**Goal:** Given 5 employees with filled calendars and different timezones, find a 45-minute slot for an urgent meeting.
**Tasks:** (E) Find an open slot for 2 people in the same timezone → (M) Find a slot for 5 people across 3 timezones → (H) Force-cancel lower priority internal meetings to squeeze in a VIP client meeting under a tight 24-hour deadline.
**Reward Signal:** Binary outcome: Was the meeting successfully booked with all mandatory attendees?

### 35. E-commerce Inventory Allocator
**Goal:** Shift stock between 3 warehouses to fulfill incoming orders while minimizing shipping distances.
**Tasks:** (E) Fulfill an order from the closest warehouse → (M) Split a multi-item order optimally across 2 warehouses → (H) Pre-emptively move stock from the East Coast warehouse to the West Coast based on predicted shipping trends simulating an upcoming holiday.
**Reward Signal:** Total simulated shipping costs (lower score = higher reward).

### 36. Hotel Reservation Concierge
**Goal:** Handle complex booking modifications via a simulated terminal against a mock Property Management System (PMS).
**Tasks:** (E) Change check-in date → (M) Upgrade a room and apply a 10% loyalty discount → (H) Handle a messy group booking where 3 rooms need to be merged to a single payer and split across different tax exemptions.
**Reward Signal:** The final invoice matches the internal objective ledger exactly.

### 37. Job Applicant Screener
**Goal:** Read 100 mock JSON resumes and parse out the top 3 candidates given a specific job description.
**Tasks:** (E) Filter out candidates without a Bachelor's degree → (M) Rank candidates based on exact required tech-stack keywords → (H) Deduce "leadership experience" from nuanced bullet points rather than explicit titles.
**Reward Signal:** Intersection over Union (IoU) with the "Golden" top 3 candidate list.

### 38. Real Estate Listing Standardizer
**Goal:** Read messy paragraph descriptions of houses and extract structured data (Beds, Baths, SqFt).
**Tasks:** (E) Extract explicitly stated "3 bed, 2 bath" → (M) Infer "master suite and two guest rooms" means 3 beds → (H) Detect conflicting information (e.g., text says 3 beds, structured payload says 2) and flag for human review.
**Reward Signal:** 1.0 for perfect JSON extraction.

### 39. Translation QA Editor
**Goal:** Review AI-translated text against context rules and fix tone/localization errors.
**Tasks:** (E) Fix a literal translation of an idiom → (M) Enforce formal vs. informal pronoun structures based on the audience target → (H) Adjust cultural references so that a joke lands safely in the target language.
**Reward Signal:** Points based on passing deterministic linguistic constraint checks.

### 40. B2B Lead Enrichment Engine
**Goal:** Take a list of raw email addresses, query a mock company profile API, and output enriched lead profiles ready for sales.
**Tasks:** (E) Map `@company.com` to the company URL → (M) Parse the job title to categorize the lead (e.g. "VP Marketing" -> "Decision Maker") → (H) Cross-reference the mock company's tech stack API to determine if they are a competitor, instantly disqualifying the lead.
**Reward Signal:** Absolute correctness of the structured output database.

---

## 🏥 Medical, Admin & Education (41-50)

### 41. Electronic Health Record (EHR) Summarizer
**Goal:** Distill 10 pages of simulated doctor notes into a standardized 1-page discharge JSON for billing.
**Tasks:** (E) Extract the primary diagnosis → (M) Extract all prescribed medications and dosages → (H) Correctly map abstract symptom notes to precise ICD-10 medical billing codes.
**Reward Signal:** Recall rate of critical medical codes extracted.

### 42. Student Essay Plagiarism Detective
**Goal:** Evaluate an essay and find inappropriately sited structures against a mock reference database.
**Tasks:** (E) Flag a direct copy-paste without quotes → (M) Flag an AI-rewritten paragraph based on structural syntax anomalies → (H) Flag "mosaic plagiarism" where synonyms were swapped but 5 core arguments remain identical to the source text.
**Reward Signal:** High classification accuracy on flagged sentences.

### 43. Pharmacovigilance Auto-Reporter
**Goal:** Scan mock social media texts to identify and report Adverse Drug Reactions (ADRs).
**Tasks:** (E) Flag "I took DrugX and got a terrible rash" → (M) Ignore "DrugX gave me a rash of energy" (False positive) → (H) Extract the severe ADR from a convoluted story spanning 3 days and map it to the MedDRA vocabulary matrix.
**Reward Signal:** Catching true positives without firing false positives.

### 44. Legal Subpoena e-Discovery Bot
**Goal:** Search through 1,000 mock corporate emails to find documents matching a legal search warrant while protecting privileged communication.
**Tasks:** (E) Retrieve all emails involving a specific keyword and date range → (M) Exclude emails heavily marked as "Attorney-Client Privilege" → (H) Find implicit code-words used by actors attempting to hide insider trading without saying the words explicitly.
**Reward Signal:** Precision and Recall percentage against the hidden target document list.

### 45. University Course Prerequisite Validator
**Goal:** Check a student's transcript JSON and safely approve/deny enrollment for next semester's classes.
**Tasks:** (E) Deny enrollment if CS101 is missing for CS102 → (M) Approve enrollment if a transfer equivalent credit satisfies the prerequisite → (H) Optimize a path to graduation for a senior missing 2 core credits by overriding a co-requisite via API permission.
**Reward Signal:** Successfully enrolling the highest credit count without violating hard curriculum rules.

### 46. Dietary Plan Constraint Solver
**Goal:** Create a 7-day meal plan from a mock grocery API matching strict macros while respecting allergies.
**Tasks:** (E) Generate meals < 2000 calories → (M) Achieve < 2000 calories while strictly avoiding "Peanuts" and "Dairy" → (H) Meet exact protein macros, avoid extreme allergies, and optimize the overall grocery cart cost to be under $50.
**Reward Signal:** +Reward for hitting macros perfectly, massive penalty for poisoning the simulated user with an allergen.

### 47. Construction Permit Auto-Checker
**Goal:** Review architectural JSON parameter inputs against a local mock city zoning code database.
**Tasks:** (E) Reject a building taller than the 30ft limit → (M) Calculate complex Floor Area Ratio (FAR) metrics to deny oversized lots → (H) Approve a variance request actively overriding FAR because of a specific historical zoning exemption in the database rulebook.
**Reward Signal:** Mathematical precision of the zoning approvals.

### 48. Government Grant Matchmaker
**Goal:** Take a non-profit's mission statement and match them exactly to the top 3 open federal funding opportunities.
**Tasks:** (E) Match an environmental group to an EPA grant → (M) Disqualify a group based on revenue cap limits stated in the grant terms → (H) Synthesize 3 disparate sub-grants that combined fund the entire highly-specialized project proposal.
**Reward Signal:** Maximizing eligible funding accurately acquired in simulation.

### 49. Flight Dispatch Weather Router
**Goal:** Read TAF/METAR aviation weather strings and route a simulated airplane around thunderstorms.
**Tasks:** (E) Divert around a massive stationary storm cell to an alternate airport → (M) Calculate fuel burn penalties to ensure the diversion is mathematically possible → (H) Thread the needle through a moving squall line utilizing dynamic updates in the OpenEnv `state()` while reserving 45-minutes of legal fuel.
**Reward Signal:** Safely landing with maximum fuel conserved without entering restricted weather polygons.

### 50. Smart Traffic Light Optimizer
**Goal:** Manipulate 4 intersections of traffic light timings to clear a simulated gridlock.
**Tasks:** (E) Extend green lights on the primary artery during rush hour → (M) Implement a "green wave" synchronization across all 4 lights → (H) Detect a simulated ambulance via an emergency API and dynamically halt cross-traffic to clear a path instantly.
**Reward Signal:** Minimizing total average wait time per queued simulated vehicle.
