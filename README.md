FestGate — Smart Event Access & Ticket Validation System
A serverless ticketing and entry-management backend built on AWS, designed for college fests and multi-day events. FestGate issues secure, tamper-proof QR tickets and validates them at the gate in real time, enforcing expiry and per-ticket visit limits without any manual checking.
Problem Statement
Event organizers need a way to sell tickets and control venue access without manually checking names at the door, and without the risk of forged or reused tickets. Multi-day events (like a 3-day fest) also need tickets that work across several days, not just once.
Architecture
```
Client (Browser)
      |
      v
 API Gateway (REST, dev stage)
      |
      +--> POST /buy-ticket  --> Lambda (festgate-buy-ticket)
      |                              |
      |                              +--> DynamoDB (FestGateTicket) -- stores ticket record
      |                              +--> S3 (QR code image, pre-signed URL)
      |                              +--> SendGrid (emails ticket to buyer)
      |
      +--> POST /scan-ticket --> Lambda (festgate-scan-ticket)
                                     |
                                     +--> DynamoDB (verify + decrement visits_remaining)
```
AWS Services Used
Service	Purpose
API Gateway	Public REST endpoints for ticket purchase and validation
AWS Lambda	Serverless compute — JWT signing/verification, business logic
DynamoDB	Stores ticket records: buyer info, visit count, expiry, status
S3	Stores generated QR code images, served via pre-signed URLs
SES / SendGrid	Emails the QR ticket to the buyer automatically
Why serverless? No servers to provision or manage — Lambda and DynamoDB scale automatically during entry rushes and cost nothing when idle, which fits a student project with unpredictable, bursty traffic.
Why DynamoDB? The access pattern is simple key-based lookups (`ticket_id` → record), which DynamoDB is optimized for, with millisecond latency for the live gate-scanning scenario.
Key Features
Signed JWT tickets — each ticket is a cryptographically signed JSON Web Token, so it cannot be forged or edited without detection
Multi-day visit counter — a ticket can be scanned multiple times (e.g., a 3-day pass), decrementing `visits_remaining` on each successful scan
Automatic expiry — tickets embed an `exp` claim and are rejected automatically once the event ends
Pre-signed S3 URLs — QR code images are served via time-limited signed links rather than a public bucket
Input validation — missing required fields return a clean `400` response instead of crashing
API Endpoints
`POST /buy-ticket`
Request body:
```json
{ "buyer_email": "user@email.com", "event_id": "FEST2026", "visits_allowed": 3 }
```
Response:
```json
{ "ticket_id": "TCK-a1b2c3d4", "qr_url": "https://...", "token": "eyJhbGc..." }
```
`POST /scan-ticket`
Request body:
```json
{ "token": "eyJhbGc..." }
```
Response (approved):
```json
{ "status": "approved", "ticket_id": "TCK-a1b2c3d4", "visits_remaining": 2 }
```
Response (denied):
```json
{ "status": "denied", "reason": "No visits remaining" }
```
Tech Stack
Backend: Python 3.14 (AWS Lambda)
Libraries: PyJWT, qrcode, Pillow, boto3, sendgrid
Frontend: Plain HTML/CSS/JavaScript (no framework), calling the API directly via `fetch()`
Infra: AWS API Gateway, Lambda, DynamoDB, S3, SES/SendGrid
Project Structure
```
festgate-backend/
  lambda_buy_ticket/     — Ticket purchase Lambda source + dependencies
  lambda_scan_ticket/    — Ticket validation Lambda source + dependencies
  frontend/              — Simple HTML demo interface
  docs/                  — Architecture diagram, report, screenshots
  .env                   — Local environment variables (gitignored, not committed)
```
Edge Cases Handled
Expired ticket → `403 Ticket expired`
Tampered/invalid JWT signature → `403 Invalid or tampered ticket`
Ticket not found → `404 Ticket not found`
No visits remaining → `403 No visits remaining`
Missing required purchase fields → `400 Missing required fields`
Security Notes
JWT secret and API keys are stored as Lambda environment variables, never hardcoded in source
QR images are accessed via pre-signed, time-limited S3 URLs rather than a public bucket
`.env` file is excluded from version control via `.gitignore`
Future Improvements
Admin dashboard for real-time check-in analytics
Ticket transfer/resale with re-signing
SMS delivery as an alternative to email
