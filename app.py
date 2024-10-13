import streamlit as st
import datetime
import os
import requests
from PIL import Image, ImageOps
from io import BytesIO

# Streamlit title and introduction
st.title("Archived MesoAnalysis GIF Generator")
st.write("Enter the parameters below to generate and download a GIF.")

# Input Fields
date_input = st.date_input("Select the date (YYYY-MM-DD):", datetime.date.today())
start_hour = st.number_input("Start Hour (UTC, 0-23):", min_value=0, max_value=23, value=0)
end_hour = st.number_input("End Hour (UTC, 0-23):", min_value=0, max_value=23, value=12)

# Define the parameter dropdown options and sections
parameter_options = {
    "Choose a Parameter":{
    },
    "Basic Surface Parameters": {
        "MSL Pressure/Wind": "pmsl",
        "T/Td/Wind": "ttd",
        "Moisture Convergence": "mcon",
        "ThetaE Advection": "thea",
        "2hr Pressure Change": "pchg"
    },

    
    "Basic UA/Forcing Fields": {
        "850 mb": "850mb",
        "700 mb": "700mb",
        "500 mb": "500mb",
        "300 mb": "300mb",
        "Deep Moisture Convergence": "dlcp",
        "Surface Frontogenesis": "sfnt",
        "850mb Temperature Advection": "tadv",
        "850mb Frontogenesis": "8fnt",
        "700mb Frontogenesis": "7fnt",
        "850-700mb Frontogenesis": "857f",
        "700-500mb Frontogenesis": "75ft",
        "700-400mb Diff. Vorticity Advection": "vadv",
        "400-250mb Pot. Vorticity Advection": "padv",
        "850-250mb Diff. Divergence": "ddiv",
        "300 mb Jet Circulation": "ageo"
    },
    "Thermodynamic Fields": {
        "SB Cape/SB CIN": "sbcp",
        "100mb ML CAPE": "mlcp",
        "MU CAPE/LPL Height": "mucp",
        "SB Lifted Index/ CINH": "muli",
        "Mid-Level Lapse Rates": "laps",
        "Low-Level Lapse Rates": "lllr",
        "Normalized CAPE": "ncap",
        "Downdraft CAPE": "dcape",
        "LFC Height": "lfch",
        "LCL Height": "lclh",
        "LCL to LFC Mean RH": "lfrh",
        "Skew-t": "skewt"
    },
    "Wind Shear": {
        "850-300mb Mean Wind": "mnwd",
        "0-6km Shear Vector": "shr6",
        "0-8km Shear Vector": "shr8",
        "Effective Shear": "eshr",
        "BRN Shear": "brns",
        "0-1km SR Helicity": "srh1",
        "0-3km SR Helicity": "srh3",
        "Effective SR Helicity": "effh",
        "0-1km Shear Vector": "shr1",
        "850 & 500mb Wind Crossover": "xover",
        "Hodographs": "hodo"
    },
    "Storm Relative Winds": {
        "0-2km SR Winds": "llsr",
        "4-6km SR Winds": "mlsr",
        "9-11km SR Winds": "hlsr",
        "Anvil Level SR Winds": "alsr"
    },
    "Composite Indices": {
        "Supercell Composite": "scp",
        "Supercell Composite (left-moving)": "lscp",
        "Significant Tornado (fixed layer)": "stor",
        "Significant Tornado (effective layer)": "stpc",
        "Significant Hail Parameter": "sigh",
        "Derecho Composite": "dcp",
        "Craven/Brooks SigSvr": "cbsig",
        "1km EHI": "ehi1",
        "3km EHI": "ehi3",
        "3km VGP": "vgp3",
        "MCS Maintenance Probability": "mcsm",
        "01km Tornadic Energy Helicity Index": "tehi",
        "Tornadic Tilting & Stretching": "tts"
    },
    "Heavy Rainfall": {
        "Precipitable Water": "pwtr",
        "850 mb Moisture Transport": "tran",
        "Upwind Propagation Vector": "prop"
    },
    "Winter Weather": {
        "Surface Wet Bulb Temperature": "swbt",
        "Freezing Level Info": "fzlv",
        "Critical Thickness": "thck",
        "800-750 mb EPVg": "epvl",
        "650-500mb EPVg": "epvm",
        "Lake Effect Snow 1": "les1",
        "Lake Effect Snow 2": "les2"
    },
    "Fire Weather": {
        "Surface RH, Temperature, Wind": "sfir",
        "Fosberg Index": "fosb",
        "Low-Altitude Haines Index": "lhan",
        "Mid-Altitude Haines Index": "mhan",
        "High-Altitude Haines Index": "hhan",
        "Lower Atmos. Severity Index": "lasi"
    }
}

# Create a dropdown with section headers
parameter_choices = []
for section, params in parameter_options.items():
    parameter_choices.append(f"--- {section} ---")
    parameter_choices.extend([key for key in params.keys()])

# Dropdown for parameter selection
selected_parameter = st.selectbox("Select a parameter:", parameter_choices)

# Get the actual parameter identifier based on the selected name
for section, params in parameter_options.items():
    if selected_parameter in params:
        parameter_identifier = params[selected_parameter]
        break
else:
    parameter_identifier = None

# Convert date input to the required string format (YYYYMMDD)
date_str = date_input.strftime("%Y%m%d")

# Define helper functions
def fetch_image(date, hour, parameter):
    base_url = "https://www.spc.noaa.gov/exper/ma_archive/images_s4"
    url = f"{base_url}/{date}/{hour:02d}_{parameter}.gif"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            image = Image.open(BytesIO(response.content)).convert("RGBA")
            white_bg = Image.new("RGBA", image.size, "WHITE")
            combined = Image.alpha_composite(white_bg, image)
            return combined.convert("RGB")
        except Exception as e:
            print(f"Failed to identify image for time {hour:02d}:00, Error: {e}")
            return None
    else:
        print(f"Failed to fetch image for time {hour:02d}:00, Status Code: {response.status_code}")
        return None

def fetch_and_save_images(date, start_hour, end_hour, parameter):
    os.makedirs('images', exist_ok=True)
    images = []
    for hour in range(start_hour, end_hour + 1):
        image = fetch_image(date, hour, parameter)
        if image:
            image_path = f'images/{hour:02d}_{parameter}.gif'
            image.save(image_path)
            images.append(image_path)
    return images

def create_gif(image_paths, output_path):
    images = [Image.open(path) for path in image_paths]
    if images:
        images[0].save(output_path, save_all=True, append_images=images[1:], loop=0, duration=500, disposal=2)
        return output_path
    else:
        return None

# When the user clicks "Generate GIF", run the GIF creation process
if st.button("Generate GIF"):
    if parameter_identifier:
        st.write(f"Generating GIF for {selected_parameter} ({parameter_identifier}) from {start_hour}:00 to {end_hour}:00 UTC on {date_str}...")
        
        image_paths = fetch_and_save_images(date_str, start_hour, end_hour, parameter_identifier)
        output_gif_path = f"{date_str}_{start_hour}z-{end_hour}z_{parameter_identifier}.gif"
        
        gif_path = create_gif(image_paths, output_gif_path)
        
        if gif_path:
            st.success("GIF Generated Successfully!")
            st.image(gif_path)  # Display the GIF
            with open(gif_path, "rb") as file:
                btn = st.download_button(
                    label="Download GIF",
                    data=file,
                    file_name=os.path.basename(gif_path),
                    mime="image/gif"
                )
        else:
            st.error("No GIF could be generated. Please check your inputs.")
    else:
        st.error("Please select a valid parameter.")
