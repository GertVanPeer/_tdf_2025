import json
import os
import re
from datetime import datetime
from playwright.sync_api import sync_playwright
from pathlib import Path

# Output directory
outdir = os.path.join(os.getcwd(), "start_list")
outdir = Path(outdir)
os.makedirs(outdir, exist_ok=True)

# Web scrape function
def scrape_giro_startlist():
    url = "https://www.procyclingstats.com/race.php?id1=giro-d-italia&id2=2025&p=startlist&view=hide_dropouts"

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=150)
        page = browser.new_page()
        print(f"🌍 Visit: {url}")
        page.goto(url, timeout=60000)

        # ✅ Accept coockies
        try:
            page.click("text='Accept All'")
            page.wait_for_timeout(1000)
            print("✅ Cookies accepted.")
        except:
            print("⚠️ Cookie banner not found.")

        # ⏳ Wait for rendering
        page.wait_for_selector("div.ridersCont", timeout=15000)
        
        # 📝 Start scraping
        output = {
            "race": "Giro d'Italia",
            "year": 2025,
            "timestamp": datetime.now().isoformat(),
            "riders": []
        }

        teams = page.locator("div.ridersCont")
        for i in range(teams.count()):
            team = teams.nth(i)
            team_name = team.locator("a.team").inner_text()
            print(f"🏁 Team found: {team_name}")
            riders = team.locator("ul > li")
            print(f"🚴‍♀️Number of riders found: {riders.count()}")

            for j in range(riders.count()):
                rider = riders.nth(j)
                number = rider.locator("span.bib").inner_text()
                name = rider.locator("a").inner_text()
                status = rider.inner_text()
                #status = re.search(r"\((DN[FS]\s*#\d+)\)", status) # regex for default start list? CHECK!
                #status = re.search(r"\(OUT\)", text) # regex for start list & view=hide_dropouts CHECK!
                status = re.search(r"\((DN[FS]\s*#\d+|OUT)\)", status) # regex that can deal with both views
                status = status.group(1) if status else "ACTIVE"

                output["riders"].append({
                    "team": team_name,
                    "number": int(number),
                    "name": name,
                    "status": status
                })

        # 📸 Screenshot
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        page.screenshot(path=outdir/f"start_list_{timestamp}.png", full_page=True)
        print("📸 Screenshot from start list saved.")

        browser.close()

        # 💾 JSON-output
        outfile = os.path.join(outdir, f"startlist_{timestamp}.json")
        with open(outfile, "w") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"✅ File saved: {outfile}")
        print(f"👥 Total number of riders: {len(output['riders'])}")

if __name__ == "__main__":
    scrape_giro_startlist()