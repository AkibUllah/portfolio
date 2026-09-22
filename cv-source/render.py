import sys, subprocess, pathlib
from playwright.sync_api import sync_playwright

here = pathlib.Path(__file__).parent
html = here / "cv.html"
out = here / "Akib_Jafor_CV.pdf"

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(html.as_uri())
    page.wait_for_load_state("networkidle")
    page.evaluate("document.fonts.ready")
    page.wait_for_timeout(800)
    # report overflow: any .page whose content is taller than the page box
    overflow = page.evaluate("""() => [...document.querySelectorAll('.page')].map((pg,i)=>{
        const main = pg.querySelector('.main'); const side = pg.querySelector('.side');
        return {page:i+1, mainScroll: main.scrollHeight, mainBox: main.clientHeight,
                sideScroll: side.scrollHeight, sideBox: side.clientHeight};
    })""")
    for o in overflow:
        flag = "OVERFLOW" if (o["mainScroll"] > o["mainBox"] + 1 or o["sideScroll"] > o["sideBox"] + 1) else "ok"
        print(f"page {o['page']}: main {o['mainScroll']}/{o['mainBox']}  side {o['sideScroll']}/{o['sideBox']}  -> {flag}")
    page.pdf(path=str(out), format="A4", print_background=True, prefer_css_page_size=True,
             margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
    browser.close()

subprocess.run(["pdfinfo", str(out)], check=False)
subprocess.run(["pdftoppm", "-png", "-r", "110", str(out), str(here / "preview")], check=True)
print("rendered:", out)
