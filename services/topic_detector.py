import re
from collections import Counter

TOPIC_DICTIONARY = {
    'Operating Systems': {
        'Deadlock': ['deadlock', 'banker', 'hold and wait', 'circular wait', 'resource allocation', 'preemption', 'starvation'],
        'Paging': ['paging', 'page table', 'page fault', 'tlb', 'frame', 'page replacement', 'lru', 'fifo page'],
        'Segmentation': ['segmentation', 'segment table', 'base address', 'limit register', 'segment fault'],
        'Process Scheduling': ['scheduling', 'fcfs', 'sjf', 'round robin', 'priority scheduling', 'gantt chart', 'cpu scheduling', 'turnaround time'],
        'Memory Management': ['memory management', 'virtual memory', 'contiguous', 'fragmentation', 'swapping', 'allocation'],
        'Synchronization & Semaphores': ['semaphore', 'mutex', 'critical section', 'race condition', 'peterson', 'producer consumer', 'monitor']
    },
    'Java': {
        'OOP (Object Oriented Programming)': ['class', 'object', 'encapsulation', 'abstraction', 'state', 'method'],
        'Inheritance & Polymorphism': ['inheritance', 'polymorphism', 'extends', 'implements', 'override', 'overload', 'super', 'subclass'],
        'Exception Handling': ['exception', 'try catch', 'finally', 'throw', 'throws', 'nullpointerexception', 'custom exception'],
        'Multithreading': ['thread', 'multithreading', 'runnable', 'synchronized', 'lock', 'executor', 'volatile', 'deadlock'],
        'Collections Framework': ['arraylist', 'hashmap', 'hashset', 'linkedlist', 'iterator', 'comparator', 'collections', 'map', 'list', 'set'],
        'JVM Architecture': ['jvm', 'bytecode', 'garbage collector', 'heap', 'stack memory', 'classloader']
    },
    'DBMS': {
        'Normalization': ['normalization', '1nf', '2nf', '3nf', 'bcnf', 'functional dependency', 'partial dependency', 'transitive dependency', 'lossless'],
        'SQL & Queries': ['sql', 'select', 'where', 'group by', 'having', 'join', 'inner join', 'left join', 'subquery', 'insert', 'update'],
        'Transactions & ACID': ['transaction', 'acid', 'atomicity', 'consistency', 'isolation', 'durability', 'commit', 'rollback', '2pl', 'concurrency'],
        'Indexing & B-Trees': ['index', 'b-tree', 'b+ tree', 'clustered index', 'hash index', 'search key'],
        'ER Modeling': ['er model', 'entity', 'attribute', 'relationship', 'cardinality', 'primary key', 'foreign key', 'weak entity']
    },
    'Computer Networks': {
        'OSI & TCP/IP Model': ['osi', 'tcp/ip', 'physical layer', 'data link', 'network layer', 'transport layer', 'application layer'],
        'Routing & Congestion Control': ['routing', 'dijkstra', 'distance vector', 'link state', 'congestion', 'leaky bucket', 'token bucket', 'bgp', 'ospf'],
        'Transport Protocols (TCP/UDP)': ['tcp', 'udp', 'three way handshake', 'sliding window', 'flow control', 'port number', 'segment'],
        'Application Protocols': ['http', 'https', 'dns', 'ftp', 'smtp', 'dhcp', 'domain name', 'url'],
        'Data Link & Ethernet': ['ethernet', 'mac address', 'framing', 'csma/cd', 'error detection', 'crc', 'parity']
    },
    'Python': {
        'Data Structures': ['list', 'tuple', 'dictionary', 'set', 'slicing', 'comprehension', 'mutable', 'immutable'],
        'Functions & Modules': ['def', 'lambda', 'args', 'kwargs', 'return', 'import', 'module', 'package', 'scope', 'decorator'],
        'Object Oriented Python': ['class', 'self', '__init__', 'inheritance', 'property', 'dunder', 'method'],
        'Exception Handling & File I/O': ['try except', 'raise', 'with open', 'read', 'write', 'file handling'],
        'Data Science Libraries': ['pandas', 'numpy', 'matplotlib', 'dataframe', 'series', 'array', 'plot']
    },
    'Data Structures': {
        'Stacks & Queues': ['stack', 'queue', 'push', 'pop', 'enqueue', 'dequeue', 'top', 'front', 'rear', 'lifo', 'fifo'],
        'Linked Lists': ['linked list', 'singly', 'doubly', 'circular', 'head', 'tail', 'next pointer', 'node'],
        'Trees & BST': ['tree', 'binary tree', 'binary search tree', 'bst', 'inorder', 'preorder', 'postorder', 'root', 'leaf', 'height'],
        'Graph Algorithms': ['graph', 'bfs', 'dfs', 'adjacency matrix', 'adjacency list', 'topological sort', 'shortest path', 'vertex', 'edge'],
        'Sorting & Searching': ['bubble sort', 'quick sort', 'merge sort', 'insertion sort', 'selection sort', 'binary search', 'linear search'],
        'Heaps & Priority Queues': ['heap', 'min heap', 'max heap', 'heapify', 'priority queue']
    },
    'Software Engineering': {
        'SDLC & Process Models': ['sdlc', 'waterfall', 'agile', 'scrum', 'spiral', 'sprint', 'kanban', 'iterative'],
        'Architecture & Design Patterns': ['design pattern', 'singleton', 'factory', 'observer', 'mvc', 'microservices', 'modularity', 'cohesion', 'coupling'],
        'Software Testing & QA': ['unit test', 'integration test', 'system test', 'black box', 'white box', 'test case', 'bug', 'qa', 'code coverage']
    },
    'Artificial Intelligence': {
        'Search Algorithms': ['a*', 'bfs', 'dfs', 'heuristic', 'greedy search', 'state space', 'search tree'],
        'Knowledge Representation & Logic': ['first order logic', 'propositional logic', 'resolution', 'inference engine', 'knowledge base', 'ontologies'],
        'Game Playing': ['minimax', 'alpha beta pruning', 'evaluation function', 'utility', 'game tree'],
        'Expert Systems': ['expert system', 'rule based', 'forward chaining', 'backward chaining', 'fact base']
    },
    'Machine Learning': {
        'Supervised Learning & Regression': ['regression', 'linear regression', 'logistic regression', 'supervised', 'cost function', 'dependent variable'],
        'Classification & Decision Trees': ['classification', 'decision tree', 'random forest', 'svm', 'naive bayes', 'knn', 'confusion matrix'],
        'Neural Networks & Deep Learning': ['neural network', 'cnn', 'rnn', 'perceptron', 'backpropagation', 'epoch', 'activation function', 'relu', 'loss'],
        'Model Evaluation & Metrics': ['accuracy', 'precision', 'recall', 'f1 score', 'roc curve', 'overfitting', 'underfitting', 'cross validation'],
        'Clustering & Unsupervised': ['k-means', 'clustering', 'unsupervised', 'pca', 'dimensionality reduction', 'silhouette']
    },
    'Cyber Security': {
        'Cryptography & Encryption': ['encryption', 'decryption', 'rsa', 'aes', 'public key', 'private key', 'hash', 'sha256', 'cipher', 'digital signature'],
        'Network & Web Security': ['firewall', 'ids', 'ips', 'vpn', 'ssl/tls', 'https', 'xss', 'csrf', 'sql injection', 'ddos'],
        'Malware & Vulnerabilities': ['malware', 'virus', 'worm', 'trojan', 'ransomware', 'zero day', 'phishing', 'exploit', 'vulnerability']
    },
    'Digital Signal Processing': {
        'Fourier & Z-Transforms': ['fourier transform', 'dft', 'fft', 'z transform', 'frequency domain', 'spectrum', 'poles and zeros'],
        'Digital Filters': ['filter', 'fir', 'iir', 'low pass', 'high pass', 'band pass', 'butterworth', 'chebyshev'],
        'Sampling & Quantization': ['sampling', 'nyquist', 'aliasing', 'quantization', 'snr', 'impulse response', 'convolution']
    }
}

def detect_topic(text, subject):
    """
    Detects topic based on text content and identified subject.
    Returns detected topic string.
    """
    if not text or not text.strip():
        return 'General Concepts'

    text_lower = text.lower()

    # Check subject dictionary first
    if subject in TOPIC_DICTIONARY:
        topic_scores = {}
        for topic, keywords in TOPIC_DICTIONARY[subject].items():
            score = 0
            for kw in keywords:
                pattern = r'\b' + re.escape(kw) + r'\b'
                score += len(re.findall(pattern, text_lower))
            if score > 0:
                topic_scores[topic] = score

        if topic_scores:
            best_topic = max(topic_scores.items(), key=lambda x: x[1])[0]
            return best_topic

    # Heuristic fallback: check first heading/line or highest frequency capitalized/technical word
    first_line = text.strip().split('\n')[0].strip()
    if len(first_line) > 3 and len(first_line) < 40 and not any(char in first_line for char in ['{', '}', ';', '=']):
        # Clean title-like line
        return first_line.title()

    # Fallback to general topic
    return 'General Concepts'
