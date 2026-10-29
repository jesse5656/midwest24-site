"""Generate a theme-safe SVG container without altering the approved raster logo."""
import base64
from pathlib import Path
root = Path('/home/jesse/Documents/Projects/midwest24-site')
data = base64.b64encode((root/'assets/branding/products/midwest24-core-identity-logo-light.png').read_bytes()).decode()
out = root/'assets/branding/releases/approved-20261029/identity-logo.svg'
out.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1640 540" role="img" aria-label="Midwest24 Core Identity"><rect width="1640" height="540" rx="24" fill="white"/><image x="20" y="20" width="1600" height="500" href="data:image/png;base64,'+data+'"/></svg>')
