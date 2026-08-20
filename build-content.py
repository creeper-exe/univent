#!/usr/bin/env python3
"""Generates the shared chrome (header, footer) and the product / certificate
grids across every page of the site.

Product data is transcribed from univents.org/products; categories and
descriptions are theirs verbatim. Rerun after editing NAV, CATEGORIES or CERTS:
    python3 build-content.py

Each page owns its own prose. This script only fills the marked regions:
    <!-- HEADER:START --> … <!-- HEADER:END -->     every page
    <!-- FOOTER:START --> … <!-- FOOTER:END -->     every page
    <!-- PRODUCTS:START --> … <!-- PRODUCTS:END --> products.html
    <!-- CERTS:START --> … <!-- CERTS:END -->       certificates.html
"""
import html, os, re, zipfile

PAGES = ["index.html", "products.html", "certificates.html", "projects.html",
         "about.html", "contact.html"]

# (href, label) — the header nav, in order
NAV = [
    ("products.html", "Products"),
    ("certificates.html", "Certifications"),
    ("projects.html", "Our Clients"),
    ("about.html", "About"),
    ("contact.html", "Contact"),
]

# (slug, label, [(image, name, description), ...])
CATEGORIES = [
    ("decorative", "Decorative Fans", [
        ("SLIM", "Slim", "Low noise fans with low power consumption"),
    ]),
    ("wall", "Wall Mounted Fans", [
        ("AXW", "AXW Model", "Axial wall mounted fan direct driven. Plate mounted casing, galvanized steel epoxy painted, c/w external rotor motors IP 54 Class F"),
        ("BXVPM", "BXV-PM", "Wall mounted axial flow fan with thermoplastic or aluminium impellers with pitch angle"),
    ]),
    ("duct", "Duct Fans", [
        ("RS", "RS", "Straight airflow and easy installation — with high pressure stability, low noise level and high efficiency"),
        ("RSRUCK", "RS Ruck", "Backward curved centrifugal fan, speed controllable and integrated thermal switch"),
    ]),
    ("mixed", "Mixed Flow Fans", [
        ("MIXEDFLOW", "Mixed Flow Fan", "High quality motor made in Nanyoo, run out only 0.35 mm, strong air volume and static pressure"),
        ("EMMRUCK", "EM Model Ruck Axial Inline Fan", "Diagonal impeller with stator. Plastic housing, 3-step integrated thermostatic switch, including mounting bracket"),
        ("ELERUCK", "EL Model Ruck Axial Inline", "Diagonal impeller with stator. Plastic housing, speed controllable, integrated thermostatic switch, including mounting bracket"),
        ("MPCRUCK", "MPC Model Ruck", "Motor inside the airflow, galvanized metal housing, speed controllable, 30 mm insulation, with bottom pan, variable outlet"),
        ("MPCTRUCK", "MPC T Model Ruck", "Motor outside of air stream, galvanized metal housing, speed controllable, bottom pan with drain, 30 mm insulation"),
        ("MPCTIRUCK", "MPC TI Model Ruck (120°C)", "Linear airflow, Star-Delta operation possible. Star: direct 400V 3~ grid or frequency converter with 400V output. Delta: direct 230V 3~ grid or frequency converter with 230V 1~ input and 230V 3~ output"),
        ("KVTRUCK", "KVT Ruck", "Forward curved centrifugal fan, galvanized metal housing, speed controllable, integrated thermostatic switch, swing-out fan unit"),
    ]),
    ("didw", "DIDW Fans", [
        ("ATMODEL", "AT Model Fan Section", "Fan section, anticorrosive galvanized steel sheet, side glass, vibration isolation of mineral wool"),
        ("ATS", "AT-S", "Double-inlet, belt-driven centrifugal fans with axis outlet on both sides and impeller with forward-facing blades"),
        ("ATTIC", "AT-TIC", "Double-inlet, belt-driven centrifugal fans with reinforced structure and rigid bridge bearings supported on the structure"),
        ("ADH", "ADH", "Double-inlet, belt-driven centrifugal fans with reinforced structure and rigid bridge bearings supported on the structure"),
        ("RDH", "RDH", "High pressure centrifugal fans, backward curved — welded"),
    ]),
    ("sisw", "SISW Fans", [
        ("RSH", "RSH", "Single-inlet, belt-driven centrifugal fans with axis outlet and impeller with backward-facing blades"),
    ]),
    ("roof", "Roof Top Fans", [
        ("RSR", "RS-R", "Backward curved centrifugal fan, metal housing RAL 7035, speed controllable"),
        ("SIWF", "SIWF", "Roof top fan with impeller motor KTI and external rotor motor, impeller with backward-facing blades"),
        ("DVARUCK", "DVA Ruck", "Backward curved centrifugal fan, housing made of aluminium AlMg3, speed controllable, integrated thermostatic switch, maintenance-free ball bearings"),
        ("DVNRUCK", "DVN Ruck", "Max. medium temperature 120°C, motor outside the air stream due to protection plate, swing-out fan section, speed controllable, drain tray"),
        ("BXVR", "BXV-R", "Short cased axial roof top ventilator with thermoplastic or aluminium impellers with pitch angle"),
        ("BXVRBOX", "BXV-R Box", "Short cased axial roof top box ventilator with thermoplastic or aluminium impellers with pitch angle"),
    ]),
    ("axial", "Axial Inline Fans", [
        ("BXV", "BXV", "Long and short cased axial flow fan with thermoplastic or aluminium impellers with pitch angle"),
        ("BXVBD", "BXV-BD", "Short cased belt driven axial flow fan with thermoplastic or aluminium impellers with pitch angle"),
    ]),
    ("smoke", "Smoke Fans", [
        ("TST", "TST", "Cased axial fans with short casing for working inside fire danger zones, 400°C/2h"),
        ("JETFAN", "Jet Fan", "Jet fans especially designed for tunnel ventilation. 400ºC/2h, 300ºC/2h and 200ºC/2h. Certificates according to model"),
        ("DSX", "DSX", "400°C/2h centrifugal belt-driven fans with backward-curved impeller"),
        ("CADSX", "CADSX", "400°C/2h belt-driven extraction units with backward-curved impeller"),
        ("MPCTIF4RUCK", "MPC TI F4 Ruck Smoke Fan", "200°C constant operation and 400°C/2h, EN 12101-3:2015, Certificate 1404-CPR-3072, Star-Delta compatible, Fire-Mode function"),
        ("DVNF4RUCK", "DVN F4 Ruck Smoke Roof Fan", "200°C constant operation and 400°C/2h, EN 12101-3:2015, Certificate 1404-CPR-3072, Star-Delta compatible, Fire-Mode function"),
    ]),
    ("curtain", "Air Curtain", [
        ("AIRCURTAIN", "Air Curtain", "Slim all metal housing with aesthetic curved design, full metal shell and minimal maintenance, easy installation and cleaning"),
        ("BXVBIF1", "BXV-BIF Cylindrical", "Bifurcated axial fans, direct motor driven, specially for handling hostile air conditions — hot, dust laden, corrosive fumes or gases. Cylindrical range 400 to 1250 mm"),
        ("BXVBIF2", "BXV-BIF Conical", "Bifurcated axial fans, direct motor driven, specially for handling hostile air conditions — hot, dust laden, corrosive fumes or gases. Conical range 315 to 630 mm"),
    ]),
    ("accessories", "Accessories", [
        ("SQGRILL", "Square Grill with Shutters", "Square grill with shutters, 100 · 120 · 150 mm diameter"),
        ("FANDAMPER", "Fan Damper", "Fan damper, 100 · 120 mm diameter"),
        ("PLASTICDIFFUSER", "All-Purpose Plastic Diffuser", "All-purpose plastic diffuser, 100 · 120 · 150 mm diameter"),
        ("CIRCGRILL", "Circular Grill", "Circular grill, 100 · 120 · 150 mm diameter"),
        ("WOODDIFF", "Wood Diffuser", "Wood diffuser, 100 · 120 · 160 mm diameter"),
        ("ROUNDGRILL", "Round Ceiling Grill", "Round ceiling grill, 100 · 120 · 150 mm diameter"),
    ]),
    ("filters", "Filters", [
        ("PREFILTER", "Pre-Filter", "Primary air filter with aluminium frame, woven aluminium wire media, 75% efficiency"),
        ("BAGFILTER", "Bag Filter", "Bag air filter with aluminium frame, polyester media, 85% efficiency"),
        ("HEPAFILTER", "HEPA Filter", "HEPA air filter with aluminium frame, glass micro-fibre media, 99.9% efficiency"),
        ("SANDTRAP", "Sand Trap Louver", "Aluminium sand trap louver to separate sand particulate and large dust"),
    ]),
]

# (slug, title, blurb, thumbnail, [file, ...])
# One download per certificate: a single file is linked directly, a group is
# zipped to assets/certificates/<slug>.zip by make_zips() below.
CERTS = [
    ("iso", "ISO 9001:2018", "Quality management system certification.",
     "iso.jpg", ["iso.png"]),
    ("atjc", "ATJC — An Teng Testing Certification", "Independent performance and type testing.",
     "atjc-1.jpg", ["atjc-1.pdf", "atjc-2.pdf", "atjc-3.png", "atjc-4.pdf", "atjc-5.pdf"]),
    ("eos", "Egyptian Organization for Standardization", "National product conformity — EOS.",
     "eos-1.jpg", ["eos-1.png", "eos-2.png", "eos-3.png", "eos-4.png", "eos-5.png"]),
    ("mcl", "Measurements &amp; Calibration Labs", "Calibrated instrumentation and test data — MCL.",
     "mcl-1.jpg", ["mcl-1.pdf", "mcl-2.png", "mcl-3.png", "mcl-4.png", "mcl-5.png"]),
    ("nopwasd", "National Organization for Potable Water &amp; Sanitary Drainage", "NOPWASD approval.",
     "nopwasd-1.jpg", ["nopwasd-1.pdf", "nopwasd-2.pdf", "nopwasd-3.pdf", "nopwasd-4.png"]),
    ("udem", "UDEM System &amp; Product Certification", "LVD and EMC product certification.",
     "udem.jpg", ["udem-lvd-emc.pdf"]),
    ("ruck", "Ruck-Germany Certification", "Official distributorship for Egypt.",
     "ruck.jpg", ["ruck.png"]),
    ("giz", "Fit for Partnership with Germany", "GIZ management training programme.",
     "giz.jpg", ["giz.png"]),
    ("trademark", "Trademark Certification", "Registered Univent trademark.",
     "trademark.jpg", ["trademark.png"]),
]

CERT_DIR = "assets/certificates"

DOC_ICON = ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
            '<path d="M12 3v11"/><path d="m8 10.5 4 4 4-4"/><path d="M4 17.5v2a1.5 1.5 0 0 0 1.5 1.5h13a1.5 1.5 0 0 0 1.5-1.5v-2"/></svg>')


def header_markup(page):
    out = ['<header class="site-header" id="header">',
           '  <div class="wrap header-inner">',
           '    <a class="brand" href="index.html" aria-label="Univent home">',
           '      <img src="assets/logo.png" alt="Univent" />',
           '    </a>',
           '',
           '    <nav class="nav" id="nav">']
    for href, label in NAV:
        active = ' class="is-active" aria-current="page"' if href == page else ''
        out.append('      <a href="%s"%s>%s</a>' % (href, active, label))
    out += ['    </nav>',
            '',
            '    <div class="header-actions">',
            '      <a class="btn btn-primary btn-sm" href="contact.html">Request a quote</a>',
            '      <button class="burger" id="burger" aria-label="Menu" aria-expanded="false">',
            '        <span></span><span></span><span></span>',
            '      </button>',
            '    </div>',
            '  </div>',
            '</header>']
    return "\n".join(out)


def footer_markup(page):
    return "\n".join([
        '<footer class="site-footer">',
        '  <div class="wrap footer-inner">',
        '    <div class="footer-brand">',
        '      <a href="index.html"><img src="assets/logo.png" alt="Univent" /></a>',
        '      <p>',
        '        At Univent we are dedicated to placing Egyptian products at the forefront of',
        '        high-quality manufacturing — making "Made in Egypt" a hallmark of excellence,',
        '        recognised and trusted worldwide.',
        '      </p>',
        '    </div>',
        '',
        '    <div class="footer-col">',
        '      <h4>Products</h4>',
        '      <a href="products.html?cat=axial">Axial &amp; duct fans</a>',
        '      <a href="products.html?cat=didw">Centrifugal fans</a>',
        '      <a href="products.html?cat=smoke">Smoke &amp; jet fans</a>',
        '      <a href="products.html?cat=filters">Filters &amp; accessories</a>',
        '    </div>',
        '',
        '    <div class="footer-col">',
        '      <h4>Company</h4>',
        '      <a href="about.html">About Univent</a>',
        '      <a href="about.html#engineering">Engineering</a>',
        '      <a href="about.html#partnership">Ruck partnership</a>',
        '      <a href="projects.html">Projects</a>',
        '      <a href="certificates.html">Certifications</a>',
        '    </div>',
        '',
        '    <div class="footer-col">',
        '      <h4>Contact</h4>',
        '      <a href="tel:+201006063909">0100 606 3909</a>',
        '      <a href="tel:+201090054330">0109 005 4330</a>',
        '      <a href="mailto:ehab@univent.com.eg">ehab@univent.com.eg</a>',
        '      <span>337 El Sudan St, Giza</span>',
        '    </div>',
        '  </div>',
        '',
        '  <div class="wrap footer-bottom">',
        '    <span>© <span id="year">2026</span> Univent. All rights reserved.</span>',
        '    <span>Quality is everything. Quality you can trust.</span>',
        '  </div>',
        '</footer>',
    ])


def products_markup(page):
    out = ['<div class="filter-bar" role="tablist" aria-label="Product categories">',
           '  <button class="filter is-active" data-filter="all" role="tab" aria-selected="true">'
           'All <span class="count">%d</span></button>' % sum(len(c[2]) for c in CATEGORIES)]
    for slug, label, items in CATEGORIES:
        out.append('  <button class="filter" data-filter="%s" role="tab" aria-selected="false">%s '
                   '<span class="count">%d</span></button>' % (slug, label, len(items)))
    out.append('</div>')
    out.append('')
    out.append('<div class="product-grid" id="product-grid">')
    for slug, label, items in CATEGORIES:
        for img, name, desc in items:
            out.append(
                '  <article class="product-card reveal" data-cat="%s">\n'
                '    <div class="pc-img"><img src="assets/products/%s.png" alt="Univent %s" loading="lazy" width="500" height="500" /></div>\n'
                '    <div class="pc-body">\n'
                '      <span class="pc-cat">%s</span>\n'
                '      <h3>%s</h3>\n'
                '      <p>%s</p>\n'
                '    </div>\n'
                '  </article>' % (slug, img, html.escape(name, quote=True), label,
                                  html.escape(name), html.escape(desc)))
    out.append('</div>')
    out.append('<p class="grid-empty" id="grid-empty" hidden>No products in this category.</p>')
    return "\n      ".join(out)


def download_target(slug, files):
    """(href, badge) for a certificate's single download button."""
    if len(files) == 1:
        return "%s/%s" % (CERT_DIR, files[0]), files[0].rsplit(".", 1)[-1].upper()
    return "%s/%s.zip" % (CERT_DIR, slug), "ZIP · %d files" % len(files)


def make_zips():
    """One archive per multi-document certificate. Entry timestamps come from
    the source files, so an unchanged set rebuilds byte-identical."""
    written = 0
    for slug, _, _, _, files in CERTS:
        if len(files) == 1:
            continue
        path = os.path.join(CERT_DIR, slug + ".zip")
        with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
            for f in files:
                src = os.path.join(CERT_DIR, f)
                if not os.path.exists(src):
                    raise SystemExit("missing certificate document: " + src)
                z.write(src, arcname="Univent-%s/%s" % (slug.upper(), f))
        written += 1
    return written


def certs_markup(page):
    out = ['<div class="cert-grid">']
    for slug, title, blurb, thumb, files in CERTS:
        href, badge = download_target(slug, files)
        out.append(
            '  <article class="cert-card reveal">\n'
            '    <a class="cert-thumb" href="%s/%s" target="_blank" rel="noopener">\n'
            '      <img src="%s/thumb/%s" alt="%s" loading="lazy" />\n'
            '      <span class="cert-view">View</span>\n'
            '    </a>\n'
            '    <div class="cert-meta">\n'
            '      <h3>%s</h3>\n'
            '      <p>%s</p>\n'
            '      <a class="cert-download" href="%s" download>%sDownload '
            '<span class="ext">%s</span></a>\n'
            '    </div>\n'
            '  </article>'
            % (CERT_DIR, files[0], CERT_DIR, thumb, re.sub("&amp;", "and", title),
               title, blurb, href, DOC_ICON, badge))
    out.append('</div>')
    return "\n      ".join(out)


# (marker, builder, indent, required-on-every-page)
REGIONS = [
    ("HEADER", header_markup, "", True),
    ("FOOTER", footer_markup, "", True),
    ("PRODUCTS", products_markup, "      ", False),
    ("CERTS", certs_markup, "      ", False),
]


def build(page):
    src = open(page, encoding="utf-8").read()
    filled = []
    for marker, builder, indent, required in REGIONS:
        pat = re.compile(r"(<!-- %s:START -->).*?(<!-- %s:END -->)" % (marker, marker), re.S)
        if not pat.search(src):
            if required:
                raise SystemExit("marker %s not found in %s" % (marker, page))
            continue
        body = builder(page)
        src = pat.sub(lambda m: m.group(1) + "\n" + indent + body + "\n" + indent + m.group(2),
                      src, count=1)
        filled.append(marker)
    open(page, "w", encoding="utf-8").write(src)
    return filled


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    zips = make_zips()
    for page in PAGES:
        print("%-20s %s" % (page, ", ".join(build(page)).lower()))
    print("\nproducts: %d in %d categories"
          % (sum(len(c[2]) for c in CATEGORIES), len(CATEGORIES)))
    print("certificates: %d groups, %d documents, %d archives"
          % (len(CERTS), sum(len(c[4]) for c in CERTS), zips))
