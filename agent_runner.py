import json
import os
from datetime import datetime, timedelta
from modules.gemini_client import generate_response

def run_agents(db, note):
    agents_path = os.path.join("mcp", "agents.json")
    if not os.path.exists(agents_path):
        print("Agents configuration file not found.")
        return
    with open(agents_path) as f:
        agents = json.load(f)
    for agent_name, agent_config in agents.items():
        trigger = agent_config.get("trigger")
        action = agent_config.get("action")
        if trigger and action:
            if check_trigger(trigger, note):
                perform_action(action, note, db)

def check_trigger(trigger, note):
    if trigger.startswith("tag:"):
        tag_condition = trigger[4:]
        if tag_condition == "[]":
            return not note.get("tags")
        else:
            return tag_condition in note.get("tags", [])
    return False

def add_to_calendar(db, note):
    title = note["title"]
    content = note["content"]
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)
    
    try:
        # Create a more detailed ICS file
        description = content.replace(chr(10), '\\n')
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//AI Notes App//Calendar Event//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:{note['_id']}@ai-notes-app
DTSTAMP:{datetime.now().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{start_time.strftime('%Y%m%dT%H%M%S')}
DTEND:{end_time.strftime('%Y%m%dT%H%M%S')}
SUMMARY:{title}
DESCRIPTION:{description}
STATUS:CONFIRMED
SEQUENCE:0
END:VEVENT
END:VCALENDAR
"""
        
        # Create calendar directory if it doesn't exist
        calendar_dir = "calendar_events"
        if not os.path.exists(calendar_dir):
            os.makedirs(calendar_dir)
        
        # Save individual event file
        event_file = os.path.join(calendar_dir, f"event_{note['_id']}.ics")
        with open(event_file, "w", encoding="utf-8") as f:
            f.write(ics_content)
        
        # Append to main calendar file
        with open("reminders.ics", "a", encoding="utf-8") as f:
            f.write(ics_content + "\n")
        
        print(f"📅 Added to calendar: {title}")
        print(f"📄 Event file: {event_file}")
        print(f"⏰ Scheduled for: {start_time.strftime('%Y-%m-%d %H:%M')}")
        
    except Exception as e:
        print(f"❌ Failed to add to calendar: {e}")

def share_to_whatsapp(db, note):
    title = note["title"]
    content = note["content"]
    message = f"📝 Shared Note: {title}\n\n{content}\n\n---\nShared via AI Notes App"
    
    try:
        # Log the share attempt with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] WhatsApp Share: {title}\nMessage: {message}\n\n"
        
        with open("whatsapp_shares.log", "a", encoding="utf-8") as f:
            f.write(log_entry)
        
        # In a real implementation, you would integrate with WhatsApp Business API
        # For now, we'll create a share file that can be used with WhatsApp Web
        share_file = f"whatsapp_share_{note['_id']}.txt"
        with open(share_file, "w", encoding="utf-8") as f:
            f.write(message)
        
        print(f"✅ Shared to WhatsApp: {title}")
        print(f"📄 Share file created: {share_file}")
        print(f"💡 Copy the content and paste it into WhatsApp Web or your phone")
        
    except Exception as e:
        print(f"❌ Failed to share to WhatsApp: {e}")

def rephrase_note(db, note):
    try:
        content = note["content"]
        prompt = f"Rephrase the following note: {content}"
        new_content = generate_response(prompt)
        db["notes"].update_one({"_id": note["_id"]}, {"$set": {"content": new_content, "updated_at": datetime.utcnow()}})
        print(f"Rephrased note {note['_id']}")
    except Exception as e:
        print(f"Failed to rephrase note {note['_id']}: {e}")

def suggest_tags(db, note):
    try:
        content = note["content"]
        prompt = f"Suggest 1 to 3 tags for this note: {content}"
        suggested_tags = generate_response(prompt).split(",")
        suggested_tags = [tag.strip() for tag in suggested_tags]
        current_tags = note.get("tags", [])
        new_tags = list(set(current_tags + suggested_tags))
        db["notes"].update_one({"_id": note["_id"]}, {"$set": {"tags": new_tags}})
        print(f"Suggested tags for note {note['_id']}: {suggested_tags}")
    except Exception as e:
        print(f"Failed to suggest tags for note {note['_id']}: {e}")

action_functions = {
    "calendar_event": add_to_calendar,
    "share_to_whatsapp": share_to_whatsapp,
    "rephrase_with_gemini": rephrase_note,
    "suggest_tags": suggest_tags,
}

def perform_action(action, note, db):
    func = action_functions.get(action)
    if func:
        func(db, note)
    else:
        print(f"Unknown action: {action}")