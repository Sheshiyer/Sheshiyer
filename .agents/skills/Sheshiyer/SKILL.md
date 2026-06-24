```markdown
# Sheshiyer Development Patterns

> Auto-generated skill from repository analysis

## Overview
This skill teaches the core development patterns and conventions used in the Sheshiyer TypeScript codebase. You'll learn how to structure files, write imports/exports, follow commit message practices, and implement and run tests. This guide is ideal for contributors aiming for consistency and maintainability in a TypeScript project without a specific framework.

## Coding Conventions

### File Naming
- Use **camelCase** for all file names.
  - Example: `userProfile.ts`, `dataFetcher.ts`

### Import Style
- Use **relative imports** for modules within the project.
  - Example:
    ```typescript
    import { fetchData } from './dataFetcher';
    ```

### Export Style
- Use **named exports** for all modules.
  - Example:
    ```typescript
    // In userProfile.ts
    export function getUserProfile(id: string) { ... }
    ```

### Commit Messages
- **Freeform** commit messages, sometimes with prefixes.
- Average length: ~28 characters.
  - Example:
    ```
    Add user profile fetch logic
    Fix bug in data processing
    ```

## Workflows

### Code Contribution
**Trigger:** When adding or updating features or bug fixes  
**Command:** `/contribute`

1. Create a new file using camelCase naming.
2. Write your TypeScript code, using relative imports and named exports.
3. Write or update corresponding test files (`*.test.*`).
4. Commit changes with a clear, concise message.
5. Open a pull request for review.

### Writing Tests
**Trigger:** When adding new functionality or fixing bugs  
**Command:** `/write-test`

1. Create a test file named with the pattern `*.test.*` (e.g., `userProfile.test.ts`).
2. Write tests for your functions or modules.
3. Ensure tests cover edge cases and expected behavior.

### Running Tests
**Trigger:** Before pushing or merging changes  
**Command:** `/run-tests`

1. Use the project's test runner (framework unknown; check project scripts).
2. Run all `*.test.*` files.
3. Ensure all tests pass before committing.

## Testing Patterns

- Test files follow the pattern `*.test.*` (e.g., `example.test.ts`).
- The specific testing framework is unknown; check the project for configuration or scripts.
- Tests should cover all exported functions and modules.

**Example Test File:**
```typescript
import { getUserProfile } from './userProfile';

test('returns correct user profile', () => {
  const profile = getUserProfile('123');
  expect(profile.id).toBe('123');
});
```

## Commands
| Command        | Purpose                                      |
|----------------|----------------------------------------------|
| /contribute    | Guide for contributing code                  |
| /write-test    | Steps for writing new or updating tests      |
| /run-tests     | Instructions for running the test suite      |
```
