import sys  # <--- CRITICAL IMPORT
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

# --- CONFIGURATION: Measured Container Weights ---
CONTAINERS = {
    'none': 0.0,
    'bento_box': 21.73,
    'small_metal': 75.73,
    'metal_bowl': 87.78,
    'big_metal': 139.13
}

# --- GLOBAL STATE (In-Memory) ---
CURRENT_RAW_WEIGHT = 0.0
CURRENT_CONTAINER = 'none'

@csrf_exempt
def receive_raw(request):
    # --- SILENCE THE LOGS (STEALTH MODE) ---
    # The data still arrives, but the terminal stays clean.
    
    # sys.stdout.write(f"\n[HIT] Method: {request.method} | Body: {request.body[:50]}...\n")  <-- COMMENT THIS
    # sys.stdout.flush()                                                                      <-- COMMENT THIS

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            global CURRENT_RAW_WEIGHT
            CURRENT_RAW_WEIGHT = data.get('raw_weight', 0.0)
            
            # sys.stdout.write(f" -> SUCCESS! Updated Weight to: {CURRENT_RAW_WEIGHT}\n")   <-- COMMENT THIS
            # sys.stdout.flush()                                                             <-- COMMENT THIS
            
            return JsonResponse({'status': 'ok'})
        except:
            pass
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def select_container(request):
    """
    ENDPOINT 2: Frontend calls this when User selects a bowl.
    URL: /api/weights/select-container/
    """
    global CURRENT_CONTAINER
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            key = data.get('container', 'none')
            if key in CONTAINERS:
                CURRENT_CONTAINER = key
                sys.stdout.write(f"[UI ACTION] User selected: {key}\n")
                sys.stdout.flush()
                return JsonResponse({'status': 'ok', 'selected': key})
        except:
            pass
    return JsonResponse({'status': 'error'}, status=400)

def get_net_weight(request):
    """
    ENDPOINT 3: Frontend calls this to display "Food Weight".
    URL: /api/weights/get-net-weight/
    """
    offset = CONTAINERS.get(CURRENT_CONTAINER, 0.0)
    net_weight = CURRENT_RAW_WEIGHT - offset
    
    return JsonResponse({
        'net_weight': round(net_weight, 2),
        'raw_weight': CURRENT_RAW_WEIGHT,
        'container': CURRENT_CONTAINER
    })