import sys
sys.stdout.reconfigure(encoding='utf-8')
for name in ['JDAnalysis.tsx', 'ResumeBuilder.tsx']:
    path = 'E:/学习/AI Job Hunt Assistant/frontend/src/pages/' + name
    with open(path, 'r', encoding='utf-8') as f:
        c = f.read()
    print(name, 'len:', len(c), 'lines:', c.count('\n'), 'exportAsPng:', c.count('exportAsPng'))
