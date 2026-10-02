"""Notion Schema & Property Mapping (Sprint 6, TAD §14, BRD §20).

Maps KoreX domain model entities and attributes to Notion database properties.
Handles property conversion for Titles, Numbers, Selects, Relations, Dates, and Rich Texts.
"""

from __future__ import annotations

from typing import Any


class NotionPropertyMapper:
    """Versioned property mapper between KoreX Domain and Notion Database schemas."""

    def __init__(self, version: str = "v1.0") -> None:
        self.version = version

    # -----------------------------------------------------------------------
    # Domain -> Notion Builders
    # -----------------------------------------------------------------------

    def build_venue_properties(self, venue_id: str, name: str, building: str, capacity: int, status: str) -> dict[str, Any]:
        return {
            "Name": {"title": [{"text": {"content": name}}]},
            "Venue ID": {"rich_text": [{"text": {"content": venue_id}}]},
            "Building": {"select": {"name": building}},
            "Capacity": {"number": capacity},
            "Status": {"select": {"name": status}},
        }

    def build_session_properties(
        self,
        session_id: str,
        title: str,
        venue_id: str,
        venue_page_id: str | None,
        start_time: str,
        end_time: str,
        registrants: int,
        status: str,
    ) -> dict[str, Any]:
        props: dict[str, Any] = {
            "Title": {"title": [{"text": {"content": title}}]},
            "Session ID": {"rich_text": [{"text": {"content": session_id}}]},
            "Registrants": {"number": registrants},
            "Status": {"select": {"name": status}},
            "Time Window": {"rich_text": [{"text": {"content": f"{start_time} - {end_time}"}}]},
        }
        if venue_page_id:
            props["Venue Relation"] = {"relation": [{"id": venue_page_id}]}
        return props

    def build_volunteer_properties(
        self,
        volunteer_id: str,
        name: str,
        skills: list[str],
        assigned_venue: str,
        status: str,
    ) -> dict[str, Any]:
        return {
            "Name": {"title": [{"text": {"content": name}}]},
            "Volunteer ID": {"rich_text": [{"text": {"content": volunteer_id}}]},
            "Skills": {"multi_select": [{"name": s} for s in skills]},
            "Assigned Venue": {"select": {"name": assigned_venue}},
            "Status": {"select": {"name": status}},
        }

    def build_task_properties(
        self,
        task_id: str,
        description: str,
        assigned_to: str,
        status: str,
        slack_minutes: int,
        is_at_risk: bool,
    ) -> dict[str, Any]:
        return {
            "Task": {"title": [{"text": {"content": description}}]},
            "Task ID": {"rich_text": [{"text": {"content": task_id}}]},
            "Assigned To": {"rich_text": [{"text": {"content": assigned_to}}]},
            "Status": {"select": {"name": status}},
            "Slack (min)": {"number": slack_minutes},
            "At Risk": {"checkbox": is_at_risk},
        }

    def build_change_proposal_properties(
        self,
        proposal_id: str,
        title: str,
        status: str,
        affected_sessions_count: int,
        volunteer_shifts_count: int,
        tasks_count: int,
        summary_markdown: str,
    ) -> dict[str, Any]:
        return {
            "Title": {"title": [{"text": {"content": title}}]},
            "Proposal ID": {"rich_text": [{"text": {"content": proposal_id}}]},
            "Status": {"select": {"name": status}},
            "Relocated Sessions": {"number": affected_sessions_count},
            "Volunteer Moves": {"number": volunteer_shifts_count},
            "Generated Tasks": {"number": tasks_count},
            "Summary": {"rich_text": [{"text": {"content": summary_markdown[:2000]}}]},
        }

    def build_impact_report_properties(
        self,
        report_id: str,
        title: str,
        hard_hits_count: int,
        soft_edges_count: int,
        total_attendees_impacted: int,
        ai_summary: str,
    ) -> dict[str, Any]:
        return {
            "Title": {"title": [{"text": {"content": title}}]},
            "Report ID": {"rich_text": [{"text": {"content": report_id}}]},
            "Hard Hits": {"number": hard_hits_count},
            "Soft Edges": {"number": soft_edges_count},
            "Impacted Attendees": {"number": total_attendees_impacted},
            "AI Narrative": {"rich_text": [{"text": {"content": ai_summary[:2000]}}]},
        }

    # -----------------------------------------------------------------------
    # Notion -> Domain Extractors
    # -----------------------------------------------------------------------

    def extract_title(self, properties: dict[str, Any], field_name: str = "Title") -> str:
        prop = properties.get(field_name, {})
        title_list = prop.get("title", [])
        if title_list and isinstance(title_list, list):
            return title_list[0].get("text", {}).get("content", "")
        # fallback for Name
        name_list = properties.get("Name", {}).get("title", [])
        if name_list and isinstance(name_list, list):
            return name_list[0].get("text", {}).get("content", "")
        return ""

    def extract_select(self, properties: dict[str, Any], field_name: str) -> str | None:
        prop = properties.get(field_name, {})
        sel = prop.get("select")
        if sel and isinstance(sel, dict):
            return sel.get("name")
        return None

    def extract_number(self, properties: dict[str, Any], field_name: str) -> int | None:
        prop = properties.get(field_name, {})
        return prop.get("number")
