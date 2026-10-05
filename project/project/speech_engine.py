import pyttsx3
import threading
import time
import queue

tts_queue = queue.Queue(maxsize=3)  

def tts_worker():
    engine = pyttsx3.init("sapi5")
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[0].id)
    engine.setProperty("rate", 180)
    engine.setProperty("volume", 1.0)

    engine.startLoop(False)

    while True:
        try:
            text = tts_queue.get(timeout=0.1)

            engine.say(text)

            while engine.isBusy():
                engine.iterate()
                time.sleep(0.01)

            tts_queue.task_done()

        except queue.Empty:
            engine.iterate()
            time.sleep(0.01)

    engine.endLoop()

threading.Thread(target=tts_worker, daemon=True).start()


def speak(audio: str):
    try:
        tts_queue.put_nowait(audio)
    except queue.Full:
        _ = tts_queue.get_nowait()
        tts_queue.put_nowait(audio)
