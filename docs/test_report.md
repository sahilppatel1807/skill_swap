# SkillSwap — Automated Test Report

**Date:** 16 May 2026
**Python Version:** 3.8.1
**Framework:** pytest 8.3.5

---

## Summary

| Suite | Total | Passed | Failed | Duration |
|---|---|---|---|---|
| Unit Tests (`unit_tests.py`) | 19 | 19 | 0 | 8.28s |
| Selenium E2E Tests (`selenium_tests.py`) | 10 | 10 | 0 | 37.83s |
| **Total** | **29** | **29** | **0** | **~46s** |

All 29 automated tests passed. ✅

---

## Unit Tests — 19 / 19 Pass

### Registration (`RegistrationTests`)

| Test | Description | Result |
|---|---|---|
| test_valid_signup | Valid fields register successfully | ✅ Pass |
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
| test_accept_request | Request accepted, status updated | ✅ Pass |
| test_duplicate_request_rejected | Duplicate request blocked | ✅ Pass |
| test_cannot_request_own_skill | Own skill request blocked | ✅ Pass |

### Chat (`ChatTests`)

| Test | Description | Result |
|---|---|---|
| test_send_message | Message sent successfully | ✅ Pass |
| test_empty_message_rejected | Empty message blocked | ✅ Pass |
| test_no_connection_rejected | Unconnected user chat access blocked | ✅ Pass |
| test_message_history | Message history loads correctly | ✅ Pass |

---

## Selenium E2E Tests — 10 / 10 Pass

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

Two non-critical warnings were raised during the test run, both related to deprecated SQLAlchemy API usage:

> `LegacyAPIWarning: The Query.get() method is considered legacy as of the 1.x series of SQLAlchemy`

This does not affect functionality. The affected calls (`User.query.get()`) should be migrated to `db.session.get(User, id)` in a future update.

---

## Test Coverage Map

| Manual Test Case | Covered by Automated Test |
|---|---|
| TC1–TC3 (valid registration) | `test_valid_signup` |
| TC8 (duplicate email) | `test_duplicate_email_rejected`, `test_02_duplicate_email_shows_error` |
| TC9 (duplicate nickname) | `test_duplicate_nickname_rejected` |
| TC7 (password mismatch) | `test_password_mismatch_rejected` |
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
| TC13 (send message) | `test_send_message` |
| TC14 (empty message) | `test_empty_message_rejected` |
| TC17 (unconnected chat) | `test_no_connection_rejected` |
| TC16 (message history) | `test_message_history` |
| TC_X1 (chat connection) | `test_10_chat_page_shows_connection` |