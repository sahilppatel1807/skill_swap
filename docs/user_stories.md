# User Stories - SkillSwap Web Application

## Overview
This document outlines the key user stories for the SkillSwap Web Application. These stories describe how university students will interact with the system and guide development priorities for the MVP.

---

## User Stories

### US-01: User Registration
**As a new student**, I want to create an account so that I can join the SkillSwap platform.

**Acceptance Criteria:**
- User can enter name, email, and password
- System validates required fields and email format
- Password is securely stored using hashing
- User account is successfully created and saved

---

### US-02: User Login
**As a registered student**, I want to log in so that I can access my account and use platform features.

**Acceptance Criteria:**
- User can enter email and password
- System verifies credentials
- User is redirected to the homepage or profile after successful login
- Error message is shown for invalid login details

---

### US-03: User Logout
**As a logged-in user**, I want to log out so that my account remains secure.

**Acceptance Criteria:**
- Logout option is available to logged-in users
- Clicking logout ends the user session
- User is redirected to the homepage or login page

---

### US-04: Create and Manage Profile
**As a student**, I want to create and update my profile so that other students can learn about me.

**Acceptance Criteria:**
- User can add or update profile details such as name, course, and bio
- Profile information is saved correctly
- Updated profile details are displayed on the profile page

---

### US-05: Add Skill
**As a student**, I want to list skills I can teach so that other students can request help from me.

**Acceptance Criteria:**
- User can enter skill name, category, level, and description
- Form validation is applied to required fields
- Skill is saved and displayed on the user's profile
- Skill is visible to other users in the skills listing

---

### US-06: Browse Skills
**As a user**, I want to browse skills posted by other students so that I can find learning opportunities.

**Acceptance Criteria:**
- Skills are displayed in a clear list or grid
- Each skill shows relevant details such as name, category, level, and owner
- Page loads efficiently and is easy to navigate

---

### US-07: Search and Filter Skills
**As a user**, I want to search and filter skills so that I can quickly find skills that match my interests.

**Acceptance Criteria:**
- Search input is available on the skills page
- Users can search by keyword, skill name, or category
- Results update based on the search or filter criteria
- Only relevant skills are displayed

---

### US-08: View Skill Details
**As a user**, I want to view detailed information about a skill so that I can decide whether to request an exchange.

**Acceptance Criteria:**
- User can view skill name, category, level, description, and owner details
- Information is presented in a readable layout
- Logged-in users can request a skill exchange from the skill details or listing view

---

### US-09: Edit/Delete Own Skills
**As a student**, I want to edit or delete my own skill posts so that I can manage my content.

**Acceptance Criteria:**
- Edit and delete options are available only for the skill owner
- User can update skill details successfully
- Deleted skills are removed from the system
- Other users cannot edit or delete skills they do not own

---

### US-10: Send Skill Exchange Request
**As a student**, I want to send a skill exchange request so that I can connect with another student.

**Acceptance Criteria:**
- Logged-in user can send a request for another user's skill
- User can include a message with the request
- Request is saved with a pending status
- Skill owner can view the incoming request

---

### US-11: Manage Skill Exchange Requests
**As a student**, I want to accept or decline requests so that I can control who I connect with.

**Acceptance Criteria:**
- User can view received and sent requests
- Incoming requests show requester details, skill details, and message
- User can accept or decline incoming requests
- Request status updates correctly after action is taken

---

### US-12: Chat After Accepted Request
**As a student**, I want to message another student after an accepted request so that we can arrange the skill exchange.

**Acceptance Criteria:**
- Chat is available between users with an accepted request
- User can send and receive messages
- Messages are stored and displayed in conversation order
- Users without an accepted connection cannot access the chat conversation

---

### US-13: Account Settings
**As a user**, I want to update my account settings so that I can keep my account information accurate and secure.

**Acceptance Criteria:**
- User can change name, email, and password
- System validates updated information
- Password changes require secure password handling
- User can delete their account if needed

---

### US-14: Responsive Design
**As a user**, I want the website to work on different devices so that I can use SkillSwap anywhere.

**Acceptance Criteria:**
- Layout adapts to mobile, tablet, and desktop screens
- Navigation remains usable on smaller screens
- Forms, skill cards, request pages, and chat interface remain readable
- No broken or overlapping UI elements

---

## Notes
- These user stories will guide MVP development for the SkillSwap platform.
- Additional features may be added in later iterations.
- The main focus is helping university students discover, share, and exchange skills in a simple and secure way.
