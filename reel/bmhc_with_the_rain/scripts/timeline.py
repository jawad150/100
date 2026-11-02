import json, os
B = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V = json.load(open(os.path.join(B, 'audio', 'vo', 'lines.json')))
R = json.load(open(os.path.join(B, 'audio', 'rec_durs.json')))
t = {}
t['L1'] = 0.35
s1_end = t['L1'] + V['L1']['dur'] + 0.45
t['L2'] = s1_end + 0.15
s2_end = t['L2'] + V['L2']['dur'] + 0.5
t['rec5'] = s2_end + 0.8
t['rec6'] = t['rec5'] + R['094005'] + 0.35
t['L3'] = t['rec6'] + R['094006'] + 0.6
s3_end = t['L3'] + V['L3']['dur'] + 0.9
t['L4'] = s3_end + 0.4
s4_end = t['L4'] + V['L4']['dur'] + 0.5
t['L5'] = s4_end + 0.2
s5_end = t['L5'] + V['L5']['dur'] + 0.25
t['L6'] = s5_end + 0.15
s6_end = t['L6'] + V['L6']['dur'] + 0.2
t['L7'] = s6_end + 0.1
s7_end = t['L7'] + V['L7']['dur'] + 0.15
t['L8'] = s7_end + 0.2
s8_end = t['L8'] + V['L8']['dur'] + 0.8
t['L9'] = s8_end + 0.3
end = s8_end + 6.3
shots = [
 {'id': 1, 'name': 'window', 'start': 0.0, 'end': s1_end},
 {'id': 2, 'name': 'man', 'start': s1_end, 'end': s2_end},
 {'id': 3, 'name': 'verse', 'start': s2_end, 'end': s3_end},
 {'id': 4, 'name': 'umbrella', 'start': s3_end, 'end': s4_end},
 {'id': 5, 'name': 'mug', 'start': s4_end, 'end': s5_end},
 {'id': 6, 'name': 'phone', 'start': s5_end, 'end': s6_end},
 {'id': 7, 'name': 'bmhc', 'start': s6_end, 'end': s8_end},
 {'id': 9, 'name': 'endcard', 'start': s8_end, 'end': end},
]
tl = {'vo': {k: round(v, 3) for k, v in t.items()}, 'shots': [{**s, 'start': round(s['start'], 3), 'end': round(s['end'], 3)} for s in shots],
      'door_line_end': round(s7_end, 3), 'end': round(end, 3)}
json.dump(tl, open(os.path.join(B, 'timeline.json'), 'w'), indent=1)
for s in tl['shots']: print(s)
print(tl['vo'], 'END', tl['end'])
