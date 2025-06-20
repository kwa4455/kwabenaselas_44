import streamlit as st
from datetime import datetime

weather_conditions = ["Clear", "Cloudy", "Rainy", "Windy"]
officers = ['Obed Korankye', 'Clement Ackaah', 'Peter Ohene-Twum', 'Benjamin Essien', 'Mawuli Amegah']
drivers = ["Kanazoe Sia", "Kofi Adjei","Fatau"]




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
    }
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
    }
    "Fertilizer": {
        "companies": {
            "Sidalco Ltd": {"region": "Greater Accra", "city": "Tema"},
            "Chemico Ghana Ltd": {"region": "Greater Accra", "city": "Tema"}
        }
    }
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
            "M&G Pharmaceuticals": {"region": "Greater Accra", "city": "James Town"}
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


def get_companies(sector):
    return list(sector_data.get(sector, {}).get("companies", {}).keys())

def get_region_city(company_name):
    for sector in sector_data.values():
        companies = sector.get("companies", {})
        if company_name in companies:
            info = companies[company_name]
            return info.get("region", "Unknown"), info.get("city", "Unknown")
    return "Unknown", "Unknown"

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
    sampling_point_name = st.text_input("Sampling Point Name", key="sampling_point_name")
    coordinate = st.text_input("Coordinates (e.g., 12.3456, 78.9012)", key="coordinate")
    description = st.text_area("Sampling Point Description", key="description")

    # Date and Time
    st.subheader("3. Date and Time")
    date_time = st.datetime_input("Select Date & Time", value=datetime.now(), key="date_time")

    # Weather
    st.subheader("4. Weather Conditions")
    weather = st.selectbox("Select Weather", ["-- Select --"] + weather_conditions, key="weather")
    temperature = wind_speed = wind_direction = humidity = None
    if weather != "-- Select --":
        temperature = st.number_input("Temperature (°C)", step=0.1, key="temperature")
        wind_speed = st.number_input("Wind Speed (km/h)", step=0.1, key="wind_speed")
        wind_direction = st.text_input("Wind Direction", key="wind_direction")
        humidity = st.slider("Humidity (%)", 0, 100, key="humidity")

    # Personnel
    st.subheader("5. Officer(s) Involved")
    selected_officers = st.multiselect("Select Officer(s)", officers, key="selected_officers")
    driver = st.selectbox("Select Driver", ["-- Select --"] + drivers, key="driver")

    return {
        "sector": sector,
        "company": company,
        "region": region,
        "city": city,
        "sampling_point_name": sampling_point_name,
        "coordinate": coordinate,
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




