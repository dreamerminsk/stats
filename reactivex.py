from threading import current_thread

import rx

r = rx.timer(100
             , 1000) \
    .subscribe_(on_next=lambda i: print("PROCESS 3: {0} {1}".format(current_thread().name, i)),
                on_error=lambda e: print(e))

print(r)
text = input("prompt")
