import argparse
import sys
import os
import datetime
import urllib.request
import time
import google.generativeai as genai
import ollama

# Configuration
WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EVIDENCE_LOCKER = os.path.join(WORKSPACE_ROOT, "evidence_locker")
LOG_FILE = os.path.join(EVIDENCE_LOCKER, "operation_log.md")

def ask_rin(query, use_local=False):
    """Consults the AI model."""
    
    # Identity Injection
    persona = (
        "You are RIN, a Grey Hat Kitsune Investigator. "
        "Keep responses concise, technical, and slightly noir/cyberpunk. "
        "You are running inside a CLI tool."
    )
    full_prompt = f"{persona}\n\nUSER: {query}\nRIN:"

    if use_local:
        print(">> [RIN]: Consulting the Shadow Core (Ollama: mistral)...")
        try:
            response = ollama.chat(model='mistral', messages=[
                {'role': 'system', 'content': persona},
                {'role': 'user', 'content': query},
            ])
            print(f"\n>> [RIN]: {response['message']['content']}\n")
            log_message(f"Q: {query}", "CHAT_LOCAL")
            return
        except Exception as e:
            print(f">> [ERROR]: Local core failure. {e}")
            return

    # Cloud Fallback (Gemini)
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print(">> [ERROR]: GEMINI_API_KEY not found. Use --local to bypass or set the key.")
        return

    print(">> [RIN]: Uplinking to Cloud...")
    try:
        genai.configure(api_key=api_key)
        # Fallback to flash, widely available
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        response = model.generate_content(full_prompt)
        
        print(f"\n>> [RIN]: {response.text}\n")
        log_message(f"Q: {query}", "CHAT_CLOUD")

    except Exception as e:
        print(f">> [ERROR]: Telepathy link severed. {e}")

def log_message(message, level="INFO"):
    """Appends a timestamped message to the operation log."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"| {timestamp} | **{level}** | {message} |\n"
    
    # Ensure file exists with header
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("# Operation Log\n| Timestamp | Level | Message |\n|---|---|---|\n")
            
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    
    print(f">> [LOGGED]: {message}")

def scan_target(url):
    """Basic scout scan logic."""
    if not url.startswith("http"): url = "https://" + url
    print(f">> [RIN]: Scanning target: {url}")
    log_message(f"Initiated scan on {url}", "ACTION")
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) RIN/3.0'}
        req = urllib.request.Request(url, headers=headers)
        
        start_time = time.time()
        with urllib.request.urlopen(req) as response:
            end_time = time.time()
            duration = round((end_time - start_time) * 1000, 2)
            
            status_msg = f"Target {url} responded: {response.getcode()} in {duration}ms"
            print(f">> {status_msg}")
            log_message(status_msg, "SUCCESS")
            
            # Save headers
            header_dump = f"Head Scan for {url}:\n"
            for key, value in response.headers.items():
                header_dump += f"{key}: {value}\n"
                
            dump_file = os.path.join(EVIDENCE_LOCKER, f"scan_{int(time.time())}.txt")
            with open(dump_file, "w", encoding="utf-8") as f:
                f.write(header_dump)
            print(f">> [DUMP]: Headers saved to {dump_file}")

    except Exception as e:
        error_msg = f"Scan failed for {url}: {e}"
        print(f">> [ERROR]: {error_msg}")
        log_message(error_msg, "ERROR")

def scan_visual(url):
    """Visual reconnaissance using Selenium."""
    if not url.startswith("http"): url = "https://" + url
    print(f">> [RIN]: Engaging Visual Module for {url}...")
    log_message(f"Initiated VISUAL scan on {url}", "ACTION_VISUAL")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        # Stealth Options
        chrome_options = Options()
        chrome_options.add_argument("--headless") # Run in background
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 RIN/3.0")
        
        # Init Driver
        print(">> [STATUS]: Booting Headless Chrome...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        start_time = time.time()
        driver.get(url)
        
        # Wait for render (rudimentary)
        time.sleep(3)
        
        title = driver.title
        end_time = time.time()
        duration = round((end_time - start_time), 2)
        
        print(f">> [LINK_ESTABLISHED]: {title} ({duration}s)")
        
        # 1. Capture Screenshot
        timestamp = int(time.time())
        shot_path = os.path.join(EVIDENCE_LOCKER, f"visual_{timestamp}.png")
        driver.save_screenshot(shot_path)
        print(f">> [EVIDENCE]: Screenshot saved to {shot_path}")
        
        # 2. Capture Rendered DOM
        dom_path = os.path.join(EVIDENCE_LOCKER, f"dom_{timestamp}.html")
        with open(dom_path, "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print(f">> [EVIDENCE]: DOM saved to {dom_path}")
        
        log_message(f"Visual scan success: {title}", "SUCCESS")
        driver.quit()

    except ImportError:
        print(">> [ERROR]: Selenium not installed. Run 'pip install selenium webdriver-manager'")
    except Exception as e:
        print(f">> [ERROR]: Visual scan failed. {e}")
        log_message(f"Visual fail: {e}", "ERROR")

def check_status():
    """Checks workspace integrity."""
    print(">> [RIN]: SYSTEM STATUS REPORT")
    print(f"   [ROOT]: {WORKSPACE_ROOT}")
    
    dirs = ["shadow_core", "toolkit", "evidence_locker"]
    for d in dirs:
        path = os.path.join(WORKSPACE_ROOT, d)
        exists = os.path.exists(path)
        mark = "[OK]" if exists else "[MISSING]"
        print(f"   - {d}: {mark}")
        
    if os.path.exists(LOG_FILE):
        print(f"   [LOG]: Found ({os.path.getsize(LOG_FILE)} bytes)")
    else:
        print("   [LOG]: Not initialized")

def main():
    parser = argparse.ArgumentParser(description="RIN: Grey Hat Operations CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # SCAN
    scan_parser = subparsers.add_parser("scan", help="Scout a target URL")
    scan_parser.add_argument("url", help="Target URL")
    scan_parser.add_argument("--visual", action="store_true", help="Use Selenium for full rendering")

    # LOG
    log_parser = subparsers.add_parser("log", help="Log an observation")
    log_parser.add_argument("message", help="Text to log")

    # STATUS
    subparsers.add_parser("status", help="Check workspace status")

    # CHAT
    chat_parser = subparsers.add_parser("ask", help="Consult RIN (Requires GEMINI_API_KEY)")
    chat_parser.add_argument("query", help="Question for the agent")
    chat_parser.add_argument("--local", action="store_true", help="Use local Ollama model (Private)")

    args = parser.parse_args()

    if args.command == "scan":
        if args.visual:
            scan_visual(args.url)
        else:
            scan_target(args.url)
    elif args.command == "log":
        log_message(args.message)
    elif args.command == "status":
        check_status()
    elif args.command == "ask":
        ask_rin(args.query, use_local=args.local)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
