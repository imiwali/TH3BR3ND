import os
import sys
import time
import random
import string
import json
import requests
import threading
import socket
import re
from functools import wraps
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Global variables
stop_event = threading.Event()
active_task = None
TASK_FILE = 'waleed_tasks.json'
TOKEN_STATUS_FILE = 'token_status.json'
offline_mode = False

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Accept': '/',
    'Accept-Language': 'en-US,en;q=0.9',
}

def is_connected():
    """Check if there's an active internet connection"""
    try:
        # Connect to a reliable host with a short timeout
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        pass
    return False

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def print_boxed_text(text, border_char="═", padding=1, color_code="\033[1;36m"):
    """Print text in a stylish box"""
    lines = text.split('\n')
    max_len = max(len(line) for line in lines)
    width = max_len + padding * 2
    
    top_border = color_code + "╔" + border_char * (width + 2) + "╗" + "\033[0m"
    bottom_border = color_code + "╚" + border_char * (width + 2) + "╝" + "\033[0m"
    
    print(top_border)
    for line in lines:
        padded_line = line.center(max_len)
        print(color_code + "║ " + "\033[0m" + padded_line + color_code + " ║" + "\033[0m")
    print(bottom_border)

def display_banner():
    banner = r"""
    ██╗    ██╗ █████╗ ██╗     ███████╗███████╗██████╗ 
    ██║    ██║██╔══██╗██║     ██╔════╝██╔════╝██╔══██╗
    ██║ █╗ ██║███████║██║     █████╗  █████╗  ██║  ██║
    ██║███╗██║██╔══██║██║     ██╔══╝  ██╔══╝  ██║  ██║
    ╚███╔███╔╝██║  ██║███████╗███████╗███████╗██████╔╝
     ╚══╝╚══╝ ╚═╝  ╚═╝╚══════╝╚══════╝╚══════╝╚═════╝ 
                                                       
    POWER FULL DEVELOPING BY WALEED OFFLINE TOOL 😘
    """
    print_boxed_text(banner, "═", 1, "\033[1;36m")
    print("")

def print_menu_option(num, text, color="\033[1;36m"):
    """Print a menu option with stylish formatting"""
    print(f"{color}║ {num}. {text}\033[0m")

def print_section_header(text, color="\033[1;36m"):
    """Print a section header with stylish formatting"""
    width = len(text) + 4
    print(f"{color}╔{'═' * width}╗\033[0m")
    print(f"{color}║  {text}  ║\033[0m")
    print(f"{color}╚{'═' * width}╝\033[0m")
def main_menu():
    while True:
        clear_screen()
        display_banner()
        
        # Display WhatsApp contact information
        whatsapp_info = "WhatsApp Support: +923150596250"
        print(f"\033[1;32m╔{'═' * (len(whatsapp_info) + 4)}╗\033[0m")
        print(f"\033[1;32m║  {whatsapp_info}  ║\033[0m")
        print(f"\033[1;32m╚{'═' * (len(whatsapp_info) + 4)}╝\033[0m")
        print("")
        
        # Display connection status
        connection_status = "\033[1;32mONLINE\033[0m" if is_connected() else "\033[1;33mOFFLINE\033[0m"
        print(f"\033[1;36m╔{'═' * 40}╗\033[0m")
        print(f"\033[1;36m║ Connection Status: {connection_status.ljust(18)} ║\033[0m")
        print(f"\033[1;36m╚{'═' * 40}╝\033[0m")
        
        print_section_header("MAIN MENU")
        print_menu_option("1", "Start New Task")
        print_menu_option("2", "View Saved Tasks")
        print_menu_option("3", "Delete Tasks")
        print_menu_option("4", "Check Tokens")
        print_menu_option("5", "View Token Status")
        print_menu_option("6", "Extract Page Tokens")
        print_menu_option("7", "Contact Support", "\033[1;32m")  # New option
        print_menu_option("8", "Exit", "\033[1;31m")
        print(f"\033[1;36m╔{'═' * 40}╗\033[0m")
        print(f"\033[1;36m║\033[0m", end="")
        
        choice = input("\033[1;36m Select an option: \033[0m").strip()
        print(f"\033[1;36m╚{'═' * 40}╝\033[0m")
        
        if choice == "1":
            start_new_task()
        elif choice == "2":
            view_tasks()
        elif choice == "3":
            delete_tasks()
        elif choice == "4":
            check_tokens_menu()
        elif choice == "5":
            view_token_status()
        elif choice == "6":
            extract_page_tokens_menu()
        elif choice == "7":  # New option for contact
            clear_screen()
            print_section_header("CONTACT SUPPORT")
            print("")
            print_boxed_text("For any issues or support, contact us on WhatsApp:\n+923150596250\n\nWe're available 24/7 to assist you!", "═", 1, "\033[1;32m")
            print("")
            input("\033[1;36m║ Press Enter to return to main menu...\033[0m")
        elif choice == "8":
            print_status("Goodbye!", "success")
            break
        else:
            print_status("Invalid option", "error")
        
        input("\n\033[1;36m║ Press Enter to continue...\033[0m")
        
def print_centered_text(text, color="\033[1;36m"):
    """Print centered text with color"""
    width = 80
    padding = (width - len(text)) // 2
    print(f"{color}{' ' * padding}{text}{' ' * padding}\033[0m")

def print_status(message, status_type="info"):
    """Print status messages with colored formatting"""
    if status_type == "success":
        print(f"\033[1;32m[✓] {message}\033[0m")
    elif status_type == "error":
        print(f"\033[1;31m[✗] {message}\033[0m")
    elif status_type == "warning":
        print(f"\033[1;33m[!] {message}\033[0m")
    elif status_type == "info":
        print(f"\033[1;34m[ℹ] {message}\033[0m")
    else:
        print(f"[ ] {message}")

def extract_page_tokens(user_token):
    """Extract page tokens from a user token"""
    try:
        # Get user's pages
        pages_res = requests.get(
            f'https://graph.facebook.com/me/accounts?access_token={user_token}&limit=100',
            headers=headers,
            timeout=10
        )
        
        if pages_res.status_code == 200:
            pages_data = pages_res.json()
            page_tokens = []
            
            if 'data' in pages_data:
                for page in pages_data['data']:
                    page_info = {
                        'name': page.get('name', 'Unknown Page'),
                        'id': page.get('id', 'Unknown'),
                        'token': page.get('access_token', '')
                    }
                    page_tokens.append(page_info)
                
                return page_tokens
            else:
                return []
        else:
            print_status(f"Error fetching pages: HTTP {pages_res.status_code}", "error")
            return []
            
    except Exception as e:
        print_status(f"Error extracting page tokens: {str(e)}", "error")
        return []

def extract_page_tokens_menu():
    """Menu option to extract page tokens"""
    print_section_header("EXTRACT PAGE TOKENS")
    
    user_token = input("\033[1;36m║ Enter your Facebook user token: \033[0m").strip()
    if not user_token:
        print_status("No token provided", "error")
        return
    
    print_status("Extracting page tokens, please wait...", "info")
    
    page_tokens = extract_page_tokens(user_token)
    
    if not page_tokens:
        print_status("No page tokens found or error occurred", "error")
        return
    
    print_section_header("EXTRACTED PAGE TOKENS")
    
    # Save tokens to file
    timestamp = int(time.time())
    filename = f"page_tokens_{timestamp}.txt"
    
    with open(filename, 'w') as f:
        for page in page_tokens:
            token_line = f"{page['token']} | {page['name']} | {page['id']}\n"
            f.write(token_line)
    
    # Display results
    for i, page in enumerate(page_tokens, 1):
        print(f"\033[1;36m╔{'═' * 78}╗\033[0m")
        print(f"\033[1;36m║ Page {i}: {page['name'][:70].ljust(70)} ║\033[0m")
        print(f"\033[1;36m║ ID: {page['id'].ljust(72)} ║\033[0m")
        print(f"\033[1;36m║ Token: {page['token'][:70].ljust(70)} ║\033[0m")
        print(f"\033[1;36m╚{'═' * 78}╝\033[0m")
        print("")
    
    print_status(f"Saved {len(page_tokens)} page tokens to {filename}", "success")

def check_token_status(token):
    """Check if a token is valid and get user info"""
    try:
        # Check basic token validity
        profile_res = requests.get(
            f'https://graph.facebook.com/me?access_token={token}&fields=name,id',
            headers=headers,
            timeout=10
        )
        
        if profile_res.status_code == 200:
            profile_data = profile_res.json()
            name = profile_data.get('name', 'Unknown')
            user_id = profile_data.get('id', 'Unknown')
            
            # Check if token can send messages
            permissions_res = requests.get(
                f'https://graph.facebook.com/me/permissions?access_token={token}',
                headers=headers,
                timeout=10
            )
            
            can_message = False
            if permissions_res.status_code == 200:
                permissions_data = permissions_res.json()
                if 'data' in permissions_data:
                    for perm in permissions_data['data']:
                        if perm.get('permission') == 'pages_messaging' and perm.get('status') == 'granted':
                            can_message = True
                            break
            
            return {
                'status': 'VALID',
                'name': name,
                'id': user_id,
                'can_message': can_message,
                'last_checked': time.time()
            }
        else:
            return {
                'status': 'INVALID',
                'error': f"HTTP {profile_res.status_code}",
                'last_checked': time.time()
            }
            
    except Exception as e:
        return {
            'status': 'ERROR',
            'error': str(e),
            'last_checked': time.time()
        }

def check_tokens(tokens):
    """Check multiple tokens concurrently"""
    results = {}
    
    print_status("Checking tokens, please wait...", "info")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_token = {executor.submit(check_token_status, token): token for token in tokens}
        
        for future in as_completed(future_to_token):
            token = future_to_token[future]
            try:
                results[token] = future.result()
            except Exception as e:
                results[token] = {
                    'status': 'ERROR',
                    'error': str(e),
                    'last_checked': time.time()
                }
    
    return results

def save_token_status(token_status):
    """Save token status to file"""
    with open(TOKEN_STATUS_FILE, 'w') as f:
        json.dump(token_status, f, indent=2)

def load_token_status():
    """Load token status from file"""
    if not os.path.exists(TOKEN_STATUS_FILE):
        return {}
    
    with open(TOKEN_STATUS_FILE, 'r') as f:
        return json.load(f)

def monitor_tokens(tokens, check_interval=300):
    """Monitor token status in the background"""
    global stop_event
    
    while not stop_event.is_set():
        if is_connected():
            print_status("Checking token status...", "info")
            token_status = check_tokens(tokens)
            save_token_status(token_status)
            
            # Count working tokens
            working_tokens = [token for token, status in token_status.items() 
                             if status.get('status') == 'VALID' and status.get('can_message')]
            
            print_status(f"{len(working_tokens)}/{len(tokens)} tokens are working", 
                        "success" if len(working_tokens) > 0 else "warning")
        
        # Wait for next check
        for _ in range(check_interval):
            if stop_event.is_set():
                break
            time.sleep(1)

def fetch_profile_name(token):
    global offline_mode
    if offline_mode:
        return "OFFLINE MODE"
    
    # Check if we have cached token status
    token_status = load_token_status()
    if token in token_status and token_status[token].get('status') == 'VALID':
        return token_status[token].get('name', 'Unknown')
    
    try:
        res = requests.get(
            f'https://graph.facebook.com/me?access_token={token}',
            timeout=8
        )
        return res.json().get('name', 'Unknown')
    except Exception:
        return 'Unknown'

def send_messages_offline(tokens, thread_id, hater_name, delay, messages, task_id):
    """Send messages with offline capability"""
    global stop_event, offline_mode
    tok_i, msg_i = 0, 0
    total_tok, total_msg = len(tokens), len(messages)
    
    # Load token status to prioritize working tokens
    token_status = load_token_status()
    working_tokens = [token for token in tokens 
                     if token in token_status 
                     and token_status[token].get('status') == 'VALID'
                     and token_status[token].get('can_message')]
    
    if working_tokens:
        tokens = working_tokens
        total_tok = len(tokens)
        print_status(f"Using {len(working_tokens)} working tokens", "success")
    
    print_section_header("STARTING MESSAGE SENDING")
    print_status(f"Using {len(tokens)} tokens and {len(messages)} messages", "info")
    print_status(f"Delay between messages: {delay} seconds", "info")
    print_status("Press Ctrl+C to stop", "warning")
    print("")
    
    # Start token monitoring in background
    monitor_thread = threading.Thread(
        target=monitor_tokens,
        args=(tokens,),
        daemon=True
    )
    monitor_thread.start()
    
    # Check initial connection
    if not is_connected():
        offline_mode = True
        print_status("No internet connection detected. Starting in OFFLINE MODE", "warning")
        print_status("Messages will be queued and sent when connection is restored", "warning")
        print("")
    
    # Queue for offline messages
    message_queue = []
    
    try:
        while not stop_event.is_set():
            # Check connection status
            current_connection = is_connected()
            if offline_mode and current_connection:
                print_status("Internet connection restored. Exiting OFFLINE MODE", "success")
                offline_mode = False
            elif not offline_mode and not current_connection:
                print_status("Internet connection lost. Entering OFFLINE MODE", "warning")
                offline_mode = True
            
            tk = tokens[tok_i]
            msg = messages[msg_i]
            full_msg = f"{hater_name} {msg}"
            
            if offline_mode:
                # Queue the message for later sending
                message_queue.append({
                    'token': tk,
                    'message': full_msg,
                    'timestamp': time.time()
                })
                print(f"\033[1;33m[⏳ QUEUED]\033[0m {full_msg[:40]}... via TOKEN-{tok_i+1} (Offline)")
            else:
                # Try to send the message
                try:
                    # Updated Facebook API endpoint
                    response = requests.post(
                        f'https://graph.facebook.com/v19.0/t_{thread_id}/messages',
                        data={'access_token': tk, 'message': full_msg},
                        headers=headers,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        # Display success message with stylish title
                        print(f"\033[1;32m╔{'═' * 80}╗\033[0m")
                        print(f"\033[1;32m║ ✓ MESSAGE SENT SUCCESSFULLY! - POWERED BY WALEED LEGEND KA ║\033[0m")
                        print(f"\033[1;32m║ Message: {full_msg[:60].ljust(60)} ║\033[0m")
                        print(f"\033[1;32m║ Token: TOKEN-{str(tok_i+1).ljust(67)} ║\033[0m")
                        print(f"\033[1;32m╚{'═' * 80}╝\033[0m")
                    else:
                        error_msg = f"HTTP Error {response.status_code}"
                        try:
                            error_data = response.json()
                            if 'error' in error_data and 'message' in error_data['error']:
                                error_msg = error_data['error']['message']
                        except:
                            pass
                        
                        print(f"\033[1;31m[✗ ERROR {response.status_code}]\033[0m {error_msg}")
                        # Add to queue if there's an error
                        message_queue.append({
                            'token': tk,
                            'message': full_msg,
                            'timestamp': time.time()
                        })
                        
                except Exception as e:
                    print(f"\033[1;31m[✗ ERROR]\033[0m {str(e)}")
                    offline_mode = True
                    message_queue.append({
                        'token': tk,
                        'message': full_msg,
                        'timestamp': time.time()
                    })
            
            # Process message queue if we have connection
            if not offline_mode and message_queue:
                print_status(f"Processing {len(message_queue)} queued messages", "info")
                successful_sends = []
                
                for i, queued_msg in enumerate(message_queue):
                    try:
                        response = requests.post(
                            f'https://graph.facebook.com/v19.0/t_{thread_id}/messages',
                            data={'access_token': queued_msg['token'], 'message': queued_msg['message']},
                            headers=headers,
                            timeout=15
                        )
                        
                        if response.status_code == 200:
                            print(f"\033[1;32m╔{'═' * 80}╗\033[0m")
                            print(f"\033[1;32m║ ✓ QUEUED MESSAGE SENT! - POWERED BY WALEED LEGEND KA ║\033[0m")
                            print(f"\033[1;32m║ Message: {queued_msg['message'][:60].ljust(60)} ║\033[0m")
                            print(f"\033[1;32m╚{'═' * 80}╝\033[0m")
                            successful_sends.append(i)
                        else:
                            print(f"\033[1;31m[✗ ERROR {response.status_code}]\033[0m Failed to send queued message")
                            
                    except Exception as e:
                        print(f"\033[1;31m[✗ ERROR]\033[0m {e}")
                        # Keep in queue if failed
                
                # Remove successfully sent messages from queue
                message_queue = [msg for i, msg in enumerate(message_queue) if i not in successful_sends]
                
                if message_queue:
                    print_status(f"{len(message_queue)} messages remain in queue", "warning")
                else:
                    print_status("All queued messages sent successfully", "success")
            
            tok_i = (tok_i + 1) % total_tok
            msg_i = (msg_i + 1) % total_msg
            time.sleep(delay)
            
    except KeyboardInterrupt:
        print("\n[!] Stopping message sending...")
        if message_queue:
            print_status(f"{len(message_queue)} messages remain in queue", "warning")
        stop_event.set()

def check_tokens_menu():
    """Menu option to check tokens"""
    print_section_header("CHECK TOKENS")
    
    print_centered_text("SELECT TOKEN OPTION", "\033[1;36m")
    print("")
    print_menu_option("1", "Single Token")
    print_menu_option("2", "Multiple Tokens from File")
    print("")
    
    token_option = input("\033[1;36m║ Select option (1 or 2): \033[0m").strip()
    
    tokens = []
    if token_option == "1":
        token = input("\033[1;36m║ Enter Facebook token: \033[0m").strip()
        if token:
            tokens = [token]
    elif token_option == "2":
        token_file = input("\033[1;36m║ Enter path to tokens file: \033[0m").strip()
        try:
            with open(token_file, 'r') as f:
                tokens = [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            print_status(f"Error reading tokens file: {e}", "error")
            return
    else:
        print_status("Invalid option", "error")
        return
    
    if not tokens:
        print_status("No tokens provided", "error")
        return
    
    # Check tokens
    token_status = check_tokens(tokens)
    save_token_status(token_status)
    
    # Display results
    print_section_header("TOKEN CHECK RESULTS")
    
    valid_count = 0
    can_message_count = 0
    
    for token, status in token_status.items():
        status_color = "\033[1;32m" if status.get('status') == 'VALID' else "\033[1;31m"
        status_text = status.get('status', 'UNKNOWN')
        
        print(f"\033[1;36m╔{'═' * 78}╗\033[0m")
        print(f"\033[1;36m║ Token: {token[:60].ljust(60)} ║\033[0m")
        print(f"\033[1;36m║ Status: {status_color}{status_text.ljust(68)}\033[1;36m ║\033[0m")
        
        if status.get('status') == 'VALID':
            valid_count += 1
            print(f"\033[1;36m║ Name: {status.get('name', 'Unknown').ljust(66)} ║\033[0m")
            print(f"\033[1;36m║ ID: {status.get('id', 'Unknown').ljust(68)} ║\033[0m")
            
            can_message = status.get('can_message', False)
            message_status = "CAN SEND MESSAGES" if can_message else "CANNOT SEND MESSAGES"
            message_color = "\033[1;32m" if can_message else "\033[1;31m"
            
            if can_message:
                can_message_count += 1
                
            print(f"\033[1;36m║ Message: {message_color}{message_status.ljust(58)}\033[1;36m ║\033[0m")
        else:
            print(f"\033[1;36m║ Error: {str(status.get('error', 'Unknown')).ljust(65)} ║\033[0m")
        
        print(f"\033[1;36m╚{'═' * 78}╝\033[0m")
        print("")
    
    print_status(f"Summary: {valid_count}/{len(tokens)} valid tokens, {can_message_count}/{valid_count} can send messages", 
                "success" if can_message_count > 0 else "warning")

def view_token_status():
    """View saved token status"""
    token_status = load_token_status()
    
    if not token_status:
        print_status("No token status data found", "warning")
        return
    
    print_section_header("SAVED TOKEN STATUS")
    
    valid_count = 0
    can_message_count = 0
    
    for token, status in token_status.items():
        status_color = "\033[1;32m" if status.get('status') == 'VALID' else "\033[1;31m"
        status_text = status.get('status', 'UNKNOWN')
        
        # Check how long ago the token was checked
        last_checked = status.get('last_checked', 0)
        time_diff = time.time() - last_checked
        time_str = f"{int(time_diff // 3600)}h {int((time_diff % 3600) // 60)}m ago"
        
        print(f"\033[1;36m╔{'═' * 78}╗\033[0m")
        print(f"\033[1;36m║ Token: {token[:60].ljust(60)} ║\033[0m")
        print(f"\033[1;36m║ Status: {status_color}{status_text.ljust(68)}\033[1;36m ║\033[0m")
        print(f"\033[1;36m║ Last Checked: {time_str.ljust(62)} ║\033[0m")
        
        if status.get('status') == 'VALID':
            valid_count += 1
            print(f"\033[1;36m║ Name: {status.get('name', 'Unknown').ljust(66)} ║\033[0m")
            
            can_message = status.get('can_message', False)
            message_status = "CAN SEND MESSAGES" if can_message else "CANNOT SEND MESSAGES"
            message_color = "\033[1;32m" if can_message else "\033[1;31m"
            
            if can_message:
                can_message_count += 1
                
            print(f"\033[1;36m║ Message: {message_color}{message_status.ljust(58)}\033[1;36m ║\033[0m")
        else:
            print(f"\033[1;36m║ Error: {str(status.get('error', 'Unknown')).ljust(65)} ║\033[0m")
        
        print(f"\033[1;36m╚{'═' * 78}╝\033[0m")
        print("")
    
    print_status(f"Summary: {valid_count}/{len(token_status)} valid tokens, {can_message_count}/{valid_count} can send messages", 
                "success" if can_message_count > 0 else "warning")

def save_task(task_id, task_info):
    tasks = {}
    if os.path.exists(TASK_FILE):
        with open(TASK_FILE, 'r') as f:
            tasks = json.load(f)
    
    tasks[task_id] = task_info
    with open(TASK_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def load_tasks():
    if not os.path.exists(TASK_FILE):
        return {}
    
    with open(TASK_FILE, 'r') as f:
        return json.load(f)

def delete_task(task_id):
    tasks = load_tasks()
    if task_id in tasks:
        del tasks[task_id]
        with open(TASK_FILE, 'w') as f:
            json.dump(tasks, f, indent=2)
        return True
    return False

def start_new_task():
    global stop_event, active_task
    
    print_section_header("STARTING NEW TASK")
    
    # Token option
    print_centered_text("SELECT TOKEN OPTION", "\033[1;36m")
    print("")
    print_menu_option("1", "Single Token")
    print_menu_option("2", "Multiple Tokens from File")
    print("")
    
    token_option = input("\033[1;36m║ Select option (1 or 2): \033[0m").strip()
    
    tokens = []
    if token_option == "1":
        token = input("\033[1;36m║ Enter Facebook token: \033[0m").strip()
        if token:
            tokens = [token]
    elif token_option == "2":
        token_file = input("\033[1;36m║ Enter path to tokens file: \033[0m").strip()
        try:
            with open(token_file, 'r') as f:
                tokens = [line.strip() for line in f.readlines() if line.strip()]
        except Exception as e:
            print_status(f"Error reading tokens file: {e}", "error")
            return
    else:
        print_status("Invalid option", "error")
        return
    
    if not tokens:
        print_status("No tokens provided", "error")
        return
    
    # Check tokens before starting if online
    if is_connected():
        print_status("Checking token status before starting...", "info")
        token_status = check_tokens(tokens)
        save_token_status(token_status)
        
        working_tokens = [token for token in tokens 
                         if token in token_status 
                         and token_status[token].get('status') == 'VALID'
                         and token_status[token].get('can_message')]
        
        if working_tokens:
            print_status(f"{len(working_tokens)}/{len(tokens)} tokens are working", "success")
        else:
            print_status("No working tokens found! Continue anyway? (y/n)", "warning")
            choice = input().strip().lower()
            if choice != 'y':
                return
    
    # Thread ID
    thread_id = input("\033[1;36m║ Enter Thread ID: \033[0m").strip()
    if not thread_id:
        print_status("Thread ID is required", "error")
        return
    
    # Hater name
    hater_name = input("\033[1;36m║ Enter Hater Name: \033[0m").strip()
    if not hater_name:
        print_status("Hater name is required", "error")
        return
    
    # Delay
    try:
        delay = int(input("\033[1;36m║ Enter delay between messages (seconds): \033[0m").strip() or "1")
    except ValueError:
        print_status("Invalid delay, using 1 second", "warning")
        delay = 1
    
    # Messages file
    msg_file = input("\033[1;36m║ Enter path to messages file: \033[0m").strip()
    try:
        with open(msg_file, 'r', encoding='utf-8', errors='ignore') as f:
            messages = [line.strip() for line in f.readlines() if line.strip()]
    except Exception as e:
        print_status(f"Error reading messages file: {e}", "error")
        return
    
    if not messages:
        print_status("No messages found in file", "error")
        return
    
    # Generate task ID
    task_id = 'waleed_' + ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    
    # Start the sending thread
    stop_event = threading.Event()
    thread = threading.Thread(
        target=send_messages_offline,
        args=(tokens, thread_id, hater_name, delay, messages, task_id),
        daemon=True
    )
    
    # Save task info
    task_info = {
        'name': hater_name,
        'token': tokens[0],
        'tokens_all': tokens,
        'fb_name': fetch_profile_name(tokens[0]),
        'thread_id': thread_id,
        'msg_file': msg_file,
        'msgs': messages,
        'delay': delay,
        'msg_count': len(messages),
        'status': 'ACTIVE',
        'start_time': time.time()
    }
    
    save_task(task_id, task_info)
    active_task = task_id
    
    print_section_header("TASK STARTED SUCCESSFULLY")
    print_status(f"Task ID: {task_id}", "info")
    print_status(f"Using {len(tokens)} tokens", "info")
    print_status(f"{len(messages)} messages loaded", "info")
    print_status(f"Delay: {delay} seconds", "info")
    print_status("OFFLINE MODE ENABLED - Will continue working without internet", "success")
    print_status("TOKEN MONITORING ENABLED - Tokens will be checked periodically", "success")
    print_status("Press Ctrl+C to stop the task", "warning")
    print("")
    
    thread.start()
    
    try:
        while thread.is_alive():
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Stopping task...")
        stop_event.set()
        thread.join()
        
        # Update task status
        tasks = load_tasks()
        if task_id in tasks:
            tasks[task_id]['status'] = 'STOPPED'
            with open(TASK_FILE, 'w') as f:
                json.dump(tasks, f, indent=2)
        
        print_status("Task stopped", "info")

def view_tasks():
    tasks = load_tasks()
    if not tasks:
        print_status("No tasks found", "warning")
        return
    
    print_section_header("SAVED TASKS")
    
    for task_id, task_info in tasks.items():
        status = task_info.get('status', 'UNKNOWN')
        status_color = "\033[1;32m" if status == 'ACTIVE' else "\033[1;31m" if status == 'STOPPED' else "\033[1;33m"
        
        print(f"\033[1;36m╔{'═' * 78}╗\033[0m")
        print(f"\033[1;36m║ Task ID: {task_id.ljust(66)} ║\033[0m")
        print(f"\033[1;36m║ Status: {status_color}{status.ljust(68)}\033[1;36m ║\033[0m")
        print(f"\033[1;36m║ Thread ID: {str(task_info.get('thread_id', 'N/A')).ljust(65)} ║\033[0m")
        print(f"\033[1;36m║ Hater Name: {str(task_info.get('name', 'N/A')).ljust(64)} ║\033[0m")
        print(f"\033[1;36m║ Tokens: {str(len(task_info.get('tokens_all', []))).ljust(68)} ║\033[0m")
        print(f"\033[1;36m║ Messages: {str(task_info.get('msg_count', 'N/A')).ljust(66)} ║\033[0m")
        print(f"\033[1;36m║ Delay: {str(task_info.get('delay', 'N/A')).ljust(70)} ║\033[0m")
        print(f"\033[1;36m║ FB Profile: {str(task_info.get('fb_name', 'Unknown')).ljust(64)} ║\033[0m")
        print(f"\033[1;36m╚{'═' * 78}╝\033[0m")
        print("")

def delete_tasks():
    tasks = load_tasks()
    if not tasks:
        print_status("No tasks found", "warning")
        return
    
    print_section_header("DELETE TASKS")
    
    for i, task_id in enumerate(tasks.keys(), 1):
        print(f"\033[1;36m║ {i}. {task_id}\033[0m")
    
    try:
        choice = int(input("\n\033[1;36m║ Select task to delete (0 to cancel): \033[0m"))
        if choice == 0:
            return
        
        task_ids = list(tasks.keys())
        if 1 <= choice <= len(task_ids):
            task_id = task_ids[choice-1]
            if delete_task(task_id):
                print_status(f"Task {task_id} deleted successfully", "success")
            else:
                print_status("Failed to delete task", "error")
        else:
            print_status("Invalid selection", "error")
    except ValueError:
        print_status("Invalid input", "error")

def main_menu():
    while True:
        clear_screen()
        display_banner()
        
        # Display connection status
        connection_status = "\033[1;32mONLINE\033[0m" if is_connected() else "\033[1;33mOFFLINE\033[0m"
        print(f"\033[1;36m╔{'═' * 40}╗\033[0m")
        print(f"\033[1;36m║ Connection Status: {connection_status.ljust(18)} ║\033[0m")
        print(f"\033[1;36m╚{'═' * 40}╝\033[0m")
        
        print_section_header("MAIN MENU")
        print_menu_option("1", "Start New Task")
        print_menu_option("2", "View Saved Tasks")
        print_menu_option("3", "Delete Tasks")
        print_menu_option("4", "Check Tokens")
        print_menu_option("5", "View Token Status")
        print_menu_option("6", "Extract Page Tokens")
        print_menu_option("7", "Exit", "\033[1;31m")
        print(f"\033[1;36m╔{'═' * 40}╗\033[0m")
        print(f"\033[1;36m║\033[0m", end="")
        
        choice = input("\033[1;36m Select an option: \033[0m").strip()
        print(f"\033[1;36m╚{'═' * 40}╝\033[0m")
        
        if choice == "1":
            start_new_task()
        elif choice == "2":
            view_tasks()
        elif choice == "3":
            delete_tasks()
        elif choice == "4":
            check_tokens_menu()
        elif choice == "5":
            view_token_status()
        elif choice == "6":
            extract_page_tokens_menu()
        elif choice == "7":
            print_status("Goodbye!", "success")
            break
        else:
            print_status("Invalid option", "error")
        
        input("\n\033[1;36m║ Press Enter to continue...\033[0m")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\033[1;33m[!] Interrupted by user\033[0m")
    except Exception as e:
        print(f"\033[1;31m[✗] Unexpected error: {e}\033[0m")