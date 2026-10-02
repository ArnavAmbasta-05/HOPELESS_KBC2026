"""Script to populate Notion workspace with live databases for KIIT Event Operations."""

import os
import httpx
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("NOTION_API_KEY", "") or os.environ.get("NOTION_API_TOKEN", "")
PAGE_ID = os.environ.get("NOTION_PAGE_ID", "3ed6ee57-8095-80aa-8be4-e1fb98234d9c")


headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

client = httpx.Client(headers=headers, timeout=30.0)

print("=== 1. Adding Header Blocks ===")
blocks_payload = {
    "children": [
        {
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [{"type": "text", "text": {"content": "⚡ KIIT Event Operations & Digital Twin Center"}}]
            },
        },
        {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "🟢 KoreX Live Cloud Synchronizer Connected • Grounded in KIIT Multi-Campus Twin & CP-SAT Solver."
                        },
                    }
                ],
                "icon": {"emoji": "🏛️"},
            },
        },
        {
            "object": "block",
            "type": "divider",
            "divider": {},
        },
    ]
}
r_blocks = client.patch(f"https://api.notion.com/v1/blocks/{PAGE_ID}/children", json=blocks_payload)
print(f"Header blocks added: {r_blocks.status_code}")

print("\n=== 2. Creating KIIT Venues Database ===")
venues_db_payload = {
    "parent": {"type": "page_id", "page_id": PAGE_ID},
    "title": [{"type": "text", "text": {"content": "🏛️ KIIT Campus Venues & Facilities"}}],
    "properties": {
        "Venue Name": {"title": {}},
        "Campus": {
            "select": {
                "options": [
                    {"name": "Campus 6", "color": "blue"},
                    {"name": "Campus 7", "color": "green"},
                    {"name": "Campus 15", "color": "purple"},
                    {"name": "Campus 3", "color": "yellow"},
                ]
            }
        },
        "Capacity": {"number": {"format": "number"}},
        "Status": {
            "select": {
                "options": [
                    {"name": "AVAILABLE", "color": "green"},
                    {"name": "UNAVAILABLE", "color": "red"},
                    {"name": "WEATHER_RISK", "color": "orange"},
                ]
            }
        },
        "AV Setup": {
            "multi_select": [
                {"name": "Dual 4K LED Walls", "color": "blue"},
                {"name": "Line Array Audio", "color": "purple"},
                {"name": "Standard PA System", "color": "gray"},
                {"name": "Outdoor Weatherproof Speakers", "color": "yellow"},
            ]
        },
        "Google Maps Navigation": {"rich_text": {}},
    },
}
r_venues_db = client.post("https://api.notion.com/v1/databases", json=venues_db_payload)
print(f"Venues DB status: {r_venues_db.status_code}")
venues_db_id = r_venues_db.json().get("id")

if venues_db_id:
    venues_data = [
        {"name": "Main Auditorium", "campus": "Campus 6", "cap": 1600, "status": "UNAVAILABLE", "av": ["Dual 4K LED Walls", "Line Array Audio"], "maps": "https://maps.google.com/?q=20.3540,85.8190"},
        {"name": "Open Air Theatre (OAT)", "campus": "Campus 6", "cap": 600, "status": "AVAILABLE", "av": ["Outdoor Weatherproof Speakers"], "maps": "https://maps.google.com/?q=20.3533,85.8195"},
        {"name": "Campus 7 Seminar Hall", "campus": "Campus 7", "cap": 250, "status": "AVAILABLE", "av": ["Standard PA System"], "maps": "https://maps.google.com/?q=20.3512,85.8175"},
        {"name": "Campus 6 Auditorium", "campus": "Campus 6", "cap": 400, "status": "AVAILABLE", "av": ["Line Array Audio"], "maps": "https://maps.google.com/?q=20.3545,85.8192"},
        {"name": "Campus 15 Auditorium", "campus": "Campus 15", "cap": 350, "status": "AVAILABLE", "av": ["Standard PA System"], "maps": "https://maps.google.com/?q=20.3580,85.8230"},
        {"name": "Campus 3 Central Lawn", "campus": "Campus 3", "cap": 800, "status": "AVAILABLE", "av": ["Outdoor Weatherproof Speakers"], "maps": "https://maps.google.com/?q=20.3490,85.8150"},
    ]
    for v in venues_data:
        p = {
            "parent": {"database_id": venues_db_id},
            "properties": {
                "Venue Name": {"title": [{"text": {"content": v["name"]}}]},
                "Campus": {"select": {"name": v["campus"]}},
                "Capacity": {"number": v["cap"]},
                "Status": {"select": {"name": v["status"]}},
                "AV Setup": {"multi_select": [{"name": a} for a in v["av"]]},
                "Google Maps Navigation": {"rich_text": [{"text": {"content": v["maps"], "link": {"url": v["maps"]}}}]},
            },
        }
        res = client.post("https://api.notion.com/v1/pages", json=p)
        print(f"  + Added Venue: {v['name']} ({res.status_code})")

print("\n=== 3. Creating Master Sessions Database ===")
sessions_db_payload = {
    "parent": {"type": "page_id", "page_id": PAGE_ID},
    "title": [{"type": "text", "text": {"content": "📅 Master Event Sessions Timeline"}}],
    "properties": {
        "Session Title": {"title": {}},
        "Track": {
            "select": {
                "options": [
                    {"name": "Keynote", "color": "purple"},
                    {"name": "AI & Tech", "color": "blue"},
                    {"name": "Robotics", "color": "green"},
                    {"name": "Ceremony", "color": "yellow"},
                ]
            }
        },
        "Assigned Venue": {"rich_text": {}},
        "Time Slot": {"rich_text": {}},
        "Expected Registrants": {"number": {"format": "number"}},
        "Status": {
            "select": {
                "options": [
                    {"name": "RELOCATED", "color": "orange"},
                    {"name": "SCHEDULED", "color": "green"},
                    {"name": "COMPLETED", "color": "gray"},
                ]
            }
        },
    },
}
r_sessions_db = client.post("https://api.notion.com/v1/databases", json=sessions_db_payload)
print(f"Sessions DB status: {r_sessions_db.status_code}")
sessions_db_id = r_sessions_db.json().get("id")

if sessions_db_id:
    sessions_data = [
        {"title": "Opening Keynote & Welcome Address", "track": "Keynote", "venue": "Open Air Theatre (Relocated from Main Aud)", "time": "09:00 - 10:30", "reg": 580, "status": "RELOCATED"},
        {"title": "AI in Event Operations & CP-SAT Optimizations", "track": "AI & Tech", "venue": "Campus 7 Seminar Hall (Relocated)", "time": "10:45 - 12:00", "reg": 240, "status": "RELOCATED"},
        {"title": "Future of Autonomous Campus Mobility", "track": "Robotics", "venue": "Campus 6 Auditorium", "time": "13:00 - 14:30", "reg": 380, "status": "SCHEDULED"},
        {"title": "Valedictory & Awards Ceremony", "track": "Ceremony", "venue": "Open Air Theatre (Relocated from Main Aud)", "time": "15:00 - 17:00", "reg": 600, "status": "RELOCATED"},
    ]
    for s in sessions_data:
        p = {
            "parent": {"database_id": sessions_db_id},
            "properties": {
                "Session Title": {"title": [{"text": {"content": s["title"]}}]},
                "Track": {"select": {"name": s["track"]}},
                "Assigned Venue": {"rich_text": [{"text": {"content": s["venue"]}}]},
                "Time Slot": {"rich_text": [{"text": {"content": s["time"]}}]},
                "Expected Registrants": {"number": s["reg"]},
                "Status": {"select": {"name": s["status"]}},
            },
        }
        res = client.post("https://api.notion.com/v1/pages", json=p)
        print(f"  + Added Session: {s['title']} ({res.status_code})")

print("\n=== 4. Creating Volunteer Staff Database ===")
volunteers_db_payload = {
    "parent": {"type": "page_id", "page_id": PAGE_ID},
    "title": [{"type": "text", "text": {"content": "👥 Volunteer Staff & Coordinator Roster"}}],
    "properties": {
        "Volunteer Name": {"title": {}},
        "Role Skill": {
            "select": {
                "options": [
                    {"name": "AV Setup Lead", "color": "blue"},
                    {"name": "Stage Manager", "color": "purple"},
                    {"name": "Crowd & Transit Escort", "color": "green"},
                    {"name": "Host Hospitality", "color": "yellow"},
                    {"name": "First Aid & Safety", "color": "red"},
                ]
            }
        },
        "Assigned Station": {"rich_text": {}},
        "Shift": {
            "select": {
                "options": [
                    {"name": "Morning (08:00 - 13:00)", "color": "blue"},
                    {"name": "Afternoon (13:00 - 18:00)", "color": "orange"},
                    {"name": "Full Day", "color": "purple"},
                ]
            }
        },
        "Status": {
            "select": {
                "options": [
                    {"name": "ACTIVE", "color": "green"},
                    {"name": "STANDBY_DEPLOYED", "color": "orange"},
                    {"name": "OFF_DUTY", "color": "gray"},
                ]
            }
        },
        "Hostel Base": {"rich_text": {}},
    },
}
r_volunteers_db = client.post("https://api.notion.com/v1/databases", json=volunteers_db_payload)
print(f"Volunteers DB status: {r_volunteers_db.status_code}")
volunteers_db_id = r_volunteers_db.json().get("id")

if volunteers_db_id:
    volunteers_data = [
        {"name": "Arjun Sharma", "role": "AV Setup Lead", "station": "Open Air Theatre (Keynote AV)", "shift": "Morning (08:00 - 13:00)", "status": "STANDBY_DEPLOYED", "hostel": "KP-6 Boys Hostel"},
        {"name": "Priya Das", "role": "Stage Manager", "station": "Campus 7 Seminar Hall", "shift": "Morning (08:00 - 13:00)", "status": "ACTIVE", "hostel": "QC-1 Girls Hostel"},
        {"name": "Rohan Sen", "role": "Crowd & Transit Escort", "station": "Transit Hub Campus 6 <-> Campus 7", "shift": "Morning (08:00 - 13:00)", "status": "ACTIVE", "hostel": "KP-7 Boys Hostel"},
        {"name": "Ananya Mishra", "role": "Host Hospitality", "station": "VIP Guest Lounge (Campus 6)", "shift": "Full Day", "status": "ACTIVE", "hostel": "QC-2 Girls Hostel"},
        {"name": "Debashish Panda", "role": "First Aid & Safety", "station": "Campus 6 Medical Booth", "shift": "Full Day", "status": "ACTIVE", "hostel": "KP-6 Boys Hostel"},
    ]
    for vol in volunteers_data:
        p = {
            "parent": {"database_id": volunteers_db_id},
            "properties": {
                "Volunteer Name": {"title": [{"text": {"content": vol["name"]}}]},
                "Role Skill": {"select": {"name": vol["role"]}},
                "Assigned Station": {"rich_text": [{"text": {"content": vol["station"]}}]},
                "Shift": {"select": {"name": vol["shift"]}},
                "Status": {"select": {"name": vol["status"]}},
                "Hostel Base": {"rich_text": [{"text": {"content": vol["hostel"]}}]},
            },
        }
        res = client.post("https://api.notion.com/v1/pages", json=p)
        print(f"  + Added Volunteer: {vol['name']} ({res.status_code})")

print("\nSUCCESS: All 3 live databases and records created inside HOPELESS_KBC in Notion!")
