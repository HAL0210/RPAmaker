import threading
import time
from lib.paramSetting import getParam, setParam
from lib.loggerSetting import getMyLogger
from functools import wraps
import inspect

nest = 0
hide = False

from tqdm import tqdm
import threading
import time

def show_elapsed(start_time, stop_event):
    pbar = tqdm(
        total=1.0, 
        bar_format="{desc}", 
        position=0,  # positionを0に固定
        leave=False,  # 終了後バーを残さない
        ncols=50,    # 表示幅を固定
    )
    while not stop_event.is_set():
        elapsed = time.perf_counter() - start_time
        seconds = int(elapsed)
        milliseconds = int((elapsed - seconds) * 1000)
        pbar.set_description_str(
            f"Elapsed time: {seconds}.{milliseconds:03d}s"
        )
        pbar.refresh()
        MEASURE_INTERVAL = float(getParam('MEASURE_INTERVAL', '0.01'))
        time.sleep(MEASURE_INTERVAL)
    pbar.close()

def instrumented(timer=False, log_level=10):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            global nest, hide
            
            temp_hide = getParam('temp_hide', False)
            if temp_hide:
                hide = True
                setParam('temp_hide', False)
            
            try:
                func_name = func.__name__
                logger = getMyLogger(func_name)

                bound_args = inspect.signature(func).bind(*args, **kwargs)
                bound_args.apply_defaults()
                
                signature = ", ".join(f"{k}={v!r}" for k, v in bound_args.arguments.items())
                if hide:
                    signature = '***'

                nest += 1
                prefix = " " * (nest - 1) + "→"
                logger.log(log_level, f"|{prefix} Run    {func_name}({signature})")

                stop_event = None
                timer_thread = None
                start_time = time.perf_counter() if timer else None

                if timer and getParam('ch.level') == 'DEBUG':
                    stop_event = threading.Event()
                    timer_thread = threading.Thread(
                        target=show_elapsed,
                        args=(start_time, stop_event)
                    )
                    timer_thread.start()

                result = func(*args, **kwargs)

                elapsed = time.perf_counter() - start_time if timer else 0
                log_suffix  = f"(Elapsed: {elapsed:.3f}s)" if timer  else ""
                log_suffix += f"(return: {result})" if result is not None else ""
                prefix = " " * (nest - 1) + "←"
                nest -= 1

                logger.log(log_level, f"|{prefix} Done   {func_name}({signature}) {log_suffix}")
            except (KeyboardInterrupt, SystemExit) as e:
                prefix = " " * (nest - 1) + "←"
                nest -= 1
                logger.log(log_level, f"|{prefix} Quit   {func_name}({signature})")
                raise
            except Exception as e:
                prefix = " " * (nest - 1) + "X"
                nest -= 1
                logger.log(log_level, f"|{prefix} Failed {func_name}({signature})")
                raise
            finally:
                if stop_event is not None:
                    stop_event.set()
                    timer_thread.join()
                
                if temp_hide:
                    hide = False

            return result
        return wrapper
    return decorator

def retryCounter(max_retry=None, retry_interval=None, breakException=None):
    if breakException is None:
        breakException = []

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retry_count = 0            
            _max_retry = (
                getParam(max_retry) if isinstance(max_retry, str)
                else max_retry if max_retry is not None
                else getParam('retry.max_count', 20)
            )
            _retry_interval = (
                getParam(retry_interval) if isinstance(retry_interval, str)
                else retry_interval if retry_interval is not None
                else getParam('retry.interval', 0.5)
            )
            while True:
                try:
                    result = func(*args, **kwargs)
                    return result
                except tuple(breakException) as e:
                    logger = getMyLogger(func.__name__)
                    logger.warning(str(e))
                    raise
                except Exception as e:
                    logger = getMyLogger(func.__name__)
                    logger.debug(str(e))
                    if retry_count >= _max_retry:
                        raise
                    retry_count += 1
                    time.sleep(_retry_interval)
                    
        return wrapper
    return decorator
