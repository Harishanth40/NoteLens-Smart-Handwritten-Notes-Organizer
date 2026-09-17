import re

SUBJECT_KEYWORDS = {
    'Operating Systems': [
        'deadlock', 'process', 'semaphore', 'scheduling', 'paging', 'segmentation', 
        'memory management', 'virtual memory', 'thread', 'mutual exclusion', 'banker', 
        'fifo', 'lru', 'thrashing', 'kernel', 'mutex', 'race condition', 'cpu scheduling', 
        'fork', 'context switch', 'interprocess', 'page fault', 'critical section'
    ],
    'Java': [
        'class', 'object', 'inheritance', 'polymorphism', 'encapsulation', 'interface', 
        'exception', 'jvm', 'constructor', 'package', 'abstract', 'override', 'overload', 
        'arraylist', 'hashmap', 'string', 'try catch', 'final', 'static', 'extends', 
        'implements', 'garbage collector', 'bytecode', 'public static void main'
    ],
    'DBMS': [
        'database', 'sql', 'normalization', 'relation', 'primary key', 'foreign key', 
        'transaction', 'b-tree', 'er model', 'entity', 'acid', 'join', 'indexing', 
        'select', 'query', 'table', 'schema', '1nf', '2nf', '3nf', 'bcnf', 'trigger', 
        'relational', 'ddl', 'dml', 'commit', 'rollback'
    ],
    'Computer Networks': [
        'osi', 'tcp', 'udp', 'ip', 'routing', 'congestion', 'network', 'protocol', 
        'ethernet', 'mac', 'socket', 'packet', 'subnet', 'dns', 'http', 'router', 
        'switch', 'latency', 'bandwidth', 'handshake', 'payload', 'frame', 'gateway', 
        'icmp', 'arp', 'topology'
    ],
    'Python': [
        'python', 'list', 'tuple', 'dictionary', 'function', 'module', 'pip', 
        'indentation', 'lambda', 'list comprehension', 'def', 'import', 'kwargs', 
        'args', 'pandas', 'numpy', 'flask', 'django', 'decorator', 'self', 'range', 
        'virtualenv', 'generator'
    ],
    'Data Structures': [
        'stack', 'queue', 'linked list', 'tree', 'graph', 'array', 'heap', 
        'binary search tree', 'bst', 'traversal', 'bfs', 'dfs', 'recursion', 
        'node', 'hash table', 'push', 'pop', 'enqueue', 'dequeue', 'pointer', 
        'time complexity', 'big o', 'avltree'
    ],
    'Software Engineering': [
        'agile', 'waterfall', 'sdlc', 'requirement', 'design pattern', 'testing', 
        'refactoring', 'scrum', 'uml', 'use case', 'deployment', 'maintainability', 
        'architecture', 'modularity', 'unit test', 'integration test', 'devops', 
        'version control', 'ci/cd'
    ],
    'Artificial Intelligence': [
        'artificial intelligence', 'search algorithm', 'knowledge representation', 
        'expert system', 'heuristic', 'minimax', 'alpha beta', 'agent', 'planning', 
        'resolution', 'prolog', 'first order logic', 'inference engine', 'search tree', 
        'a* search', 'dfs search', 'bfs search'
    ],
    'Machine Learning': [
        'regression', 'classification', 'dataset', 'training', 'model', 'accuracy', 
        'feature', 'neural network', 'deep learning', 'loss function', 'gradient descent', 
        'supervised', 'unsupervised', 'clustering', 'svm', 'random forest', 
        'precision', 'recall', 'epoch', 'overfitting', 'hyperparameter'
    ],
    'Cyber Security': [
        'encryption', 'authentication', 'malware', 'firewall', 'vulnerability', 
        'security', 'cryptography', 'rsa', 'aes', 'hash', 'zero day', 'phishing', 
        'authorization', 'token', 'cipher', 'symmetric', 'asymmetric', 'trojan', 
        'buffer overflow', 'penetration testing', 'xss', 'csrf'
    ],
    'Digital Signal Processing': [
        'dsp', 'signal', 'sampling', 'fourier transform', 'fft', 'z transform', 
        'filter', 'fir', 'iir', 'frequency', 'spectrum', 'convolution', 
        'impulse response', 'aliasing', 'nyquist', 'quantization', 'dft', 'bode plot'
    ]
}

def detect_subject(text):
    """
    Detects subject category based on keyword scoring.
    Returns tuple: (detected_subject, confidence_score)
    """
    if not text or not text.strip():
        return ('Other', 0.0)

    text_lower = text.lower()
    subject_scores = {}

    for subject, keywords in SUBJECT_KEYWORDS.items():
        score = 0
        matches = 0
        for kw in keywords:
            # Word boundary search or exact phrase match
            pattern = r'\b' + re.escape(kw) + r'\b'
            found = len(re.findall(pattern, text_lower))
            if found > 0:
                score += (found * (len(kw.split()) + 1))  # Give higher weight to multi-word phrases
                matches += found

        if score > 0:
            subject_scores[subject] = (score, matches)

    if not subject_scores:
        return ('Other', 10.0)

    # Sort subjects by score descending
    best_subject, (best_score, best_matches) = max(subject_scores.items(), key=lambda item: item[1][0])

    # Calculate confidence percentage (capped at 98.5%)
    # Base confidence calculation based on match count and score relative to text length
    words_in_text = len(text_lower.split())
    density = min(1.0, (best_matches * 5) / max(1, words_in_text))
    
    confidence = min(98.5, max(45.0, round(50.0 + (best_score * 8.0) + (density * 30.0), 1)))

    # If score is too weak (e.g. only 1 tiny match in long text), drop to Other
    if best_score < 2:
        return ('Other', 30.0)

    return (best_subject, confidence)
