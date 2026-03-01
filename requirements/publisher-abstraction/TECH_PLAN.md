# Tech Plan: Publisher Abstraction (T1: Lib-Init)

## 📋 Status
- **Current Phase:** Phase 1 (Migration & Abstraction)
- **Status:** Initialized Repository and defined Core Interfaces.

## 🏗 Repository Structure
- `social_media_publisher/`: Root package.
    - `models.py`: Pydantic/Dataclass schemas for standardized post requests.
    - `publishers/`: Contains platform-specific implementations.
        - `base.py`: `BasePublisher` abstract class.
        - `rednote.py`: (Pending) Rednote implementation using Selenium.

## 🎯 Implementation Strategy

### 1. Data Modeling
- Implement `SocialPost` schema to unify posting requests.
- Ensure validation of image paths and auth credentials before attempting publication.

### 2. Base Interface
- `BasePublisher` defines `login()` and `publish(post: SocialPost)`.
- Error handling should be standardized across publishers (custom exception classes).

### 3. Rednote Publisher Migration
- Migrate `uploaders/selenium.py` from the legacy repo.
- Refactor the existing logic to fit the `BasePublisher` interface.
- Implement session management (saving/loading cookies).

### 4. Dependency Management
- Primary dependencies: `selenium`, `webdriver-manager`, `pydantic` (optional but recommended), `pytest`.
- Use `requirements.txt` for initial development.

## 🧪 Testing Plan
- Mock the Selenium WebDriver to test the `publish` logic without opening a real browser.
- Create a test suite under `tests/` for validating the `SocialPost` schema.

## 🔗 Integration with Rednote Automation
- Once `social-media-publisher` is stable, `rednote-automation` will be updated to include this repo as a dependency (likely via `pip install -e` during dev).
- Refactor `runner.py` in the main project to pass content in the new standardized JSON format.

## 📅 Milestones
1. [x] Repository Initialization & Directory Structure.
2. [x] Definition of `BasePublisher` and `SocialPost` models.
3. [ ] Migration and Refactoring of Rednote Publisher logic.
4. [ ] Integration testing with a dummy/test Rednote account.
5. [ ] OpenClaw Skill development.
