from __future__ import annotations

import random
from typing import Dict, List

import pandas as pd
import streamlit as st


GAME_DAYS = 15
MAX_YIELD_SCORE = 100.0
MIN_YIELD_SCORE = 0.0


st.set_page_config(
    page_title="Harvest Shield Farm Challenge",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)


CSS = """
<style>
    .main-title {
        font-size: 2.6rem;
        font-weight: 850;
        margin-bottom: 0.2rem;
    }
    .subtitle {
        color: #4b5563;
        font-size: 1.05rem;
        margin-bottom: 1rem;
    }
    .brand-card {
        padding: 1rem 1.15rem;
        border-radius: 1rem;
        border: 1px solid rgba(16, 185, 129, 0.22);
        background: linear-gradient(135deg, rgba(236, 253, 245, 0.95), rgba(240, 253, 244, 0.75));
        margin-bottom: 1rem;
    }
    .status-card {
        padding: 0.9rem 1rem;
        border-radius: 0.85rem;
        border: 1px solid rgba(148, 163, 184, 0.35);
        background: rgba(248, 250, 252, 0.82);
        min-height: 6.3rem;
    }
    .farm-grid {
        display: grid;
        grid-template-columns: repeat(8, minmax(2.1rem, 1fr));
        gap: 0.35rem;
        padding: 0.65rem;
        border-radius: 1rem;
        background: linear-gradient(180deg, #fef3c7 0%, #fde68a 100%);
        border: 1px solid rgba(180, 83, 9, 0.28);
    }
    .farm-cell {
        aspect-ratio: 1 / 1;
        border-radius: 0.65rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.6rem;
        background: rgba(255, 251, 235, 0.8);
        box-shadow: inset 0 0 0 1px rgba(146, 64, 14, 0.08);
    }
    .log-box {
        border-left: 4px solid #10b981;
        padding: 0.65rem 0.85rem;
        background: rgba(236, 253, 245, 0.75);
        border-radius: 0.5rem;
        margin: 0.35rem 0;
    }
    .small-muted {
        color: #64748b;
        font-size: 0.88rem;
    }
</style>
"""

st.markdown(CSS, unsafe_allow_html=True)


def clamp(value: float, low: float, high: float) -> float:
    """Keep a numeric value inside a safe range."""
    return max(low, min(high, value))


def reset_game() -> None:
    """Start a fresh single-harvest season while preserving the session high score."""
    st.session_state.day = 1
    st.session_state.moisture = 55.0
    st.session_state.yield_score = 48.0
    st.session_state.pests = random.randint(2, 5)
    st.session_state.weeds = random.randint(2, 5)
    st.session_state.harvest_shield_uses = 0
    st.session_state.regular_uses = 0
    st.session_state.regular_penalty = 0.0
    st.session_state.game_over = False
    st.session_state.last_message = "Your wheat is sprouting. Balance water, sunlight, and crop protection to maximize the final harvest."
    st.session_state.event_log = [st.session_state.last_message]
    st.session_state.history = []
    record_history("Season start")


def ensure_state() -> None:
    """Initialize Streamlit session state on the first run."""
    if "high_score" not in st.session_state:
        st.session_state.high_score = 0.0
    if "day" not in st.session_state:
        reset_game()


def growth_stage() -> str:
    day = min(st.session_state.day, GAME_DAYS)
    if day <= 3:
        return "Seedling"
    if day <= 7:
        return "Tillering"
    if day <= 11:
        return "Heading"
    return "Grain fill"


def maturity_factor() -> float:
    """Early harvest is possible, but immature wheat earns less of its potential."""
    days_completed = min(max(st.session_state.day - 1, 0), GAME_DAYS)
    return 0.45 + 0.55 * (days_completed / GAME_DAYS)


def projected_harvest_score() -> float:
    base = st.session_state.yield_score * maturity_factor()
    return clamp(base - st.session_state.regular_penalty, 0.0, MAX_YIELD_SCORE)


def pressure_label() -> str:
    pressure = st.session_state.pests + st.session_state.weeds
    if pressure >= 30:
        return "Severe pest and weed pressure"
    if pressure >= 18:
        return "High pest and weed pressure"
    if pressure >= 9:
        return "Moderate pest and weed pressure"
    return "Low pest and weed pressure"


def water_status() -> str:
    moisture = st.session_state.moisture
    if moisture >= 88:
        return "Waterlogged"
    if moisture >= 76:
        return "Too wet"
    if moisture <= 18:
        return "Drought stress"
    if moisture <= 30:
        return "Dry"
    if 42 <= moisture <= 68:
        return "Ideal"
    return "Workable"


def crop_status() -> str:
    moisture = st.session_state.moisture
    pressure = st.session_state.pests + st.session_state.weeds
    if moisture >= 88:
        return "Waterlogged roots need sun."
    if moisture <= 18:
        return "Drought stress needs water."
    if pressure >= 22:
        return "Pests and weeds are stealing yield."
    if 42 <= moisture <= 68 and pressure <= 8:
        return "Crop is in a sweet spot."
    return "Crop is stable, but optimization is possible."


def record_history(action: str) -> None:
    st.session_state.history.append(
        {
            "Day": min(st.session_state.day, GAME_DAYS),
            "Action": action,
            "Yield Potential": round(st.session_state.yield_score, 1),
            "Projected Harvest": round(projected_harvest_score(), 1),
            "Soil Moisture": round(st.session_state.moisture, 1),
            "Pests": int(st.session_state.pests),
            "Weeds": int(st.session_state.weeds),
        }
    )


def add_log(message: str) -> None:
    st.session_state.last_message = message
    st.session_state.event_log.append(message)
    st.session_state.event_log = st.session_state.event_log[-8:]


def finish_game(reason: str) -> None:
    st.session_state.game_over = True
    final_score = projected_harvest_score()
    if final_score > st.session_state.high_score:
        st.session_state.high_score = final_score
    add_log(f"{reason} Final harvest score: {final_score:.1f}/100.")
    record_history("Harvest")


def end_of_day(action_name: str, action_message: str) -> None:
    """Apply farm pressure, random new pests/weeds, and crop growth after an action."""
    state = st.session_state
    messages: List[str] = [action_message]

    # Pests and weeds that remain after the player's action reduce yield potential.
    pest_weed_damage = min(6.0, state.pests * 0.35 + state.weeds * 0.25)
    if pest_weed_damage > 0:
        state.yield_score -= pest_weed_damage
        messages.append(f"Existing pests and weeds cost {pest_weed_damage:.1f} yield potential.")

    # Water balance is the central risk/reward mechanic.
    if state.moisture >= 88:
        state.yield_score -= 4.0
        messages.append("Waterlogged soil damaged roots. Add sun to dry the field.")
    elif state.moisture >= 76:
        state.yield_score -= 1.5
        messages.append("Soil is too wet. A little sun would help.")
    elif state.moisture <= 18:
        state.yield_score -= 4.0
        messages.append("Drought stress damaged the wheat. Add water soon.")
    elif state.moisture <= 30:
        state.yield_score -= 1.5
        messages.append("The field is getting dry.")
    elif 42 <= state.moisture <= 68 and (state.pests + state.weeds) <= 8:
        state.yield_score += 1.5
        messages.append("Balanced water and low pressure added +1.5 yield potential.")
    elif 35 <= state.moisture <= 75:
        state.yield_score += 0.5
        messages.append("Acceptable growing conditions added +0.5 yield potential.")

    # Daily weather drift keeps the farm dynamic.
    weather = random.choice(
        [
            ("clear, warm afternoon", -5),
            ("light breeze", -3),
            ("cool humid evening", 2),
            ("ordinary field day", -1),
        ]
    )
    weather_name, moisture_delta = weather
    state.moisture = clamp(state.moisture + moisture_delta, 0, 100)
    messages.append(f"Weather: {weather_name}; soil moisture changed by {moisture_delta:+.0f}.")

    # There are always new pests and weeds appearing.
    new_pests = random.randint(1, 4)
    new_weeds = random.randint(1, 4)
    state.pests = min(30, state.pests + new_pests)
    state.weeds = min(30, state.weeds + new_weeds)
    messages.append(f"New pressure appeared: +{new_pests} pests and +{new_weeds} weeds.")

    state.yield_score = clamp(state.yield_score, MIN_YIELD_SCORE, MAX_YIELD_SCORE)
    record_history(action_name)

    state.day += 1
    add_log(" ".join(messages))

    if state.day > GAME_DAYS:
        finish_game("The wheat reached the end of the season.")


def take_action(action: str) -> None:
    if st.session_state.game_over:
        return

    state = st.session_state

    if action == "water":
        state.moisture = clamp(state.moisture + 22, 0, 100)
        if 42 <= state.moisture <= 68:
            state.yield_score += 2.0
            message = "Water landed in the ideal zone, giving the crop a growth boost."
        elif state.moisture > 85:
            message = "You added water, but the soil is now waterlogged."
        elif state.moisture > 75:
            message = "You added water, but the field is getting too wet."
        else:
            message = "You added water and helped relieve dryness."
        end_of_day("Add water", message)

    elif action == "sun":
        state.moisture = clamp(state.moisture - 16, 0, 100)
        if 35 <= state.moisture <= 75:
            state.yield_score += 3.0
            message = "Sun boosted photosynthesis and kept moisture in a workable range."
        elif state.moisture > 75:
            state.yield_score += 1.0
            message = "Sun helped dry the field, but the soil is still wetter than ideal."
        elif state.moisture < 25:
            state.yield_score += 0.5
            message = "Sun boosted photosynthesis, but the field is now drought-prone."
        else:
            state.yield_score += 1.5
            message = "Sun added photosynthesis, but moisture is not yet ideal."
        end_of_day("Add sun", message)

    elif action == "shield":
        removed_pests = state.pests
        removed_weeds = state.weeds
        state.pests = 0
        state.weeds = 0
        state.harvest_shield_uses += 1
        message = (
            "Harvest Shield colonized the crop microbiome and cleared "
            f"{removed_pests} pests and {removed_weeds} weeds with no harvest penalty."
        )
        end_of_day("Harvest Shield", message)

    elif action == "regular":
        removed_pests = state.pests
        removed_weeds = state.weeds
        state.pests = 0
        state.weeds = 0
        state.regular_uses += 1
        state.regular_penalty += 1.0
        message = (
            "Regular protectant cleared "
            f"{removed_pests} pests and {removed_weeds} weeds, but added a permanent -1 harvest penalty."
        )
        end_of_day("Regular protectant", message)


def farm_grid_html() -> str:
    cells = ["🌾" for _ in range(40)]
    rng = random.Random(
        int(st.session_state.day * 101 + st.session_state.pests * 13 + st.session_state.weeds * 17)
    )
    indices = list(range(len(cells)))
    rng.shuffle(indices)

    pest_icons = min(st.session_state.pests, 14)
    weed_icons = min(st.session_state.weeds, 14)

    for idx in indices[:pest_icons]:
        cells[idx] = "🐛"
    for idx in indices[pest_icons : pest_icons + weed_icons]:
        cells[idx] = "🌱"

    return "<div class='farm-grid'>" + "".join(
        f"<div class='farm-cell'>{cell}</div>" for cell in cells
    ) + "</div>"


def action_panel() -> None:
    st.subheader("Choose one action for today")
    disabled = st.session_state.game_over
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("💧 Add water", use_container_width=True, disabled=disabled):
            take_action("water")
    with col2:
        if st.button("☀️ Add sun", use_container_width=True, disabled=disabled):
            take_action("sun")
    with col3:
        if st.button("🛡️ Harvest Shield", use_container_width=True, disabled=disabled):
            take_action("shield")
    with col4:
        if st.button("🧪 Regular protectant", use_container_width=True, disabled=disabled):
            take_action("regular")

    hcol1, hcol2 = st.columns([1, 3])
    with hcol1:
        if st.button("🌾 Harvest now", use_container_width=True, disabled=disabled):
            finish_game("You harvested early.")
    with hcol2:
        st.caption(
            "Early harvest ends the game, but immature wheat receives a maturity discount. "
            "The highest scores usually come from protecting the crop through the full season."
        )


def sidebar_rules() -> None:
    with st.sidebar:
        st.header("Harvest Shield")
        st.write(
            "A turn-based wheat farm game about crop microbiome protection, water balance, "
            "and single-harvest yield optimization."
        )
        st.divider()
        st.subheader("Rules")
        st.markdown(
            """
            - **Add water** raises soil moisture. Ideal amounts help growth; too much waterlogs the soil.
            - **Add sun** dries wet soil and boosts photosynthesis. Too much drying causes drought stress.
            - **Harvest Shield** removes all current pests and weeds with **no harvest penalty**.
            - **Regular protectant** removes all current pests and weeds, but each use adds a **permanent -1 harvest penalty**.
            - New pests and weeds appear every day.
            - The season lasts 15 days, then wheat is harvested once.
            """
        )
        st.divider()
        st.metric("Session high score", f"{st.session_state.high_score:.1f}/100")
        if st.button("🔄 New season", use_container_width=True):
            reset_game()


def render_dashboard() -> None:
    st.markdown("<div class='main-title'>🌾 Harvest Shield Farm Challenge</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='subtitle'>Engineer the crop microbiome, manage soil conditions, and defend wheat from pests and weeds before one final harvest.</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class='brand-card'>
            <b>Company premise:</b> Harvest Shield creates engineered bacteria that incorporate into a crop microbiome and produce protective peptides and dsRNA against insect pressure.
            In this game, the Harvest Shield action clears pest and weed pressure without reducing harvest potential.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.game_over:
        final_score = projected_harvest_score()
        if final_score >= 85:
            st.success(f"🏆 Excellent harvest! Final score: {final_score:.1f}/100")
        elif final_score >= 65:
            st.info(f"🌾 Solid harvest. Final score: {final_score:.1f}/100")
        else:
            st.warning(f"🌧️ Tough season. Final score: {final_score:.1f}/100")

    action_panel()
    st.divider()

    day_label = f"Day {min(st.session_state.day, GAME_DAYS)} of {GAME_DAYS}"
    metric_cols = st.columns(5)
    metric_cols[0].metric("Season", day_label, growth_stage())
    metric_cols[1].metric("Projected harvest", f"{projected_harvest_score():.1f}/100")
    metric_cols[2].metric("Yield potential", f"{st.session_state.yield_score:.1f}/100")
    metric_cols[3].metric("Pests", int(st.session_state.pests))
    metric_cols[4].metric("Weeds", int(st.session_state.weeds))

    left, right = st.columns([1.1, 1])
    with left:
        st.subheader("Farm plot")
        st.markdown(farm_grid_html(), unsafe_allow_html=True)
        st.caption("🌾 wheat · 🐛 pests · 🌱 weeds")

    with right:
        st.subheader("Field status")
        card_cols = st.columns(2)
        with card_cols[0]:
            st.markdown("<div class='status-card'>", unsafe_allow_html=True)
            st.write(f"**Soil moisture:** {st.session_state.moisture:.0f}%")
            st.progress(int(st.session_state.moisture))
            st.write(f"Status: **{water_status()}**")
            st.markdown("</div>", unsafe_allow_html=True)
        with card_cols[1]:
            st.markdown("<div class='status-card'>", unsafe_allow_html=True)
            st.write(f"**Pressure:** {pressure_label()}")
            st.write(f"**Harvest Shield uses:** {st.session_state.harvest_shield_uses}")
            st.write(f"**Regular protectant penalty:** -{st.session_state.regular_penalty:.0f}")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(f"<div class='log-box'><b>Scout report:</b> {crop_status()}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='log-box'><b>Latest event:</b> {st.session_state.last_message}</div>", unsafe_allow_html=True)

    st.divider()
    history_df = pd.DataFrame(st.session_state.history)
    if not history_df.empty:
        st.subheader("Season trend")
        chart_df = history_df.set_index("Day")[["Projected Harvest", "Yield Potential", "Soil Moisture", "Pests", "Weeds"]]
        st.line_chart(chart_df)

        with st.expander("Show action history"):
            st.dataframe(history_df, use_container_width=True, hide_index=True)

    st.subheader("Recent farm log")
    for message in reversed(st.session_state.event_log[-5:]):
        st.markdown(f"<div class='small-muted'>• {message}</div>", unsafe_allow_html=True)


ensure_state()
sidebar_rules()
render_dashboard()
