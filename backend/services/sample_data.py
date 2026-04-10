"""
Sample ticket data for testing and demonstration.
"""
from typing import List
from backend.schemas import SampleTicket


SAMPLE_TICKETS: List[SampleTicket] = [
    SampleTicket(
        id="ticket-001",
        title="Unable to connect to database from application",
        description="Our main application is unable to connect to the PostgreSQL database. Users are seeing timeout errors when trying to login. This started happening about 2 hours ago. We haven't made any configuration changes recently.",
        expected_issue_type="database",
        expected_priority="high"
    ),
    SampleTicket(
        id="ticket-002",
        title="VPN users cannot access internal portal",
        description="Multiple employees working remotely report they cannot access the internal company portal through VPN. They can connect to VPN successfully but get a 'connection refused' error when trying to open internal URLs. This is affecting about 50 remote workers.",
        expected_issue_type="network",
        expected_priority="high"
    ),
    SampleTicket(
        id="ticket-003",
        title="Production application returns HTTP 500",
        description="The production web application is returning HTTP 500 errors to all users. The error started at 9 AM today. Users cannot access the dashboard. We deployed a new version last night but rolled back but issue persists.",
        expected_issue_type="application",
        expected_priority="critical"
    ),
    SampleTicket(
        id="ticket-004",
        title="Need access to production server",
        description="I need sudo access to the production web server (prod-web-01) to investigate the 500 errors. My employee ID is 12345 and I'm a senior DevOps engineer. Manager approval pending.",
        expected_issue_type="access/request",
        expected_priority="medium"
    ),
    SampleTicket(
        id="ticket-005",
        title="Linux server CPU usage is 98 percent",
        description="Production server prod-db-01 is showing 98% CPU usage. The server is very slow to respond. We have multiple PostgreSQL queries running but they usually complete quickly. Checked processes but nothing obvious stands out.",
        expected_issue_type="server",
        expected_priority="high"
    ),
    SampleTicket(
        id="ticket-006",
        title="Email password reset request",
        description="I forgot my password and need a reset. I tried the self-service portal but it's not sending me the reset email. I've checked my spam folder too. My username is jsmith.",
        expected_issue_type="access/request",
        expected_priority="low"
    ),
    SampleTicket(
        id="ticket-007",
        title="Network latency to US-East region",
        description="We're experiencing high latency (300ms+) when connecting to our US-East cloud resources. This started this morning. European connections seem fine. Internal network team has been notified.",
        expected_issue_type="network",
        expected_priority="medium"
    ),
    SampleTicket(
        id="ticket-008",
        title="Database replication lag",
        description="Our read replica is 30 minutes behind the primary database. This is causing stale data for some reporting queries. The replication process appears to be running but very slow.",
        expected_issue_type="database",
        expected_priority="medium"
    ),
    SampleTicket(
        id="ticket-009",
        title="Application crash on startup",
        description="The mobile app crashes immediately after opening. Version 2.5.0 was released yesterday. We've received 200+ crash reports. iOS and Android both affected.",
        expected_issue_type="application",
        expected_priority="high"
    ),
    SampleTicket(
        id="ticket-010",
        title="Request for admin access to analytics platform",
        description="Our marketing team needs admin access to the analytics dashboard to create custom reports. There are 5 team members who need this access. Business justification: Q2 reporting requirements.",
        expected_issue_type="access/request",
        expected_priority="low"
    ),
    SampleTicket(
        id="ticket-011",
        title="Web server unreachable",
        description="We cannot ping or SSH to web-server-01. The server is not responding to any network requests. No alerts were triggered. This is the main front-end server.",
        expected_issue_type="server",
        expected_priority="critical"
    ),
    SampleTicket(
        id="ticket-012",
        title="Strange login attempts detected",
        description="Security monitoring detected multiple failed login attempts from external IP addresses to our VPN gateway. About 500 attempts in the last hour. No successful logins observed. Should we block these IPs?",
        expected_issue_type="network",
        expected_priority="high"
    )
]