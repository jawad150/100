"""v2 timeline: 11 picture shots + end card, cut points taken from the narration's word timings."""
import json, os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = json.load(open(os.path.join(B, 'audio', 'vo', 'lines.json')))
R = json.load(open(os.path.join(B, 'audio', 'rec_durs.json')))
def w(L, word_idx): return V[L]['words'][word_idx]['s']
t = {}
t['L1'] = 0.45
s1_end = t['L1'] + V['L1']['dur'] + 0.4
t['L2'] = s1_end + 0.15
s2_end = t['L2'] + V['L2']['dur'] + 0.5
t['rec5'] = s2_end + 0.8
t['rec6'] = t['rec5'] + R['094005'] + 0.35
t['L3'] = t['rec6'] + R['094006'] + 0.6
s3_end = t['L3'] + V['L3']['dur'] + 0.9
t['L4'] = s3_end + 0.35
s4a_end = t['L4'] + w('L4', 4) - 0.08            # cut just before "Not only after..."
s4_end = t['L4'] + V['L4']['dur'] + 0.45
t['L5'] = s4_end + 0.2
s5a_end = t['L5'] + w('L5', 7) - 0.12            # cut just before "someone who sits with you"
s5_end = t['L5'] + V['L5']['dur'] + 0.6   # hold on the consoling shot a beat longer
t['L6'] = s5_end + 0.12                         # phone buzz lands on the cut, voice right after
s6_end = t['L6'] + V['L6']['dur'] + 0.2
t['L7'] = s6_end + 0.15
s7_end = t['L7'] + V['L7']['dur'] + 0.3
t['L8'] = s7_end + 0.15
s8a_end = t['L8'] + w('L8', 5) - 0.12           # cut just before "support is just a conversation away"
s8_end = t['L8'] + V['L8']['dur'] + 0.7
t['L9'] = s8_end + 0.45
end = s8_end + 7.3
shots = [
 ('window', 0.0, s1_end), ('man', s1_end, s2_end), ('verse', s2_end, s3_end),
 ('umbrella', s3_end, s4a_end), ('with2', s4a_end, s4_end),
 ('ease', s4_end, s5a_end), ('console', s5a_end, s5_end),
 ('phonep', s5_end, s6_end), ('bmhc', s6_end, s7_end),
 ('inside', s7_end, s8a_end), ('convo', s8a_end, s8_end),
 ('endcard', s8_end, end),
]
tl = {'vo': {k: round(v, 3) for k, v in t.items()},
      'shots': [{'name': n, 'start': round(a, 3), 'end': round(b, 3)} for n, a, b in shots],
      'end': round(end, 3)}
json.dump(tl, open(os.path.join(B, 'timeline.json'), 'w'), indent=1)
for s in tl['shots']: print(f"{s['name']:9s} {s['start']:6.2f} -> {s['end']:6.2f}  ({s['end']-s['start']:.2f}s)")
print(tl['vo'], 'END', tl['end'])
