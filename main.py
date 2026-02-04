# root/main.py (Updated with Engines 001-006)
import threading
import time

from engines.engine_002.mother_core import MotherEngine
from engines.engine_001_uig.controller import UIGController
from engines.engine_001_uig.listeners import TextListener, AudioListener, EventListener, SignalListener
from engines.engine_001_uig.normalizer import Normalizer
from engines.engine_001_uig.gateway import UIGGateway
from engines.engine_001_uig.mother_stub import MotherEngineStub

# Import Engine 003 (Perception Layer)
from engines.engine_003_010_perception_layer.controller import UIPController

# Import Engine 004 (Session Manager)
from engines.engine_004_session.controller import SessionController

# Import Engine 005 (Conscious/Understanding Engine)
from engines.engine_005_conscious.controller import ConsciousController

# NEW: Import Engine 006 (Signal Classifier)
from engines.engine_006_signal_classifier.controller import SignalClassifierController


# ---------------- Listener Loop ----------------
def listener_loop(listener, normalizer, gateway, controller):
    """
    Continuously listens for input, normalizes messages, and forwards to Gateway.
    Each listener runs in its own thread.
    """
    while controller.engine_on:
        # Skip if the channel is disabled
        if isinstance(listener, TextListener) and not controller.text_enabled:
            time.sleep(0.1)
            continue
        if isinstance(listener, AudioListener) and not controller.audio_enabled:
            time.sleep(0.1)
            continue
        if isinstance(listener, EventListener) and not controller.events_enabled:
            time.sleep(0.1)
            continue
        if isinstance(listener, SignalListener) and not controller.signals_enabled:
            time.sleep(0.1)
            continue

        # Capture message
        try:
            msg = listener.listen()
            if msg is None:
                continue
        except Exception as e:
            print(f"[Listener Error] {listener.__class__.__name__}: {e}")
            continue

        # Normalize message
        normalized_msg = normalizer.normalize(msg)

        # Forward to Gateway → MotherEngine
        gateway.forward(normalized_msg)

        time.sleep(0.05)  # prevent CPU spike


# ---------------- Engine Health Monitor ----------------
def monitor_engines(engines):
    """Monitor engine health periodically"""
    while True:
        time.sleep(10)  # Check every 10 seconds

        for name, controller in engines.items():
            if hasattr(controller, 'is_running'):
                if not controller.is_running():
                    print(f"[Health Monitor] WARNING: {name} is not running!")

            # Log engine status
            if hasattr(controller, 'get_status'):
                status = controller.get_status()
                print(f"[Health Monitor] {name}: {status.get('status', 'unknown')}")


# ---------------- Root Main ----------------
def main():
    print("[ROOT MAIN] Starting Engine 001-006...")
    print("[ROOT MAIN] Architecture: 001 → 002 → 003 → 004 → 005 → 006 → ...")

    # Dictionary to track all engines
    all_engines = {}

    # ---------------- Engine 003: Perception Engine ----------------
    print("[ROOT MAIN] Starting Engine 003 Perception Engine...")
    engine_003_controller = UIPController()
    engine_003_controller.start()
    all_engines['Engine_003'] = engine_003_controller
    print("[ROOT MAIN] Engine 003 started (listening on port 57003).")

    # ---------------- Engine 004: Session Manager ----------------
    print("[ROOT MAIN] Starting Engine 004 Session Manager...")
    engine_004_controller = SessionController()
    engine_004_controller.start()
    all_engines['Engine_004'] = engine_004_controller
    print("[ROOT MAIN] Engine 004 started (listening on port 57004).")

    # ---------------- Engine 005: Conscious/Understanding Engine ----------------
    print("[ROOT MAIN] Starting Engine 005 Understanding Engine...")
    engine_005_controller = ConsciousController()
    engine_005_controller.start()
    all_engines['Engine_005'] = engine_005_controller
    print("[ROOT MAIN] Engine 005 started (listening on port 57005).")

    # ---------------- Engine 006: Signal Classifier ----------------
    print("[ROOT MAIN] Starting Engine 006 Signal Classifier...")
    engine_006_controller = SignalClassifierController()
    engine_006_controller.start()
    all_engines['Engine_006'] = engine_006_controller
    print("[ROOT MAIN] Engine 006 started (listening on port 57006).")
    print("[ROOT MAIN] Engine 006 connected to Engine 005: ✓")

    # ---------------- Engine 002: Mother Engine ----------------
    print("[ROOT MAIN] Starting Engine 002 Mother Engine...")
    mother_engine = MotherEngine()
    me_thread = threading.Thread(target=mother_engine.start)
    me_thread.daemon = True
    me_thread.start()
    all_engines['Engine_002'] = mother_engine
    print("[ROOT MAIN] Mother Engine started.")

    # ---------------- Engine 001: UIG ----------------
    print("[ROOT MAIN] Starting Engine 001 UIG...")
    controller = UIGController()
    normalizer = Normalizer()
    gateway = UIGGateway(MotherEngineStub(mother_engine))

    listeners = [
        TextListener(source_device="pc"),
        AudioListener(source_device="microphone", duration=2),
        EventListener(source_device="system_events"),
        SignalListener(source_device="iot_sensor")
    ]

    threads = []
    for listener in listeners:
        t = threading.Thread(target=listener_loop, args=(listener, normalizer, gateway, controller))
        t.daemon = True
        t.start()
        threads.append(t)

    all_engines['Engine_001'] = controller
    print("[ROOT MAIN] Engine 001 UIG started.")

    # Start health monitor
    monitor_thread = threading.Thread(target=monitor_engines, args=(all_engines,), daemon=True)
    monitor_thread.start()

    print("\n" + "=" * 60)
    print("[ROOT MAIN] ALL ENGINES (001-006) RUNNING")
    print("=" * 60)
    print("Data Flow: 001 → 002 → 003 → 004 → 005 → 006")
    print("Ports: 57003(3), 57004(4), 57005(5), 57006(6)")
    print("=" * 60 + "\n")

    # ---------------- Keep root alive ----------------
    try:
        while controller.engine_on:
            # Monitor engine status
            status_msgs = []
            for name, eng in all_engines.items():
                if hasattr(eng, 'is_running'):
                    if not eng.is_running():
                        status_msgs.append(f"{name}: ❌ NOT RUNNING")
                    else:
                        if hasattr(eng, 'get_status'):
                            status = eng.get_status()
                            status_msgs.append(f"{name}: ✓ ({status.get('status', 'running')})")
                        else:
                            status_msgs.append(f"{name}: ✓")

            # Log status every 30 seconds
            if int(time.time()) % 30 == 0:
                print("\n" + "-" * 40)
                print("[ROOT MAIN] Engine Status:")
                for msg in status_msgs:
                    print(f"  {msg}")
                print("-" * 40 + "\n")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[ROOT MAIN] Keyboard interrupt received. Shutting down...")
        controller.engine_on = False

        # Stop engines in reverse order (006 → 005 → 004 → 003 → 002 → 001)
        print("\n[ROOT MAIN] Shutting down engines...")

        print("[ROOT MAIN] Stopping Engine 006 Signal Classifier...")
        engine_006_controller.stop()

        print("[ROOT MAIN] Stopping Engine 005 Understanding Engine...")
        engine_005_controller.stop()

        print("[ROOT MAIN] Stopping Engine 004 Session Manager...")
        engine_004_controller.stop()

        print("[ROOT MAIN] Stopping Engine 003 Perception Engine...")
        engine_003_controller.stop()

        print("[ROOT MAIN] Stopping Mother Engine...")
        mother_engine.stop()

    # ---------------- Cleanup ----------------
    print("[ROOT MAIN] Waiting for threads to finish...")
    for t in threads:
        t.join(timeout=1)

    me_thread.join(timeout=1)
    print("[ROOT MAIN] All engines stopped.")


if __name__ == "__main__":
    main()