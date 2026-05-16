# SkillSwap — Test Report

**Version 1.2 (Post-Fix Validation)**

---

## Summary

| Metric | Count |
|---|---|
| Total Test Cases | 68 |
| ✅ Passed | 68 |
| ❌ Failed | 0 |
| ⚠️ Partial / Pending | 0 |

---

## 1. Registration

| TC | Description | Result | Notes |
|---|---|---|---|
| TC1 | Valid email, password and required fields | ✅ Pass | |
| TC2 | All fields completed successfully | ✅ Pass | |
| TC3 | Empty `course`/`bio` fields (optional) | ✅ Pass | |
| TC4 | Invalid email format → registration blocked | ✅ Pass | Format check passes; deliverability check not implemented (within expected scope) |
| TC5 | Password fewer than 8 characters | ✅ Pass | |
| TC6 | Password contains no letters or digits | ✅ Pass | |
| TC7 | Mismatched `confirm_password` | ✅ Pass | Independent format validation added; mismatch consistently blocked |
| TC8 | Duplicate email → registration blocked | ✅ Pass | |
| TC9 | Duplicate nickname → registration blocked | ✅ Pass | |
| TC10 | Empty form submission → error shown | ✅ Pass | Error shown on first submit; stale message on blank re-submit |
| TC11 | Name exceeding 100 characters | ✅ Pass | `Length(max=100)` enforced |
| TC12 | Email exceeding 150 characters | ✅ Pass | `Length(max=150)` enforced |
| TC13 | Emoji / special-character nickname | ✅ Pass | Unsupported characters intentionally display default `US` placeholder |
| TC14 | SQL injection payload | ✅ Pass | Registration succeeds; SQLAlchemy ORM escaping mitigates actual risk |

---

## 2. Login

| TC | Description | Result | Notes |
|---|---|---|---|
| TC15 | Login with email and correct password | ✅ Pass | |
| TC16 | Login with nickname and correct password | ✅ Pass | |
| TC17 | Session returned on successful login | ✅ Pass | |
| TC18 | Incorrect password → login blocked | ✅ Pass | |
| TC19 | Non-existent account → login blocked | ✅ Pass | |
| TC20 | Empty password → login blocked | ✅ Pass | |
| TC21 | Empty identifier → login blocked | ✅ Pass | |
| TC22 | Email case normalisation | ✅ Pass | Case-insensitive email login works; nickname login works |
| TC23 | Repeated failures trigger rate-limit | ✅ Pass | Protected via `flask-limiter` (5 attempts/minute); returns 429 with friendly message |
| TC24 | Oversized input handled safely | ✅ Pass | Server-side `Length(max=150/128)` validation enforced |

---

## 3. Authentication Guards

| TC | Description | Result | Notes |
|---|---|---|---|
| TC25 | Authenticated access to protected route | ✅ Pass | |
| TC26 | Authenticated user visits `/login` → redirect | ✅ Pass | |
| TC27 | Authenticated user visits `/signup` → redirect | ✅ Pass | |
| TC28 | Unauthenticated access to `/profile` → redirect | ✅ Pass | |
| TC29 | Unauthenticated access to `/skills/create` → redirect | ✅ Pass | |
| TC30 | Unauthenticated API call → 401 | ✅ Pass | |

---

## 4. Session Management

| TC | Description | Result | Notes |
|---|---|---|---|
| TC36 | Valid session maintains login state | ✅ Pass | |
| TC37 | Cleared session logs user out | ✅ Pass | |
| TC38 | Session-hijacking attempt → rejected | ✅ Pass | Flask signed cookie tamper protection confirmed |

---

## 5. Security

| TC | Description | Result | Notes |
|---|---|---|---|
| TC39 | SQL injection → fails safely | ✅ Pass | SQLAlchemy ORM escaping applied automatically |
| TC40 | XSS payload → not executed | ✅ Pass | Jinja2 auto-escaping active; script rendered as plain text |
| TC41 | Weak password `12345678` → evaluated per policy | ✅ Pass | Rejected — no letters present |
| TC42 | Passwords stored as hashes | ✅ Pass | `pbkdf2:sha256` confirmed in database |
| TC43 | Missing CSRF token → request rejected | ✅ Pass | PowerShell: `Bad Request — The CSRF token is missing` |

---

## 6. Skills Module

| TC | Description | Result | Notes |
|---|---|---|---|
| TC1 | Add skill successfully | ✅ Pass | |
| TC2 | Add empty skill → error shown | ✅ Pass | |
| TC3 | Add duplicate skill → blocked | ✅ Pass | Backend uniqueness constraint added on `name + level` |
| TC4 | Oversized skill input | ✅ Pass | Character limit enforced; over-limit input rejected |
| TC5 | Delete skill | ✅ Pass | |
| TC6 | Unauthenticated access to `/skills` → redirect | ✅ Pass | |

---

## 7. Requests Module

| TC | Description | Result | Notes |
|---|---|---|---|
| TC7 | Send request successfully (status: pending) | ✅ Pass | |
| TC8 | Request own skill → disabled | ✅ Pass | Button greyed out |
| TC9 | Duplicate request → not created | ✅ Pass | |
| TC10 | Accept request → status changes to accepted | ✅ Pass | |
| TC11 | Invalid request ID → 404 | ✅ Pass | |
| TC12 | Unauthenticated request API call → 401 | ✅ Pass | |

---

## 8. Chat Module

| TC | Description | Result | Notes |
|---|---|---|---|
| TC13 | Send message successfully | ✅ Pass | |
| TC14 | Send empty message → not sent | ✅ Pass | |
| TC15 | Missing CSRF token → 400 | ✅ Pass | |
| TC16 | Load message history | ✅ Pass | |
| TC17 | Access another user's chat → rejected | ✅ Pass | Returns: `Not an accepted connection` |
| TC18 | Oversized message → blocked | ✅ Pass | 500-character limit enforced frontend and backend |
| TC_C1 | Switching contacts updates chat view | ✅ Pass | |
| TC_C2 | Long username does not overflow | ✅ Pass | |
| TC_C3 | Input cleared after send | ✅ Pass | |
| TC_C4 | Message list auto-scrolls | ✅ Pass | |
| TC_C5 | Single contact opened by default | ✅ Pass | |
| TC_C6 | Send button disabled with no connection | ✅ Pass | |
| TC_C7 | Message bubble direction and colour correct | ✅ Pass | |

---

## 9. Profile Module

| TC | Description | Result | Notes |
|---|---|---|---|
| TC19 | View profile page | ✅ Pass | |
| TC20 | Update bio successfully | ✅ Pass | |
| TC21 | Add skill to profile | ✅ Pass | |
| TC22 | Access `/profile/2` (another user) → 403/404 | ✅ Pass | |
| TC23 | Unauthenticated access to profile → redirect | ✅ Pass | |
| TC24 | Empty bio update → no error | ✅ Pass | |
| TC_P1 | Avatar initials display | ✅ Pass | Single-character usernames intentionally duplicate letter; unsupported symbols show default `US` placeholder |
| TC_P2 | Empty bio shows placeholder text | ✅ Pass | |
| TC_P3 | Edit Profile saves and takes effect | ✅ Pass | |
| TC_P4 | Skill list shows complete information | ✅ Pass | |
| TC_P5 | Skill edit functionality | ✅ Pass | |
| TC_P6 | Skill deletion requires confirmation | ✅ Pass | |
| TC_P7 | Adding skill updates list immediately | ✅ Pass | |
| TC_P8 | Badge colours consistent | ✅ Pass | |
| TC_P9 | No-skill state shows guide prompt | ✅ Pass | |

---

## 10. Settings Module

| TC | Description | Result | Notes |
|---|---|---|---|
| TC25 | Update name successfully | ✅ Pass | Settings update persists correctly |
| TC26 | Duplicate name → error shown | ✅ Pass | Duplicate prevention validated |
| TC27 | Update full name with special characters | ✅ Pass | Full-name editing supported; nickname managed via Profile page |
| TC28 | Oversized name → error shown | ✅ Pass | `Length` validation enforced |
| TC29 | Change takes effect immediately | ✅ Pass | Flash success message shown; UI reflects update |
| TC30 | Unauthenticated access to settings → redirect | ✅ Pass | |

---

## 11. Cross-Module Integration

| TC | Description | Result |
|---|---|---|
| TC_X1 | Accepted connection appears in both users' Chat lists | ✅ Pass |
| TC_X2 | Sent request visible in Sent list | ✅ Pass |
| TC_X3 | Deleted skill disappears from browse page | ✅ Pass |
| TC_X4 | Nickname change propagates site-wide | ✅ Pass |

---

## Automated Test Results

### Unit Tests (`tests/unit_tests.py`) — 11 / 11 Pass

| Test | Description | Result |
|---|---|---|
| test_password_hashing | Correct password accepted | ✅ Pass |
| test_wrong_password_rejected | Wrong password rejected | ✅ Pass |
| test_user_saved_to_db | User persisted to database | ✅ Pass |
| test_duplicate_email_rejected | Duplicate email raises IntegrityError | ✅ Pass |
| test_skill_linked_to_user | Skill FK links to user correctly | ✅ Pass |
| test_multiple_skills_per_user | Multiple skills stored correctly | ✅ Pass |
| test_avatar_initials_two_names | Two-word name → two initials | ✅ Pass |
| test_avatar_initials_single_name | Single word → first two chars | ✅ Pass |
| test_avatar_initials_empty | Empty name → `??` | ✅ Pass |
| test_normalize_avatar_initials | Normalisation uppercases correctly | ✅ Pass |
| test_user_repr | `__repr__` returns expected string | ✅ Pass |

### Selenium UI Tests (`tests/selenium_tests.py`) — 7 / 7 Pass

| Test | Description | Result |
|---|---|---|
| test_login_page_loads | Login page renders correctly | ✅ Pass |
| test_signup_page_loads | Signup page renders correctly | ✅ Pass |
| test_login_with_invalid_credentials | Invalid credentials show error | ✅ Pass |
| test_login_with_valid_credentials | Valid credentials redirect to Skills | ✅ Pass |
| test_protected_page_redirects_to_login | Unauthenticated redirect works | ✅ Pass |
| test_signup_link_goes_to_signup | Sign Up link navigates correctly | ✅ Pass |
| test_login_link_on_signup_page | Login link navigates correctly | ✅ Pass |