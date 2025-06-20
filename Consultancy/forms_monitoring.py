import streamlit as st

installation_options = {
    "Generator Set": ["Diesel", "Petrol", "Natural Gas"],
    "Boiler": ["Coal", "Natural Gas", "Fuel Oil"],
    "Furnace": ["Electricity", "Natural Gas", "LPG"]
}

def monitoring_type_form():
    st.subheader("2. Type of Monitoring")
    monitoring_type = st.selectbox("Monitoring Type", ["-- Select --", "Noise", "Gases", "Stack Emission", "VOCs"], key="monitoring_type")

    if monitoring_type == "Noise":
        leq = st.text_input("Leq", key="leq")
        l10 = st.text_input("L10", key="l10")
        l50 = st.text_input("L50", key="l50")
        l90 = st.text_input("L90", key="l90")
        lmax = st.text_input("Lmax", key="lmax")
        return monitoring_type, {
            "leq": leq, "l10": l10, "l50": l50, "l90": l90, "lmax": lmax
        }

    elif monitoring_type == "Gases":
        no2 = st.text_input("NO₂ (Nitrogen Dioxide)", key="no2")
        so2 = st.text_input("SO₂ (Sulfur Dioxide)", key="so2")
        return monitoring_type, {
            "no2": no2, "so2": so2
        }

    elif monitoring_type == "Stack Emission":
        gen_set = st.text_input("Type of Generator Set", key="gen_set")
        installation = st.selectbox("Type of Fuel Burning Installation", ["-- Select --"] + list(installation_options.keys()), key="installation")
        fuel = None
        if installation != "-- Select --":
            fuel = st.selectbox("Type of Fuel", ["-- Select --"] + installation_options[installation], key="fuel")

        measurement_result = st.text_input("Measurement Result", key="measurement_result")

        st.markdown("### Stack Emission Measurement Area")
        t_room = st.number_input("T-room (°C)", format="%.2f", key="t_room")
        t_gas = st.number_input("T-gas (°C)", format="%.2f", key="t_gas")
        co2 = st.number_input("CO2 (%)", format="%.2f", key="co2")
        o2 = st.number_input("O2 (%)", format="%.2f", key="o2")
        co = st.number_input("CO (mg/Nm³)", format="%.2f", key="co")
        so2_stack = st.number_input("SO2 (mg/Nm³)", format="%.2f", key="so2_stack")
        no2_stack = st.number_input("NO2 (mg/Nm³)", format="%.2f", key="no2_stack")

        return monitoring_type, {
            "gen_set": gen_set,
            "installation": installation,
            "fuel": fuel,
            "measurement_result": measurement_result,
            "t_room": t_room,
            "t_gas": t_gas,
            "co2": co2,
            "o2": o2,
            "co": co,
            "so2_stack": so2_stack,
            "no2_stack": no2_stack,
        }

    elif monitoring_type == "VOCs":
        st.markdown("### VOCs Monitoring")
        voc_total = st.number_input("Total VOCs (mg/m³)", format="%.2f", key="voc_total")
        benzene = st.number_input("Benzene (mg/m³)", format="%.2f", key="benzene")
        toluene = st.number_input("Toluene (mg/m³)", format="%.2f", key="toluene")
        xylene = st.number_input("Xylene (mg/m³)", format="%.2f", key="xylene")

        return monitoring_type, {
            "voc_total": voc_total,
            "benzene": benzene,
            "toluene": toluene,
            "xylene": xylene
        }

    else:
        return monitoring_type, {}
