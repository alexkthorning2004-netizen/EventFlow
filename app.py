import streamlit as st
import json
from dataclasses import dataclass, field

# ── Load Test Data ────────────────────────────────────────────────────────────

@st.cache_data
def load_test_data():
    with open("eventflow_test_data.json", encoding="utf-8") as f:
        return json.load(f)

TEST_DATA = load_test_data()

# ── Data Models ───────────────────────────────────────────────────────────────

@dataclass
class Review:
    id: str
    user_name: str
    user_id: str
    rating: int
    comment: str
    date: str

@dataclass
class Message:
    id: str
    user_name: str
    user_id: str
    content: str
    timestamp: str

@dataclass
class Event:
    id: str
    title: str
    host: str
    host_user_id: str
    time: str
    attendees: int
    spots_left: int
    rating: float
    category: str
    max_attendees: int
    description: str = ""
    distance: str = ""
    mode: str = "In-Person"
    reviews: list = field(default_factory=list)
    messages: list = field(default_factory=list)
    registered_user_ids: list = field(default_factory=list)

@dataclass
class Achievement:
    id: str
    title: str
    description: str
    icon: str
    earned: bool
    progress: int = 0
    max_progress: int = 1

# ── Build Data from JSON ──────────────────────────────────────────────────────

def build_events():
    events = {}
    for e in TEST_DATA["events"]:
        reviews = [
            Review(r["id"], r["user_name"], r.get("user_id", ""), r["rating"], r["comment"], r["date"])
            for r in e.get("reviews", [])
        ]
        messages = [
            Message(m["id"], m["user_name"], m["user_id"], m["content"], m["timestamp"])
            for m in e.get("messages", [])
        ]
        events[e["id"]] = Event(
            id=e["id"], title=e["title"], host=e["host"],
            host_user_id=e.get("host_user_id", ""),
            time=e["time"], attendees=e["attendees"],
            spots_left=e["spots_left"], rating=e["rating"],
            category=e["category"], max_attendees=e["max_attendees"],
            description=e.get("description", ""),
            distance=e.get("distance", ""), mode=e.get("mode", "In-Person"),
            reviews=reviews, messages=messages,
            registered_user_ids=list(e.get("registered_user_ids", []))
        )
    return events

def build_achievements_for_user(user):
    earned_ids = user.get("achievements_earned", [])
    achievements = []
    for a in TEST_DATA["achievements"]:
        earned = a["id"] in earned_ids
        progress = a["max_progress"] if earned else min(user["events_attended"], a["max_progress"] - 1)
        achievements.append(Achievement(
            id=a["id"], title=a["title"], description=a["description"],
            icon=a["icon"], earned=earned, progress=progress,
            max_progress=a["max_progress"]
        ))
    return achievements

CATEGORIES = ["All", "Sports", "Study", "Arts", "Social", "Wellness", "Tech"]

# ── Session State ─────────────────────────────────────────────────────────────

def init_state():
    if "events" not in st.session_state:
        st.session_state.events = build_events()
    if "activity_feed" not in st.session_state:
        st.session_state.activity_feed = [
            {"user": "Chloe Dupont",    "action": "hosted",       "target": "Yoga in the Park",      "time": "2 hours ago", "icon": "🎤"},
            {"user": "Jordan Kim",      "action": "joined",       "target": "Coding Bootcamp Q&A",   "time": "3 hours ago", "icon": "✅"},
            {"user": "Nadia Tremblay",  "action": "reviewed",     "target": "Group Study Night",     "time": "4 hours ago", "icon": "⭐"},
            {"user": "Marcus Lee",      "action": "joined",       "target": "Board Game Night",      "time": "5 hours ago", "icon": "✅"},
            {"user": "Sofia Reyes",     "action": "commented on", "target": "Photography Walk",      "time": "6 hours ago", "icon": "💬"},
            {"user": "Amara Osei",      "action": "joined",       "target": "Yoga in the Park",      "time": "7 hours ago", "icon": "✅"},
            {"user": "Priya Sharma",    "action": "reviewed",     "target": "Coding Bootcamp Q&A",   "time": "8 hours ago", "icon": "⭐"},
        ]
    defaults = {
        "profile_created": False, "screen": "events",
        "selected_event_id": None, "notifications": [],
        "user_name": "", "user_id": "", "user_location": "",
        "category_filter": "All", "user_interests": [],
        "user_achievements": [], "user_stats": {},
        "user_settings": {}, "prev_screen": "events"
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def add_activity(action, target, icon):
    st.session_state.activity_feed.insert(0, {
        "user": st.session_state.user_name,
        "action": action, "target": target,
        "time": "Just now", "icon": icon
    })
    st.session_state.activity_feed = st.session_state.activity_feed[:20]

def add_notification(title, message):
    nid = f"n_{len(st.session_state.notifications) + 1}"
    st.session_state.notifications.insert(0, {
        "id": nid, "title": title,
        "message": message, "time": "Just now", "read": False
    })

def check_achievements():
    attended = st.session_state.user_stats.get("events_attended", 0)
    thresholds = {"1": 1, "2": 5, "3": 10}
    for ach in st.session_state.user_achievements:
        if not ach.earned and ach.id in thresholds:
            if attended >= thresholds[ach.id]:
                ach.earned = True
                ach.progress = ach.max_progress
                add_notification("🎉 Achievement unlocked!", f'You earned "{ach.title}"')
                add_activity("earned the achievement", ach.title, "🏆")
            else:
                ach.progress = min(attended, ach.max_progress)

# ── User Select ───────────────────────────────────────────────────────────────

def show_profile_creation():
    st.markdown("<h1 style='text-align:center'>📅 EventFlow</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:gray'>Select a test user to begin</p>", unsafe_allow_html=True)
    st.divider()

    user_options = {f"{u['name']} — {u['location']}": u for u in TEST_DATA["users"]}
    chosen_label = st.selectbox("Choose a test user", list(user_options.keys()))
    selected_user = user_options[chosen_label]

    with st.container(border=True):
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"### {selected_user['name']}")
            st.caption(f"📍 {selected_user['location']}")
            st.caption(f"❤️ {', '.join(selected_user['interests'])}")
        with col2:
            st.metric("Attended", selected_user["events_attended"])
            st.metric("Hosted", selected_user["events_hosted"])
        col3, col4 = st.columns(2)
        with col3:
            earned = len(selected_user["achievements_earned"])
            st.metric("Achievements", f"{earned}/{len(TEST_DATA['achievements'])}")
        with col4:
            unread = sum(1 for n in selected_user["notifications"] if not n["read"])
            st.metric("Notifications", f"🔔 {unread}")

    if st.button("Log in as this user →", type="primary", use_container_width=True):
        st.session_state.profile_created = True
        st.session_state.user_name = selected_user["name"]
        st.session_state.user_id = selected_user["id"]
        st.session_state.user_location = selected_user["location"]
        st.session_state.notifications = list(selected_user["notifications"])
        st.session_state.user_interests = list(selected_user["interests"])
        st.session_state.user_achievements = build_achievements_for_user(selected_user)
        st.session_state.user_stats = {
            "events_attended": selected_user["events_attended"],
            "events_hosted": selected_user["events_hosted"],
        }
        st.session_state.user_settings = dict(selected_user["settings"])
        st.rerun()

# ── Top Bar ───────────────────────────────────────────────────────────────────

def show_top_bar():
    unread = sum(1 for n in st.session_state.notifications if not n["read"])
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        st.markdown(f"**📅 EventFlow** &nbsp; *{st.session_state.user_name}*", unsafe_allow_html=True)
    with col2:
        bell = f"🔔 {unread}" if unread else "🔔"
        if st.button(bell, use_container_width=True):
            st.session_state.prev_screen = st.session_state.screen
            st.session_state.screen = "notifications"
            st.rerun()
    with col3:
        if st.button("⚙️", use_container_width=True):
            st.session_state.prev_screen = st.session_state.screen
            st.session_state.screen = "settings"
            st.rerun()
    with col4:
        if st.button("🔄", use_container_width=True, help="Switch user"):
            st.session_state.profile_created = False
            st.session_state.screen = "events"
            st.rerun()
    st.divider()

# ── Bottom Nav ────────────────────────────────────────────────────────────────

def show_bottom_nav():
    st.divider()
    cols = st.columns(5)
    nav = [("🏠", "Events", "events"), ("🧭", "Interests", "discover"),
           ("📡", "Feed", "feed"), ("📊", "Stats", "analytics"), ("👤", "Profile", "profile")]
    for col, (icon, label, screen) in zip(cols, nav):
        with col:
            if st.button(f"{icon} {label}", use_container_width=True, key=f"nav_{screen}"):
                st.session_state.screen = screen
                st.rerun()

# ── Events Screen ─────────────────────────────────────────────────────────────

def show_events():
    st.subheader("Upcoming Events")
    st.session_state.category_filter = st.radio(
        "Category", CATEGORIES, horizontal=True,
        index=CATEGORIES.index(st.session_state.category_filter),
        label_visibility="collapsed"
    )
    events = list(st.session_state.events.values())
    filtered = events if st.session_state.category_filter == "All" \
        else [e for e in events if e.category == st.session_state.category_filter]

    if not filtered:
        st.info("No events found for this category.")
        return

    uid = st.session_state.user_id
    for event in filtered:
        joined = uid in event.registered_user_ids
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                badge = " ✅" if joined else ""
                st.markdown(f"**{event.title}**{badge}")
                st.caption(f"🏷️ {event.category}  |  🕐 {event.time}  |  📡 {event.mode}")
                loc = f"📍 {event.distance}" if event.distance else "🌐 Online"
                st.caption(f"{loc}  |  👥 {event.attendees}/{event.max_attendees}  |  ⭐ {event.rating}")
                st.caption(f"💬 {len(event.messages)} messages  |  📝 {len(event.reviews)} reviews  |  🪑 {event.spots_left} spots")
            with col2:
                if st.button("View →", key=f"view_{event.id}", use_container_width=True):
                    st.session_state.selected_event_id = event.id
                    st.session_state.screen = "detail"
                    st.rerun()

# ── Event Detail ──────────────────────────────────────────────────────────────

def show_event_detail():
    eid = st.session_state.selected_event_id
    if not eid or eid not in st.session_state.events:
        st.session_state.screen = "events"
        st.rerun()
        return

    event = st.session_state.events[eid]
    uid = st.session_state.user_id
    uname = st.session_state.user_name
    joined = uid in event.registered_user_ids

    if st.button("← Back to Events"):
        st.session_state.screen = "events"
        st.rerun()

    st.markdown(f"# {event.title}")
    st.caption(f"Hosted by **{event.host}**  |  🏷️ {event.category}  |  📡 {event.mode}")

    col1, col2, col3 = st.columns(3)
    col1.metric("Rating", f"⭐ {event.rating}")
    col2.metric("Attendees", f"{event.attendees}/{event.max_attendees}")
    col3.metric("Spots Left", event.spots_left)

    st.divider()
    st.markdown(f"**🕐 Time:** {event.time}")
    if event.distance:
        st.markdown(f"**📍 Distance:** {event.distance}")
    st.write(event.description or "No description provided.")

    st.divider()
    if joined:
        col1, col2 = st.columns(2)
        with col1:
            st.success("✅ You're attending this event")
        with col2:
            if st.button("Leave Event", use_container_width=True, key=f"leave_{eid}"):
                event.registered_user_ids.remove(uid)
                event.attendees -= 1
                event.spots_left += 1
                st.session_state.user_stats["events_attended"] = max(0, st.session_state.user_stats["events_attended"] - 1)
                add_activity("left", event.title, "👋")
                add_notification("Left event", f"You left {event.title}")
                st.rerun()
    else:
        if event.spots_left > 0:
            if st.button("✅ Join Event", type="primary", use_container_width=True, key=f"join_{eid}"):
                event.registered_user_ids.append(uid)
                event.attendees += 1
                event.spots_left -= 1
                st.session_state.user_stats["events_attended"] += 1
                add_activity("joined", event.title, "✅")
                add_notification("Joined event!", f"You joined {event.title}. See you there!")
                check_achievements()
                st.rerun()
        else:
            st.warning("This event is full.")

    st.divider()
    tab1, tab2 = st.tabs([f"💬 Messages ({len(event.messages)})", f"⭐ Reviews ({len(event.reviews)})"])

    with tab1:
        if event.messages:
            for msg in event.messages:
                is_me = msg.user_id == uid
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        label = "**You**" if is_me else f"**{msg.user_name}**"
                        st.markdown(label)
                        st.write(msg.content)
                    with col2:
                        st.caption(msg.timestamp)
        else:
            st.info("No messages yet. Be the first!")

        st.markdown("**Post a message**")
        msg_text = st.text_area("Message", key=f"msg_input_{eid}",
                                label_visibility="collapsed",
                                placeholder="Ask a question or say hello...")
        if st.button("Send 💬", key=f"send_{eid}"):
            if msg_text.strip():
                new_msg = Message(
                    id=f"m_{len(event.messages)+1}",
                    user_name=uname, user_id=uid,
                    content=msg_text.strip(), timestamp="Just now"
                )
                event.messages.append(new_msg)
                add_activity("commented on", event.title, "💬")
                add_notification("Message sent!", f"Your message was posted to {event.title}")
                st.rerun()
            else:
                st.warning("Message can't be empty.")

    with tab2:
        if event.reviews:
            for rev in event.reviews:
                is_me = rev.user_id == uid
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        label = "**You**" if is_me else f"**{rev.user_name}**"
                        st.markdown(f"{label} — {'⭐' * rev.rating}")
                        st.write(rev.comment)
                    with col2:
                        st.caption(rev.date)
        else:
            st.info("No reviews yet.")

        already_reviewed = any(r.user_id == uid for r in event.reviews)
        if joined and not already_reviewed:
            st.markdown("**Leave a Review**")
            rating = st.slider("Rating", 1, 5, 5, key=f"rating_{eid}")
            st.caption("⭐" * rating)
            review_text = st.text_area("Review", key=f"rev_input_{eid}",
                                       label_visibility="collapsed",
                                       placeholder="Share your experience...")
            if st.button("Submit Review ⭐", key=f"subrev_{eid}"):
                if review_text.strip():
                    new_rev = Review(
                        id=f"r_{len(event.reviews)+1}",
                        user_name=uname, user_id=uid,
                        rating=rating, comment=review_text.strip(), date="Just now"
                    )
                    event.reviews.append(new_rev)
                    all_ratings = [r.rating for r in event.reviews]
                    event.rating = round(sum(all_ratings) / len(all_ratings), 1)
                    add_activity("reviewed", event.title, "⭐")
                    add_notification("Review posted!", f"Your {rating}⭐ review of {event.title} was submitted")
                    st.rerun()
                else:
                    st.warning("Review can't be empty.")
        elif joined and already_reviewed:
            st.info("✅ You've already reviewed this event.")
        else:
            st.caption("*Join this event to leave a review.*")

# ── Activity Feed ─────────────────────────────────────────────────────────────

def show_feed():
    st.subheader("📡 Activity Feed")
    st.caption("Live activity from all users")
    st.divider()

    if not st.session_state.activity_feed:
        st.info("No activity yet.")
        return

    for item in st.session_state.activity_feed:
        with st.container(border=True):
            col1, col2 = st.columns([5, 1])
            with col1:
                is_me = item["user"] == st.session_state.user_name
                user_display = "**You**" if is_me else f"**{item['user']}**"
                st.markdown(f"{item['icon']} {user_display} {item['action']} *{item['target']}*")
            with col2:
                st.caption(item["time"])

# ── Discover / Interests ──────────────────────────────────────────────────────

def show_discover():
    st.subheader("🧭 Your Interests")
    all_interests = ["Sports", "Study", "Arts", "Social", "Wellness", "Tech", "Music", "Food", "Travel", "Gaming"]
    selected = []
    cols = st.columns(3)
    for i, interest in enumerate(all_interests):
        with cols[i % 3]:
            if st.checkbox(interest, value=interest in st.session_state.user_interests, key=f"int_{interest}"):
                selected.append(interest)

    if st.button("Save Interests", type="primary", use_container_width=True):
        st.session_state.user_interests = selected
        st.success("Interests saved!")

    st.divider()
    st.subheader("✨ Recommended for You")
    recs = [e for e in st.session_state.events.values()
            if e.category in st.session_state.user_interests and e.spots_left > 0]
    if recs:
        for event in recs[:3]:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{event.title}**")
                    st.caption(f"🏷️ {event.category}  |  🕐 {event.time}  |  🪑 {event.spots_left} spots left")
                with col2:
                    if st.button("View", key=f"rec_{event.id}", use_container_width=True):
                        st.session_state.selected_event_id = event.id
                        st.session_state.screen = "detail"
                        st.rerun()
    else:
        st.info("No recommendations — try selecting more interests above.")

# ── Profile ───────────────────────────────────────────────────────────────────

def show_profile():
    st.subheader(f"👤 {st.session_state.user_name}")
    st.caption(f"📍 {st.session_state.user_location}  |  ❤️ {', '.join(st.session_state.user_interests)}")

    stats = st.session_state.user_stats
    earned = sum(1 for a in st.session_state.user_achievements if a.earned)
    col1, col2, col3 = st.columns(3)
    col1.metric("Attended", stats.get("events_attended", 0))
    col2.metric("Hosted", stats.get("events_hosted", 0))
    col3.metric("Achievements", f"{earned}/{len(st.session_state.user_achievements)}")

    st.divider()
    st.subheader("📅 Events You've Joined")
    uid = st.session_state.user_id
    joined_events = [e for e in st.session_state.events.values() if uid in e.registered_user_ids]
    if joined_events:
        for event in joined_events:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{event.title}**")
                    st.caption(f"🕐 {event.time}  |  🏷️ {event.category}")
                with col2:
                    if st.button("View", key=f"pev_{event.id}", use_container_width=True):
                        st.session_state.selected_event_id = event.id
                        st.session_state.screen = "detail"
                        st.rerun()
    else:
        st.info("You haven't joined any events yet.")

    st.divider()
    st.subheader("🏆 Achievements")
    for ach in st.session_state.user_achievements:
        with st.container(border=True):
            col1, col2 = st.columns([1, 5])
            with col1:
                st.markdown(f"## {ach.icon}")
            with col2:
                status = "✅ Earned" if ach.earned else f"🔒 {ach.progress}/{ach.max_progress}"
                st.markdown(f"**{ach.title}** — {status}")
                st.caption(ach.description)
                if not ach.earned and ach.max_progress > 1:
                    st.progress(ach.progress / ach.max_progress)

# ── Analytics ─────────────────────────────────────────────────────────────────

def show_analytics():
    st.subheader("📊 Your Activity")

    stats = st.session_state.user_stats
    uid = st.session_state.user_id
    earned = sum(1 for a in st.session_state.user_achievements if a.earned)
    total_msgs = sum(1 for e in st.session_state.events.values() for m in e.messages if m.user_id == uid)
    total_revs = sum(1 for e in st.session_state.events.values() for r in e.reviews if r.user_id == uid)

    col1, col2, col3 = st.columns(3)
    col1.metric("Events Attended", stats.get("events_attended", 0))
    col2.metric("Events Hosted", stats.get("events_hosted", 0))
    col3.metric("Achievements", f"{earned}/{len(st.session_state.user_achievements)}")

    col4, col5 = st.columns(2)
    col4.metric("Messages Posted", total_msgs)
    col5.metric("Reviews Written", total_revs)

    st.divider()
    st.subheader("Events Joined by Category")
    joined_events = [e for e in st.session_state.events.values() if uid in e.registered_user_ids]
    if joined_events:
        cat_counts = {}
        for e in joined_events:
            cat_counts[e.category] = cat_counts.get(e.category, 0) + 1
        data = pd.DataFrame({"Category": list(cat_counts.keys()), "Events": list(cat_counts.values())})
        st.bar_chart(data.set_index("Category"))
    else:
        st.info("Join some events to see your category breakdown.")

    st.divider()
    st.subheader("Your Recent Activity")
    my_activity = [a for a in st.session_state.activity_feed if a["user"] == st.session_state.user_name]
    if my_activity:
        for item in my_activity[:5]:
            st.markdown(f"{item['icon']} {item['action'].capitalize()} *{item['target']}* — {item['time']}")
    else:
        st.info("No personal activity yet. Join an event to get started!")

# ── Notifications ─────────────────────────────────────────────────────────────

def show_notifications():
    if st.button("← Back"):
        st.session_state.screen = st.session_state.get("prev_screen", "events")
        st.rerun()

    st.subheader("🔔 Notifications")
    unread = [n for n in st.session_state.notifications if not n["read"]]
    if unread:
        if st.button("Mark all as read"):
            for n in st.session_state.notifications:
                n["read"] = True
            st.rerun()

    if not st.session_state.notifications:
        st.info("No notifications yet.")
        return

    for n in st.session_state.notifications:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            with col1:
                prefix = "🔵 " if not n["read"] else ""
                st.markdown(f"{prefix}**{n['title']}**")
                st.caption(f"{n['message']}  ·  {n['time']}")
            with col2:
                if not n["read"]:
                    if st.button("✓", key=f"read_{n['id']}"):
                        n["read"] = True
                        st.rerun()

# ── Settings ──────────────────────────────────────────────────────────────────

def show_settings():
    if st.button("← Back"):
        st.session_state.screen = st.session_state.get("prev_screen", "events")
        st.rerun()

    st.subheader("⚙️ Settings")
    settings = st.session_state.get("user_settings", {})

    dist = st.slider("Max distance (mi)", 1, 20, settings.get("max_distance_mi", 5))
    size = st.slider("Max group size", 2, 100, settings.get("max_group_size", 20))
    notifs = st.toggle("Enable notifications", value=settings.get("notifications_enabled", True))

    if st.button("Save Settings", type="primary"):
        st.session_state.user_settings = {
            "max_distance_mi": dist,
            "max_group_size": size,
            "notifications_enabled": notifs
        }
        st.success("Settings saved!")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(page_title="EventFlow", page_icon="📅", layout="centered")
    init_state()

    if not st.session_state.profile_created:
        show_profile_creation()
        return

    show_top_bar()
    screen = st.session_state.screen

    if   screen == "events":          show_events()
    elif screen == "detail":          show_event_detail()
    elif screen == "discover":        show_discover()
    elif screen == "feed":            show_feed()
    elif screen == "profile":         show_profile()
    elif screen == "analytics":       show_analytics()
    elif screen == "notifications":   show_notifications()
    elif screen == "settings":        show_settings()

    if screen not in ("notifications", "settings", "detail"):
        show_bottom_nav()

if __name__ == "__main__":
    main()
