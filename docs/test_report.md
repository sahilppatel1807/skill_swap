# SkillSwap — Automated Test Report

**Date:** 17 May 2026  
**Python Version:** 3.13  
**Framework:** `unittest` (Python standard library)

---

## Summary

| Suite | Total | Passed | Failed | Duration |
|---|---|---|---|---|
| Unit Tests (`unit_tests.py`) | 23 | 23 | 0 | ~5.3s |
| Selenium E2E Tests (`selenium_tests.py`) | 10 | 10 | 0 | ~15.2s |
| **Total** | **33** | **33** | **0** | **~21s** |

All 33 automated tests passed. ✅

### How to reproduce

```bash
python -m unittest tests.unit_tests -v
python -m unittest tests.selenium_tests -v   # requires Chrome + ChromeDriver
```

---

## Unit Tests — 23 / 23 Pass

### Registration (`RegistrationTests`)

| Test | Description | Result |
|---|---|---|
| test_valid_signup | Valid fields register successfully | ✅ Pass |
| test_non_student_email_rejected | Non-`@student.uwa.edu.au` email blocked | ✅ Pass |
| test_duplicate_email_rejected | Duplicate email blocked | ✅ Pass |
| test_duplicate_nickname_rejected | Duplicate nickname blocked | ✅ Pass |
| test_password_mismatch_rejected | Mismatched confirm password blocked | ✅ Pass |

### Login (`LoginTests`)

| Test | Description | Result |
|---|---|---|
| test_login_with_email | Login with email and correct password | ✅ Pass |
| test_login_with_nickname | Login with nickname and correct password | ✅ Pass |
| test_wrong_password_rejected | Wrong password blocked | ✅ Pass |
| test_logout_clears_session | Logout clears session correctly | ✅ Pass |

### Skills (`SkillsTests`)

| Test | Description | Result |
|---|---|---|
| test_add_skill | Skill added successfully | ✅ Pass |
| test_empty_skill_name_rejected | Empty skill name blocked | ✅ Pass |
| test_unauthenticated_redirects | Unauthenticated access redirects to login | ✅ Pass |

### Requests (`RequestsTests`)

| Test | Description | Result |
|---|---|---|
| test_send_request | Request sent with status pending | ✅ Pass |
| test_cannot_request_own_skill | Own skill request blocked | ✅ Pass |
| test_duplicate_request_rejected | Duplicate request blocked | ✅ Pass |
| test_accept_request | Request accepted, status updated | ✅ Pass |
| test_accepting_one_skill_accepts_other_pending_from_same_user | Accepting one request accepts other pending from same user | ✅ Pass |
| test_connected_user_shows_accepted_on_all_skills | Connected user's skills show Accepted on browse page | ✅ Pass |
| test_cannot_request_another_skill_when_already_connected | New request blocked when already connected | ✅ Pass |

### Chat (`ChatTests`)

| Test | Description | Result |
|---|---|---|
| test_send_message | Message sent successfully | ✅ Pass |
| test_empty_message_rejected | Empty message blocked | ✅ Pass |
| test_no_connection_rejected | Unconnected user chat access blocked | ✅ Pass |
| test_message_history | Message history loads correctly | ✅ Pass |

---

## Selenium E2E Tests — 10 / 10 Pass

Selenium tests start a live Flask server on port **5001** and drive Chrome.

| Test | Description | Result |
|---|---|---|
| test_01_valid_signup | User signs up with valid credentials | ✅ Pass |
| test_02_duplicate_email_shows_error | Duplicate email shows error message | ✅ Pass |
| test_03_login_valid_credentials | Login redirects to Skills page | ✅ Pass |
| test_04_login_invalid_credentials | Invalid credentials show error | ✅ Pass |
| test_05_protected_route_redirects | Unauthenticated access redirects to login | ✅ Pass |
| test_06_add_skill_appears_in_grid | Added skill appears in browse grid | ✅ Pass |
| test_07_send_request_updates_button | Request button updates to Requested | ✅ Pass |
| test_08_own_skill_button_disabled | Own skill button is greyed out | ✅ Pass |
| test_09_accept_request_shows_badge | Accepted request shows Accepted badge | ✅ Pass |
| test_10_chat_page_shows_connection | Accepted connection appears in Chat | ✅ Pass |

---

## Warnings

Non-critical warnings may appear during the test run:

- **Flask-Limiter:** in-memory rate-limit storage (expected in test/dev).
- **SQLAlchemy:** `LegacyAPIWarning` for `Query.get()` and `datetime.utcnow()` deprecation.

These do not affect test outcomes or application behaviour.

---

## Test Coverage Map

| Manual Test Case | Covered by Automated Test |
|---|---|
| TC1–TC3 (valid registration) | `test_valid_signup`, `test_01_valid_signup` |
| TC8 (duplicate email) | `test_duplicate_email_rejected`, `test_02_duplicate_email_shows_error` |
| TC9 (duplicate nickname) | `test_duplicate_nickname_rejected` |
| TC7 (password mismatch) | `test_password_mismatch_rejected` |
| Non-student email | `test_non_student_email_rejected` |
| TC15–TC16 (login) | `test_login_with_email`, `test_login_with_nickname`, `test_03_login_valid_credentials` |
| TC18 (wrong password) | `test_wrong_password_rejected`, `test_04_login_invalid_credentials` |
| TC28–TC29 (auth redirect) | `test_unauthenticated_redirects`, `test_05_protected_route_redirects` |
| TC37 (logout) | `test_logout_clears_session` |
| Skill TC1 (add skill) | `test_add_skill`, `test_06_add_skill_appears_in_grid` |
| Skill TC2 (empty skill) | `test_empty_skill_name_rejected` |
| TC7 (send request) | `test_send_request`, `test_07_send_request_updates_button` |
| TC8 (own skill disabled) | `test_cannot_request_own_skill`, `test_08_own_skill_button_disabled` |
| TC9 (duplicate request) | `test_duplicate_request_rejected` |
| TC10 (accept request) | `test_accept_request`, `test_09_accept_request_shows_badge` |
| Person-level connections | `test_accepting_one_skill_accepts_other_pending_from_same_user`, `test_connected_user_shows_accepted_on_all_skills`, `test_cannot_request_another_skill_when_already_connected` |
| TC13 (send message) | `test_send_message` |
| TC14 (empty message) | `test_empty_message_rejected` |
| TC17 (unconnected chat) | `test_no_connection_rejected` |
| TC16 (message history) | `test_message_history` |
| TC_X1 (chat connection) | `test_10_chat_page_shows_connection` |
