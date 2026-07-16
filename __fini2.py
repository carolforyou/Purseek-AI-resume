import sys, subprocess
sys.stdout.reconfigure(encoding='utf-8')

# Fix duplicate exportAsPng in JDAnalysis.tsx
jd = r'E:\学习\AI Job Hunt Assistant\frontend\src\pages\JDAnalysis.tsx'
with open(jd, 'r', encoding='utf-8') as f:
    jst = f.read()

# Remove duplicate exportAsPng (there should be only one)
# Count how many there are
cnt = jst.count('const exportAsPng')
if cnt > 1:
    # Remove all but the first occurrence
    first = jst.find('const exportAsPng')
    if first >= 0:
        # Find where this function ends and the next one starts
        second = jst.find('const exportAsPng', first + 10)
        if second >= 0:
            # Find where the first one ends (return before the next function)
            before = jst[:second]
            after = jst[second:]
            # Remove the second occurrence
            # Find the end of the function (next '  return (' or 'const')
            func_end = after.find('  const', 10)
            if func_end >= 0:
                after = after[:jst.find('const', 10)]  # wrong, let me be more careful
            # Simpler: just keep the first occurrence
            # Remove everything between first occurrence's end and the content before second occurrence
            first_end = first + jst[first:].find('\n  return (')
            # Keep first occurrence plus everything from second occurrence onwards
            second_start = second
            second_end = second + jst[second:].find('\n  };\n') + 5
            jst = before + after[second_end - second:]
    
    # Actually simpler: just count occurances and handle
    first_idx = jst.find('const exportAsPng')
    last_idx = jst.rfind('const exportAsPng')
    if first_idx != last_idx:
        # Remove everything between the end of first occurrence and start of last_idx
        first_end = first_idx + jst[first_idx:].find('\n  };\n') + 5
        jst = jst[:first_end] + jst[last_idx:]

with open(jd, 'w', encoding='utf-8') as f:
    f.write(jst)

# Also fix ctx null with non-null assertion
with open(jd, 'r', encoding='utf-8') as f:
    jst = f.read()

jst = jst.replace('const ctx = canvas.getContext("2d");', 'const ctx = canvas.getContext("2d")!;')
jst = jst.replace('ctx.scale', 'ctx!.scale')
jst = jst.replace('ctx.drawImage', 'ctx!.drawImage')
# Fix the comparison: (ctx) is possibly null -> ctx is not null in this context

# Remove duplicate PNG button
# The inline one was duplicated in the modal section
jst = jst.replace('React.createElement("button", { onClick: function() { doExport("pdf"); } }, "PDF"), React.createElement("button", { onClick: function() { doExport("png"); } }, "PNG")',
                  'React.createElement("button", { onClick: function() { doExport("pdf"); } }, "PDF")')

with open(jd, 'r', encoding='utf-8') as f:
    jst2 = f.read()
# Fix again for the remaining
jst2 = jst2.replace('const ctx = canvas.getContext("2d");', 'const ctx = canvas.getContext("2d")!;')
jst2 = jst2.replace('ctx.scale', 'ctx!.scale')
jst2 = jst2.replace('ctx.drawImage', 'ctx!.drawImage')
with open(jd, 'w', encoding='utf-8') as f:
    f.write(jst2)

print('Fixed JDAnalysis.tsx duplicates and ctx')

# Do similar for ResumeBuilder.tsx
rb = r'E:\学习\AI Job Hunt Assistant\frontend\src\pages\ResumeBuilder.tsx'
with open(rb, 'r', encoding='utf-8') as f:
    rbt = f.read()

cnt2 = rbt.count('const exportAsPng')
if cnt2 > 1:
    first = rbt.find('const exportAsPng')
    last = rbt.rfind('const exportAsPng')
    first_end = first + rbt[first:].find('\n  };\n') + 5
    rbt = rbt[:first_end] + rbt[last:]

# Fix ctx
rbt = rbt.replace('const ctx = canvas.getContext("2d");', 'const ctx = canvas.getContext("2d")!;')
rbt = rbt.replace('ctx.scale', 'ctx!.scale')
rbt = rbt.replace('ctx.drawImage', 'ctx!.drawImage')

with open(rb, 'w', encoding='utf-8') as f:
    f.write(rbt)
print('Fixed ResumeBuilder.tsx')

# Verify TS
r = subprocess.run(["cmd", "/c", "npx tsc --noEmit 2>&1"], capture_output=True, text=True,
                   cwd=r"E:\学习\AI Job Hunt Assistant\frontend", timeout=20)
errs = [l for l in (r.stderr + r.stdout).split(chr(10)) if "error TS" in l]
print(f"TS errors: {len(errs)}")
for e in errs[:5]: print(e.strip())
if not errs: print("ALL CLEAN")
