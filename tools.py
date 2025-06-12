import platform
import json

def get_host_info() -> str:
    """
    Retrieves system information about the current device.
    
    Returns:
        str: A JSON string containing system information such as CPU count and architecture.
    """
    system_info = {
        "os": platform.system(),
        "architecture": platform.machine(),
        "platform": platform.platform()
    }
    return json.dumps(system_info)

if __name__ == "__main__":
    print(get_host_info())
    