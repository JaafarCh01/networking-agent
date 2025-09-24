import os
import pandas as pd
import requests
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

load_dotenv()

# --- Environment Variables ---
APOLLO_API_KEY = os.getenv("APOLLO_API_KEY")
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")

def load_leads_from_csv(file_path):
    """Loads leads from a CSV file."""
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame()

def scrape_linkedin_search_results(playwright, search_url):
    """Scrapes LinkedIn search results for public profiles using Playwright."""
    print(f"Scraping LinkedIn search results from: {search_url}")
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    try:
        page.goto("https://www.linkedin.com/login")
        page.fill('input[name="session_key"]', LINKEDIN_EMAIL)
        page.fill('input[name="session_password"]', LINKEDIN_PASSWORD)
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')

        page.goto(search_url)
        page.wait_for_load_state('domcontentloaded')

        profiles = page.query_selector_all('li.reusable-search__result-container')
        leads = []
        for profile in profiles[:10]:
            try:
                name_element = profile.query_selector('span[aria-hidden="true"]')
                headline_element = profile.query_selector('div.entity-result__primary-subtitle')
                url_element = profile.query_selector('a.app-aware-link')

                if name_element and headline_element and url_element:
                    leads.append({
                        'full_name': name_element.inner_text(),
                        'headline': headline_element.inner_text(),
                        'profile_url': "https://www.linkedin.com" + url_element.get_attribute('href'),
                        'company': '', 
                        'school': '',
                    })
            except Exception as e:
                print(f"Could not parse a profile: {e}")
        return pd.DataFrame(leads)

    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return pd.DataFrame()
    finally:
        browser.close()

def enrich_with_apollo(df):
    """Enriches lead data with email addresses from Apollo.io."""
    print("Enriching leads with Apollo.io...")
    if not APOLLO_API_KEY:
        print("Warning: APOLLO_API_KEY not found. Skipping enrichment.")
        return df

    for index, row in df.iterrows():
        if pd.isna(row.get('email')) or row.get('email') == '':
            try:
                url = "https://api.apollo.io/v1/people/search"
                headers = {"Cache-Control": "no-cache"}
                params = {
                    "api_key": APOLLO_API_KEY,
                    "q_keywords": row['full_name'],
                    "organization_name": row.get('company', ''),
                    "page": 1
                }
                r = requests.get(url, headers=headers, params=params).json()
                person = r.get("people", [{}])[0]
                email = person.get("email")
                if email:
                    df.at[index, 'email'] = email
                    print(f"Found email for {row['full_name']}: {email}")
            except Exception as e:
                print(f"Could not enrich {row['full_name']}: {e}")
    return df

def deduplicate_leads(df):
    """De-duplicates leads based on profile_url."""
    return df.drop_duplicates(subset=['profile_url'], keep='first')

if __name__ == "__main__":
    leads_df = load_leads_from_csv('leads.csv')

    search_url = "https://www.linkedin.com/search/results/people/?keywords=Google&schoolFilter=['1014']"
    with sync_playwright() as p:
        scraped_leads = scrape_linkedin_search_results(p, search_url)
    
    all_leads = pd.concat([leads_df, scraped_leads], ignore_index=True)

    unique_leads = deduplicate_leads(all_leads)

    enriched_leads = enrich_with_apollo(unique_leads)

    enriched_leads.to_csv("leads_processed.csv", index=False)
    print("Lead generation process complete. Output saved to leads_processed.csv")