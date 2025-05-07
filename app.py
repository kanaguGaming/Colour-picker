import streamlit as st
import base64
import io
from PIL import Image

st.set_page_config(page_title="Live Hover Color Detector", layout="centered")
st.title("🎨 Live Hover Color Detector")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    # Load and convert image
    image = Image.open(uploaded_file).convert("RGB")
    
    # Resize for consistent display (max width 700px)
    max_width = 700
    if image.width > max_width:
        scale = max_width / image.width
        new_size = (int(image.width * scale), int(image.height * scale))
        image = image.resize(new_size)

    # Convert to base64
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    width, height = image.size

    st.components.v1.html(f"""
    <html>
    <head>
    <style>
        #canvas {{
            border: 2px solid #ccc;
            cursor: crosshair;
            max-width: 100%;
        }}
        #tooltip {{
            position: absolute;
            padding: 8px;
            background: rgba(255,255,255,0.95);
            border: 1px solid #888;
            border-radius: 5px;
            font-family: Arial;
            font-size: 12px;
            display: none;
            pointer-events: none;
            z-index: 100;
        }}
        #wrapper {{
            position: relative;
            width: fit-content;
            margin: auto;
        }}
    </style>
    </head>
    <body>
        <div id="wrapper">
            <canvas id="canvas" width="{width}" height="{height}"></canvas>
            <img id="img" src="data:image/png;base64,{img_base64}" style="display:none;" />
            <div id="tooltip"></div>
        </div>

        <script>
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const img = document.getElementById('img');
    const tooltip = document.getElementById('tooltip');

    let lastRGB = "";
    let fetchTimeout;

    if (img.complete) {{
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
    }} else {{
        img.onload = function() {{
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        }};
    }}

    function rgbToHex(r, g, b) {{
        return "#" + [r, g, b].map(x =>
            x.toString(16).padStart(2, '0')
        ).join('');
    }}

    canvas.addEventListener('mousemove', function(e) {{
        const rect = canvas.getBoundingClientRect();
        const x = Math.floor(e.clientX - rect.left);
        const y = Math.floor(e.clientY - rect.top);

        const pixel = ctx.getImageData(x, y, 1, 1).data;
        const [r, g, b] = pixel;
        const rgbStr = `rgb(${{r}}, ${{g}}, ${{b}})`;
        const hex = rgbToHex(r, g, b);

        // Move tooltip
        tooltip.style.left = (x + 15) + "px";
        tooltip.style.top = (y + 15) + "px";
        tooltip.style.display = "block";
        tooltip.innerHTML = `
            <div style='display: flex; align-items: center;'>
                <div style='width: 30px; height: 20px; background-color: ${{rgbStr}}; border: 1px solid #000; margin-right: 8px;'></div>
                <div>
                    <strong>Loading name…</strong><br/>
                    RGB: (${{r}}, ${{g}}, ${{b}})<br/>
                    HEX: ${{hex}}
                </div>
            </div>
        `;

        // Debounce API call
        if (rgbStr !== lastRGB) {{
            lastRGB = rgbStr;

            if (fetchTimeout) clearTimeout(fetchTimeout);

            fetchTimeout = setTimeout(() => {{
                fetch(`https://www.thecolorapi.com/id?rgb=${{rgbStr}}`)
                    .then(res => res.json())
                    .then(data => {{
                        const name = data.name.value;
                        tooltip.innerHTML = `
                            <div style='display: flex; align-items: center;'>
                                <div style='width: 30px; height: 20px; background-color: ${{rgbStr}}; border: 1px solid #000; margin-right: 8px;'></div>
                                <div>
                                    <strong>${{name}}</strong><br/>
                                    RGB: (${{r}}, ${{g}}, ${{b}})<br/>
                                    HEX: ${{hex}}
                                </div>
                            </div>
                        `;
                    }})
                    .catch(() => {{
                        tooltip.innerHTML = `
                            <div style='display: flex; align-items: center;'>
                                <div style='width: 30px; height: 20px; background-color: ${{rgbStr}}; border: 1px solid #000; margin-right: 8px;'></div>
                                <div>
                                    <strong>Unknown</strong><br/>
                                    RGB: (${{r}}, ${{g}}, ${{b}})<br/>
                                    HEX: ${{hex}}
                                </div>
                            </div>
                        `;
                    }});
            }}, 300);
        }}
    }});

    canvas.addEventListener('mouseleave', function() {{
        tooltip.style.display = "none";
    }});
</script>

    </body>
    </html>
    """, height=height + 100)
