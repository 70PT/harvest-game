# Harvest Shield Farm Challenge

A Streamlit game for Harvest Shield, a fictional agritech company premise where engineered crop-microbiome bacteria produce protective peptides and dsRNA against insect pressure.

## Game premise

Players manage a single wheat season and try to maximize one final harvest score. Each day, they choose one action:

- Add water: helps in the right amount, but too much waterlogs the soil.
- Add sun: dries wet soil and increases photosynthesis, but too much causes drought stress.
- Harvest Shield: clears current pests and weeds with no harvest penalty.
- Regular protectant: clears current pests and weeds but adds a permanent -1 harvest penalty per use.

New pests and weeds appear every day.

## Run locally

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Files

- `streamlit_app.py`: the full game app.
- `requirements.txt`: Python dependencies.
- `.streamlit/config.toml`: simple green Harvest Shield theme.
