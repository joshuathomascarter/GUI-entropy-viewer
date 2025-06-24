import time
import random

def generate_log_entry(cycle, states, triggers):
    """Generates a single log entry string."""
    state = random.choice(states)
    entropy = random.randint(0, 255) # 8-bit entropy score
    trigger = random.choice(triggers)
    return f"[Cycle {cycle}] State: {state} | Entropy: {entropy} | Trigger: {trigger}"

def simulate_log_stream(output_filename="fsm_log.txt", num_entries=200, delay_seconds=0.1, continuous=False):
    """
    Simulates a real-time log stream and writes entries to a file.

    Args:
        output_filename (str): The name of the file to write logs to.
        num_entries (int): The total number of log entries to generate (ignored if continuous=True).
        delay_seconds (float): The delay between writing each log entry to the file.
        continuous (bool): If True, runs indefinitely. If False, stops after num_entries.
    """
    fsm_states = ["OK", "STALL", "FLUSH", "LOCK"]
    trigger_sources = ["ML", "Analog", "Entropy Logic", "AHO", "None"] # "None" for no specific trigger

    print(f"Starting log simulation. Writing to '{output_filename}'...")
    
    if continuous:
        print(f"Running in CONTINUOUS mode with {delay_seconds}-second delay between entries.")
        print("Press Ctrl+C to stop.")
    else:
        print(f"Generating {num_entries} entries with a {delay_seconds}-second delay between each.")

    try:
        with open(output_filename, 'w') as f:  # Clear the file first
            cycle = 1
            
            if continuous:
                # Run indefinitely
                while True:
                    log_entry = generate_log_entry(cycle, fsm_states, trigger_sources)
                    f.write(log_entry + '\n')
                    f.flush() # Ensure data is written to disk immediately
                    print(f"Logged: {log_entry}") # Print to console for real-time feedback
                    cycle += 1
                    time.sleep(delay_seconds)
            else:
                # Run for specified number of entries
                for cycle in range(1, num_entries + 1):
                    log_entry = generate_log_entry(cycle, fsm_states, trigger_sources)
                    f.write(log_entry + '\n')
                    f.flush() # Ensure data is written to disk immediately
                    print(f"Logged: {log_entry}") # Print to console for real-time feedback
                    time.sleep(delay_seconds)
                    
        if not continuous:
            print("\nLog simulation finished.")
            
    except KeyboardInterrupt:
        print("\nLog simulation stopped by user.")
    except Exception as e:
        print(f"An error occurred during log simulation: {e}")

if __name__ == "__main__":
    # Option 1: Run continuously (recommended for testing with dashboard)
    simulate_log_stream(continuous=True, delay_seconds=0.5)
    
    # Option 2: Run for specific number of entries (uncomment to use instead)
    # simulate_log_stream(num_entries=100, delay_seconds=0.1)