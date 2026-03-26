import streamlit as st
import pandas as pd
from dataclasses import dataclass, field

# ── Theme ─────────────────────────────────────────────────────────────────────

THEME_CSS = """
<style>
.stApp { background-color: #e0fdff; }
.stButton > button { background-color: #00EFFF !important; color: #000 !important; border: none !important; font-weight: 600 !important; border-radius: 8px !important; }
.stButton > button:hover { background-color: #00d4e6 !important; }
div[data-testid="stMetricValue"] { color: #007a8a !important; }
h1, h2, h3 { color: #006b7a !important; }
</style>
"""

# ── Personal Events ───────────────────────────────────────────────────────────

PERSONAL_EVENTS_DATA = [
    {
        "id": "e1", "title": "Basketball Pickup Game", "host": "Mike Johnson",
        "time": "Today, 6:00 PM", "attendees": 8, "spots_left": 4, "rating": 4.5,
        "category": "Sports", "max_attendees": 12, "distance": "0.3 mi", "mode": "In-Person",
        "description": "Casual pickup basketball game at the local court. All skill levels welcome!",
        "age_min": 18, "age_max": 35,
        "reviews": [
            {"id": "r1", "user_name": "Marcus Lee", "rating": 5, "comment": "Super fun, great group!", "date": "2 weeks ago"},
        ],
    },
    {
        "id": "e2", "title": "Group Study Night", "host": "Study Squad",
        "time": "Tomorrow, 7:00 PM", "attendees": 12, "spots_left": 8, "rating": 4.8,
        "category": "Study", "max_attendees": 20, "distance": "0.8 mi", "mode": "Hybrid",
        "description": "Weekly group study session. Bring your books and laptops!",
        "age_min": 16, "age_max": 30,
        "reviews": [
            {"id": "r3", "user_name": "Nadia Tremblay", "rating": 5, "comment": "Really productive session.", "date": "3 days ago"},
        ],
    },
    {
        "id": "e3", "title": "Photography Walk", "host": "Jane Smith",
        "time": "Sat, 10:00 AM", "attendees": 6, "spots_left": 2, "rating": 4.2,
        "category": "Arts", "max_attendees": 8, "distance": "1.2 mi", "mode": "In-Person",
        "description": "Explore the city through your lens. All camera types welcome.",
        "age_min": 20, "age_max": 45,
        "reviews": [
            {"id": "r4", "user_name": "Sofia Reyes", "rating": 5, "comment": "Amazing walk, learned so much!", "date": "2 weeks ago"},
        ],
    },
    {
        "id": "e4", "title": "Board Game Night", "host": "GameMasters",
        "time": "Fri, 7:30 PM", "attendees": 10, "spots_left": 5, "rating": 4.9,
        "category": "Social", "max_attendees": 15, "distance": "0.5 mi", "mode": "In-Person",
        "description": "Monthly board game extravaganza. Games provided!",
        "age_min": 18, "age_max": 40,
        "reviews": [
            {"id": "r5", "user_name": "Liam Foster", "rating": 5, "comment": "Best night out!", "date": "1 week ago"},
        ],
    },
    {
        "id": "e5", "title": "Yoga in the Park", "host": "Wellness Hub",
        "time": "Sun, 8:00 AM", "attendees": 15, "spots_left": 5, "rating": 4.7,
        "category": "Wellness", "max_attendees": 20, "distance": "0.4 mi", "mode": "In-Person",
        "description": "Start your Sunday with a peaceful yoga session outdoors.",
        "age_min": 25, "age_max": 55,
        "reviews": [
            {"id": "r6", "user_name": "Amara Osei", "rating": 5, "comment": "Very calming.", "date": "4 days ago"},
        ],
    },
    {
        "id": "e6", "title": "Coding Bootcamp Q&A", "host": "DevCircle",
        "time": "Wed, 6:00 PM", "attendees": 30, "spots_left": 20, "rating": 4.6,
        "category": "Tech", "max_attendees": 50, "distance": "", "mode": "Online",
        "description": "Open Q&A for aspiring developers. No experience needed.",
        "age_min": 18, "age_max": 35,
        "reviews": [
            {"id": "r7", "user_name": "Jordan Kim", "rating": 5, "comment": "Super helpful!", "date": "5 days ago"},
        ],
    },
]

# ── Business Events ───────────────────────────────────────────────────────────

BUSINESS_EVENTS_DATA = [
    {
        "id": "b1", "title": "Grand Opening Celebration", "host": "The Fitness Co.",
        "time": "Sat, 11:00 AM", "attendees": 45, "spots_left": 55, "rating": 4.9,
        "category": "Fitness", "max_attendees": 100, "distance": "0.5 mi", "mode": "In-Person",
        "description": "Join us for our grand opening! Free classes, giveaways and refreshments.",
        "promoted": True,
        "reviews": [
            {"id": "rb1", "user_name": "Alex J.", "rating": 5, "comment": "Amazing event, great energy!", "date": "1 week ago"},
        ],
    },
    {
        "id": "b2", "title": "Python for Beginners Workshop", "host": "TechHub Academy",
        "time": "Mon, 6:00 PM", "attendees": 20, "spots_left": 10, "rating": 4.7,
        "category": "Education", "max_attendees": 30, "distance": "", "mode": "Online",
        "description": "A beginner-friendly Python workshop covering variables, loops, and functions.",
        "promoted": False,
        "reviews": [
            {"id": "rb2", "user_name": "Priya S.", "rating": 5, "comment": "Excellent instructor!", "date": "3 days ago"},
        ],
    },
    {
        "id": "b3", "title": "Wine Tasting Evening", "host": "Cellar & Co.",
        "time": "Fri, 7:00 PM", "attendees": 18, "spots_left": 12, "rating": 4.8,
        "category": "Food & Drink", "max_attendees": 30, "distance": "1.1 mi", "mode": "In-Person",
        "description": "Sample 6 curated wines with expert guidance from our sommelier.",
        "promoted": True,
        "reviews": [
            {"id": "rb3", "user_name": "Chloe D.", "rating": 5, "comment": "Fantastic selection of wines.", "date": "2 weeks ago"},
        ],
    },
    {
        "id": "b4", "title": "Morning Bootcamp", "host": "The Fitness Co.",
        "time": "Tue & Thu, 7:00 AM", "attendees": 12, "spots_left": 8, "rating": 4.6,
        "category": "Fitness", "max_attendees": 20, "distance": "0.5 mi", "mode": "In-Person",
        "description": "High intensity morning bootcamp. All fitness levels welcome.",
        "promoted": False,
        "reviews": [],
    },
    {
        "id": "b5", "title": "Small Business Networking Night", "host": "BizConnect",
        "time": "Wed, 5:30 PM", "attendees": 35, "spots_left": 15, "rating": 4.5,
        "category": "Networking", "max_attendees": 50, "distance": "0.9 mi", "mode": "In-Person",
        "description": "Meet local business owners, share ideas and grow your network.",
        "promoted": False,
        "reviews": [
            {"id": "rb4", "user_name": "Marcus L.", "rating": 4, "comment": "Great connections made!", "date": "1 week ago"},
        ],
    },
    {
        "id": "b6", "title": "Kids Cooking Class", "host": "The Kitchen Studio",
        "time": "Sat, 10:00 AM", "attendees": 8, "spots_left": 4, "rating": 4.9,
        "category": "Food & Drink", "max_attendees": 12, "distance": "1.5 mi", "mode": "In-Person",
        "description": "A fun hands-on cooking class for kids aged 6-12. Aprons provided!",
        "promoted": True,
        "reviews": [
            {"id": "rb5", "user_name": "Sofia R.", "rating": 5, "comment": "My kids absolutely loved it!", "date": "5 days ago"},
        ],
    },
]

BUSINESS_CATEGORIES = ["All", "Fitness", "Education", "Food & Drink", "Networking"]
PERSONAL_CATEGORIES = ["All", "Sports", "Study", "Arts", "Social", "Wellness", "Tech"]

ALL_GOALS = [
    "🤝 Make new friends", "💪 Stay active", "📚 Learn new skills",
    "🎯 Try new experiences", "🌍 Explore my city", "💼 Network professionally",
]

BUSINESS_TYPES = ["Gym / Fitness", "Restaurant / Cafe", "Education / Academy",
                  "Retail / Shop", "Entertainment", "Health & Wellness", "Other"]

# ── Data Models ───────────────────────────────────────────────────────────────

@dataclass
class Review:
    id: str
    user_name: str
    rating: int
    comment: str
    date: str

@dataclass
class Event:
    id: str
    title: str
    host: str
    time: str
    attendees: int
    spots_left: int
    rating: float
    category: str
    max_attendees: int
    description: str = ""
    distance: str = ""
    mode: str = "In-Person"
    promoted: bool = False
    age_min: int = 0
    age_max: int = 99
    reviews: list = field(default_factory=list)
    messages: list = field(default_factory=list)

@dataclass
class Achievement:
    id: str
    title: str
    description: str
    icon: str
    earned: bool
    progress: int = 0
    max_progress: int = 1

# ── Build Objects ─────────────────────────────────────────────────────────────

def build_personal_events():
    events = []
    for e in PERSONAL_EVENTS_DATA:
        reviews = [Review(**r) for r in e.get("reviews", [])]
        events.append(Event(
            id=e["id"], title=e["title"], host=e["host"], time=e["time"],
            attendees=e["attendees"], spots_left=e["spots_left"], rating=e["rating"],
            category=e["category"], max_attendees=e["max_attendees"],
            description=e["description"], distance=e["distance"], mode=e["mode"],
            age_min=e.get("age_min", 0), age_max=e.get("age_max", 99),
            reviews=reviews
        ))
    return events

def build_business_events():
    events = []
    for e in BUSINESS_EVENTS_DATA:
        reviews = [Review(**r) for r in e.get("reviews", [])]
        events.append(Event(
            id=e["id"], title=e["title"], host=e["host"], time=e["time"],
            attendees=e["attendees"], spots_left=e["spots_left"], rating=e["rating"],
            category=e["category"], max_attendees=e["max_attendees"],
            description=e["description"], distance=e["distance"], mode=e["mode"],
            promoted=e.get("promoted", False), reviews=reviews
        ))
    return events

PERSONAL_EVENTS = build_personal_events()
BUSINESS_EVENTS = build_business_events()

# ── Experience Badge ──────────────────────────────────────────────────────────

def get_experience_badge(events_attended):
    if events_attended == 0:
        return "🌱 Newcomer"
    elif events_attended < 5:
        return "⭐ Regular"
    elif events_attended < 10:
        return "🔥 Veteran"
    else:
        return "🏆 Super Attendee"

# ── Session State ─────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "logged_in": False,
        "account_type": None,
        "screen": "events",
        "selected_event": None,
        "notifications": [],
        "user_name": "",
        "user_location": "",
        "category_filter": "All",
        "user_interests": [],
        "user_achievements": [],
        "user_stats": {},
        "profile_picture": None,
        "user_password": "",
        "user_settings": {"max_distance_mi": 5, "max_group_size": 20, "notifications_enabled": True},
        "user_bio": "",
        "user_goals": [],
        "user_age": 25,
        "search_query": "",
        # Business fields
        "biz_name": "",
        "biz_type": "",
        "biz_description": "",
        "biz_website": "",
        "biz_events": [],
        "biz_category_filter": "All",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

# ── Account Type Selection ────────────────────────────────────────────────────

def show_account_selection():
    st.markdown("<h1 style='text-align:center'>📅 EventFlow</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:gray'>Choose your account type</p>", unsafe_allow_html=True)
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("### 👤 Personal")
            st.caption("Join and discover events in your community. Track your activity and connect with others.")
            if st.button("Personal Account", type="primary", use_container_width=True):
                st.session_state.account_type = "personal"
                st.rerun()
    with col2:
        with st.container(border=True):
            st.markdown("### 🏢 Business")
            st.caption("Host and promote your business events. Reach new customers and grow your audience.")
            if st.button("Business Account", type="primary", use_container_width=True):
                st.session_state.account_type = "business"
                st.rerun()

# ── Personal Login ────────────────────────────────────────────────────────────

def show_personal_login():
    st.markdown("<h1 style='text-align:center'>📅 EventFlow</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:gray'>Personal Account</p>", unsafe_allow_html=True)
    st.divider()

    with st.container(border=True):
        name     = st.text_input("Your Name",        placeholder="e.g. Alex Johnson")
        location = st.text_input("Your Location",    placeholder="e.g. Toronto, ON")
        age      = st.number_input("Your Age", min_value=13, max_value=100, value=25, step=1)
        bio      = st.text_input("Bio / Tagline",    placeholder="e.g. Outdoor enthusiast looking to meet new people")
        password = st.text_input("Password",         type="password", placeholder="Create a password")
        confirm  = st.text_input("Confirm Password", type="password", placeholder="Repeat your password")

        st.markdown("**Your Goals**")
        selected_goals = []
        cols = st.columns(2)
        for i, goal in enumerate(ALL_GOALS):
            with cols[i % 2]:
                if st.checkbox(goal, key=f"goal_{i}"):
                    selected_goals.append(goal)

    if st.button("← Back", key="back_personal"):
        st.session_state.account_type = None
        st.rerun()

    if st.button("Log In →", type="primary", use_container_width=True):
        if not name.strip():
            st.warning("Please enter your name.")
        elif not location.strip():
            st.warning("Please enter your location.")
        elif not password:
            st.warning("Please enter a password.")
        elif password != confirm:
            st.error("Passwords do not match.")
        else:
            st.session_state.logged_in       = True
            st.session_state.user_name       = name.strip()
            st.session_state.user_location   = location.strip()
            st.session_state.user_age        = int(age)
            st.session_state.user_bio        = bio.strip()
            st.session_state.user_goals      = selected_goals
            st.session_state.user_password   = password
            st.session_state.user_achievements = []
            st.session_state.user_stats      = {"events_attended": 0, "events_hosted": 0}
            st.session_state.screen          = "events"
            st.rerun()

# ── Business Login ────────────────────────────────────────────────────────────

def show_business_login():
    st.markdown("<h1 style='text-align:center'>📅 EventFlow</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:gray'>Business Account</p>", unsafe_allow_html=True)
    st.divider()

    with st.container(border=True):
        biz_name = st.text_input("Business Name",        placeholder="e.g. The Fitness Co.")
        biz_type = st.selectbox("Business Type",         BUSINESS_TYPES)
        biz_desc = st.text_area("Business Description",  placeholder="Tell people what your business is about...")
        biz_web  = st.text_input("Website / Contact",    placeholder="e.g. www.yourbusiness.com")
        location = st.text_input("Business Location",    placeholder="e.g. Toronto, ON")
        password = st.text_input("Password",             type="password", placeholder="Create a password")
        confirm  = st.text_input("Confirm Password",     type="password", placeholder="Repeat your password")

    if st.button("← Back", key="back_business"):
        st.session_state.account_type = None
        st.rerun()

    if st.button("Create Business Account →", type="primary", use_container_width=True):
        if not biz_name.strip():
            st.warning("Please enter your business name.")
        elif not location.strip():
            st.warning("Please enter your business location.")
        elif not password:
            st.warning("Please enter a password.")
        elif password != confirm:
            st.error("Passwords do not match.")
        else:
            st.session_state.logged_in       = True
            st.session_state.user_name       = biz_name.strip()
            st.session_state.user_location   = location.strip()
            st.session_state.user_password   = password
            st.session_state.biz_name        = biz_name.strip()
            st.session_state.biz_type        = biz_type
            st.session_state.biz_description = biz_desc.strip()
            st.session_state.biz_website     = biz_web.strip()
            st.session_state.user_stats      = {"events_hosted": 0, "total_attendees": 0}
            st.session_state.screen          = "events"
            st.rerun()

# ── Top Bar ───────────────────────────────────────────────────────────────────

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def show_top_bar():
    unread = sum(1 for n in st.session_state.notifications if not n["read"])
    is_biz = st.session_state.account_type == "business"
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    with col1:
        label = "🏢" if is_biz else "👤"
        st.markdown(f"**📅 EventFlow** &nbsp; {label} *{st.session_state.user_name}*", unsafe_allow_html=True)
    with col2:
        bell_label = f"🔔 ({unread})" if unread else "🔔"
        if st.button(bell_label, use_container_width=True):
            st.session_state.screen = "notifications"
            st.rerun()
    with col3:
        if st.button("⚙️", use_container_width=True):
            st.session_state.screen = "settings"
            st.rerun()
    with col4:
        if st.button("🚪", use_container_width=True, help="Log out"):
            logout()
    st.divider()

# ── Bottom Nav Personal ───────────────────────────────────────────────────────

def show_bottom_nav_personal():
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🏠 Events", use_container_width=True):
            st.session_state.screen = "events"
            st.rerun()
    with col2:
        if st.button("🧭 Interests", use_container_width=True):
            st.session_state.screen = "discover"
            st.rerun()
    with col3:
        if st.button("📊 Analytics", use_container_width=True):
            st.session_state.screen = "analytics"
            st.rerun()
    with col4:
        if st.button("👤 Profile", use_container_width=True):
            st.session_state.screen = "profile"
            st.rerun()

# ── Bottom Nav Business ───────────────────────────────────────────────────────

def show_bottom_nav_business():
    st.divider()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("🏠 Events", use_container_width=True):
            st.session_state.screen = "events"
            st.rerun()
    with col2:
        if st.button("➕ Host Event", use_container_width=True):
            st.session_state.screen = "host_event"
            st.rerun()
    with col3:
        if st.button("📊 Analytics", use_container_width=True):
            st.session_state.screen = "analytics"
            st.rerun()
    with col4:
        if st.button("🏢 Profile", use_container_width=True):
            st.session_state.screen = "profile"
            st.rerun()

# ── Personal Events Screen ────────────────────────────────────────────────────

def show_personal_events():
    st.subheader("Upcoming Events")

    search = st.text_input("🔍 Search events", placeholder="Search by title, host, category or description...", key="search_box")

    st.session_state.category_filter = st.radio(
        "Filter by category", PERSONAL_CATEGORIES, horizontal=True,
        index=PERSONAL_CATEGORIES.index(st.session_state.category_filter)
        if st.session_state.category_filter in PERSONAL_CATEGORIES else 0
    )

    user_age = st.session_state.get("user_age", 25)
    age_filtered = [e for e in PERSONAL_EVENTS if e.age_min <= user_age <= e.age_max]

    cat_filtered = age_filtered if st.session_state.category_filter == "All"         else [e for e in age_filtered if e.category == st.session_state.category_filter]

    if search.strip():
        q = search.strip().lower()
        filtered = [e for e in cat_filtered if
                    q in e.title.lower() or
                    q in e.host.lower() or
                    q in e.category.lower() or
                    q in e.description.lower()]
        if filtered:
            st.caption(f'Found {len(filtered)} result(s) for "{search.strip()}"')
    else:
        filtered = cat_filtered

    if not filtered:
        st.info("No events found. Try a different search or category.")
        return

    for event in filtered:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{event.title}**")
                st.caption(f"🏷️ {event.category}  |  🕐 {event.time}")
                if event.distance:
                    st.caption(f"📍 {event.distance}  |  👥 {event.attendees} attending")
                else:
                    st.caption(f"🌐 Online  |  👥 {event.attendees} attending")
                st.caption(f"⭐ {event.rating}  |  🪑 {event.spots_left} spots left  |  📡 {event.mode}  |  👥 Ages {event.age_min}–{event.age_max}")
            with col2:
                if st.button("View", key=f"view_{event.id}", use_container_width=True):
                    st.session_state.selected_event = event
                    st.session_state.screen = "detail"
                    st.rerun()

# ── Business Events Screen ────────────────────────────────────────────────────

def show_business_events():
    st.subheader("Business Events")

    all_events = BUSINESS_EVENTS + st.session_state.biz_events

    promoted = [e for e in all_events if e.promoted]
    if promoted:
        st.markdown("### ⭐ Featured Events")
        for event in promoted:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**{event.title}** 🌟 *Featured*")
                    st.caption(f"🏢 {event.host}  |  🏷️ {event.category}  |  🕐 {event.time}")
                    if event.distance:
                        st.caption(f"📍 {event.distance}  |  👥 {event.attendees} attending")
                    else:
                        st.caption(f"🌐 Online  |  👥 {event.attendees} attending")
                    st.caption(f"⭐ {event.rating}  |  🪑 {event.spots_left} spots left  |  📡 {event.mode}")
                with col2:
                    if st.button("View", key=f"bview_{event.id}", use_container_width=True):
                        st.session_state.selected_event = event
                        st.session_state.screen = "detail"
                        st.rerun()
        st.divider()

    st.markdown("### 📋 All Business Events")
    st.session_state.biz_category_filter = st.radio(
        "Filter", BUSINESS_CATEGORIES, horizontal=True,
        index=BUSINESS_CATEGORIES.index(st.session_state.biz_category_filter)
        if st.session_state.biz_category_filter in BUSINESS_CATEGORIES else 0
    )
    filtered = all_events if st.session_state.biz_category_filter == "All" \
        else [e for e in all_events if e.category == st.session_state.biz_category_filter]

    if not filtered:
        st.info("No events found for this category.")
        return

    for event in filtered:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{event.title}**")
                st.caption(f"🏢 {event.host}  |  🏷️ {event.category}  |  🕐 {event.time}")
                if event.distance:
                    st.caption(f"📍 {event.distance}  |  👥 {event.attendees} attending")
                else:
                    st.caption(f"🌐 Online  |  👥 {event.attendees} attending")
                st.caption(f"⭐ {event.rating}  |  🪑 {event.spots_left} spots left  |  📡 {event.mode}")
            with col2:
                if st.button("View", key=f"bview2_{event.id}", use_container_width=True):
                    st.session_state.selected_event = event
                    st.session_state.screen = "detail"
                    st.rerun()

# ── Event Detail ──────────────────────────────────────────────────────────────

def show_event_detail():
    event = st.session_state.selected_event
    if not event:
        st.session_state.screen = "events"
        st.rerun()
        return

    if st.button("← Back to Events"):
        st.session_state.screen = "events"
        st.session_state.selected_event = None
        st.rerun()

    st.markdown(f"# {event.title}")
    if st.session_state.account_type == "business":
        st.caption(f"🏢 Hosted by **{event.host}**")
    else:
        st.caption(f"Hosted by **{event.host}**")

    col1, col2, col3 = st.columns(3)
    col1.metric("Rating",     f"⭐ {event.rating}")
    col2.metric("Attendees",  f"👥 {event.attendees}/{event.max_attendees}")
    col3.metric("Spots Left", f"🪑 {event.spots_left}")

    st.divider()
    st.markdown(f"**🕐 Time:** {event.time}")
    st.markdown(f"**📡 Mode:** {event.mode}")
    if event.distance:
        st.markdown(f"**📍 Distance:** {event.distance}")
    st.markdown(f"**🏷️ Category:** {event.category}")

    st.divider()
    st.subheader("About this Event")
    st.write(event.description or "No description provided.")

    st.divider()
    if event.spots_left > 0:
        if st.button("✅ Join Event", type="primary", use_container_width=True):
            st.success("You've joined the event! 🎉")
    else:
        st.warning("This event is full.")

    # Tabs for Chat and Reviews
    st.divider()
    tab1, tab2 = st.tabs([f"💬 Chat ({len(event.messages)})", f"⭐ Reviews ({len(event.reviews)})"])

    with tab1:
        if event.messages:
            for msg in event.messages:
                is_me = msg.get("user") == st.session_state.user_name
                with st.container(border=True):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        name_label = "**You**" if is_me else f"**{msg['user']}**"
                        st.markdown(name_label)
                        st.write(msg["content"])
                    with col2:
                        st.caption(msg["time"])
        else:
            st.info("No messages yet — be the first to say something!")

        msg_input = st.text_area("Message", key=f"chat_{event.id}",
                                  label_visibility="collapsed",
                                  placeholder="Say something to the group...")
        if st.button("Send 💬", key=f"send_{event.id}"):
            if msg_input.strip():
                event.messages.append({
                    "user": st.session_state.user_name,
                    "content": msg_input.strip(),
                    "time": "Just now"
                })
                st.rerun()
            else:
                st.warning("Message cannot be empty.")

    with tab2:
        if event.reviews:
            for review in event.reviews:
                with st.container(border=True):
                    st.markdown(f"**{review.user_name}** — {'⭐' * review.rating}")
                    st.write(review.comment)
                    st.caption(review.date)
        else:
            st.info("No reviews yet.")

# ── Host Event (Business only) ────────────────────────────────────────────────

def show_host_event():
    st.subheader("➕ Host a New Event")

    with st.container(border=True):
        title       = st.text_input("Event Title",       placeholder="e.g. Morning Yoga Class")
        category    = st.selectbox("Category",           ["Fitness", "Education", "Food & Drink", "Networking", "Other"])
        description = st.text_area("Description",        placeholder="Tell people about your event...")
        time        = st.text_input("Date & Time",       placeholder="e.g. Sat, 10:00 AM")
        mode        = st.selectbox("Mode",               ["In-Person", "Online", "Hybrid"])
        distance    = st.text_input("Location / Distance", placeholder="e.g. 1.2 mi or leave blank if online")
        max_att     = st.number_input("Max Attendees",   min_value=2, max_value=500, value=20)
        promoted    = st.toggle("⭐ Feature this event (promote it to the top)")

    if st.button("Post Event", type="primary", use_container_width=True):
        if not title.strip():
            st.warning("Please enter an event title.")
        elif not time.strip():
            st.warning("Please enter a date and time.")
        else:
            new_event = Event(
                id=f"biz_{len(st.session_state.biz_events)+1}",
                title=title.strip(),
                host=st.session_state.biz_name,
                time=time.strip(),
                attendees=0,
                spots_left=int(max_att),
                rating=0.0,
                category=category,
                max_attendees=int(max_att),
                description=description.strip(),
                distance=distance.strip(),
                mode=mode,
                promoted=promoted,
                reviews=[],
            )
            st.session_state.biz_events.append(new_event)
            st.session_state.user_stats["events_hosted"] = \
                st.session_state.user_stats.get("events_hosted", 0) + 1
            st.success(f"✅ '{title}' has been posted!")
            st.session_state.screen = "events"
            st.rerun()

# ── Personal Profile ──────────────────────────────────────────────────────────

def show_personal_profile():
    attended = st.session_state.user_stats.get("events_attended", 0)
    badge    = get_experience_badge(attended)

    st.subheader(f"👤 {st.session_state.user_name}'s Profile")
    st.caption(f"📍 {st.session_state.user_location}  |  🎂 Age: {st.session_state.get('user_age', '')}")
    if st.session_state.user_bio:
        st.markdown(f"*\"{st.session_state.user_bio}\"*")
    st.markdown(f"**Experience:** {badge}")
    if st.session_state.user_goals:
        st.markdown("**Goals:** " + "  ·  ".join(st.session_state.user_goals))

    st.divider()
    st.subheader("🖼️ Profile Picture")
    if st.session_state.profile_picture is not None:
        st.image(st.session_state.profile_picture, width=120)
    uploaded = st.file_uploader("Upload a profile picture", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    if uploaded is not None:
        st.session_state.profile_picture = uploaded
        st.image(uploaded, width=120)
        st.success("Profile picture updated!")

    st.divider()
    st.subheader("✏️ Edit Bio & Goals")
    with st.container(border=True):
        new_bio = st.text_input("Bio / Tagline", value=st.session_state.user_bio, key="edit_bio")
        st.markdown("**Goals**")
        updated_goals = []
        cols = st.columns(2)
        for i, goal in enumerate(ALL_GOALS):
            with cols[i % 2]:
                if st.checkbox(goal, value=goal in st.session_state.user_goals, key=f"edit_goal_{i}"):
                    updated_goals.append(goal)
        if st.button("Save Bio & Goals"):
            st.session_state.user_bio   = new_bio.strip()
            st.session_state.user_goals = updated_goals
            st.success("Profile updated!")
            st.rerun()

    st.divider()
    st.subheader("🔒 Change Password")
    with st.container(border=True):
        new_pw  = st.text_input("New Password",     type="password", key="new_pw")
        conf_pw = st.text_input("Confirm Password", type="password", key="confirm_pw")
        if st.button("Save Password", key="save_pw"):
            if not new_pw:
                st.warning("Password cannot be empty.")
            elif new_pw != conf_pw:
                st.error("Passwords do not match.")
            else:
                st.session_state.user_password = new_pw
                st.success("Password saved!")

    st.divider()
    st.subheader("🏆 Achievements")
    if st.session_state.user_achievements:
        for ach in st.session_state.user_achievements:
            with st.container(border=True):
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.markdown(f"# {ach.icon}")
                with col2:
                    status = "✅ Earned" if ach.earned else f"🔒 {ach.progress}/{ach.max_progress}"
                    st.markdown(f"**{ach.title}** — {status}")
                    st.caption(ach.description)
                    if not ach.earned and ach.max_progress > 1:
                        st.progress(ach.progress / ach.max_progress)
    else:
        st.info("No achievements yet — join some events to get started!")

# ── Business Profile ──────────────────────────────────────────────────────────

def show_business_profile():
    st.subheader(f"🏢 {st.session_state.biz_name}")
    st.caption(f"📍 {st.session_state.user_location}  |  🏷️ {st.session_state.biz_type}")
    if st.session_state.biz_description:
        st.write(st.session_state.biz_description)
    if st.session_state.biz_website:
        st.markdown(f"🌐 {st.session_state.biz_website}")

    st.divider()
    st.subheader("🖼️ Business Logo / Picture")
    if st.session_state.profile_picture is not None:
        st.image(st.session_state.profile_picture, width=120)
    uploaded = st.file_uploader("Upload a logo or picture", type=["png", "jpg", "jpeg"], label_visibility="collapsed")
    if uploaded is not None:
        st.session_state.profile_picture = uploaded
        st.image(uploaded, width=120)
        st.success("Picture updated!")

    st.divider()
    st.subheader("✏️ Edit Business Info")
    with st.container(border=True):
        new_desc = st.text_area("Business Description", value=st.session_state.biz_description, key="edit_desc")
        new_web  = st.text_input("Website / Contact",   value=st.session_state.biz_website,     key="edit_web")
        if st.button("Save Changes"):
            st.session_state.biz_description = new_desc.strip()
            st.session_state.biz_website     = new_web.strip()
            st.success("Business profile updated!")
            st.rerun()

    st.divider()
    st.subheader("📋 Your Posted Events")
    if st.session_state.biz_events:
        for event in st.session_state.biz_events:
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    promoted_tag = " 🌟" if event.promoted else ""
                    st.markdown(f"**{event.title}**{promoted_tag}")
                    st.caption(f"🕐 {event.time}  |  👥 {event.attendees}/{event.max_attendees}  |  🪑 {event.spots_left} spots")
                with col2:
                    if st.button("View", key=f"prof_{event.id}", use_container_width=True):
                        st.session_state.selected_event = event
                        st.session_state.screen = "detail"
                        st.rerun()
    else:
        st.info("You haven't posted any events yet. Use ➕ Host Event to get started!")

    st.divider()
    st.subheader("🔒 Change Password")
    with st.container(border=True):
        new_pw  = st.text_input("New Password",     type="password", key="biz_new_pw")
        conf_pw = st.text_input("Confirm Password", type="password", key="biz_conf_pw")
        if st.button("Save Password", key="biz_save_pw"):
            if not new_pw:
                st.warning("Password cannot be empty.")
            elif new_pw != conf_pw:
                st.error("Passwords do not match.")
            else:
                st.session_state.user_password = new_pw
                st.success("Password saved!")

# ── Personal Analytics ────────────────────────────────────────────────────────

def show_personal_analytics():
    st.subheader("📊 Your Activity")
    stats  = st.session_state.user_stats
    earned = sum(1 for a in st.session_state.user_achievements if a.earned)
    total  = len(st.session_state.user_achievements)

    col1, col2, col3 = st.columns(3)
    col1.metric("Events Attended", stats.get("events_attended", 0))
    col2.metric("Events Hosted",   stats.get("events_hosted",   0))
    col3.metric("Achievements",    f"{earned}/{total}")

    st.divider()
    st.subheader("Events by Category")
    interest_counts = {i: 0 for i in st.session_state.user_interests}
    total_attended  = stats.get("events_attended", 0)
    if interest_counts:
        base      = total_attended // len(interest_counts)
        remainder = total_attended % len(interest_counts)
        for i, key in enumerate(interest_counts):
            interest_counts[key] = base + (1 if i < remainder else 0)
    if interest_counts:
        data = pd.DataFrame({"Category": list(interest_counts.keys()), "Events": list(interest_counts.values())})
        st.bar_chart(data.set_index("Category"))
    else:
        st.info("No interest data to display.")

# ── Business Analytics ────────────────────────────────────────────────────────

def show_business_analytics():
    st.subheader("📊 Business Analytics")

    all_events     = BUSINESS_EVENTS + st.session_state.biz_events
    total_events   = len(all_events)
    total_att      = sum(e.attendees for e in all_events)
    avg_rating     = round(sum(e.rating for e in all_events if e.rating > 0) /
                           max(1, len([e for e in all_events if e.rating > 0])), 1)
    hosted         = st.session_state.user_stats.get("events_hosted", 0)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Events",      total_events)
    col2.metric("Total Attendees",   total_att)
    col3.metric("Avg Rating",        f"⭐ {avg_rating}")
    col4.metric("Your Posted",       hosted)

    st.divider()
    st.subheader("Attendees by Category")
    cat_counts = {}
    for e in all_events:
        cat_counts[e.category] = cat_counts.get(e.category, 0) + e.attendees
    if cat_counts:
        data = pd.DataFrame({"Category": list(cat_counts.keys()), "Attendees": list(cat_counts.values())})
        st.bar_chart(data.set_index("Category"))

    st.divider()
    st.subheader("📋 Event Performance")
    for event in all_events:
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(f"**{event.title}**")
                st.caption(f"🏢 {event.host}  |  🕐 {event.time}")
            with col2:
                st.metric("Attendees", event.attendees)
            with col3:
                st.metric("Rating", f"⭐ {event.rating}" if event.rating > 0 else "N/A")

# ── Discover (Personal only) ──────────────────────────────────────────────────

def show_discover():
    st.subheader("🧭 Your Interests")
    st.write("Select the categories you're most interested in:")
    interests = ["Sports", "Study", "Arts", "Social", "Wellness", "Tech", "Music", "Food", "Travel", "Gaming"]
    selected  = []
    cols      = st.columns(3)
    for i, interest in enumerate(interests):
        with cols[i % 3]:
            checked = interest in st.session_state.user_interests
            if st.checkbox(interest, value=checked, key=f"interest_{interest}"):
                selected.append(interest)
    if st.button("Save Interests", type="primary", use_container_width=True):
        st.session_state.user_interests = selected
        st.success("Interests saved!")

# ── Notifications ─────────────────────────────────────────────────────────────

def show_notifications():
    if st.button("← Back"):
        st.session_state.screen = "events"
        st.rerun()
    st.subheader("🔔 Notifications")
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
                    if st.button("Mark read", key=f"read_{n['id']}"):
                        n["read"] = True
                        st.rerun()

# ── Settings ──────────────────────────────────────────────────────────────────

def show_settings():
    if st.button("← Back"):
        st.session_state.screen = "events"
        st.rerun()
    st.subheader("⚙️ Settings")
    settings = st.session_state.get("user_settings", {})
    st.markdown("**Distance Range**")
    dist   = st.slider("Max distance (mi)", 1, 20, settings.get("max_distance_mi", 5))
    st.markdown("**Max Group Size**")
    size   = st.slider("Max group size", 2, 100, settings.get("max_group_size", 20))
    st.markdown("**Notifications**")
    notifs = st.toggle("Enable notifications", value=settings.get("notifications_enabled", True))
    if st.button("Save Settings", type="primary"):
        st.session_state.user_settings = {
            "max_distance_mi": dist, "max_group_size": size, "notifications_enabled": notifs
        }
        st.success("Settings saved!")

# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(page_title="EventFlow", page_icon="📅", layout="centered")
    st.markdown(THEME_CSS, unsafe_allow_html=True)
    init_state()

    is_biz = st.session_state.account_type == "business"

    # Not logged in
    if not st.session_state.logged_in:
        if st.session_state.account_type is None:
            show_account_selection()
        elif is_biz:
            show_business_login()
        else:
            show_personal_login()
        return

    show_top_bar()
    screen = st.session_state.screen

    if is_biz:
        if   screen == "events":      show_business_events()
        elif screen == "detail":      show_event_detail()
        elif screen == "host_event":  show_host_event()
        elif screen == "analytics":   show_business_analytics()
        elif screen == "profile":     show_business_profile()
        elif screen == "notifications": show_notifications()
        elif screen == "settings":    show_settings()
        if screen not in ("notifications", "settings", "detail", "host_event"):
            show_bottom_nav_business()
    else:
        if   screen == "events":      show_personal_events()
        elif screen == "detail":      show_event_detail()
        elif screen == "discover":    show_discover()
        elif screen == "analytics":   show_personal_analytics()
        elif screen == "profile":     show_personal_profile()
        elif screen == "notifications": show_notifications()
        elif screen == "settings":    show_settings()
        if screen not in ("notifications", "settings", "detail"):
            show_bottom_nav_personal()

if __name__ == "__main__":
    main()