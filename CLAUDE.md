# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python-based AI agent demonstration that uses Google's Gemini API to create a customer support assistant for a mock travel company. The agent can query a SQLite database containing customer records, bookings, destinations, packages, payments, and support cases to help answer customer service inquiries.

## Development Environment

The project is configured to run in a Nix-based environment with a Python virtual environment at `.venv`. Dependencies are managed through `requirements.txt`.

### Setup Commands

```bash
# Activate virtual environment (required before running commands)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the CLI agent
python main.py

# Run the Flask development server
./devserver.sh
```

## Architecture

### Core Components

1. **main.py** - Main entry point for the CLI-based AI agent
   - Implements conversational loop with user
   - Calls Gemini API with function calling capabilities
   - Manages chat history and saves logs to `./chat_logs/`
   - Uses system instruction to guide agent behavior for customer support

2. **db.py** - Database generation and querying module
   - `generate_db()` - Creates SQLite database with mock travel company data (10,000 customers by default)
   - `query_db()` - Executes SELECT queries (blocks DROP operations)
   - `delete_db()` - Removes database file
   - Includes extensive verification checks for referential integrity

3. **sample_datasets/travel_company_customer_db/** - Database schema and sample data
   - `schema.sql` - Defines 6 tables: customers, destinations, packages, bookings, payments, cases
   - `data.py` - Contains extensive lists of sample data (names, cities, destinations, case types, etc.)
   - `case_descriptions.py` - Realistic case descriptions organized by case type
   - Foreign key relationships: packages → destinations, bookings → customers/packages, payments → bookings, cases → customers/bookings

4. **flask.py** - Commented out Flask boilerplate (not currently active)

### Database Schema

The SQLite database models a travel company with these relationships:
- Customers can have multiple bookings and support cases
- Bookings link customers to travel packages (which reference destinations)
- Payments are tied to bookings
- Cases can optionally link to a specific booking (70% of cases) or just a customer

Key tables:
- `customers` - Customer profiles with contact info, loyalty points
- `destinations` - Travel locations with pricing and seasonal info
- `packages` - Pre-built travel packages with duration and capacity
- `bookings` - Customer reservations with travel dates and status
- `payments` - Transaction records for bookings
- `cases` - Support tickets with type, priority, status, and assignment

### AI Agent Flow

1. User submits query via CLI
2. `call_gemini_api()` sends request to Gemini 2.5 Flash with:
   - Chat history context
   - System instruction defining customer support role
   - Function declaration for `query_db` tool
3. If Gemini calls the `query_db` function:
   - Execute SQL query against database
   - Send results back to Gemini
   - Gemini generates natural language response
4. Response displayed to user and appended to chat history

## Configuration

### Environment Variables

The project requires a `.env` file with:
- `GOOGLE_API_KEY` - Gemini API key (loaded via `python-dotenv`)

### Database Location

The database is generated at: `./sample_datasets/travel_company_customer_db/travel_company.db`

## Testing

Tests are located in `__test__/db_test.py` (run with pytest framework).

## Important Notes

- The database is generated on first run if it doesn't exist
- Chat logs are saved with timestamp filenames in `./chat_logs/`
- Type "exit" to quit the CLI agent
- The agent maintains conversation context throughout the session
- DROP operations are blocked in `query_db()` for safety
- Database generation includes referential integrity verification
