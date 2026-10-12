import type { Status } from '../types'

export const fixture: Status = {
  "product": "bldg-os",
  "goal": "Montana runs on BLDG OS alone",
  "targetSetOn": "2026-10-11",
  "checkedAt": "2026-10-11T14:00:00.000Z",
  "flags": [
    {
      "id": "procore",
      "name": "Procore off",
      "jobs": [
        {
          "id": "P1",
          "name": "Submittals",
          "short": "submittals",
          "state": "not_yet",
          "stuck": false,
          "since": "2026-10-01",
          "evidence": "0 submittal.create events in 14 days",
          "needs": "",
          "source": "eos/rocks.md, Rock M2",
          "proofKind": "owner_press"
        },
        {
          "id": "P2",
          "name": "RFIs",
          "short": "RFIs",
          "state": "moved",
          "stuck": false,
          "since": "2026-09-20",
          "evidence": "31 rfi.create events, no new procore_rfis rows for 14 days",
          "needs": "",
          "source": "eos/processes/05-project-management.md",
          "proofKind": "data"
        },
        {
          "id": "P3",
          "name": "Daily reports and photos",
          "short": "daily reports",
          "state": "not_yet",
          "stuck": false,
          "since": "2026-10-05",
          "evidence": "daily_report.submit seen on 2 of 9 projects",
          "needs": "",
          "source": "eos/processes/06-supervision.md",
          "proofKind": "data"
        },
        {
          "id": "P4",
          "name": "Timecards",
          "short": "timecards",
          "state": "gray",
          "stuck": false,
          "since": "2026-10-11",
          "evidence": "procore_timecard_entries mirror is not readable",
          "needs": "",
          "source": "PROCORE_CUTOVER_PLAN.md",
          "proofKind": "data"
        },
        {
          "id": "P5",
          "name": "Punch lists",
          "short": "punch lists",
          "state": "not_yet",
          "stuck": false,
          "since": "2026-10-01",
          "evidence": "",
          "needs": "",
          "source": "eos/processes/07-experience.md",
          "proofKind": "owner_press"
        },
        {
          "id": "P6",
          "name": "Owner change orders",
          "short": "change orders",
          "state": "not_yet",
          "stuck": false,
          "since": "2026-10-01",
          "evidence": "",
          "needs": "",
          "source": "eos/processes/05-project-management.md",
          "proofKind": "owner_press"
        },
        {
          "id": "P7",
          "name": "One project key for accounting",
          "short": "project key",
          "state": "not_yet",
          "stuck": true,
          "since": "2026-06-12",
          "evidence": "16 foreign keys still point at the Procore id",
          "needs": "Option A or B",
          "source": "PROCORE_CUTOVER_PLAN.md, #22",
          "proofKind": "schema"
        },
        {
          "id": "P8",
          "name": "Commitments made in BLDG OS",
          "short": "commitments",
          "state": "not_yet",
          "stuck": false,
          "since": "2026-10-01",
          "evidence": "",
          "needs": "P7",
          "source": "PROCORE_CUTOVER_PLAN.md",
          "proofKind": "data"
        },
        {
          "id": "P9",
          "name": "Sync off",
          "short": "sync off",
          "state": "not_yet",
          "stuck": false,
          "since": "2026-10-01",
          "evidence": "orgs.procore_sync_paused is false",
          "needs": "P1 to P8",
          "source": "PROCORE_CUTOVER_PLAN.md, #25",
          "proofKind": "flag"
        }
      ]
    },
    {
      "id": "quickbooks",
      "name": "QuickBooks off",
      "jobs": [
        {
          "id": "Q1",
          "name": "Chart of accounts and opening balances loaded",
          "short": "opening balances",
          "state": "moved",
          "stuck": false,
          "since": "2026-10-08",
          "evidence": "trial balance signed off 2026-10-08",
          "needs": "",
          "source": "ACCOUNTING_SPEC.md §3",
          "proofKind": "owner_press"
        },
        {
          "id": "Q2",
          "name": "AP bills re-keyed",
          "short": "AP bills",
          "state": "not_yet",
          "stuck": false,
          "since": "2026-10-08",
          "evidence": "qb_entry_queue AP count is 12",
          "needs": "Q1",
          "source": "migration 337",
          "proofKind": "data"
        },
        {
          "id": "Q3",
          "name": "AR billings and receipts re-keyed",
          "short": "AR billings",
          "state": "not_yet",
          "stuck": false,
          "since": "2026-10-08",
          "evidence": "qb_entry_queue AR count is 4",
          "needs": "Q1",
          "source": "migration 337",
          "proofKind": "data"
        },
        {
          "id": "Q4",
          "name": "Journal entries re-keyed",
          "short": "journal entries",
          "state": "not_yet",
          "stuck": false,
          "since": "2026-10-08",
          "evidence": "qb_entry_queue journal count is 7",
          "needs": "Q1",
          "source": "migration 337",
          "proofKind": "data"
        },
        {
          "id": "Q5",
          "name": "Bank reconciliation",
          "short": "bank rec",
          "state": "not_yet",
          "stuck": false,
          "since": "2026-10-01",
          "evidence": "",
          "needs": "Q2 to Q4",
          "source": "ACCOUNTING_SPEC.md §4.7",
          "proofKind": "owner_press"
        },
        {
          "id": "Q6",
          "name": "Payroll",
          "short": "payroll",
          "state": "gray",
          "stuck": false,
          "since": "2026-10-11",
          "evidence": "no data trail",
          "needs": "deductions list from Lynn",
          "source": "ACCOUNTING_SPEC.md §4.6, §8",
          "proofKind": "owner_press"
        },
        {
          "id": "Q7",
          "name": "Scorecard P&L, cash and AR aging read from BLDG OS",
          "short": "scorecard",
          "state": "not_yet",
          "stuck": false,
          "since": "2026-10-01",
          "evidence": "",
          "needs": "Q2 to Q4",
          "source": "eos/scorecard.md",
          "proofKind": "config"
        },
        {
          "id": "Q8",
          "name": "1099s and year-end close",
          "short": "1099s",
          "state": "not_yet",
          "stuck": false,
          "since": "2026-10-01",
          "evidence": "",
          "needs": "Q1",
          "source": "ACCOUNTING_SPEC.md §4.10, §4.21",
          "proofKind": "owner_press"
        }
      ]
    },
    {
      "id": "other",
      "name": "Other tools off",
      "note": "No other tools are on the map yet.",
      "jobs": []
    }
  ],
  "roads": [
    {
      "id": "A",
      "name": "One project key",
      "from": "P7",
      "crossesOff": [
        "P7"
      ],
      "unlocks": [
        "P9"
      ],
      "source": "PROCORE_CUTOVER_PLAN.md, #22"
    },
    {
      "id": "B",
      "name": "Drop the Procore photo archive",
      "from": "P3",
      "crossesOff": [],
      "unlocks": [],
      "source": "eos/processes/06-supervision.md"
    }
  ],
  "decisions": [
    "Option A or B for the project key",
    "When Montana Housing Builders merges into MCC"
  ]
}
