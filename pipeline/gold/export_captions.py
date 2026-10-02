"""Write the synced Roman Urdu captions as SRT (one cue per on-screen phrase) for use in AE/Premiere."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import gold_reel as R


def ts(x):
    ms = int(round(x * 1000))
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else R.S + '/out/captions_roman_urdu.srt'
    with open(out, 'w', encoding='utf-8') as f:
        for n, ph in enumerate(R._parse_captions(), 1):
            text = '\n'.join(' '.join(w['text'] for w in row) for row in ph['rows'])
            f.write(f"{n}\n{ts(max(ph['t_on'], 0))} --> {ts(ph['t_off'])}\n{text}\n\n")
    print(out)
