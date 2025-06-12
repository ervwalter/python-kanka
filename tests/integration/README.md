# Kanka SDK Integration Tests

These integration tests verify that the python-kanka SDK works correctly with the real Kanka API.

## ⚠️ WARNING

**These tests create and delete real data in your Kanka campaign!**

All test entities will be created with names containing:
- "Integration Test"
- "DELETE ME"
- A timestamp

The tests attempt to clean up after themselves, but if a test fails, you may need to manually delete test entities from your campaign.

## Prerequisites

1. A Kanka account with an active campaign
2. A Kanka API token (get one from https://kanka.io/en/settings/api)
3. The campaign ID you want to use for testing

## Setup

### 1. Set Environment Variables

You need to set two environment variables before running the tests:

```bash
export KANKA_TOKEN='your-api-token-here'
export KANKA_CAMPAIGN_ID='your-campaign-id'
```

### 2. Using a .env File (Recommended)

For convenience, create a `.env` file in the `tests/integration/` directory:

```bash
# tests/integration/.env
KANKA_TOKEN=your-api-token-here
KANKA_CAMPAIGN_ID=12345
```

The test runner automatically loads this file using `python-dotenv`, so you don't need to source it manually.

**Note:** The `.env` file is ignored by git for security.

## Running the Tests

### Run All Integration Tests

From the project root:

```bash
python tests/integration/run_integration_tests.py
```

Or make the script executable and run directly:

```bash
chmod +x tests/integration/run_integration_tests.py
./tests/integration/run_integration_tests.py
```

### Run with Pause Mode

To inspect created entities in the Kanka web app before they are cleaned up:

```bash
python tests/integration/run_integration_tests.py --pause
# or
python tests/integration/run_integration_tests.py -p
```

In pause mode:
1. All entity cleanup is deferred until the end of the test run
2. After all tests complete, you'll see a list of entities to be cleaned up
3. The script pauses, allowing you to log into Kanka and inspect the test entities
4. Press Enter in the terminal to continue with cleanup

### Run Individual Test Suites

You can also run individual test files directly. Each test file automatically loads the `.env` file if present:

```bash
# Test characters
python tests/integration/test_characters_integration.py

# Test locations
python tests/integration/test_locations_integration.py

# Test organisations
python tests/integration/test_organisations_integration.py

# Test notes
python tests/integration/test_notes_integration.py

# Test posts (sub-resources)
python tests/integration/test_posts_integration.py
```

When running individual test files, they will:
1. Automatically load environment variables from `.env` if it exists
2. Set up the Python path correctly
3. Run all tests in that file
4. Display a summary of results

## Test Coverage

The integration tests cover:

1. **Basic Entity CRUD Operations**:
   - Characters
   - Locations
   - Organisations
   - Notes

2. **Sub-resource Operations**:
   - Posts on Characters

3. **Each test suite verifies**:
   - Create operations with various fields
   - Listing with filters
   - Update operations
   - Get by ID
   - Delete operations

## Troubleshooting

### Rate Limiting

The tests include small delays between operations to avoid rate limiting. If you encounter rate limit errors, you may need to increase the delays in `base.py`.

### Cleanup Failures

If tests fail and leave entities behind:

1. Go to your Kanka campaign
2. Search for entities with "Integration Test" in the name
3. Delete them manually

### Authentication Errors

If you get authentication errors:
- Verify your API token is correct
- Check that the token has not expired
- Ensure you're using the correct campaign ID

## Adding New Tests

To add tests for a new entity type:

1. Create a new test file: `test_[entity]_integration.py`
2. Follow the pattern from existing test files
3. Import and add your test class to `run_integration_tests.py`
4. Ensure proper cleanup in the `teardown()` method

## Best Practices

1. **Always use unique names**: Include timestamps to avoid conflicts
2. **Clean up after tests**: Use try/finally blocks to ensure cleanup
3. **Use descriptive names**: Make it clear these are test entities
4. **Handle failures gracefully**: Don't let one test failure break all tests
5. **Be patient**: Allow time for the API to process changes

## Questions or Issues?

If you encounter problems with the integration tests, please:

1. Check that your credentials are correct
2. Verify you have permissions in the campaign
3. Look for any remaining test entities in your campaign
4. Report issues with full error output
