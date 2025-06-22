import streamlit as st
from datetime import datetime

sector_data = {
    "Alcoholic and Non-Alcoholic": {
        "companies": {
            "Guinness Ghana Ltd": {"region": "Greater Accra", "city": "Achimota"},
            "Kasapreko Company Ltd": {"region": "Greater Accra", "city": "Spintex"},
            "Liberty Industries (kpoo keke)": {"region": "Greater Accra", "city": "Nungua"},
            "African Cola": {"region": "Eastern", "city": "Nsawam"},
            "Accra Brewery Ltd": {"region": "Greater Accra", "city": "Accra"},
            "Healthilife Beverages": {"region": "Greater Accra", "city": "Spintex"},
            "Ghana Specialty Beer": {"region": "Eastern", "city": "Akwadum"},
            "White Hill Beverages": {"region": "Greater Accra", "city": "Dodowa"},
            "Dada Food": {"region": "Greater Accra", "city": "Kpone"},
            "Special Beverages": {"region": "Greater Accra", "city": "Oyarifa"},
            "GIHOC ": {"region": "Greater Accra", "city": "North Industrial Area"}
        }
    },

    "Dairy Industry": {
        "companies": {
            "FanMilk Ltd": {"region": "Greater Accra", "city": "North Industrial Area"},
            "Ice Joy": {"region": "Greater Accra", "city": "Adjern Kotoku"},
            "Lan T soymilk": {"region": "Greater Accra", "city": "Kpone"}
        }
    },
    "General Industry": {
        "companies": {
            "Baron Distilleries": {"region": "Greater Accra", "city": "Adenta"},
            "Unilever Ghana": {"region": "Greater Accra", "city": "Tema"},
            "Special Ice Drinking water": {"region": "Greater Accra", "city": "Oyarifa"},
            "Ice cool": {"region": "Greater Accra", "city": "Manya Jorpanya"},
            "Everpure Processed Water": {"region": "Greater Accra", "city": "Tema"},
            "Everpure Water": {"region": "Central", "city": "Kasoa"},
            "Sky water": {"region": "Eastern", "city": "Adeiso"},
            "Fedek Group": {"region": "Eastern", "city": "Adeiso"},
            "Paradise Pack Mineral ": {"region": "Eastern", "city": "Nsawam"},
            "Voltic Ghana Medie": {"region": "Greater Accra", "city": "Medie"},
            "Voltic Ghana Akwadum": {"region": "Eastern", "city": "Akwadum"},
            "Ayensu starch": {"region": "Central", "city": "Badwease"},
            "Bel-Aqua Mineral Water": {"region": "Greater Accra", "city": "Kpone"}
        }
    },
    "Lubricant $ Oil Refinery": {
        "companies": {
            "Tema Lube Oil": {"region": "Greater Accra", "city": "Tema"},
            "Akwaaba oil": {"region": "Greater Accra", "city": "Tema"},
            "Chase Petroleum": {"region": "Greater Accra", "city": "Kpone"},
            "Blue Ocean Petroleum Ltd": {"region": "Greater Accra", "city": "Kpone"},
            "Cyrus Oil ": {"region": "Greater Accra", "city": "Tema"},
            "Petroleum Hub Ltd": {"region": "Greater Accra", "city": "Kpone"},
            "Quantum Petroleum Ltd": {"region": "Greater Accra", "city": "Kpone"}
        }
    },
    "Fertilizer": {
        "companies": {
            "Sidalco Ltd": {"region": "Greater Accra", "city": "Tema"},
            "Chemico Ghana Ltd": {"region": "Greater Accra", "city": "Tema"}
        }
    },
    "Paper": {
        "companies": {
            "Three Dreamers": {"region": "Greater Accra", "city": "Tema"},
            "Sec-Print": {"region": "Greater Accra", "city": "Achimota"},
            "Shinefeel Ghana Ltd": {"region": "Eastern", "city": "Akosombo"},
            "Akosombo Paper Company": {"region": "Eastern", "city": "Akosombo"},
            "Nixin Paper Mill": {"region": "Greater Accra", "city": "Tema"}
        }
    },
    "Cocoa Processing": {
        "companies": {
            "Cocoa Processing Company": {"region": "Greater Accra", "city": "Tema"},
            "Barry Callebaut Ghana": {"region": "Greater Accra", "city": "Tema"},
            "Niche Cocoa": {"region": "Greater Accra", "city": "Tema"},
            "Cargill Ghana Ltd": {"region": "Greater Accra", "city": "Tema"},
            "Touton Cocoa Processing": {"region": "Greater Accra", "city": "Tema"}
        }
    },

    "Oil and Fat Processing Industry": {
        "companies": {
            "Wilmar Africa Ltd": {"region": "Greater Accra", "city": "Tema"},
            "GOPDC": {"region": "Eastern", "city": "Kwae"},
            "Seftech Oil": {"region": "Central", "city": "Cape Coast"},
            "Avnash Industries": {"region": "Northern", "city": "Tamale"}
        }
    },

    "Food Processing": {
        "companies": {
            "Nestlé Ghana Ltd": {"region": "Greater Accra", "city": "Tema"},
            "Pioneer Food Cannery": {"region": "Greater Accra", "city": "Tema"},
            "Cosmos Fish Processing": {"region": "Greater Accra", "city": "Tema"},
            "GB Foods": {"region": "Greater Accra", "city": "Tema"},
            "Nutrifoods (Bisquit)": {"region": "Greater Accra", "city": "Tema"},
            "Nutrifoods (Tasty Tom)": {"region": "Greater Accra", "city": "Tema"},
            "Food Processes Int.": {"region": "Greater Accra", "city": "Tema"},
            "Ignis": {"region": "Greater Accra", "city": "Tema"},
            "Nsawam Food Canary": {"region": "Eastern", "city": "Nsawam"},
            "Happy Sunshine": {"region": "Eastern", "city": "Suhum"},
            "HPW Fresh and Dry Ltd": {"region": "Eastern", "city": "Adeiso-Bawjiase"},
            "WAD Africa": {"region": "Greater Accra", "city": "Agyin Kotoku "},
            "Abasakese Industries": {"region": "Greater Accra", "city": "Agyin Kotoku "},
            "Promasidor Ghana": {"region": "Greater Accra", "city": "Accra"},
            "Praise Export": {"region": "Greater Accra", "city": "Pokuase"},
            "Daily Food": {"region": "Greater Accra", "city": "Accra"},
            "D-United Food Industries": {"region": "Greater Accra", "city": "Spintex"},
            "Twellium Industries": {"region": "Greater Accra", "city": "Medie"}
        }
    },
    "Textile": {
        "companies": {
            "Tex Styles Ghana Ltd ": {"region": "Greater Accra", "city": "Tema"},
            "GTP": {"region": "Greater Accra", "city": "Tema"},
            "Akosombo Textiles Ltd": {"region": "Greater Accra", "city": "Akosombo"},
            "Printex Ghana Ltd": {"region": "Eastern", "city": "Spintex"}
        }
    },

    "Chemical": {
        "companies": {
            "Maxtachem": {"region": "Greater Accra", "city": "Accra"},
            "Cleaning Solution Ghana": {"region": "Greater Accra", "city": "Tema"},
            "Delta Agro Ghana Ltd": {"region": "Greater Accra", "city": "Tema"},
            "Ghandou Cosmetics Ltd": {"region": "Greater Accra", "city": "Spintex"},
            "Gilsan Ltd": {"region": "Greater Accra", "city": "Weija"},
            "Kofi Ababio & sons": {"region": "Greater Accra", "city": "Pantang"},
            "MC Bauchemie": {"region": "Greater Accra", "city": "Ahyiyie"},
            "Cevag Ltd": {"region": "Greater Accra", "city": "Tema"}
        }
    },
    "Fruit Processing": {
        "companies": {
            "Blue Skies Ghana": {"region": "Eastern", "city": "Nsawam"},
            "Sono Ghana Ltd": {"region": "Eastern", "city": "Asamankese"}
        }
    },

    "Pharmaceutical Industry": {
        "companies": {
            "Ernest Chemists": {"region": "Greater Accra", "city": "Tema"},
            "OA & J Pharmacy": {"region": "Greater Accra", "city": "Tema"},
            "Kinapharma Ltd": {"region": "Greater Accra", "city": "Spintex"},
            "Phyro-Riker Pharmaceutical Ltd": {"region": "Greater Accra", "city": "Achimota"},
            "Danadams Pharmaceutical": {"region": "Greater Accra", "city": "Spintex"},
            "Pams Phamarceuticals": {"region": "Eastern", "city": "Nsawam"},
            "Pharmanova Pharmaceutical Ltd": {"region": "Greater Accra", "city": "Kpone"},
            "Letap Pharmaceutical Ltd.": {"region": "Greater Accra", "city": "South Industrial Area"},
            "Pharmacare": {"region": "Greater Accra", "city": "North Industrial Area"},
            "Dannex": {"region": "Greater Accra", "city": "North Industrial Area"},
            "Ayrton Drug(Syrup)": {"region": "Greater Accra", "city": "North Industrial Area"},
            "Ayrton Drug(Tablet)": {"region": "Greater Accra", "city": "North Industrial Area"},
            "Entrance Pharmaceuticals": {"region": "Greater Accra", "city": "Spintex"},
            "Unichem Ghana Ltd": {"region": "Greater Accra", "city": "Spintex"},
            "Eskay Therapeutics": {"region": "Greater Accra", "city": "Spintex"},
            "New Global Pharmacy": {"region": "Greater Accra", "city": "Weija"},
            "M & G Pharmaceuticals": {"region": "Greater Accra", "city": "James Town"}
        }
    },

    "Paint Industry": {
        "companies": {
            "Azar Paints": {"region": "Greater Accra", "city": "Accra"},
            "Coral Paints": {"region": "Greater Accra", "city": "Tema"},
            "BBC Industry Ltd": {"region": "Greater Accra", "city": "Tema"},
            "Neuce Paint": {"region": "Greater Accra", "city": "Tema"},
            "Essay Paints": {"region": "Greater Accra", "city": "North Industrial Area"},
            "De-luxy Paint": {"region": "Greater Accra", "city": "North Industrial Area"},
            "Anchor Paints ": {"region": "Greater Accra", "city": "North Industrial Area"},
            "Zaktex Paint": {"region": "Greater Accra", "city": "North Industrial Area"},
            "Yamco Ghana ": {"region": "Greater Accra", "city": "Spintex"}
        }
    }
}


# Constants
weather_conditions = ["-- Select --", "Sunny", "Cloudy", "Partly Cloudy", "Rainy", "Windy", "Hazy", "Stormy", "Foggy"]
wind_directions = ["-- Select --", "N", "NE", "E", "SE", "S", "SW", "W", "NW", "NNE", "ENE", "ESE", "SSE", "SSW", "WSW", "WNW", "NNW"]
officers = ['Obed Korankye', 'Clement Ackaah', 'Peter Ohene-Twum', 'Benjamin Essien', 'Mawuli Amegah']
drivers = ["Kanazoe Sia", "Kofi Adjei", "Fatau"]
sampling_points = ["-- Select --", "Point 1", "Point 2", "Point 3", "Point 4"]

# Weather defaults
weather_defaults = {
    "Sunny": {"temp": list(range(25, 41)), "rh": list(range(40, 91))},
    "Rainy": {"temp": list(range(20, 27)), "rh": list(range(70, 101))},
    "Cloudy": {"temp": list(range(25, 35)), "rh": list(range(40, 91))},
    "Partly Cloudy": {"temp": list(range(21, 35)), "rh": list(range(35, 91))},
    "Windy": {"temp": list(range(20, 30)), "rh": list(range(40, 91))},
    "Hazy": {"temp": list(range(20, 31)), "rh": list(range(40, 91))},
    "Stormy": {"temp": list(range(17, 25)), "rh": list(range(80, 101))},
    "Foggy": {"temp": list(range(15, 22)), "rh": list(range(85, 101))}
}

# Helper for selecting time
def get_custom_time(label, key_prefix, hour_key="hour", minute_key="minute"):
    col1, col2 = st.columns(2)
    with col1:
        hour = st.selectbox(f"{label} - Hour", list(range(0, 24)), key=f"{key_prefix}_{hour_key}")
    with col2:
        minute = st.selectbox(f"{label} - Minute", list(range(0, 60, 1)), key=f"{key_prefix}_{minute_key}")
    return datetime.strptime(f"{hour}:{minute}", "%H:%M").time()


def get_companies(sector):
    return list(sector_data.get(sector, {}).get("companies", {}).keys())

def get_region_city(company_name):
    for sector in sector_data.values():
        companies = sector.get("companies", {})
        if company_name in companies:
            info = companies[company_name]
            return info.get("region", "Unknown"), info.get("city", "Unknown")
    return "Unknown", "Unknown"

# === Main Form Function ===
def general_info_form():
    st.subheader("1. General Information")
    sector_options = ["-- Select --"] + list(sector_data.keys())
    sector = st.selectbox("Select Industry Sector", sector_options, key="sector")

    company = None
    region = city = ""
    if sector != "-- Select --":
        companies = get_companies(sector)
        company = st.selectbox("Select Company", ["-- Select --"] + companies, key="company")
        if company != "-- Select --":
            region, city = get_region_city(company)
            st.text_input("Region", value=region, disabled=True, key="region")
            st.text_input("Town/City", value=city, disabled=True, key="city")
        else:
            st.info("Please select a company.")
    else:
        st.info("Please select a sector to begin.")

    # Sampling Point
    st.subheader("2. Sampling Point Details")
    sampling_point = st.selectbox("📍 Sampling Point", sampling_points)
    description = st.text_area("Sampling Point Description", key="description")
    longitude = st.number_input("🌐 Longitude", step=0.0001, format="%.4f")
    latitude = st.number_input("🌐 Latitude", step=0.0001, format="%.4f")

    # Date and Time
    st.subheader("3. Date and Time")
    date = st.date_input("📅 Start Date", value=datetime.today())
    time = get_custom_time("⏱️ Start Time", "start", "hour", "minute")
    date_time = datetime.combine(date, time)

    # Weather
    st.subheader("4. Weather Conditions")
    weather = st.selectbox("🌦️ Weather", weather_conditions)

    if weather != "-- Select --":
        temp_options = ["-- Select --"] + [str(t) for t in weather_defaults[weather]["temp"]]
        rh_options = ["-- Select --"] + [str(rh) for rh in weather_defaults[weather]["rh"]]
        wind_speed_options = ["-- Select --"] + [f"{round(ws, 1)}" for ws in [x * 0.5 for x in range(0, 41)]]

        temperature = st.selectbox("🌡️ Temperature (°C)", temp_options)
        wind_speed = st.selectbox("💨 Wind Speed (km/h)", wind_speed_options, key="wind_speed")
        wind_direction = st.selectbox("🧭 Wind Direction", wind_directions, key="wind_direction")
        humidity = st.selectbox("💧 Humidity (%)", rh_options)

        # Convert selected values to numbers
        temperature = int(temperature) if temperature != "-- Select --" else None
        wind_speed = float(wind_speed) if wind_speed != "-- Select --" else None
        humidity = int(humidity) if humidity != "-- Select --" else None
    else:
        temperature = humidity = wind_speed = wind_direction = None

    # Personnel
    st.subheader("5. Officer(s) Involved")
    selected_officers = st.multiselect("Select Officer(s)", officers, key="selected_officers")
    driver = st.selectbox("Select Driver", ["-- Select --"] + drivers, key="driver")

    return {
        "sector": sector,
        "company": company,
        "region": region,
        "city": city,
        "sampling_point_name": sampling_point,
        "coordinate": f"{latitude}, {longitude}",
        "description": description,
        "date_time": date_time,
        "weather": weather,
        "temperature": temperature,
        "wind_speed": wind_speed,
        "wind_direction": wind_direction,
        "humidity": humidity,
        "selected_officers": selected_officers,
        "driver": driver,
    }
