import math

def softmax(logits):
    m=max(logits)
    ex=[math.exp(v-m) for v in logits]
    s=sum(ex) or 1.0
    return [e/s for e in ex]
