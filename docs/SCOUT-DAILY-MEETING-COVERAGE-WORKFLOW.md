# Scout Daily Accepted-Meeting Coverage Workflow

This runbook documents the weekday 6:00 AM Pacific workflow for daily accepted-meeting coverage.

## Schedule

- Run every weekday at 6:00 AM in `America/Los_Angeles`.
- Use the run date as "today".

## Identity and attendance rule

- Do not join Teams meetings live.
- Do not impersonate Fereydoun or any other identity.
- Use only accessible Microsoft 365 artifacts and calendar data.

## Execution steps

1. Query Outlook calendar for today (`00:00` to `23:59` local time).
2. Filter to meetings where Fereydoun is clearly accepted/busy.
3. Exclude declined, cancelled, free, out-of-office holds, FYI OOF items, and tentative meetings unless attendee status clearly says accepted.
4. Classify each accepted meeting:
   - Informational
   - One-on-one
   - Working/decision/collaboration
5. For informational meetings, summarize from available sources in this order:
   1. transcript/recording metadata
   2. meeting chat
   3. event body/invite
   4. related links and accessible artifacts
6. For each processed meeting, include:
   - title
   - time
   - organizer
   - classification
   - artifact availability/status
   - concise summary
   - key links/resources
   - action items
7. For one-on-one and working meetings, explicitly state:
   - the meeting was not attended
   - summary is based only on available artifacts

## Privacy constraints

- Send outputs only to `fbabaei@microsoft.com`.
- Do not expose private schedule or sensitive meeting content to others.
- Keep claims grounded strictly in retrieved calendar/invite/transcript/chat artifacts.

## Delivery steps

1. Send email to `fbabaei@microsoft.com` with subject:
   - `Daily accepted meeting report - <YYYY-MM-DD>`
2. Send a brief Teams message to Fereydoun confirming report completion and email delivery.
3. If there are no qualifying accepted informational meetings, still send a short email that:
   - lists accepted meetings reviewed
   - explains why none were summarized as informational

